
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.ai.validation import (
    validate_gemini_records,
    validate_potency_descriptions,
)

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")


def analyze_scientific_data(records):
    """
    Structure scientific records using Gemini.

    Gemini must not invent experimental measurements,
    references, or clinical conclusions.
    """

    if not isinstance(records, list) or not records:
        raise ValueError("Expected a non-empty list of records.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a scientific data structuring assistant
for NeuroScope.AI.

Analyze the following pharmacological records.

Rules:
1. Preserve all original molecule names, targets,
   IC50 values, units and ChEMBL identifiers.
2. Never invent experimental data or references.
3. Do not claim clinical efficacy from in-vitro IC50.
4. Do not rank compounds across different assays.
5. Clearly distinguish observations from limitations.
6. Use the term "sub-nanomolar" only when IC50 is strictly
   below 1 nM. Never use "sub-nanomolar" for IC50 >= 1 nM.
7. Avoid unsupported potency classifications and preserve
   the experimental assay context.
8. Return valid JSON only.

Required JSON structure:
{{
  "research_domain": "computational neuropharmacology",
  "records": [
    {{
      "molecule": "name",
      "target": "target",
      "ic50_nm": 0.0,
      "assay_id": "CHEMBL...",
      "interpretation": "short explanation"
    }}
  ],
  "scientific_limitations": [
    "limitation"
  ]
}}

Input records:
{json.dumps(records, ensure_ascii=False)}
"""

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

    result = json.loads(response.text)

    if not isinstance(result, dict):
        raise ValueError("Gemini response is not a JSON object.")

    if not isinstance(result.get("records"), list):
        raise ValueError("Gemini response has no records list.")

    validated = validate_gemini_records(records, result)
    return validate_potency_descriptions(validated)


def main():
    input_path = Path("reports/exact_activity_matches.json")
    output_path = Path("reports/gemini_scientific_analysis.json")

    if not input_path.exists():
        print("ERROR: Scientific input report not found.")
        sys.exit(1)

    records = json.loads(input_path.read_text(encoding="utf-8"))

    if not isinstance(records, list):
        print("ERROR: Expected a list of scientific records.")
        sys.exit(1)

    print("\nNEUROSCOPE GEMINI SCIENTIFIC PROCESSOR")
    print("Input records:", len(records))
    print("Model:", MODEL)
    print("Calling Gemini API...")

    result = analyze_scientific_data(records)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Structured records:", len(result["records"]))
    print("Output:", output_path)
    print("STATUS: COMPLETED")


if __name__ == "__main__":
    main()
