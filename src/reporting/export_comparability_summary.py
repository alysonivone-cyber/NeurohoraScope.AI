
import json
from pathlib import Path
from datetime import datetime, timezone

from src.analysis.comparability_summary import (
    build_comparability_summary,
)


def export_comparability_summary():
    reports_dir = Path("reports")

    files = sorted(
        reports_dir.glob("experimental_matrix_*.json"),
        key=lambda p: p.stat().st_mtime,
    )

    if not files:
        raise FileNotFoundError(
            "No experimental matrix JSON found."
        )

    source_path = files[-1]

    matrix = json.loads(
        source_path.read_text(encoding="utf-8")
    )

    summary = build_comparability_summary(
        matrix
    )

    generated_at = datetime.now(timezone.utc)

    summary["generated_at_utc"] = (
        generated_at.isoformat()
    )

    summary["source_file"] = source_path.name

    timestamp = generated_at.strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    output_path = reports_dir / (
        f"comparability_summary_{timestamp}.json"
    )

    output_path.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path, summary


if __name__ == "__main__":
    output_path, summary = (
        export_comparability_summary()
    )

    print("\nCOMPARABILITY SUMMARY EXPORTED")
    print(
        "Total comparisons:",
        summary["total_comparisons"],
    )
    print(
        "Same-target pairs:",
        summary["same_target_pairs"],
    )
    print(
        "Review candidates:",
        summary["same_target_same_format_pairs"],
    )
    print("File:", output_path.resolve())
