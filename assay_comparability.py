
import json

from pharmacology_comparison import extract_btk_ic50
from integrated_research_report import (
    build_integrated_research_report,
)


def check_assay_comparability(report_a, report_b):
    activities_a = extract_btk_ic50(report_a)
    activities_b = extract_btk_ic50(report_b)

    assays_a = {
        activity["assay_chembl_id"]
        for activity in activities_a
        if activity.get("assay_chembl_id")
    }

    assays_b = {
        activity["assay_chembl_id"]
        for activity in activities_b
        if activity.get("assay_chembl_id")
    }

    shared_assays = sorted(
        assays_a.intersection(assays_b)
    )

    return {
        "molecule_a": report_a.get("molecule"),
        "molecule_b": report_b.get("molecule"),
        "shared_assays": shared_assays,
        "shared_assay_count": len(shared_assays),
        "comparability_status": (
            "Shared assay identifiers found; "
            "experimental conditions still require review."
            if shared_assays
            else
            "No shared assay identifiers identified "
            "in the retrieved BTK IC50 records."
        ),
        "scientific_note": (
            "A shared assay identifier supports further "
            "comparability assessment but does not "
            "guarantee identical experimental conditions."
        ),
    }


if __name__ == "__main__":
    disease = "Multiple Sclerosis"

    print("Retrieving Orelabrutinib...")
    report_a = build_integrated_research_report(
        "Orelabrutinib",
        disease,
    )

    print("Retrieving Tolebrutinib...")
    report_b = build_integrated_research_report(
        "Tolebrutinib",
        disease,
    )

    result = check_assay_comparability(
        report_a,
        report_b,
    )

    print("\nASSAY COMPARABILITY RESULTS")
    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
    ))
