
import json

from integrated_research_report import (
    build_integrated_research_report,
)
from src.analysis.molecular_selectivity import extract_target_profile


def build_target_matrix(report_a, report_b):
    profile_a = extract_target_profile(report_a)
    profile_b = extract_target_profile(report_b)

    targets_a = profile_a["target_profile"]
    targets_b = profile_b["target_profile"]

    all_targets = sorted(
        set(targets_a) | set(targets_b)
    )

    matrix = []

    for target in all_targets:
        matrix.append({
            "target": target,
            "molecule_a": targets_a.get(target, []),
            "molecule_b": targets_b.get(target, []),
        })

    return {
        "molecule_a": report_a.get("molecule"),
        "molecule_b": report_b.get("molecule"),
        "measurement": "IC50",
        "unit": "nM",
        "targets_in_matrix": len(all_targets),
        "matrix": matrix,
        "interpretation": (
            "This matrix summarizes retrieved IC50 "
            "measurements by annotated target. "
            "Target annotations may represent different "
            "assay contexts, including cellular readouts. "
            "Missing entries do not demonstrate "
            "absence of pharmacological activity."
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

    result = build_target_matrix(
        report_a,
        report_b,
    )

    print("\nTARGET MATRIX RESULTS")
    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
    ))
