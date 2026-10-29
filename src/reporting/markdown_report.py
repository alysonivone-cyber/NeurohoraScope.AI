
from pathlib import Path
import json


def generate_markdown_report(json_path):
    json_path = Path(json_path)

    with json_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    molecule = report.get("molecule", "Unknown")
    disease = report.get("disease") or "Not specified"

    pharmacology = report.get("pharmacology", {})
    literature = report.get("literature", {})
    clinical = report.get("clinical_trials", {})
    
    molecule_data = pharmacology.get("molecule") or {}

    bioactivities = (
        pharmacology.get("bioactivities") or {}
    ).get("activities", [])

    trials = clinical.get("studies", [])
    publications = literature.get("publications", [])

    chembl_id = molecule_data.get("chembl_id") or "N/A"

    lines = [
        "# NeuroScope.AI — Scientific Research Report",
        "",
        f"**Molecule:** {molecule}",
        f"**Disease:** {disease}",
        "",
        "## Research overview",
        "",
        "| Indicator | Retrieved data |",
        "|---|---|",
        f"| ChEMBL compound | {chembl_id} |",
        f"| Bioactivity records | {len(bioactivities)} |",
        f"| Clinical trials | {len(trials)} |",
        f"| PubMed publications | {len(publications)} |",
        "",
        "These counts describe retrieved records, "
        "not evidence of clinical efficacy.",
        "",
        "> Research data aggregation, not a clinical recommendation.",
        "",
        "## 1. Molecular pharmacology",
        "",
    ]

    molecule_data = pharmacology.get("molecule") or {}

    lines.extend([
        f"**ChEMBL ID:** {molecule_data.get('chembl_id', 'N/A')}",
        "",
        f"**Molecular weight:** {molecule_data.get('molecular_weight', 'N/A')}",
        "",
        "### Mechanisms of action",
        "",
    ])

    mechanisms = (
        pharmacology.get("mechanisms") or {}
    ).get("mechanisms", [])

    if mechanisms:
        for mechanism in mechanisms:
            lines.append(
                f"- {mechanism.get('mechanism_of_action', 'Unknown')}"
            )
    else:
        lines.append("- No mechanism annotations returned.")

    lines.extend([
        "",
        "### Experimental bioactivities",
        "",
    ])

    activities = (
        pharmacology.get("bioactivities") or {}
    ).get("activities", [])

    for activity in activities:
        lines.append(
            f"- {activity.get('target_name', 'Unknown')}: "
            f"{activity.get('standard_type', 'N/A')} "
            f"{activity.get('standard_relation', '')} "
            f"{activity.get('standard_value', 'N/A')} "
            f"{activity.get('standard_units') or ''} "
            f"(Assay: {activity.get('assay_chembl_id', 'N/A')})"
        )

    if not activities:
        lines.append("- No bioactivity records returned.")

    lines.extend([
        "",
        "## 2. Clinical trials",
        "",
        f"**Relevant studies retrieved:** {clinical.get('relevant_count', 0)}",
        "",
    ])

    for study in clinical.get("studies", []):
        lines.extend([
            f"### {study.get('nct_id', 'Unknown')}",
            "",
            f"**Title:** {study.get('title', 'N/A')}",
            "",
            f"**Status:** {study.get('status', 'N/A')}",
            "",
            f"**Phases:** {', '.join(study.get('phases', [])) or 'N/A'}",
            "",
            f"**Source:** {study.get('url', 'N/A')}",
            "",
        ])

    lines.extend([
        "## 3. Scientific literature",
        "",
        f"**Publications retrieved:** {literature.get('returned_count', 0)}",
        "",
    ])

    for publication in literature.get("publications", []):
        lines.extend([
            f"### {publication.get('title', 'Untitled')}",
            "",
            f"**PMID:** {publication.get('pmid', 'N/A')}",
            "",
            f"**Publication types:** {', '.join(publication.get('publication_types', [])) or 'N/A'}",
            "",
            f"**Source:** {publication.get('url', 'N/A')}",
            "",
            f"**Abstract:** {publication.get('abstract') or 'Unavailable'}",
            "",
        ])

    lines.extend([
        "## 4. Scientific limitations",
        "",
    ])

    for limitation in report.get(
        "scientific_limitations", []
    ):
        lines.append(f"- {limitation}")

    output_path = json_path.with_suffix(".md")

    output_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return output_path


if __name__ == "__main__":
    reports_directory = Path("reports")

    json_files = sorted(
        reports_directory.glob("research_report_*.json"),
        key=lambda path: path.stat().st_mtime,
    )

    if not json_files:
        raise FileNotFoundError(
            "No exported JSON report found."
        )

    output = generate_markdown_report(
        json_files[-1]
    )

    print("\nMARKDOWN REPORT GENERATED")
    print(f"File: {output.resolve()}")
