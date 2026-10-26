
import json


from integrated_research_report import (
    build_integrated_research_report,
)
from src.analysis.molecular_comparison import compare_molecules
from pathlib import Path
from datetime import datetime, timezone
from pharmacology_comparison import extract_btk_ic50
from comparison_reliability import assess_comparison_reliability


def main():
    disease = "Multiple Sclerosis"

    print("Retrieving Orelabrutinib research data...")
    report_a = build_integrated_research_report(
        "Orelabrutinib",
        disease,
    )

    print("Retrieving Tolebrutinib research data...")
    report_b = build_integrated_research_report(
        "Tolebrutinib",
        disease,
    )

    comparison = compare_molecules(
        report_a,
        report_b,
    )

    comparison["pharmacology"] = {
        "target": "Tyrosine-protein kinase BTK",
        "measurement": "IC50",
        "unit": "nM",
        "molecule_a": extract_btk_ic50(report_a),
        "molecule_b": extract_btk_ic50(report_b),
    }

    comparison["comparability"] = (
        assess_comparison_reliability(
            report_a,
            report_b,
        )
    )

    output_directory = Path("reports")
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S_%f")

    output_path = output_directory / (
        f"molecular_comparison_{timestamp}.json"
    )

    output_path.write_text(
        json.dumps(
            comparison,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "\nCOMPARISON SAVED:",
        output_path.resolve(),
    )

    print("\nMOLECULAR COMPARISON RESULTS")
    print(json.dumps(
        comparison,
        indent=2,
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
