
from pathlib import Path
import json

from evidence_assessment import assess_evidence


def detect_research_gaps(report):
    assessment = assess_evidence(report)

    pharmacology = report.get("pharmacology") or {}
    clinical = report.get("clinical_trials") or {}
    literature = report.get("literature") or {}

    activities = (
        pharmacology.get("bioactivities") or {}
    ).get("activities", [])

    trials = clinical.get("studies", [])
    publications = literature.get("publications", [])

    gaps = []

    # Missing experimental measurements
    missing_values = [
        activity for activity in activities
        if activity.get("standard_value") in (None, "")
    ]

    if missing_values:
        gaps.append({
            "category": "Experimental pharmacology",
            "severity": "Data quality",
            "description": (
                f"{len(missing_values)} retrieved bioactivity "
                "records have no reported standard value."
            ),
        })

    # Missing registered clinical results
    trials_without_results = [
        trial for trial in trials
        if trial.get("has_results") is False
    ]

    trials_unknown_results = [
        trial for trial in trials
        if trial.get("has_results") is None
    ]

    if trials_without_results:
        gaps.append({
            "category": "Clinical evidence",
            "severity": "Evidence availability",
            "description": (
                f"{len(trials_without_results)} retrieved trials "
                "have no registered results according to "
                "the available data."
            ),
        })

    if trials_unknown_results:
        gaps.append({
            "category": "Clinical evidence",
            "severity": "Unknown",
            "description": (
                f"Results availability is unknown for "
                f"{len(trials_unknown_results)} retrieved trials."
            ),
        })

    # Literature evidence type
    if publications:
        review_count = assessment[
            "literature_evidence"
        ]["review_articles"]

        if review_count == len(publications):
            gaps.append({
                "category": "Scientific literature",
                "severity": "Evidence coverage",
                "description": (
                    "All retrieved publications are classified "
                    "as reviews. No original research article "
                    "was identified in this retrieved set."
                ),
            })

    return {
        "molecule": report.get("molecule"),
        "disease": report.get("disease"),
        "gaps_identified": len(gaps),
        "research_gaps": gaps,
        "interpretation": (
            "These gaps describe limitations of retrieved "
            "records, not necessarily gaps in the entire "
            "scientific literature."
        ),
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

    with json_files[-1].open(
        "r", encoding="utf-8"
    ) as file:
        report = json.load(file)

    gaps = detect_research_gaps(report)

    print(json.dumps(
        gaps,
        indent=2,
        ensure_ascii=False,
    ))
