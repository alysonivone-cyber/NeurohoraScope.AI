
import json
from pathlib import Path
from datetime import datetime, timezone

from chembl_cache import CACHE_DIR, cache_key


HISTORY_DIR = Path("cache/chembl_history")

API = (
    "https://www.ebi.ac.uk/"
    "chembl/api/data/activity.json"
)


def activity_index(payload):
    activities = payload.get(
        "data", {}
    ).get("activities", [])

    indexed = {}

    for activity in activities:
        activity_id = activity.get("activity_id")

        if activity_id is None:
            raise ValueError(
                "Activity without activity_id"
            )

        key = str(activity_id)

        if key in indexed:
            raise ValueError(
                f"Duplicate activity_id: {key}"
            )

        indexed[key] = activity

    return indexed


def compare_versions(old_payload, new_payload):
    old = activity_index(old_payload)
    new = activity_index(new_payload)

    old_ids = set(old)
    new_ids = set(new)

    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)

    shared = old_ids & new_ids

    modified = sorted(
        activity_id
        for activity_id in shared
        if old[activity_id] != new[activity_id]
    )

    unchanged = sorted(
        activity_id
        for activity_id in shared
        if old[activity_id] == new[activity_id]
    )

    return {
        "old_count": len(old),
        "new_count": len(new),
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged_count": len(unchanged),
        "changed": bool(
            added or removed or modified
        ),
    }


if __name__ == "__main__":
    assay_id = "CHEMBL4714265"

    params = {
        "assay_chembl_id": assay_id,
        "limit": 100,
    }

    key = cache_key(API, params)

    current_path = CACHE_DIR / f"{key}.json"

    history_files = sorted(
        HISTORY_DIR.glob(f"{key}_*.json")
    )

    if not current_path.exists():
        raise FileNotFoundError(
            "Current cache file not found"
        )

    if not history_files:
        raise FileNotFoundError(
            "No archived version found"
        )

    previous_path = history_files[-1]

    old_payload = json.loads(
        previous_path.read_text(
            encoding="utf-8"
        )
    )

    new_payload = json.loads(
        current_path.read_text(
            encoding="utf-8"
        )
    )

    comparison = compare_versions(
        old_payload,
        new_payload,
    )

    report = {
        "analysis_type": (
            "scientific_data_version_comparison"
        ),
        "assay_chembl_id": assay_id,
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "previous_file": previous_path.name,
        "current_file": current_path.name,
        "previous_retrieved_at_utc": (
            old_payload.get("retrieved_at_utc")
        ),
        "current_retrieved_at_utc": (
            new_payload.get("retrieved_at_utc")
        ),
        "comparison": comparison,
        "limitations": (
            "Compares the cached activity records "
            "by activity_id and JSON field values. "
            "Does not independently validate "
            "experimental findings."
        ),
    }

    output_path = Path(
        "reports/cache_version_comparison.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "\nSCIENTIFIC DATA VERSION COMPARISON"
    )
    print("Assay:", assay_id)
    print("Old activities:", comparison["old_count"])
    print("New activities:", comparison["new_count"])
    print("Added:", len(comparison["added"]))
    print("Removed:", len(comparison["removed"]))
    print("Modified:", len(comparison["modified"]))
    print(
        "Unchanged:",
        comparison["unchanged_count"],
    )
    print(
        "Scientific data changed:",
        comparison["changed"],
    )
    print("Report:", output_path.resolve())
