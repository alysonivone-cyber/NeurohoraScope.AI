
import json
from pathlib import Path
from decimal import Decimal, InvalidOperation
from src.storage.chembl_cache import cached_chembl_get
import requests
import time

API = "https://www.ebi.ac.uk/chembl/api/data"

def chembl_get(url, params=None, attempts=3):
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=(10, 30),
            )

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as error:
            status_code = getattr(
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
                or status_code in (429, 500, 502, 503, 504)
            )

            print(
                f"ChEMBL request failed "
                f"({attempt}/{attempts}): {error}"
            )

            if not retryable or attempt == attempts:
                raise

            wait_seconds = 2 ** attempt

            print(
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

def normalize_number(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def get_molecule_id(name):
    response = chembl_get(
    f"{API}/molecule/search.json",
    params={
        "q": name,
        "limit": 100,
    },
)
    response.raise_for_status()

    matches = []

    for molecule in response.json().get(
        "molecules", []
    ):
        preferred_name = (
            molecule.get("pref_name") or ""
        )

        if preferred_name.casefold() == name.casefold():
            matches.append(
                molecule["molecule_chembl_id"]
            )

    if len(matches) == 1:
        return matches[0]

    raise ValueError(
        f"Expected one exact molecule match "
        f"for {name}; found {matches}"
    )

def get_all_assay_activities(assay_id):
    url = f"{API}/activity.json"

    params = {
        "assay_chembl_id": assay_id,
        "limit": 100,
    }

    activities = []
    visited_urls = set()

    while url:
        request_url = requests.Request(
            "GET",
            url,
            params=params,
        ).prepare().url

        if request_url in visited_urls:
            raise RuntimeError(
                f"Repeated pagination URL: {request_url}"
            )

        visited_urls.add(request_url)

        data = cached_chembl_get(
            url,
            params=params,
            timeout=45,
        )

        activities.extend(
            data.get("activities", [])
        )

        next_page = (
            data.get("page_meta") or {}
        ).get("next")

        if next_page:
            url = requests.compat.urljoin(
                request_url,
                next_page,
            )
            params = None
        else:
            url = None

    return activities

def find_exact_activity(measurement, molecule_id):
    assay_id = measurement["assay_chembl_id"]

    activities = get_all_assay_activities(
        assay_id
    )

    expected_value = normalize_number(
        measurement["ic50_nM"]
    )

    matches = []

    for activity in activities:
        if (
            activity.get("molecule_chembl_id")
            != molecule_id
        ):
            continue

        if activity.get("standard_type") != "IC50":
            continue

        if activity.get("standard_units") != "nM":
            continue

        if activity.get("standard_relation") != "=":
            continue

        actual_value = normalize_number(
            activity.get("standard_value")
        )

        if actual_value != expected_value:
            continue

        matches.append({
            "activity_id": activity.get(
                "activity_id"
            ),
            "molecule_chembl_id": molecule_id,
            "assay_chembl_id": assay_id,
            "document_chembl_id": activity.get(
                "document_chembl_id"
            ),
            "standard_value": activity.get(
                "standard_value"
            ),
            "standard_units": activity.get(
                "standard_units"
            ),
        })

    if len(matches) == 1:
        status = "EXACT_MATCH"
    elif len(matches) == 0:
        status = "NO_MATCH"
    else:
        status = "AMBIGUOUS_MATCH"

    return {
        "molecule": measurement["molecule"],
        "target": measurement["target"],
        "assay_chembl_id": assay_id,
        "ic50_nM": measurement["ic50_nM"],
        "match_status": status,
        "match_count": len(matches),
        "matches": matches,
    }


if __name__ == "__main__":
    source = Path(
        "reports/scientific_data_provenance.json"
    )

    provenance = json.loads(
        source.read_text(encoding="utf-8")
    )

    molecule_ids = {
    "Orelabrutinib": "CHEMBL4650321",
    "Tolebrutinib": "CHEMBL4650323",
}

    print("Molecule identifiers:")
    print(json.dumps(
        molecule_ids,
        indent=2,
    ))

    
    results = []

    output_path = Path(
        "reports/exact_activity_matches.json"
    )

    for record in provenance["records"]:
        print(
            "\nMatching:",
            record["molecule"],
            record["target"],
            record["ic50_nM"],
            "nM",
            flush=True,
        )

        try:
            result = find_exact_activity(
                record,
                molecule_ids[record["molecule"]],
            )

        except requests.exceptions.RequestException as error:
            result = {
                "molecule": record["molecule"],
                "target": record["target"],
                "assay_chembl_id": record["assay_chembl_id"],
                "ic50_nM": record["ic50_nM"],
                "match_status": "RETRIEVAL_ERROR",
                "match_count": 0,
                "matches": [],
                "error": str(error),
            }

        results.append(result)

        # Save immediately after every measurement.
        output_path.write_text(
            json.dumps(
                results,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print(
            "Status:",
            result["match_status"],
            "| Matches:",
            result["match_count"],
            flush=True,
        )

        for match in result["matches"]:
            print(
                "Activity:",
                match["activity_id"],
                "| Document:",
                match["document_chembl_id"],
            )

        print(
            "Saved:",
            len(results),
            "records",
            flush=True,
        )

    print(
        "\nEXACT ACTIVITY MATCHING COMPLETED"
    )
    print("Records analyzed:", len(results))
    print("File:", output_path.resolve())
