from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlparse
from mcp.server.transport_security import TransportSecuritySettings

from mcp.server.fastmcp import FastMCP

from src.analysis.scientific_analyzer import detect_mechanisms

from src.ai.gemini_scientific_processor import (
    analyze_scientific_data,
)

from src.clients.chembl_client import (
    get_chembl_bioactivities,
    get_chembl_mechanisms,
    get_chembl_target,
    search_chembl_molecule,
)

from src.clients.clinical_trials_client import (
    search_clinical_trials as clinical_trials_search,
)

from src.clients.pubmed_client import search_pubmed

from src.storage.database import (
    count_publications,
    initialize_database,
    save_publications,
)


from src.analysis.search_engine import (
    get_disease_molecules as local_get_disease_molecules,
    search_diseases as local_search_diseases,
)

from src.analysis.molecule_research import (
    research_molecule as molecule_search,
)

from src.analysis.pharmacology_report import (
    build_pharmacology_report,
)

from src.analysis.integrated_research_report import (
    build_integrated_research_report,
)

def create_mcp_server():
    """Configure le serveur MCP selon son environnement."""

    if os.getenv("MCP_EXTERNAL_AUTH", "false").lower() == "true":
        if os.getenv("MCP_REQUIRE_AUTH", "").lower() != "true":
            raise RuntimeError("Authentification externe non activee.")

        public_url = os.getenv("MCP_PUBLIC_URL", "").strip()
        parsed_url = urlparse(public_url)
        if parsed_url.scheme != "https" or not parsed_url.hostname:
            raise RuntimeError("MCP_PUBLIC_URL doit etre une URL HTTPS valide.")

        hostname = parsed_url.hostname
        security = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[hostname, f"{hostname}:443", "localhost:*", "127.0.0.1:*", "[::1]:*"],
            allowed_origins=[f"https://{hostname}", "http://localhost:*", "http://127.0.0.1:*", "http://[::1]:*"],
        )
        return FastMCP("NeurohoraScope.AI", transport_security=security)

    if os.getenv("MCP_REQUIRE_AUTH", "false").lower() != "true":
        return FastMCP("NeurohoraScope.AI")

    from mcp.server.auth.settings import AuthSettings
    from src.mcp.auth import NeurohoraTokenVerifier

    public_url = os.getenv("MCP_PUBLIC_URL", "").strip()
    access_token = os.getenv("MCP_ACCESS_TOKEN", "").strip()
    issuer_url = os.getenv("MCP_ISSUER_URL", "").strip()
    if not public_url.startswith("https://"):
        raise RuntimeError("MCP_PUBLIC_URL doit etre une URL HTTPS.")
    if not issuer_url.startswith("https://"):
        raise RuntimeError("MCP_ISSUER_URL doit etre une URL HTTPS.")
    if len(access_token) < 32:
        raise RuntimeError("MCP_ACCESS_TOKEN doit contenir au moins 32 caracteres.")

    hostname = urlparse(public_url).hostname
    if not hostname:
        raise RuntimeError("Domaine MCP_PUBLIC_URL invalide.")

    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[hostname, f"{hostname}:443", "localhost:*", "127.0.0.1:*", "[::1]:*"],
        allowed_origins=[f"https://{hostname}", "http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"],
    )
    return FastMCP(
        "NeurohoraScope.AI",
        transport_security=security,
        token_verifier=NeurohoraTokenVerifier(),
        auth=AuthSettings(
            issuer_url=issuer_url,
            resource_server_url=public_url,
            required_scopes=["mcp:tools"],
            validate_token_resource=True,
        ),
    )


mcp = create_mcp_server()

