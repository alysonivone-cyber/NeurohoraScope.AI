
import hashlib
import json
import os
import time

from datetime import datetime, timezone
from pathlib import Path

import requests

from chembl_cache import CACHE_DIR, cache_key


API = (
    "https://www.ebi.ac.uk/"
    "chembl/api/data/activity.json"
)

HISTORY_DIR = Path("cache/chembl_history")


def save_json_atomic(path, payload):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_name(
        path.name + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    os.replace(temporary, path)


def refresh_cached_request(url, params=None):
    key = cache_key(url, params)
    cache_file = CACHE_DIR / f"{key}.json"

    old_payload = None

    if cache_file.exists():
        old_payload = json.loads(
            cache_file.read_text(
                encoding="utf-8"
            )
        )

    response = None

    for attempt in range(1, 4):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=(10, 45),
            )
            response.raise_for_status()
            break

        except requests.exceptions.RequestException as error:
            status = getattr(
                getattr(error, "response", None),
                "status_code",
                None,
            )

            retryable = (
                isinstance(
                    error,
                    (
                        requests.exceptions.Timeout,
                        requests.exceptions.ConnectionError,
                    ),
                )
                or status in (429, 500, 502, 503, 504)
            )

            if not retryable or attempt == 3:
                raise

            print(
                f"Temporary API failure "
                f"({attempt}/3): {error}"
            )

            time.sleep(2 ** attempt)

    data = response.json()

    retrieved_at = datetime.now(
        timezone.utc
    ).isoformat()

    new_payload = {
        "request_url": response.url,
        "retrieved_at_utc": retrieved_at,
        "data": data,
    }

    archived_path = None

    if old_payload is not None:
        HISTORY_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%dT%H%M%S%fZ")

        archived_path = HISTORY_DIR / (
            f"{key}_{timestamp}.json"
        )

        save_json_atomic(
            archived_path,
            old_payload,
        )

    save_json_atomic(
        cache_file,
        new_payload,
    )

    return {
        "cache_file": str(cache_file),
        "archived_file": (
            str(archived_path)
            if archived_path
            else None
        ),
        "retrieved_at_utc": retrieved_at,
        "activities": len(
            data.get("activities", [])
        ),
    }


if __name__ == "__main__":
    assay_id = "CHEMBL4714265"

    print(
        "\nREFRESHING ChEMBL ASSAY:",
        assay_id,
    )

    result = refresh_cached_request(
        API,
        params={
            "assay_chembl_id": assay_id,
            "limit": 100,
        },
    )

    print(
        "\nSCIENTIFIC CACHE REFRESH COMPLETED"
    )
    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )
