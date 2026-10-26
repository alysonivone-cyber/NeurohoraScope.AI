
import json
import requests


API_URL = "https://clinicaltrials.gov/api/v2/studies"


def research_molecule(molecule, max_results=10, disease=None):
    """
    Find clinical studies involving a molecule.
    """

    molecule = molecule.strip()

    if not molecule:
        raise ValueError("Molecule name is required.")

    max_results = max(1, min(int(max_results), 20))

    params = {
        "query.intr": molecule,
        "pageSize": max_results,
        "countTotal": "true",
        "format": "json",
    }

    if disease and disease.strip():
        params["query.cond"] = disease.strip()

    response = requests.get(
        API_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    studies = []

    for study in data.get("studies", []):
        protocol = study.get("protocolSection", {})

        identification = protocol.get(
            "identificationModule", {}
        )
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        conditions = protocol.get(
            "conditionsModule", {}
        )
        interventions_module = protocol.get(
            "armsInterventionsModule", {}
        )

        nct_id = identification.get("nctId")

        interventions = [
            {
                "name": item.get("name"),
                "type": item.get("type"),
            }
            for item in interventions_module.get(
                "interventions", []
            )
        ]

        studies.append({
            "nct_id": nct_id,
            "title": identification.get("briefTitle"),
            "conditions": conditions.get(
                "conditions", []
            ),
            "status": status.get("overallStatus"),
            "phases": design.get("phases", []),
            "study_type": design.get("studyType"),
            "interventions": interventions,
            "has_results": study.get(
                "hasResults", False
            ),
            "url": (
                f"https://clinicaltrials.gov/study/{nct_id}"
                if nct_id else None
            ),
        })

    return {
        "molecule": molecule,
        "disease_filter": disease,
        "total_count": data.get("totalCount"),
        "returned_count": len(studies),
        "studies": studies,
        "scientific_note": (
            "Clinical trial registration does not "
            "demonstrate efficacy or safety. "
            "Results must be critically evaluated."
        ),
    }


if __name__ == "__main__":
    print("\nNEUROSCOPE.AI — MOLECULE RESEARCH\n")

    try:
        result = research_molecule(
            molecule="Orelabrutinib",
            disease="Multiple Sclerosis",
            max_results=10,
        )


        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

    except requests.RequestException as error:
        print(f"API connection error: {error}")

    except ValueError as error:
        print(f"Input error: {error}")
