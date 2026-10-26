
import json
import requests

CHEMBL_API = "https://www.ebi.ac.uk/chembl/api/data"


def search_chembl_molecule(name, max_results=5):
    """
    Search ChEMBL for a molecule and return
    its identifiers and chemical properties.
    """

    name = name.strip()

    if not name:
        raise ValueError("Molecule name is required.")

    max_results = max(1, min(int(max_results), 20))

    response = requests.get(
        f"{CHEMBL_API}/molecule/search.json",
        params={
            "q": name,
            "limit": max_results,
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    molecules = []

    for item in data.get("molecules", []):
        properties = item.get("molecule_properties") or {}
        structures = item.get("molecule_structures") or {}

        chembl_id = item.get("molecule_chembl_id")

        molecules.append({
            "chembl_id": chembl_id,
            "preferred_name": item.get("pref_name"),
            "molecule_type": item.get("molecule_type"),
            "max_phase": item.get("max_phase"),
            "molecular_weight": properties.get("full_mwt"),
            "alogp": properties.get("alogp"),
            "canonical_smiles": structures.get(
                "canonical_smiles"
            ),
            "url": (
                f"https://www.ebi.ac.uk/chembl/compound_report_card/{chembl_id}/"
                if chembl_id else None
            ),
        })

    return {
        "query": name,
        "returned_count": len(molecules),
        "molecules": molecules,
        "scientific_note": (
            "Search matches require identity verification. "
            "Chemical properties and maximum clinical phase "
            "do not establish therapeutic efficacy."
        ),
    }


def get_chembl_mechanisms(chembl_id):
    """
    Retrieve documented drug mechanisms from ChEMBL.
    """

    chembl_id = chembl_id.strip().upper()

    if not chembl_id.startswith("CHEMBL"):
        raise ValueError("Invalid ChEMBL identifier.")

    response = requests.get(
        f"{CHEMBL_API}/mechanism.json",
        params={
            "molecule_chembl_id": chembl_id,
            "limit": 100,
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    mechanisms = []

    for item in data.get("mechanisms", []):
        mechanisms.append({
            "mechanism_of_action": item.get("mechanism_of_action"),
            "action_type": item.get("action_type"),
            "target_chembl_id": item.get("target_chembl_id"),
            "direct_interaction": item.get("direct_interaction"),
            "target_name": None,
        })

    return {
        "chembl_id": chembl_id,
        "mechanism_count": len(mechanisms),
        "mechanisms": mechanisms,
        "scientific_note": (
            "These are curated mechanism annotations. "
            "An empty result does not establish that "
            "the molecule has no biological mechanism."
        ),
    }


def get_chembl_target(target_chembl_id):
    """
    Retrieve biological target information from ChEMBL.
    """

    target_chembl_id = target_chembl_id.strip().upper()

    if not target_chembl_id.startswith("CHEMBL"):
        raise ValueError("Invalid ChEMBL target identifier.")

    response = requests.get(
        f"{CHEMBL_API}/target/{target_chembl_id}.json",
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    components = []

    for component in data.get("target_components", []):
        components.append({
            "accession": component.get("accession"),
            "component_type": component.get("component_type"),
            "organism": component.get("organism"),
            "synonyms": [
                {
                    "name": synonym.get("component_synonym"),
                    "type": synonym.get("syn_type"),
                }
                for synonym in component.get(
                    "target_component_synonyms", []
                )
            ],
        })

    return {
        "target_chembl_id": data.get("target_chembl_id"),
        "preferred_name": data.get("pref_name"),
        "target_type": data.get("target_type"),
        "organism": data.get("organism"),
        "components": components,
        "url": (
            "https://www.ebi.ac.uk/chembl/"
            f"target_report_card/{target_chembl_id}/"
        ),
    }


def get_chembl_bioactivities(
    molecule_chembl_id,
    max_results=20,
):
    """
    Retrieve experimental bioactivity records
    for a molecule from ChEMBL.
    """

    molecule_chembl_id = molecule_chembl_id.strip().upper()

    if not molecule_chembl_id.startswith("CHEMBL"):
        raise ValueError("Invalid ChEMBL molecule identifier.")

    max_results = max(1, min(int(max_results), 100))

    response = requests.get(
        f"{CHEMBL_API}/activity.json",
        params={
            "molecule_chembl_id": molecule_chembl_id,
            "limit": max_results,
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    activities = []

    for item in data.get("activities", []):
        activities.append({
            "activity_id": item.get("activity_id"),
            "target_chembl_id": item.get("target_chembl_id"),
            "target_name": item.get("target_pref_name"),
            "standard_type": item.get("standard_type"),
            "standard_relation": item.get("standard_relation"),
            "standard_value": item.get("standard_value"),
            "standard_units": item.get("standard_units"),
            "assay_chembl_id": item.get("assay_chembl_id"),
            "assay_type": item.get("assay_type"),
            "document_chembl_id": item.get("document_chembl_id"),
            "data_validity_comment": item.get(
                "data_validity_comment"
            ),
        })

    return {
        "molecule_chembl_id": molecule_chembl_id,
        "returned_count": len(activities),
        "total_count": data.get("page_meta", {}).get(
            "total_count"
        ),
        "activities": activities,
        "scientific_note": (
            "Bioactivity measurements depend on assay "
            "conditions, target, units, and data quality. "
            "They do not independently demonstrate "
            "clinical efficacy or safety."
        ),
    }

if __name__ == "__main__":
    print("\nNEUROSCOPE.AI — CHEMBL TEST\n")

    try:
        result = get_chembl_bioactivities(
    molecule_chembl_id="CHEMBL4650321",
    max_results=10,
)
        
        print(json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ))

    except requests.RequestException as error:
        print(f"ChEMBL API error: {error}")

    except (ValueError, TypeError) as error:
        print(f"Input error: {error}")
