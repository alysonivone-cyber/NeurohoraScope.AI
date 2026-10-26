
import json
import requests

from pathlib import Path


CHEMBL_API = (
    "https://www.ebi.ac.uk/chembl/api/data"
)


def get_activity_records(assay_id):
    url = f"{CHEMBL_API}/activity.json"

    response = requests.get(
        url,
        params={
            "assay_chembl_id": assay_id,
            "limit": 100,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "assay_chembl_id": assay_id,
        "activities": [
            {
                "activity_id": item.get(
                    "activity_id"
                ),
                "molecule_chembl_id": item.get(
                    "molecule_chembl_id"
                ),
                "standard_type": item.get(
                    "standard_type"
                ),
                "standard_value": item.get(
                    "standard_value"
                ),
                "standard_units": item.get(
                    "standard_units"
                ),
                "document_chembl_id": item.get(
                    "document_chembl_id"
                ),
            }
            for item in data.get(
                "activities", []
            )
        ],
        "total_count": (
            data.get("page_meta") or {}
        ).get("total_count"),
    }


if __name__ == "__main__":
    provenance_path = Path(
        "reports/scientific_data_provenance.json"
    )

    provenance = json.loads(
        provenance_path.read_text(
            encoding="utf-8"
        )
    )

    assay_ids = sorted({
        record["assay_chembl_id"]
        for record in provenance["records"]
        if record.get("assay_chembl_id")
    })

    for assay_id in assay_ids:
        print(f"\nRetrieving {assay_id}...")

        try:
            result = get_activity_records(
                assay_id
            )

            print(
                "Total activities:",
                result["total_count"],
            )

            print(json.dumps(
                result["activities"][:3],
                indent=2,
                ensure_ascii=False,
            ))

        except requests.RequestException as error:
            print(
                "Retrieval error:",
                error,
            )
