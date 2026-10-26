
from trial_relevance import is_relevant_trial


def test_relevant_ms():
    assert is_relevant_trial(
        "Multiple Sclerosis",
        ["Relapsing Remitting Multiple Sclerosis"],
    )

    assert is_relevant_trial(
        "Multiple Sclerosis",
        ["Multiple Sclerosis (MS) Primary Progressive"],
    )


def test_unrelated_tuberous_sclerosis():
    assert not is_relevant_trial(
        "Multiple Sclerosis",
        ["Tuberous Sclerosis Complex"],
    )


def test_other_disease():
    assert is_relevant_trial(
        "Parkinson Disease",
        ["Parkinson Disease"],
    )


if __name__ == "__main__":
    test_relevant_ms()
    test_unrelated_tuberous_sclerosis()
    test_other_disease()

    print("NEUROSCOPE.AI — RELEVANCE TEST")
    print("4 assertions passed.")
