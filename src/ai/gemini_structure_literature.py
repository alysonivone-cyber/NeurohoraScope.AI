"""Structure PubMed abstracts with Gemini (offline ingestion step, one Gemini call per disease).

Pipeline: PubMed abstracts (raw text) -> Gemini structuring -> deterministic
validation -> deploy_data/gemini_structured_literature.json -> MCP tool.

Run locally (the Gemini key is read from the environment / .env, never printed):

    python -m src.ai.gemini_structure_literature
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
DISEASES = [
    "Alzheimer's disease",
    "Parkinson's disease",
    "multiple sclerosis",
    "amyotrophic lateral sclerosis",
    "Huntington's disease",
    "Lewy body disease",
    "frontotemporal dementia",
    "progressive supranuclear palsy",
    "multiple system atrophy",
    "Friedreich ataxia",
    "spinal muscular atrophy",
]
PER_DISEASE = 5
def _warn(message):
    print(message, file=sys.stderr)


OUTPUT_PATH = Path(__file__).resolve().parents[2] / "deploy_data" / "gemini_structured_literature.json"


def build_prompt(publications):
    items = [
        {"pmid": p["pmid"], "title": p["title"], "abstract": p["abstract"]}
        for p in publications
    ]
    return f"""
You are a scientific data structuring assistant for NeurohoraScope.AI.
Convert each PubMed abstract below into structured data.

Rules:
1. Use only information explicitly present in the title or abstract.
2. "molecules_mentioned": drug or compound names that appear verbatim in the
   text. Return an empty list if there are none. Never add names from memory.
3. "study_type": one of "review", "clinical trial", "meta-analysis",
   "in vitro", "animal study", "case report", "other".
4. "main_finding": one factual sentence (max 40 words) taken from the abstract.
   Do not claim efficacy or safety that the abstract does not state.
5. "limitations": one short sentence on what the abstract does not show.
6. Keep every pmid exactly as given. Return valid JSON only.

Required JSON structure:
{{"publications": [{{"pmid": "...", "study_type": "...",
  "molecules_mentioned": ["..."], "main_finding": "...", "limitations": "..."}}]}}

