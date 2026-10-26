
import json

from assay_metadata import get_assay_metadata


BAO_FORMATS = {
    "BAO_0000357": "SINGLE_PROTEIN",
    "BAO_0000219": "CELL_BASED",
    "BAO_0000221": "TISSUE_BASED",
}


def classify_assay(assay_id):
    metadata = get_assay_metadata(assay_id)

    bao_format = metadata.get("bao_format")

    classification = BAO_FORMATS.get(
        bao_format,
        "UNKNOWN",
    )

    return {
        "assay_chembl_id": assay_id,
        "assay_format": classification,
        "bao_label": metadata.get("bao_label"),
        "assay_description": metadata.get(
            "assay_description"
        ),
        "target_chembl_id": metadata.get(
            "target_chembl_id"
        ),
        "confidence_score": metadata.get(
            "confidence_score"
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

    results = []

    for assay_id in assay_ids:
        print(f"Classifying {assay_id}...")

        try:
            result = classify_assay(assay_id)
            results.append(result)

        except Exception as error:
            print(
                f"Unable to classify {assay_id}: "
                f"{error}"
            )

    print("\nASSAY CLASSIFICATION RESULTS")
    print(json.dumps(
        results,
        indent=2,
        ensure_ascii=False,
    ))
