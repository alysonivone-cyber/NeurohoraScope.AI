
from mcp.server.fastmcp import FastMCP

from database import (
    initialize_database,
    save_publications,
)
from pubmed_client import search_pubmed
from scientific_analyzer import detect_mechanisms
from search_engine import (
    search_diseases as local_search_diseases,
    get_disease_molecules as local_get_disease_molecules,
)
from clinical_trials_client import search_clinical_trials as clinical_trials_search
from molecule_research import research_molecule as molecule_search
from chembl_client import (
    search_chembl_molecule,
    get_chembl_mechanisms,
    get_chembl_target,
    get_chembl_bioactivities,
)
from pharmacology_report import build_pharmacology_report
from integrated_research_report import build_integrated_research_report

# Création du serveur MCP
mcp = FastMCP("NeuroScope.AI")


@mcp.tool()
def search_neuroscience_literature(
    disease: str,
    max_results: int = 10,
) -> dict:
    """
    Recherche des publications scientifiques sur PubMed
    concernant une maladie et la neuroprotection.

    Retourne les titres, PMID, liens, types PubMed,
    résumés et thèmes biologiques détectés.
    """

    disease = disease.strip()

    if not disease:
        return {"error": "Le nom de la maladie est obligatoire."}

    max_results = max(1, min(max_results, 20))

    query = f'("{disease}"[Title/Abstract]) AND neuroprotection'

    publications = search_pubmed(
        query,
        max_results=max_results,
    )

    initialize_database()
    save_publications(publications)

    results = []

    for publication in publications:
        text = (
            publication["title"]
            + " "
            + publication.get("abstract", "")
        )

        results.append({
            "pmid": publication["pmid"],
            "title": publication["title"],
            "abstract": publication.get("abstract", ""),
            "url": publication["url"],
            "publication_types": publication.get(
                "publication_types", []
            ),
            "detected_topics": detect_mechanisms(text),
        })

    return {
        "disease": disease,
        "query": query,
        "publication_count": len(results),
        "publications": results,
        "scientific_note": (
            "Detected topics are keyword matches, not "
            "validated biological mechanisms. Publication "
            "types do not establish clinical efficacy."
        ),
    }


@mcp.tool()
def search_diseases(keyword: str) -> dict:
    """
    Recherche une maladie dans la base locale NeuroScope.AI.
    """

    initialize_database()

    results = local_search_diseases(keyword.strip())

    return {
        "keyword": keyword,
        "results": results,
    }


