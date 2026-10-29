
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


REPORT_PATH = Path(
    "reports/cache_version_comparison.json"
)

LOG_PATH = Path(
    "reports/scientific_change_log.json"
)


def load_json(path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def save_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def create_change_log_entry(report):
    comparison = report["comparison"]

    identity = {
        "assay_chembl_id": report[
            "assay_chembl_id"
        ],
        "previous_file": report[
            "previous_file"
        ],
        "current_file": report[
            "current_file"
        ],
        "previous_retrieved_at_utc": report.get(
            "previous_retrieved_at_utc"
        ),
        "current_retrieved_at_utc": report.get(
            "current_retrieved_at_utc"
        ),
        "comparison": comparison,
    }

    canonical = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    entry_id = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return {
        "entry_id": entry_id,
        "logged_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        **identity,
        "status": (
            "CHANGED"
            if comparison["changed"]
            else "UNCHANGED"
        ),
    }


def main():
    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            f"Missing comparison report: {REPORT_PATH}"
        )

    report = load_json(REPORT_PATH)

    if LOG_PATH.exists():
        history = load_json(LOG_PATH)
    else:
        history = {
            "schema_version": "1.0",
            "project": "NeuroScope.AI",
            "entries": [],
        }

    entry = create_change_log_entry(report)

    existing_ids = {
        item["entry_id"]
        for item in history["entries"]
    }

    if entry["entry_id"] in existing_ids:
        print(
            "Comparison already recorded. "
            "No duplicate added."
        )
    else:
        history["entries"].append(entry)
        save_json(LOG_PATH, history)
        print("New comparison added to log.")

    print("\nSCIENTIFIC CHANGE LOG")
    print(
        "Total entries:",
        len(history["entries"]),
    )
    print(
        "Assay:",
        entry["assay_chembl_id"],
    )
    print("Status:", entry["status"])
    print("Added:", len(entry["comparison"]["added"]))
    print("Removed:", len(entry["comparison"]["removed"]))
    print("Modified:", len(entry["comparison"]["modified"]))
    print("Log file:", LOG_PATH.resolve())


if __name__ == "__main__":
    main()
