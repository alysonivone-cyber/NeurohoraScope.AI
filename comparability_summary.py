
import json
from pathlib import Path
from collections import Counter

from experimental_comparability import (
    assess_experimental_comparability,
)


def build_comparability_summary(matrix):
    analysis = assess_experimental_comparability(
        matrix
    )

    comparisons = analysis["comparisons"]

    status_counts = Counter(
        item["status"]
        for item in comparisons
    )

    same_target_pairs = [
        item
        for item in comparisons
        if item["same_target"]
    ]

    review_candidates = [
        item
        for item in same_target_pairs
        if item["same_format"]
    ]

    return {
        "molecule_a": matrix.get("molecule_a"),
        "molecule_b": matrix.get("molecule_b"),
        "total_comparisons": len(comparisons),
        "same_target_pairs": len(
            same_target_pairs
        ),
        "same_target_same_format_pairs": len(
            review_candidates
        ),
        "status_distribution": dict(
            status_counts
        ),
        "review_candidates": review_candidates,
        "scientific_recommendations": [
            (
                "Review assay descriptions and "
                "experimental conditions before "
                "quantitative comparisons."
            ),
            (
                "Do not interpret identical assay "
                "formats as proof of comparability."
            ),
            (
                "Do not infer molecular superiority "
                "from unharmonized IC50 measurements."
            ),
        ],
    }


if __name__ == "__main__":
    reports_dir = Path("reports")

    files = sorted(
        reports_dir.glob("experimental_matrix_*.json"),
        key=lambda p: p.stat().st_mtime,
    )

    if not files:
        raise FileNotFoundError(
            "No experimental matrix JSON found."
        )

    latest_file = files[-1]

    matrix = json.loads(
        latest_file.read_text(encoding="utf-8")
    )

    summary = build_comparability_summary(
        matrix
    )

    print("\nSCIENTIFIC COMPARABILITY SUMMARY")
    print(json.dumps(
        summary,
        indent=2,
        ensure_ascii=False,
    ))
