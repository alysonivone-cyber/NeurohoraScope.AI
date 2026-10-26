
import json

from integrated_research_report import (
    build_integrated_research_report,
)
from molecular_selectivity import extract_target_profile
from assay_classifier import classify_assay


def build_experimental_context(report):
    profile = extract_target_profile(report)

    enriched_measurements = []
    metadata_cache = {}

    for target, activities in (
        profile["target_profile"].items()
    ):
        for activity in activities:
            assay_id = activity.get(
                "assay_chembl_id"
            )

            if not assay_id:
                continue

            if assay_id not in metadata_cache:
                try:
                    metadata_cache[assay_id] = (
                        classify_assay(assay_id)
                    )
                except Exception as error:
                    metadata_cache[assay_id] = {
                        "assay_chembl_id": assay_id,
                        "assay_format": "UNKNOWN",
                        "metadata_error": str(error),
                    }

            metadata = metadata_cache[assay_id]

            enriched_measurements.append({
                "target": target,
                "ic50_nM": activity["ic50_nM"],
                "assay_chembl_id": assay_id,
                "assay_format": metadata.get(
                    "assay_format", "UNKNOWN"
                ),
                "bao_label": metadata.get(
                    "bao_label"
                ),
                "assay_description": metadata.get(
                    "assay_description"
                ),
                "target_chembl_id": metadata.get(
                    "target_chembl_id"
                ),
                "confidence_score": metadata.get(
                    "confidence_score"
                ),
            })

    return {
        "molecule": report.get("molecule"),
        "measurement_count": len(
            enriched_measurements
        ),
        "measurements": enriched_measurements,
        "interpretation": (
            "Experimental context is derived from "
            "ChEMBL assay metadata. Matching assay "
            "formats do not guarantee comparable "
            "protocols or biological conditions."
        ),
    }


if __name__ == "__main__":
    disease = "Multiple Sclerosis"

    for molecule in [
        "Orelabrutinib",
        "Tolebrutinib",
    ]:
        print(f"\nRetrieving {molecule}...")

        report = build_integrated_research_report(
            molecule,
            disease,
        )

        context = build_experimental_context(
            report
        )

        print(json.dumps(
            context,
            indent=2,
            ensure_ascii=False,
        ))
