
import json
import requests

from src.analysis.trial_relevance import is_relevant_trial


API_URL = "https://clinicaltrials.gov/api/v2/studies"


def filter_trials_by_disease(
    trials: list[dict],
    disease: str,
) -> dict:
    """
    Filter trials using registered conditions.
    """

    relevant = []
    excluded = []
    missing_conditions = []

    for trial in trials:
        conditions = trial.get("conditions")

        if not isinstance(conditions, list) or not conditions:
            missing_conditions.append(trial)
            continue

        if is_relevant_trial(disease, conditions):
            relevant.append(trial)
        else:
            excluded.append(trial)

    return {
        "disease": disease,
        "examined_count": len(trials),
        "relevant_count": len(relevant),
        "excluded_count": len(excluded),
        "missing_conditions_count": len(missing_conditions),
        "trials": relevant,
        "excluded_nct_ids": [
            trial.get("nct_id")
            for trial in excluded
        ],
        "scientific_note": (
            "Conservative condition-name filtering. "
            "This is not a validated medical "
            "ontology matcher."
        ),
    }


def search_clinical_trials(
    disease,
    max_results=5,
    intervention_type="DRUG",
    phase=None,
    status=None,
):
    """
    Search ClinicalTrials.gov and filter studies
    using their registered conditions.
    """

    disease = disease.strip()

    if not disease:
        raise ValueError("Disease name cannot be empty.")

    max_results = max(1, min(int(max_results), 20))

    filters = [
        "AREA[StudyType](INTERVENTIONAL)"
    ]

    if intervention_type:
        filters.append(
            f"AREA[InterventionType]({intervention_type})"
        )

    if phase:
        filters.append(
            f"AREA[Phase]({phase})"
        )

    if status:
        filters.append(
            f"AREA[OverallStatus]({status})"
        )

    params = {
        "query.cond": disease,
        "filter.advanced": " AND ".join(filters),
        "pageSize": 100,
        "format": "json",
        "countTotal": "true",
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    trials = []

    for study in data.get("studies", []):
        protocol = study.get("protocolSection", {})

        identification = protocol.get(
            "identificationModule", {}
        )

        conditions_module = protocol.get(
            "conditionsModule", {}
        )

        conditions = conditions_module.get(
            "conditions", []
        )

        status_module = protocol.get(
            "statusModule", {}
        )

        design = protocol.get(
            "designModule", {}
        )

        interventions_module = protocol.get(
            "armsInterventionsModule", {}
        )

        interventions = []

        for item in interventions_module.get(
            "interventions", []
        ):
            interventions.append({
                "name": item.get("name"),
                "type": item.get("type"),
            })

        nct_id = identification.get("nctId")

        trials.append({
            "nct_id": nct_id,
            "title": identification.get("briefTitle"),
            "conditions": conditions,
            "status": status_module.get("overallStatus"),
            "phases": design.get("phases", []),
            "study_type": design.get("studyType"),
            "interventions": interventions,
            "start_date": status_module.get(
                "startDateStruct", {}
            ).get("date"),
            "completion_date": status_module.get(
                "completionDateStruct", {}
            ).get("date"),
            "has_results": study.get(
                "hasResults", False
            ),
            "url": (
                f"https://clinicaltrials.gov/study/{nct_id}"
                if nct_id else None
            ),
        })

    filtered = filter_trials_by_disease(
        trials=trials,
        disease=disease,
    )

    relevant_trials = filtered["trials"][:max_results]

    return {
        "disease": disease,
        "total_count": data.get("totalCount"),
        "examined_count": filtered["examined_count"],
        "relevant_count": filtered["relevant_count"],
        "excluded_count": filtered["excluded_count"],
        "missing_conditions_count": filtered[
            "missing_conditions_count"
        ],
        "returned_count": len(relevant_trials),
        "trials": relevant_trials,
        "excluded_nct_ids": filtered["excluded_nct_ids"],
        "scientific_note": (
            "ClinicalTrials.gov results were filtered "
            "using registered condition names. "
            "Counts of relevant and excluded trials "
            "apply only to the fetched API page. "
            "The filter is not a validated medical "
            "ontology matcher. Trial registration "
            "does not establish efficacy or safety."
        ),
    }


if __name__ == "__main__":
    print("\nNEUROSCOPE.AI - CLINICAL TRIALS TEST\n")

    try:
        results = search_clinical_trials(
            disease="Multiple Sclerosis",
            max_results=5,
            intervention_type="DRUG",
            phase="PHASE3",
            status="RECRUITING",
        )

        print(
            json.dumps(
                results,
                indent=2,
                ensure_ascii=False,
            )
        )

    except requests.RequestException as error:
        print(f"API connection error: {error}")

    except (ValueError, TypeError) as error:
        print(f"Input error: {error}")
