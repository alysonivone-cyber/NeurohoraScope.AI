
import json
from pathlib import Path
from datetime import datetime, timezone

from integrated_research_report import (
    build_integrated_research_report,
)
from experimental_context import build_experimental_context


def build_experimental_matrix(report_a, report_b):
    context_a = build_experimental_context(report_a)
    context_b = build_experimental_context(report_b)

    rows = []

    for context in [context_a, context_b]:
        for measurement in context["measurements"]:
            rows.append({
                "molecule": context["molecule"],
                **measurement,
            })

    return {
        "analysis_type": "experimental_context_matrix",
        "molecule_a": report_a.get("molecule"),
        "molecule_b": report_b.get("molecule"),
        "measurement": "IC50",
        "unit": "nM",
        "total_measurements": len(rows),
        "matrix": rows,
        "interpretation": (
            "Measurements are grouped with their "
            "ChEMBL experimental metadata. "
            "Matching target and assay format alone "
            "do not establish direct comparability. "
            "No selectivity or potency ranking is made."
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

    print("Building experimental matrix...")
    matrix = build_experimental_matrix(
        report_a,
        report_b,
    )

    reports_directory = Path("reports")
    reports_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S_%f")

    output_path = reports_directory / (
        f"experimental_matrix_{timestamp}.json"
    )

    output_path.write_text(
        json.dumps(
            matrix,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nEXPERIMENTAL MATRIX GENERATED")
    print("Total measurements:", matrix["total_measurements"])
    print("File:", output_path.resolve())
