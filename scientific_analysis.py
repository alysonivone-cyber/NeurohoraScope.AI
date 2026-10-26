
from pathlib import Path
from datetime import datetime, timezone
import json

from evidence_assessment import assess_evidence
from research_gap_detector import detect_research_gaps


def generate_scientific_analysis(report):
    return {
        "analysis_type": "scientific_evidence_assessment",
        "molecule": report.get("molecule"),
        "disease": report.get("disease"),
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "evidence_assessment": assess_evidence(report),
        "research_gap_analysis": detect_research_gaps(report),
        "methodology": {
            "approach": "Rule-based evidence inventory",
            "sources": [
                "ChEMBL",
                "ClinicalTrials.gov",
                "PubMed",
            ],
            "clinical_efficacy_evaluated": False,
            "limitations": (
                "This analysis describes retrieved records. "
                "It does not establish clinical efficacy, "
                "safety, or the completeness of the evidence."
            ),
        },
    }


if __name__ == "__main__":
    reports_directory = Path("reports")

    json_files = sorted(
        reports_directory.glob("research_report_*.json"),
        key=lambda path: path.stat().st_mtime,
    )

    if not json_files:
        raise FileNotFoundError(
            "No integrated research report found."
        )

    source_path = json_files[-1]

    with source_path.open(
        "r", encoding="utf-8"
    ) as file:
        report = json.load(file)

    analysis = generate_scientific_analysis(report)

    output_path = source_path.with_name(
        source_path.stem + "_analysis.json"
    )

    output_path.write_text(
        json.dumps(
            analysis,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nSCIENTIFIC ANALYSIS GENERATED")
    print(f"File: {output_path.resolve()}")
    print(
        "Research gaps:",
        analysis["research_gap_analysis"]["gaps_identified"],
    )
