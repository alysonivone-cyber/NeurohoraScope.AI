
import json
import requests


CHEMBL_API = (
    "https://www.ebi.ac.uk/chembl/api/data"
)


def get_assay_metadata(assay_id):
    url = f"{CHEMBL_API}/assay/{assay_id}.json"

    response = requests.get(
        url,
        timeout=30,
    )

    response.raise_for_status()
    assay = response.json()

    return {
        "assay_chembl_id": assay.get(
            "assay_chembl_id"
        ),
        "assay_type": assay.get("assay_type"),
        "assay_description": assay.get(
            "description"
        ),
        "bao_format": assay.get("bao_format"),
        "bao_label": assay.get("bao_label"),
        "confidence_score": assay.get(
            "confidence_score"
        ),
        "target_chembl_id": assay.get(
            "target_chembl_id"
        ),
    }


if __name__ == "__main__":
    assay_ids = [
        "CHEMBL5242619",
        "CHEMBL5251905",
        "CHEMBL4714265",
        "CHEMBL5043203",
        "CHEMBL5251928",
        "CHEMBL5251929",
        "CHEMBL5043205",
    ]

    for assay_id in assay_ids:
        print(f"\nRetrieving {assay_id}...")

        try:
            metadata = get_assay_metadata(
                assay_id
            )

            print(json.dumps(
                metadata,
                indent=2,
                ensure_ascii=False,
            ))

        except requests.RequestException as error:
            print(
                f"Unable to retrieve {assay_id}: "
                f"{error}"
            )
