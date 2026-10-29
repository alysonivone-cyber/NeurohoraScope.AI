
import json
from datetime import datetime, timezone
from pathlib import Path


CACHE_DIR = Path("cache/chembl")


def parse_timestamp(value):
    if not value:
        return None

    try:
        timestamp = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if timestamp.tzinfo is None:
            return None

        return timestamp.astimezone(
            timezone.utc
        )

    except (ValueError, TypeError):
        return None


def inspect_cache(max_age_days=30):
    now = datetime.now(timezone.utc)
    results = []

    for path in sorted(
        CACHE_DIR.glob("*.json")
    ):
        try:
            payload = json.loads(
                path.read_text(encoding="utf-8")
            )

            retrieved_at = parse_timestamp(
                payload.get("retrieved_at_utc")
            )

            if retrieved_at is None:
                status = "UNKNOWN_DATE"
                age_days = None

            else:
                age_days = (
                    now - retrieved_at
                ).total_seconds() / 86400

                if age_days < 0:
                    status = "FUTURE_TIMESTAMP"
                elif age_days <= max_age_days:
                    status = "FRESH"
                else:
                    status = "STALE"

            results.append({
                "cache_file": path.name,
                "request_url": payload.get(
                    "request_url"
                ),
                "retrieved_at_utc": payload.get(
                    "retrieved_at_utc"
                ),
                "age_days": (
                    round(age_days, 2)
                    if age_days is not None
                    else None
                ),
                "status": status,
            })

        except (
            json.JSONDecodeError,
            OSError,
            AttributeError,
        ) as error:
            results.append({
                "cache_file": path.name,
                "status": "INVALID_CACHE",
                "error": str(error),
            })

    return results


if __name__ == "__main__":
    results = inspect_cache(
        max_age_days=30
    )

    print("\nSCIENTIFIC CACHE FRESHNESS REPORT")
    print("Cache files:", len(results))

    for item in results:
        print(
            item["cache_file"][:12],
            "|",
            item["status"],
            "| Age:",
            item.get("age_days"),
            "days",
        )

    output_path = Path(
        "reports/cache_freshness_report.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nReport:", output_path.resolve())
