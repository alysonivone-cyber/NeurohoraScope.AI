
import json

from src.analysis.pharmacology_comparison import extract_btk_ic50
from src.analysis.assay_comparability import check_assay_comparability
from src.analysis.integrated_research_report import (
    build_integrated_research_report,
)


def assess_comparison_reliability(report_a, report_b):
    activities_a = extract_btk_ic50(report_a)
    activities_b = extract_btk_ic50(report_b)

    comparability = check_assay_comparability(
        report_a,
        report_b,
    )

    if not activities_a or not activities_b:
        status = "INSUFFICIENT_DATA"
        explanation = (
            "At least one molecule has no eligible "
            "BTK IC50 measurement in the retrieved records."
        )

    elif comparability["shared_assay_count"] > 0:
        status = "SHARED_ASSAY_FOUND"
        explanation = (
            "Shared assay identifiers were found. "
            "Experimental protocols and conditions "
            "must still be reviewed before comparing values."
        )

    else:
        status = "DIFFERENT_ASSAYS"
        explanation = (
            "Both molecules have eligible BTK IC50 "
            "measurements, but no shared assay identifier "
            "was found in the retrieved records."
        )

    return {
        "molecule_a": report_a.get("molecule"),
        "molecule_b": report_b.get("molecule"),
        "eligible_measurements_a": len(activities_a),
        "eligible_measurements_b": len(activities_b),
        "shared_assay_count": comparability[
            "shared_assay_count"
        ],
        "comparability_status": status,
        "explanation": explanation,
        "quantitative_superiority_assessed": False,
        "scientific_limitation": (
            "This rule-based status is not a validated "
            "measure of assay quality, comparative potency, "
            "or clinical efficacy."
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

    result = assess_comparison_reliability(
        report_a,
        report_b,
    )

    print("\nCOMPARISON RELIABILITY RESULTS")
    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
    ))
