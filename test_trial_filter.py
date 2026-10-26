
from clinical_trials_client import filter_trials_by_disease


def main():
    trials = [
        {
            "nct_id": "NCT07067463",
            "conditions": [
                "Multiple Sclerosis (MS) Primary Progressive"
            ],
        },
        {
            "nct_id": "NCT07403266",
            "conditions": [
                "Tuberous Sclerosis Complex"
            ],
        },
        {
            "nct_id": "NCT07299019",
            "conditions": [
                "Secondary Progressive Multiple Sclerosis"
            ],
        },
    ]

    result = filter_trials_by_disease(
        trials=trials,
        disease="Multiple Sclerosis",
    )

    assert result["examined_count"] == 3
    assert result["relevant_count"] == 2
    assert result["excluded_count"] == 1
    assert result["missing_conditions_count"] == 0

    assert (
        "NCT07403266"
        in result["excluded_nct_ids"]
    )

    print("NEUROSCOPE.AI — TRIAL FILTER TEST")
    print("All assertions passed.")
    print()
    print("Trials examined:", result["examined_count"])
    print("Relevant trials:", result["relevant_count"])
    print("Excluded trials:", result["excluded_count"])
    print("Excluded IDs:", result["excluded_nct_ids"])


if __name__ == "__main__":
    main()
