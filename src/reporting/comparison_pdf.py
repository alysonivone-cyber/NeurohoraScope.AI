
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_comparison_pdf():
    reports_directory = Path("reports")

    comparison_files = sorted(
        reports_directory.glob(
            "molecular_comparison_*.json"
        ),
        key=lambda path: path.stat().st_mtime,
    )

    if not comparison_files:
        raise FileNotFoundError(
            "No molecular comparison JSON found."
        )

    source_path = comparison_files[-1]

    with source_path.open(
        "r", encoding="utf-8"
    ) as file:
        comparison = json.load(file)

    molecule_a = comparison["molecule_a"]
    molecule_b = comparison["molecule_b"]

    output_path = source_path.with_suffix(".pdf")

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "NeuroScope.AI",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            "Molecular Comparison Report",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 1 * cm))

    story.append(
        Paragraph(
            f"<b>Molecule A:</b> "
            f"{escape(str(molecule_a['molecule']))}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Molecule B:</b> "
            f"{escape(str(molecule_b['molecule']))}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 1 * cm))

    story.append(
        Paragraph(
            "1. Comparative research overview",
            styles["Heading2"],
        )
    )

    data = [
        [
            "Indicator",
            "Molecule A",
            "Molecule B",
        ],
        [
            "Bioactivity records",
            molecule_a["bioactivity_records"],
            molecule_b["bioactivity_records"],
        ],
        [
            "Clinical trials",
            molecule_a["clinical_trials"],
            molecule_b["clinical_trials"],
        ],
        [
            "PubMed publications",
            molecule_a["publications"],
            molecule_b["publications"],
        ],
    ]

    table = Table(
        data,
        colWidths=[
            6 * cm,
            4.5 * cm,
            4.5 * cm,
        ],
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#DCEAF5"),
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),
        ])
    )

    story.append(table)
    story.append(Spacer(1, 1 * cm))

    story.append(
        Paragraph(
            "2. Scientific interpretation",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            escape(comparison["interpretation"]),
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 0.7 * cm))
    
    # EXPERIMENTAL PHARMACOLOGY
    pharmacology = comparison.get("pharmacology") or {}

    if pharmacology:
        story.append(
            Paragraph(
                "3. Experimental pharmacology",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "Target: "
                + escape(str(pharmacology.get("target", "N/A")))
                + " | Measurement: IC50 (nM)",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.4 * cm))

        activity_rows = [
            ["Molecule", "IC50 (nM)", "ChEMBL assay"]
        ]

        for key in ["molecule_a", "molecule_b"]:
            molecule_name = comparison[key]["molecule"]

            for activity in pharmacology.get(key, []):
                activity_rows.append([
                    molecule_name,
                    str(activity["ic50_nM"]),
                    str(activity["assay_chembl_id"]),
                ])

        activity_table = Table(
            activity_rows,
            colWidths=[4.5 * cm, 3 * cm, 7.5 * cm],
            repeatRows=1,
        )

        activity_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#DCEAF5"),
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ])
        )

        story.append(activity_table)
        story.append(Spacer(1, 0.5 * cm))

    # ASSAY COMPARABILITY
    comparability = comparison.get("comparability") or {}

    if comparability:
        story.append(
            Paragraph(
                "4. Assay comparability assessment",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "<b>Status:</b> "
                + escape(str(
                    comparability.get(
                        "comparability_status",
                        "Not assessed",
                    )
                )),
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.2 * cm))

        story.append(
            Paragraph(
                escape(str(
                    comparability.get("explanation", "")
                )),
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.2 * cm))

        story.append(
            Paragraph(
                escape(str(
                    comparability.get(
                        "scientific_limitation", ""
                    )
                )),
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.5 * cm))

    story.append(
        Paragraph(
            "5. Methodological limitations",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            "This comparison describes retrieved "
            "research records only. Differences in "
            "record counts may reflect search coverage, "
            "database indexing, or publication activity. "
            "No comparative clinical efficacy or safety "
            "conclusion is established.",
            styles["Normal"],
        )
    )

    document.build(story)

    print("\nCOMPARISON PDF GENERATED")
    print(f"File: {output_path.resolve()}")


if __name__ == "__main__":
    generate_comparison_pdf()