Input publications:
{json.dumps(items, ensure_ascii=False)}
"""


def call_gemini(prompt, attempts=3):
    """Call Gemini and return the parsed JSON object."""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)
    last_error = None
    for attempt in range(attempts):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )
            if not response.text:
                raise RuntimeError("Gemini returned an empty response.")
            return json.loads(response.text)
        except Exception as error:  # retry transient API errors
            last_error = error
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Gemini call failed: {type(last_error).__name__}")


def validate_and_merge(publications, response):
    """Keep source title/URL; drop anything Gemini added that the text does not support."""
    if not isinstance(response, dict) or not isinstance(response.get("publications"), list):
        raise ValueError("Gemini response has no publications list.")

    by_pmid = {
        str(row.get("pmid")): row
        for row in response["publications"]
        if isinstance(row, dict)
    }

    structured = []
    for pub in publications:
        row = by_pmid.get(pub["pmid"])
        if row is None:
            _warn(f"  ignore PMID {pub['pmid']}: absent de la reponse Gemini")
            continue

        text = f"{pub['title']} {pub['abstract']}".lower()
        molecules = []
        for name in row.get("molecules_mentioned") or []:
            if isinstance(name, str) and name.strip() and name.strip().lower() in text:
                molecules.append(name.strip())
            else:
                _warn(f"  molecule rejetee (absente du texte) : {name!r}")

        structured.append(
            {
                "pmid": pub["pmid"],
                "title": pub["title"],
                "url": pub["url"],
                "disease": pub["disease"],
                "study_type": str(row.get("study_type", "other"))[:40],
                "molecules_mentioned": sorted(set(molecules)),
                "main_finding": str(row.get("main_finding", ""))[:400],
                "limitations": str(row.get("limitations", ""))[:300],
                "source": "PubMed",
            }
        )

    if not structured:
        raise ValueError("No publication could be structured.")
    return structured


def collect_publications(disease, limit=PER_DISEASE):
    from src.clients.pubmed_client import search_pubmed

    query = f'("{disease}"[Title/Abstract]) AND neuroprotection'
    found = search_pubmed(query, max_results=limit * 2)
    kept = [p for p in found if p.get("abstract", "").strip()][:limit]
    time.sleep(0.5)
    return [{**pub, "disease": disease} for pub in kept]


# ---------------------------------------------------------------------------
# Live mode used by the MCP server (bounded: known diseases only, small batches,
# daily cap, one-hour cache). The API key never leaves the server environment.
# ---------------------------------------------------------------------------

LIVE_PER_DISEASE = 3
LIVE_CACHE_SECONDS = 3600
_live_cache = {}
_live_usage = {"day": None, "count": 0}

_ALIASES = {
    "sclérose en plaques": "multiple sclerosis",
    "sclerose en plaques": "multiple sclerosis",
    "sep": "multiple sclerosis",
    "sla": "amyotrophic lateral sclerosis",
    "sclérose latérale amyotrophique": "amyotrophic lateral sclerosis",
    "huntington": "Huntington's disease",
    "lewy": "Lewy body disease",
    "friedreich": "Friedreich ataxia",
    "atrophie musculaire spinale": "spinal muscular atrophy",
    "amyotrophie spinale": "spinal muscular atrophy",
}


class LiveUnavailable(Exception):
    """Live Gemini structuring cannot be used for this request."""


def resolve_disease(name):
    wanted = (name or "").strip().lower()
    if not wanted:
        return None
    if wanted in _ALIASES:
        wanted = _ALIASES[wanted].lower()
    for disease in DISEASES:
        low = disease.lower()
        if wanted in low or low in wanted:
            return disease
    return None


def live_structure(name):
    """Fetch a few PubMed abstracts and structure them with Gemini right now."""
    disease = resolve_disease(name)
    if disease is None:
        raise LiveUnavailable("disease not covered by the live mode")
    if not os.getenv("GEMINI_API_KEY", "").strip():
        raise LiveUnavailable("Gemini key not configured on the server")

    now = time.time()
    cached = _live_cache.get(disease)
    if cached and now - cached[0] < LIVE_CACHE_SECONDS:
        return {**cached[1], "cache": "result generated live less than one hour ago"}

    limit = int(os.getenv("GEMINI_LIVE_DAILY_LIMIT", "30"))
    today = datetime.now(timezone.utc).date().isoformat()
    if _live_usage["day"] != today:
        _live_usage["day"], _live_usage["count"] = today, 0
    if _live_usage["count"] >= limit:
        raise LiveUnavailable("daily live limit reached")
    _live_usage["count"] += 1

    publications = collect_publications(disease, LIVE_PER_DISEASE)
    if not publications:
        raise LiveUnavailable("no PubMed abstract found")
    response = call_gemini(build_prompt(publications), attempts=2)
    rows = validate_and_merge(publications, response)

    result = {
        "status": "success",
        "mode": "live",
        "message": "Structured by Gemini just now from PubMed abstracts (live call from the MCP server).",
        "generated_by": f"Gemini ({MODEL})",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "disease": disease,
        "records_returned": len(rows),
        "publications": rows,
        "scientific_note": (
            "Generated by an AI model from PubMed abstracts. Fields are extracted from "
            "abstracts only; they are not validated scientific conclusions and do not "
            "establish efficacy or safety."
        ),
    }
    _live_cache[disease] = (now, result)
    return result


def main():
    structured = []
    for disease in DISEASES:
        try:
            publications = collect_publications(disease)
            if not publications:
                print(f"{disease}: aucune publication avec resume, ignoree")
                continue
            response = call_gemini(build_prompt(publications))
            rows = validate_and_merge(publications, response)
            structured.extend(rows)
            print(f"{disease}: {len(rows)} publications structurees")
        except Exception as error:
            print(f"{disease}: ECHEC ({error}), ignoree")

    if not structured:
        print("ECHEC : aucune publication structuree.")
        sys.exit(1)

    output = {
        "generated_by": f"Gemini ({MODEL})",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pipeline": "PubMed abstracts -> Gemini structuring -> validation -> MCP",
        "diseases": DISEASES,
        "scientific_note": (
            "Generated offline by an AI model from PubMed abstracts, not a live call. "
            "Fields are extracted from abstracts only; they are not validated "
            "scientific conclusions and do not establish efficacy or safety."
        ),
        "publications": structured,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK : {len(structured)} publications structurees ({len(set(r['disease'] for r in structured))} maladies) -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