@mcp.tool()
def get_disease_molecules(disease_id: int) -> dict:
    """
    Retourne les molécules associées à une maladie
    dans la base locale.

    Ces associations ne démontrent pas une efficacité
    thérapeutique ni une autorisation clinique.
    """

    initialize_database()

    molecules = local_get_disease_molecules(disease_id)

    return {
        "disease_id": disease_id,
        "molecules": molecules,
        "scientific_note": (
            "These are database associations, not "
            "verified therapeutic recommendations."
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
    """
    Search ClinicalTrials.gov for clinical studies.

    Parameters:
        disease: Disease or condition to investigate.
        max_results: Number of trials, from 1 to 20.
        intervention_type: DRUG, DEVICE, BIOLOGICAL,
            BEHAVIORAL, or empty for any type.
        phase: PHASE1, PHASE2, PHASE3, PHASE4,
            or empty for any phase.
        status: RECRUITING, COMPLETED,
            NOT_YET_RECRUITING, etc.
            Empty means any status.

    Returns structured trial information.
    """

    disease = disease.strip()

    if not disease:
        return {
            "error": "Disease name is required."
        }

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

    allowed_phases = {
        "",
        "EARLY_PHASE1",
        "PHASE1",
        "PHASE2",
        "PHASE3",
        "PHASE4",
        "NA",
    }

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
        return {
            "error": "ClinicalTrials.gov request failed.",
            "details": str(error),
        }

    disease = disease.strip()

    if not disease:
        return {
            "error": "Disease name is required."
        }

    max_results = max(1, min(max_results, 20))

    try:
        return clinical_trials_search(
            disease=disease,
            max_results=max_results,
        )

    except Exception as error:
        return {
            "error": "ClinicalTrials.gov request failed.",
            "details": str(error),
        }


@mcp.tool()
def research_molecule(
    molecule: str,
    disease: str = "",
    max_results: int = 10,
) -> dict:
    """
    Search ClinicalTrials.gov for clinical studies
    involving a molecule, optionally filtered
    by disease or condition.

    This tool does not determine whether a
    molecule is effective or safe.
    """

    molecule = molecule.strip()
    disease = disease.strip()

    if not molecule:
        return {
            "error": "Molecule name is required."
        }

    try:
        max_results = max(1, min(int(max_results), 20))

        return molecule_search(
            molecule=molecule,
            disease=disease or None,
            max_results=max_results,
        )

    except (ValueError, TypeError):
        return {
            "error": "Invalid search parameters."
        }

    except Exception:
        return {
            "error": "Molecule research request failed."
        }


@mcp.tool()
def search_molecule_chembl(
    molecule: str,
    max_results: int = 5,
) -> dict:
    """
    Search ChEMBL for molecular identity,
    chemical properties and identifiers.

    Results are database matches and must
    be verified before scientific interpretation.
    """

    molecule = molecule.strip()

    if not molecule:
        return {"error": "Molecule name is required."}

    try:
        return search_chembl_molecule(
            name=molecule,
            max_results=max_results,
        )

    except (ValueError, TypeError):
        return {"error": "Invalid search parameters."}

    except Exception:
        return {"error": "ChEMBL search failed."}


@mcp.tool()
def get_molecule_mechanisms(
    chembl_id: str,
) -> dict:
    """
    Retrieve curated pharmacological mechanisms
    of a molecule from ChEMBL.
    """

    try:
        return get_chembl_mechanisms(
            chembl_id=chembl_id,
        )
    except (ValueError, TypeError) as error:
        return {"error": str(error)}
    except Exception:
        return {"error": "ChEMBL mechanism lookup failed."}


@mcp.tool()
def get_biological_target(
    target_chembl_id: str,
) -> dict:
    """
    Retrieve target protein information,
    organism and UniProt accession from ChEMBL.
    """

    try:
        return get_chembl_target(
            target_chembl_id=target_chembl_id,
        )
    except (ValueError, TypeError) as error:
        return {"error": str(error)}
    except Exception:
        return {"error": "ChEMBL target lookup failed."}


@mcp.tool()
def get_molecule_bioactivities(
    molecule_chembl_id: str,
    max_results: int = 20,
) -> dict:
    """
    Retrieve experimental bioactivity records
    from ChEMBL, including IC50, Ki or Kd
    when available.

    Results require assay-specific interpretation.
    """

    try:
        return get_chembl_bioactivities(
            molecule_chembl_id=molecule_chembl_id,
            max_results=max_results,
        )
    except (ValueError, TypeError) as error:
        return {"error": str(error)}
    except Exception:
        return {"error": "ChEMBL bioactivity lookup failed."}


@mcp.tool()
def generate_pharmacology_report(
    molecule_name: str,
    max_activities: int = 10,
) -> dict:
    """
    Generate an integrated pharmacology report
    from ChEMBL.

    Includes molecular identity, annotated
    mechanisms, biological targets and
    experimental bioactivities.

    This tool does not establish clinical
    efficacy or treatment recommendations.
    """

    molecule_name = molecule_name.strip()

    if not molecule_name:
        return {
            "status": "error",
            "message": "Molecule name is required.",
        }

    try:
        return build_pharmacology_report(
            molecule_name=molecule_name,
            max_activities=max_activities,
        )

    except (ValueError, TypeError) as error:
        return {
            "status": "error",
            "message": str(error),
        }

    except Exception:
        return {
            "status": "error",
            "message": "Pharmacology report generation failed.",
        }


@mcp.tool()
def generate_integrated_research_report(
    molecule_name: str,
    disease: str = "",
    max_activities: int = 10,
    max_trials: int = 10,
) -> dict:
    """
    Generate an integrated neuropharmacology
    research report.

    Combines ChEMBL molecular pharmacology
    with ClinicalTrials.gov studies.

    Intended for research, not clinical
    decision-making.
    """

    molecule_name = molecule_name.strip()

    if not molecule_name:
        return {
            "status": "error",
            "message": "Molecule name is required.",
        }

    try:
        return build_integrated_research_report(
            molecule_name=molecule_name,
            disease=disease or None,
            max_activities=max_activities,
            max_trials=max_trials,
        )

    except (ValueError, TypeError) as error:
        return {
            "status": "error",
            "message": str(error),
        }

    except Exception:
        return {
            "status": "error",
            "message": (
                "Integrated research report "
                "generation failed."
            ),
        }

if __name__ == "__main__":
    import os

    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")

