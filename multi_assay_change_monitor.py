
import hashlib
import json

from datetime import datetime, timezone
from pathlib import Path

from chembl_cache import CACHE_DIR, cache_key
from cache_version_comparator import compare_versions


API = (
    "https://www.ebi.ac.uk/"
    "chembl/api/data/activity.json"
)

HISTORY_DIR = Path("cache/chembl_history")

PROVENANCE_PATH = Path(
    "reports/scientific_data_provenance.json"
)

OUTPUT_PATH = Path(
    "reports/multi_assay_change_report.json"
)


def load_json(path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def main():
    provenance = load_json(PROVENANCE_PATH)

    assay_ids = sorted({
        record["assay_chembl_id"]
        for record in provenance["records"]
        if record.get("assay_chembl_id")
    })

    results = []

    for assay_id in assay_ids:
        params = {
            "assay_chembl_id": assay_id,
            "limit": 100,
        }

        key = cache_key(API, params)

        current_path = (
            CACHE_DIR / f"{key}.json"
        )

        history_files = sorted(
            HISTORY_DIR.glob(f"{key}_*.json")
        )

        result = {
            "assay_chembl_id": assay_id,
            "status": None,
        }

        if not current_path.exists():
            result["status"] = "MISSING_CACHE"

        elif not history_files:
            result["status"] = "NO_HISTORY"

        else:
            previous_path = history_files[-1]

            try:
                old_payload = load_json(
                    previous_path
                )

                new_payload = load_json(
                    current_path
                )

                comparison = compare_versions(
                    old_payload,
                    new_payload
                )

                result.update({
                    "status": (
                        "CHANGED"
                        if comparison["changed"]
                        else "UNCHANGED"
                    ),
                    "previous_file": (
                        previous_path.name
                    ),
                    "current_file": (
                        current_path.name
                    ),
                    "comparison": comparison,
                })

            except (
                OSError,
                ValueError,
                KeyError,
                TypeError,
            ) as error:
                result["status"] = (
                    "COMPARISON_ERROR"
                )
                result["error"] = str(error)

        results.append(result)

        print(
            f"{assay_id}: {result['status']}"
        )

    summary = {}

    for result in results:
        status = result["status"]
        summary[status] = (
            summary.get(status, 0) + 1
        )

    report = {
        "project": "NeuroScope.AI",
        "analysis_type": (
            "multi_assay_change_monitor"
        ),
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_assays": len(assay_ids),
        "summary": summary,
        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "\nMULTI-ASSAY CHANGE MONITOR COMPLETED"
    )
    print("Total assays:", len(assay_ids))
    print(
        json.dumps(
            summary,
            indent=2
        )
    )
    print("Report:", OUTPUT_PATH.resolve())


if __name__ == "__main__":
    main()
