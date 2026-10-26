
from integrated_research_report import (
    build_integrated_research_report,
)


for molecule in ["Orelabrutinib", "Tolebrutinib"]:
    print(f"\nMOLECULE: {molecule}")

    report = build_integrated_research_report(
        molecule,
        "Multiple Sclerosis",
    )

    pharmacology = report.get("pharmacology") or {}
    bioactivities = (
        pharmacology.get("bioactivities") or {}
    ).get("activities") or []

    for activity in bioactivities[:5]:
        print({
            "target": activity.get("target_name"),
            "type": activity.get("standard_type"),
            "relation": activity.get("standard_relation"),
            "value": activity.get("standard_value"),
            "units": activity.get("standard_units"),
            "assay": activity.get("assay_chembl_id"),
        })
