
import json

from pharmacology_report import build_pharmacology_report
from molecule_research import research_molecule
from trial_relevance import is_relevant_trial
from molecule_literature import research_molecule_literature

def build_integrated_research_report(
    molecule_name,
    disease=None,
    max_activities=10,
    max_trials=10,
    max_publications=10,
):
    """
    Combine ChEMBL pharmacology data with
    ClinicalTrials.gov registered studies.

    The report is intended for scientific
    exploration, not clinical decision-making.
    """

    molecule_name = molecule_name.strip()

    if not molecule_name:
        raise ValueError("Molecule name is required.")

    disease = disease.strip() if disease else None

    if not disease:
        disease = None

    max_activities = max(
        1, min(int(max_activities), 20)
    )

    max_trials = max(
        1, min(int(max_trials), 20)
    )

    # 1. Molecular pharmacology
    pharmacology = build_pharmacology_report(
        molecule_name=molecule_name,
        max_activities=max_activities,
    )

    # 2. Registered clinical studies
    clinical = research_molecule(
        molecule=molecule_name,
        disease=disease,
        max_results=max_trials,
    )

    studies = clinical.get("studies", [])

        # 3. Scientific literature
    literature = research_molecule_literature(
        molecule_name=molecule_name,
        disease=disease,
        max_results=max_publications,
    )

    # 3. Optional conservative disease filtering
    if disease:
        relevant_studies = []
        excluded_studies = []
        missing_conditions = []

        for study in studies:
            conditions = study.get("conditions", [])

            if not conditions:
                missing_conditions.append(study)
            elif is_relevant_trial(disease, conditions):
                relevant_studies.append(study)
            else:
                excluded_studies.append(study)

    else:
        relevant_studies = studies
        excluded_studies = []
        missing_conditions = []

    # 4. Summarize trial phases and result availability
    phase_counts = {}

    for study in relevant_studies:
        for phase in study.get("phases", []):
            phase_counts[phase] = (
                phase_counts.get(phase, 0) + 1
            )

    studies_with_results = sum(
        1
        for study in relevant_studies
        if study.get("has_results") is True
    )

    # 5. Structured report
    return {
        "report_type": "integrated_neuropharmacology",
        "molecule": molecule_name,
        "disease": disease,
        "pharmacology": pharmacology,
        "literature": literature,
        "clinical_trials": {
            "api_total_count": clinical.get(
                "total_count"
            ),
            "examined_count": len(studies),
            "relevant_count": len(relevant_studies),
            "excluded_count": len(excluded_studies),
            "missing_conditions_count": len(
                missing_conditions
            ),
            "studies_with_registered_results": (
                studies_with_results
            ),
            "phase_counts": phase_counts,
            "studies": relevant_studies,
            "excluded_nct_ids": [
                study.get("nct_id")
                for study in excluded_studies
            ],
        },
        "scientific_limitations": [
            (
                "ChEMBL bioactivity values are "
                "experimental measurements and "
                "cannot independently establish "
                "clinical efficacy or safety."
            ),
            (
                "A registered clinical trial "
                "does not demonstrate that a "
                "treatment is effective."
            ),
            (
                "The has_results field indicates "
                "whether results are registered "
                "on ClinicalTrials.gov, not whether "
                "positive results were obtained."
            ),
            (
                "Clinical trial relevance filtering "
                "is based on condition names and "
                "is not a validated ontology matcher."
            ),
            (
                "Trial counts and phase summaries "
                "are limited to the fetched records. "
                "They are not necessarily exhaustive."
            ),
            (
                "PubMed search results are bibliographic "
                "matches, not independently validated "
                "evidence of therapeutic efficacy."
            ),
        ],
    }


if __name__ == "__main__":
    report = build_integrated_research_report(
        molecule_name="Orelabrutinib",
        disease="Multiple Sclerosis",
        max_activities=5,
        max_trials=10,
    )

    print(
        "\nNEUROSCOPE.AI - INTEGRATED RESEARCH REPORT\n"
    )

    print(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
    )
