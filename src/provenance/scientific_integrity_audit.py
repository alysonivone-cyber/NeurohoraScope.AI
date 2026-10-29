
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPORTS_DIR = Path("reports")

FILES = {
    "matches": "exact_activity_matches.json",
    "provenance": "scientific_data_provenance.json",
    "freshness": "cache_freshness_report.json",
    "versions": "multi_assay_change_report.json",
    "change_log": "scientific_change_log.json",
}


def load_report(filename):
    path = REPORTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing required report: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def extract_records(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("records", "results"):
            if isinstance(data.get(key), list):
                return data[key]

    raise ValueError(
        "Unsupported report record structure"
    )


def main():
    reports = {
        key: load_report(filename)
        for key, filename in FILES.items()
    }

    matches = extract_records(
        reports["matches"]
    )

    provenance = extract_records(
        reports["provenance"]
    )

    freshness = reports["freshness"]

    versions = reports["versions"]

    change_log = reports["change_log"]

    if not isinstance(freshness, list):
        raise ValueError(
            "Unexpected freshness report format"
        )

    if not isinstance(
        versions.get("results"), list
    ):
        raise ValueError(
            "Unexpected version report format"
        )

    if not isinstance(
        change_log.get("entries"), list
    ):
        raise ValueError(
            "Unexpected change log format"
        )

    match_statuses = Counter(
    record.get("match_status", "UNKNOWN")
    for record in matches
    )

    cache_statuses = Counter(
        record.get("status", "UNKNOWN")
        for record in freshness
    )

    version_statuses = Counter(
        record.get("status", "UNKNOWN")
        for record in versions["results"]
    )

    checks = {
        "seven_exact_matches": (
            len(matches) == 7
            and match_statuses["EXACT_MATCH"] == 7
        ),
        "seven_provenance_records": (
            len(provenance) == 7
        ),
        "seven_cached_responses": (
            len(freshness) == 7
        ),
        "all_cache_files_fresh": (
            cache_statuses["FRESH"] == 7
        ),
        "seven_assays_monitored": (
            len(versions["results"]) == 7
        ),
        "no_version_comparison_errors": (
            version_statuses[
                "COMPARISON_ERROR"
            ] == 0
            and version_statuses[
                "MISSING_CACHE"
            ] == 0
        ),
        "change_log_not_empty": (
            len(change_log["entries"]) >= 1
        ),
        "no_duplicate_log_entries": (
            len({
                entry.get("entry_id")
                for entry in change_log["entries"]
            }) == len(change_log["entries"])
        ),
    }

    passed = sum(checks.values())
    total = len(checks)

    report = {
        "project": "NeuroScope.AI",
        "audit_type": (
            "scientific_integrity_audit"
        ),
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "checks": checks,
        "summary": {
            "passed": passed,
            "total": total,
            "all_passed": passed == total,
        },
        "metrics": {
            "exact_activity_matches": (
                match_statuses["EXACT_MATCH"]
            ),
            "provenance_records": (
                len(provenance)
            ),
            "cached_responses": (
                len(freshness)
            ),
            "fresh_cache_files": (
                cache_statuses["FRESH"]
            ),
            "monitored_assays": (
                len(versions["results"])
            ),
            "historical_comparisons": (
                len(change_log["entries"])
            ),
        },
        "limitations": [
            "Checks internal consistency of local reports.",
            "Does not independently validate ChEMBL records.",
            "Does not establish clinical efficacy or superiority.",
            "Freshness depends on the configured cache age threshold.",
        ],
    }

    output_path = (
        REPORTS_DIR
        / "scientific_integrity_audit.json"
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
        "\nNEUROSCOPE SCIENTIFIC INTEGRITY AUDIT"
    )

    for name, success in checks.items():
        print(
            "[PASS]" if success else "[FAIL]",
            name
        )

    print(
        f"\nAUDIT RESULT: {passed}/{total}"
    )

    print(
        "STATUS:",
        "PASSED" if passed == total else "FAILED"
    )

    print(
        "Report:",
        output_path.resolve()
    )

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
