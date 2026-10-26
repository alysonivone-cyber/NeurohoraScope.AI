
import re


def normalize_condition(text: str) -> str:
    """Normalize disease names for comparison."""
    return re.sub(
        r"\s+",
        " ",
        re.sub(r"[^a-z0-9]+", " ", text.casefold()),
    ).strip()


def is_relevant_trial(
    requested_disease: str,
    trial_conditions: list[str],
) -> bool:
    """
    Conservatively check trial-condition relevance.

    Currently includes an explicit rule for
    multiple sclerosis and its common subtypes.
    Other diseases require separate validation.
    """

    disease = normalize_condition(requested_disease)

    conditions = [
        normalize_condition(condition)
        for condition in trial_conditions
        if isinstance(condition, str)
    ]

    if disease in {"multiple sclerosis", "ms"}:
        return any(
            "multiple sclerosis" in condition
            for condition in conditions
        )

    return any(
        disease == condition
        for condition in conditions
    )
