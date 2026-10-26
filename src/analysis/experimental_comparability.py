
import json
from pathlib import Path
from itertools import combinations


def assess_experimental_comparability(matrix):
    measurements = matrix.get("matrix", [])

    comparisons = []

    for a, b in combinations(measurements, 2):
        if a["molecule"] == b["molecule"]:
            continue

        same_target = (
            a.get("target_chembl_id") is not None
            and a.get("target_chembl_id")
            == b.get("target_chembl_id")
        )

        same_format = (
            a.get("assay_format") is not None
            and a.get("assay_format") != "UNKNOWN"
            and a.get("assay_format")
            == b.get("assay_format")
        )

        same_assay = (
            a.get("assay_chembl_id") is not None
            and a.get("assay_chembl_id")
            == b.get("assay_chembl_id")
        )

        if not same_target:
            status = "DIFFERENT_TARGETS"

        elif same_assay:
            status = "SHARED_ASSAY_REVIEW_REQUIRED"

        elif same_format:
            status = "SAME_FORMAT_DIFFERENT_ASSAYS"

        else:
            status = "DIFFERENT_EXPERIMENTAL_FORMATS"

        comparisons.append({
            "molecule_a": a["molecule"],
            "molecule_b": b["molecule"],
            "target_a": a.get("target"),
            "target_b": b.get("target"),
            "ic50_a_nM": a.get("ic50_nM"),
            "ic50_b_nM": b.get("ic50_nM"),
            "assay_a": a.get("assay_chembl_id"),
            "assay_b": b.get("assay_chembl_id"),
            "format_a": a.get("assay_format"),
            "format_b": b.get("assay_format"),
            "same_target": same_target,
            "same_format": same_format,
            "same_assay": same_assay,
            "status": status,
        })

    return {
        "comparison_count": len(comparisons),
        "comparisons": comparisons,
        "interpretation": (
            "These are descriptive screening flags, "
            "not validated comparability scores. "
            "Even shared assays require review of "
            "experimental conditions before quantitative "
            "potency comparisons."
        ),
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

    result = assess_experimental_comparability(
        matrix
    )

    print("EXPERIMENTAL COMPARABILITY ANALYSIS")
    print("Total comparisons:",
          result["comparison_count"])

    for comparison in result["comparisons"]:
        if comparison["same_target"]:
            print(
                comparison["molecule_a"],
                comparison["ic50_a_nM"],
                "vs",
                comparison["molecule_b"],
                comparison["ic50_b_nM"],
                "|",
                comparison["status"],
            )
