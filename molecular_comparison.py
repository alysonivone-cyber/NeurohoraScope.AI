
def compare_molecules(report_a, report_b):
    def summarize(report):
        pharmacology = report.get("pharmacology") or {}
        clinical = report.get("clinical_trials") or {}
        literature = report.get("literature") or {}

        bioactivities = (
            pharmacology.get("bioactivities") or {}
        ).get("activities") or []

        return {
            "molecule": report.get("molecule"),
            "disease": report.get("disease"),
            "bioactivity_records": len(bioactivities),
            "clinical_trials": len(
                clinical.get("studies") or []
            ),
            "publications": len(
                literature.get("publications") or []
            ),
        }

    return {
        "comparison_type": "descriptive_evidence_inventory",
        "molecule_a": summarize(report_a),
        "molecule_b": summarize(report_b),
        "interpretation": (
            "Record counts describe retrieved data coverage. "
            "They do not measure comparative efficacy, "
            "potency, safety, or therapeutic superiority."
        ),
    }


if __name__ == "__main__":
    import json
    from pathlib import Path

    reports = sorted(
        (
            path
            for path in Path("reports").glob(
                "research_report_*.json"
            )
            if not path.stem.endswith("_analysis")
        ),
        key=lambda path: path.stat().st_mtime,
    )

    if not reports:
        raise FileNotFoundError(
            "No research report found."
        )

    with reports[-1].open(
        encoding="utf-8"
    ) as file:
        report = json.load(file)

    # Initial test using the same report twice.
    comparison = compare_molecules(report, report)

    print(json.dumps(
        comparison,
        indent=2,
        ensure_ascii=False,
    ))
