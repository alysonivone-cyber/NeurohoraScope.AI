
from chembl_client import (
    search_chembl_molecule,
    get_chembl_mechanisms,
    get_chembl_target,
    get_chembl_bioactivities,
)


def build_pharmacology_report(
    molecule_name,
    max_activities=10,
):
    """
    Build a structured pharmacology research report
    using ChEMBL molecular, mechanism, target
    and experimental bioactivity data.
    """

    search = search_chembl_molecule(
        name=molecule_name,
        max_results=5,
    )

    matches = search.get("molecules", [])

    if not matches:
        return {
            "query": molecule_name,
            "status": "not_found",
            "message": "No ChEMBL molecule match found.",
        }

    # Use only a verified exact preferred-name match.
    exact_matches = [
        item for item in matches
        if (item.get("preferred_name") or "").casefold()
        == molecule_name.strip().casefold()
    ]

    if len(exact_matches) != 1:
        return {
            "query": molecule_name,
            "status": "identity_verification_required",
            "candidates": matches,
            "message": (
                "Molecule identity could not be established "
                "from a unique exact preferred-name match."
            ),
        }

    molecule = exact_matches[0]
    chembl_id = molecule["chembl_id"]

    mechanisms = get_chembl_mechanisms(chembl_id)
    bioactivities = get_chembl_bioactivities(
        molecule_chembl_id=chembl_id,
        max_results=max_activities,
    )

    targets = []
    seen_targets = set()

    for mechanism in mechanisms.get("mechanisms", []):
        target_id = mechanism.get("target_chembl_id")

        if not target_id or target_id in seen_targets:
            continue

        seen_targets.add(target_id)
        targets.append(get_chembl_target(target_id))

    return {
        "query": molecule_name,
        "status": "success",
        "molecule": molecule,
        "mechanisms": mechanisms,
        "targets": targets,
        "bioactivities": bioactivities,
        "scientific_note": (
            "This is a research data aggregation, not "
            "a clinical recommendation. Bioactivity "
            "measurements depend on experimental "
            "conditions and must be evaluated separately."
        ),
    }


if __name__ == "__main__":
    import json

    report = build_pharmacology_report(
        molecule_name="Orelabrutinib",
        max_activities=5,
    )

    print("\nNEUROSCOPE.AI — PHARMACOLOGY REPORT\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
