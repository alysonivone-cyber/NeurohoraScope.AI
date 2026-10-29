
import json
from datetime import datetime, timezone
from pathlib import Path

from src.analysis.integrated_research_report import (
    build_integrated_research_report,
)


def export_research_report(
    molecule_name,
    disease=None,
):
    report = build_integrated_research_report(
        molecule_name=molecule_name,
        disease=disease,
        max_activities=10,
        max_trials=10,
        max_publications=10,
    )

    output_directory = Path("reports")
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S_%f")

    filename = (
        f"research_report_{timestamp}.json"
    )

    output_path = output_directory / filename

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRESEARCH REPORT EXPORTED")
    print(f"File: {output_path.resolve()}")

    return output_path


if __name__ == "__main__":
    export_research_report(
        molecule_name="Orelabrutinib",
        disease="Multiple Sclerosis",
    )