@mcp.tool()
def search_neuroscience_literature(disease: str, max_results: int = 10) -> dict:
    """Search PubMed for scientific literature relevant to a disease."""
    disease = disease.strip()
    if not disease:
        return {"error": "Le nom de la maladie est obligatoire."}

    max_results = max(1, min(max_results, 20))
    query = f'("{disease}"[Title/Abstract]) AND neuroprotection'
    publications = search_pubmed(query, max_results=max_results)

    initialize_database()
    save_publications(publications)

    results = []
    for publication in publications:
        text = publication["title"] + " " + publication.get("abstract", "")
        results.append(
            {
                "pmid": publication["pmid"],
                "title": publication["title"],
                "abstract": publication.get("abstract", ""),
                "url": publication["url"],
                "publication_types": publication.get("publication_types", []),
                "detected_topics": detect_mechanisms(text),
            }
        )

    return {
        "disease": disease,
        "query": query,
        "publication_count": len(results),
        "publications": results,
        "scientific_note": (
            "Detected topics are keyword matches, not validated biological mechanisms. "
            "Publication types do not establish clinical efficacy."
        ),
    }


@mcp.tool()
def search_diseases(keyword: str) -> dict:
    """Search locally stored disease records."""
    initialize_database()
    results = local_search_diseases(keyword.strip())
    return {"keyword": keyword, "results": results}


@mcp.tool()
def get_disease_molecules(disease_id: int) -> dict:
    """Return molecules associated with a local disease record."""
    initialize_database()
    molecules = local_get_disease_molecules(disease_id)
    return {
        "disease_id": disease_id,
        "molecules": molecules,
        "scientific_note": (
            "These are database associations, not verified therapeutic recommendations."
        ),
    }


@mcp.tool()
def search_clinical_trials(
    disease: str,
    max_results: int = 5,
    intervention_type: str = "DRUG",
    phase: str = "",
    status: str = "",
) -> dict:
    """Search ClinicalTrials.gov for medical studies matching a disease."""
    disease = disease.strip()
    if not disease:
        return {"error": "Disease name is required."}

    allowed_interventions = {
        "",
        "DRUG",
        "DEVICE",
        "BIOLOGICAL",
        "BEHAVIORAL",
        "DIAGNOSTIC_TEST",
        "DIETARY_SUPPLEMENT",
        "PROCEDURE",
        "OTHER",
    }
    allowed_phases = {"", "EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4", "NA"}
    allowed_statuses = {
        "",
        "RECRUITING",
        "NOT_YET_RECRUITING",
        "ACTIVE_NOT_RECRUITING",
        "COMPLETED",
        "TERMINATED",
        "SUSPENDED",
        "WITHDRAWN",
        "ENROLLING_BY_INVITATION",
        "UNKNOWN",
    }

    intervention_type = intervention_type.strip().upper()
    phase = phase.strip().upper()
    status = status.strip().upper()

    if intervention_type not in allowed_interventions:
        return {"error": "Invalid intervention type."}
    if phase not in allowed_phases:
        return {"error": "Invalid clinical trial phase."}
    if status not in allowed_statuses:
        return {"error": "Invalid trial status."}

    try:
        return clinical_trials_search(
            disease=disease,
            max_results=max_results,
            intervention_type=intervention_type,
            phase=phase or None,
            status=status or None,
        )
    except Exception as error:
        return {"error": "ClinicalTrials.gov request failed.", "details": str(error)}


@mcp.tool()
def research_molecule(molecule: str, disease: str = "", max_results: int = 10) -> dict:
    """Search ClinicalTrials.gov for studies involving a molecule."""
    molecule = molecule.strip()
    disease = disease.strip()
    if not molecule:
        return {"error": "Molecule name is required."}

    try:
        max_results = max(1, min(int(max_results), 20))
        return molecule_search(molecule=molecule, disease=disease or None, max_results=max_results)
    except (ValueError, TypeError):
        return {"error": "Invalid search parameters."}
    except Exception:
        return {"error": "Molecule research request failed."}


@mcp.tool()
def search_molecule_chembl(molecule: str, max_results: int = 5) -> dict:
    """Search ChEMBL for molecule identity and properties."""
    molecule = molecule.strip()
    if not molecule:
        return {"error": "Molecule name is required."}

    try:
        return search_chembl_molecule(name=molecule, max_results=max_results)
    except (ValueError, TypeError):
        return {"error": "Invalid search parameters."}
    except Exception:
        return {"error": "ChEMBL search failed."}


