
import json

from integrated_research_report import (
    build_integrated_research_report,
)


def extract_btk_ic50(report):
    pharmacology = report.get("pharmacology") or {}

    activities = (
        pharmacology.get("bioactivities") or {}
    ).get("activities") or []

    results = []

    for activity in activities:
        target = activity.get("target_name") or ""

        if target != "Tyrosine-protein kinase BTK":
            continue

        if activity.get("standard_type") != "IC50":
            continue

        if activity.get("standard_units") != "nM":
            continue

        if activity.get("standard_relation") != "=":
            continue

        value = activity.get("standard_value")

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue

        if numeric_value <= 0:
            continue

        results.append({
            "ic50_nM": numeric_value,
            "assay_chembl_id": activity.get(
                "assay_chembl_id"
            ),
        })

    return results


def main():
    disease = "Multiple Sclerosis"

    comparison = {}

    for molecule in [
        "Orelabrutinib",
        "Tolebrutinib",
    ]:
        print(f"Analyzing {molecule}...")

        report = build_integrated_research_report(
            molecule,
            disease,
        )

        comparison[molecule] = extract_btk_ic50(
            report
        )

    print("\nBTK IC50 COMPARISON")
    print(json.dumps(
        comparison,
        indent=2,
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
