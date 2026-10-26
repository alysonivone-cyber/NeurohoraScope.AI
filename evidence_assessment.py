
from pathlib import Path
import json


def assess_evidence(report):
    pharmacology = report.get("pharmacology") or {}
    clinical = report.get("clinical_trials") or {}
    literature = report.get("literature") or {}

    activities = (
        pharmacology.get("bioactivities") or {}
    ).get("activities", [])

    trials = clinical.get("studies", [])
    publications = literature.get("publications", [])

    clinical_results = [
        trial for trial in trials
        if trial.get("has_results") is True
    ]

    review_articles = [
        publication for publication in publications
        if "review" in [
            str(item).lower()
            for item in publication.get("publication_types", [])
        ]
    ]

    assessment = {
        "molecule": report.get("molecule"),
        "disease": report.get("disease"),

        "experimental_evidence": {
            "records_retrieved": len(activities),
            "classification": (
                "Experimental pharmacological data available"
                if activities
                else "No experimental records retrieved"
            ),
            "clinical_efficacy_established": False,
        },

        "clinical_evidence": {
            "trials_retrieved": len(trials),
            "trials_with_registered_results": len(
                clinical_results
            ),
            "classification": (
                "Registered trial results available for review"
                if clinical_results
                else "No registered trial results identified "
                     "in retrieved records"
            ),
            "efficacy_conclusion": "Not assessed",
        },

        "literature_evidence": {
            "publications_retrieved": len(publications),
            "review_articles": len(review_articles),
            "classification": (
                "Bibliographic evidence retrieved"
                if publications
                else "No publications retrieved"
            ),
        },

        "overall_assessment": (
            "Evidence inventory only. "
            "No automated conclusion regarding "
            "clinical efficacy or safety."
        ),
    }

    return assessment


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

    assessment = assess_evidence(report)

    print(json.dumps(
        assessment,
        indent=2,
        ensure_ascii=False,
    ))