@mcp.tool()
def get_molecule_mechanisms(chembl_id: str) -> dict:
    """Fetch curated mechanism annotations for a ChEMBL molecule."""
    try:
        return get_chembl_mechanisms(chembl_id=chembl_id)
    except (ValueError, TypeError) as error:
        return {"error": str(error)}
    except Exception:
        return {"error": "ChEMBL mechanism lookup failed."}


@mcp.tool()
def get_biological_target(target_chembl_id: str) -> dict:
    """Fetch a target protein record from ChEMBL."""
    try:
        return get_chembl_target(target_chembl_id=target_chembl_id)
    except (ValueError, TypeError) as error:
        return {"error": str(error)}
    except Exception:
        return {"error": "ChEMBL target lookup failed."}


@mcp.tool()
def get_molecule_bioactivities(molecule_chembl_id: str, max_results: int = 20) -> dict:
    """Fetch experimental bioactivity records for a ChEMBL molecule."""
    try:
        return get_chembl_bioactivities(molecule_chembl_id=molecule_chembl_id, max_results=max_results)
    except (ValueError, TypeError) as error:
        return {"error": str(error)}
    except Exception:
        return {"error": "ChEMBL bioactivity lookup failed."}


@mcp.tool()
def generate_pharmacology_report(molecule_name: str, max_activities: int = 10) -> dict:
    """Generate a ChEMBL pharmacology report for a molecule."""
    molecule_name = molecule_name.strip()
    if not molecule_name:
        return {"status": "error", "message": "Molecule name is required."}

    try:
        return build_pharmacology_report(molecule_name=molecule_name, max_activities=max_activities)
    except (ValueError, TypeError) as error:
        return {"status": "error", "message": str(error)}
    except Exception:
        return {"status": "error", "message": "Pharmacology report generation failed."}


@mcp.tool()
def generate_integrated_research_report(
    molecule_name: str,
    disease: str = "",
    max_activities: int = 10,
    max_trials: int = 10,
) -> dict:
    """Generate a combined pharmacology + trial + literature report."""
    molecule_name = molecule_name.strip()
    if not molecule_name:
        return {"status": "error", "message": "Molecule name is required."}

    try:
        return build_integrated_research_report(
            molecule_name=molecule_name,
            disease=disease or None,
            max_activities=max_activities,
            max_trials=max_trials,
        )
    except (ValueError, TypeError) as error:
        return {"status": "error", "message": str(error)}
    except Exception:
        return {"status": "error", "message": "Integrated research report generation failed."}


@mcp.tool()
def analyze_scientific_evidence_with_gemini(
    max_records: int = 7,
) -> dict:
    """Analyze local ChEMBL evidence with Gemini and scientific validation."""

    if not 1 <= max_records <= 20:
        return {
            "status": "error",
            "message": "max_records must be between 1 and 20.",
        }

    project_root = Path(__file__).resolve().parents[2]
    report_path = (
        project_root
        / "reports"
        / "exact_activity_matches.json"
    )

    if not report_path.is_file():
        return {
            "status": "error",
            "message": "Scientific evidence file not found.",
        }

    try:
        with report_path.open("r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            return {
                "status": "error",
                "message": "Scientific evidence must be a JSON list.",
            }

        selected_records = records[:max_records]

        if not selected_records:
            return {
                "status": "error",
                "message": "No scientific evidence available.",
            }

        analysis = analyze_scientific_data(selected_records)

        return {
            "status": "success",
            "project": "NeurohoraScope.AI",
            "source": str(report_path.name),
            "records_analyzed": len(selected_records),
            "scientific_analysis": analysis,
            "scientific_note": (
                "AI-generated scientific interpretation. "
                "Experimental evidence must remain traceable "
                "to its original scientific sources."
            ),
        }

    except Exception as error:
        return {
            "status": "error",
            "message": "Gemini scientific analysis failed.",
            "details": str(error),
        }

if __name__ == "__main__":
    import os

    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
