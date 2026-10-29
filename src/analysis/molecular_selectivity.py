
import json

from src.analysis.integrated_research_report import (
    build_integrated_research_report,
)


def extract_target_profile(report):
    pharmacology = report.get("pharmacology") or {}

    activities = (
        pharmacology.get("bioactivities") or {}
    ).get("activities") or []

    target_profile = {}

    for activity in activities:
        if activity.get("standard_type") != "IC50":
            continue

        if activity.get("standard_units") != "nM":
            continue

        if activity.get("standard_relation") != "=":
            continue

        target = activity.get("target_name")

        if not target or target == "Unchecked":
            continue

        try:
            value = float(
                activity.get("standard_value")
            )
        except (TypeError, ValueError):
            continue

        if value <= 0:
            continue

        target_profile.setdefault(
            target, []
        ).append({
            "ic50_nM": value,
            "assay_chembl_id": activity.get(
                "assay_chembl_id"
            ),
        })

    return {
        "molecule": report.get("molecule"),
        "targets_identified": len(target_profile),
        "target_profile": target_profile,
        "interpretation": (
            "This is a descriptive experimental "
            "target profile. Selectivity ratios and "
            "comparative potency are not assessed "
            "without verifying assay comparability."
        ),
    }


if __name__ == "__main__":
    disease = "Multiple Sclerosis"

    for molecule in [
        "Orelabrutinib",
        "Tolebrutinib",
    ]:
        print(f"\nAnalyzing {molecule}...")

        report = build_integrated_research_report(
            molecule,
            disease,
        )

        profile = extract_target_profile(report)

        print(json.dumps(
            profile,
            indent=2,
            ensure_ascii=False,
        ))
