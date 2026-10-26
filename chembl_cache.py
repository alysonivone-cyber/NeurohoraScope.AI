
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


CACHE_DIR = Path("cache/chembl")
CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def cache_key(url, params=None):
    request = requests.Request(
        "GET",
        url,
        params=params,
    ).prepare()

    return hashlib.sha256(
        request.url.encode("utf-8")
    ).hexdigest()


def cached_chembl_get(
    url,
    params=None,
    timeout=30,
    offline=False,
):
    key = cache_key(url, params)
    cache_file = CACHE_DIR / f"{key}.json"

    if cache_file.exists():
        cached = json.loads(
            cache_file.read_text(
                encoding="utf-8"
            )
        )

        print("[CACHE HIT]", url)

        return cached["data"]

    if offline:
        raise FileNotFoundError(
            f"No cached response for {url}"
        )

    print("[API REQUEST]", url)

    response = requests.get(
        url,
        params=params,
        timeout=timeout,
    )

    response.raise_for_status()

    data = response.json()

    payload = {
        "request_url": response.url,
        "retrieved_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "data": data,
    }

    cache_file.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return data


if __name__ == "__main__":
    assay_id = "CHEMBL4714265"

    url = (
        "https://www.ebi.ac.uk/"
        "chembl/api/data/activity.json"
    )

    params = {
        "assay_chembl_id": assay_id,
        "limit": 100,
    }

    print("\nFIRST REQUEST")
    first = cached_chembl_get(
        url,
        params=params,
    )

    print(
        "Activities:",
        len(first.get("activities", [])),
    )

    print("\nSECOND REQUEST")
    second = cached_chembl_get(
        url,
        params=params,
        offline=True,
    )

    print(
        "Activities:",
        len(second.get("activities", [])),
    )

    print(
        "\nCACHE TEST:",
        "SUCCESS" if first == second else "FAILED",
    )
