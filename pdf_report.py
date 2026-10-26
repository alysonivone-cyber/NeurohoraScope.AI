
import json
from scientific_analysis import generate_scientific_analysis
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


def safe(value):
    return escape(str(value)) if value is not None else "N/A"


def generate_pdf_report(json_path):
    json_path = Path(json_path)

    with json_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    output_path = json_path.with_suffix(".pdf")

    scientific_analysis = generate_scientific_analysis(report)

    evidence = scientific_analysis["evidence_assessment"]
    gap_analysis = scientific_analysis["research_gap_analysis"]

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#17365D"),
        alignment=TA_CENTER,
        spaceAfter=20,
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#17365D"),
        spaceBefore=16,
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        spaceAfter=5,
        wordWrap="CJK",
    ))

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []

    def paragraph(text):
        story.append(
            Paragraph(text, styles["ReportBody"])
        )

    def section(text):
        story.append(
            Paragraph(text, styles["SectionTitle"])
        )

    molecule = report.get("molecule", "Unknown")
    disease = report.get("disease") or "Not specified"

    pharmacology = report.get("pharmacology") or {}
    literature = report.get("literature") or {}
    clinical = report.get("clinical_trials") or {}

    molecule_data = pharmacology.get("molecule") or {}
    activities = (
        pharmacology.get("bioactivities") or {}
    ).get("activities", [])

    trials = clinical.get("studies", [])
    publications = literature.get("publications", [])

    # COVER PAGE
    story.append(Spacer(1, 5 * cm))

    story.append(Paragraph(
        "NeuroScope.AI",
        styles["ReportTitle"],
    ))

    story.append(Paragraph(
        "Scientific Research Report",
        styles["Title"],
    ))

    story.append(Spacer(1, 2 * cm))

    paragraph(f"<b>Molecule:</b> {safe(molecule)}")
    paragraph(f"<b>Disease:</b> {safe(disease)}")

    paragraph(
        "Research data aggregation. "
        "Not a clinical recommendation."
    )

    story.append(PageBreak())

    # OVERVIEW
    section("1. Research overview")

    overview = [
        ["Indicator", "Retrieved data"],
        ["ChEMBL compound",
         safe(molecule_data.get("chembl_id"))],
        ["Bioactivity records", str(len(activities))],
        ["Clinical trials", str(len(trials))],
        ["PubMed publications", str(len(publications))],
    ]

    table = Table(
        overview,
        colWidths=[8 * cm, 8 * cm],
        repeatRows=1,
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#EDF3F8")]),
        ("GRID", (0, 0), (-1, -1),
         0.3, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 9),
    ]))

    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    paragraph(
        "Counts reflect retrieved records, "
        "not proof of treatment efficacy."
    )

    # PHARMACOLOGY
    section("2. Molecular pharmacology")

    paragraph(
        "<b>ChEMBL ID:</b> "
        + safe(molecule_data.get("chembl_id"))
    )

    paragraph(
        "<b>Molecular weight:</b> "
        + safe(molecule_data.get("molecular_weight"))
    )

    mechanisms = (
        pharmacology.get("mechanisms") or {}
    ).get("mechanisms", [])

    for mechanism in mechanisms:
        paragraph(
            "<b>Mechanism:</b> "
            + safe(mechanism.get("mechanism_of_action"))
        )

    section("3. Experimental bioactivities")

    for activity in activities:
        value = activity.get("standard_value")
        units = activity.get("standard_units") or ""
        relation = activity.get("standard_relation") or ""

        measurement = (
            f"{safe(activity.get('standard_type'))} "
            f"{safe(relation)} "
            f"{safe(value) if value is not None else 'Not reported'} "
            f"{safe(units)}"
        )

        paragraph(
            f"<b>{safe(activity.get('target_name'))}</b>: "
            + measurement
            + " | Assay: "
            + safe(activity.get("assay_chembl_id"))
        )

    # CLINICAL TRIALS
    section("4. Clinical trials")

    for trial in trials:
        block = [
            Paragraph(
                "<b>" + safe(trial.get("nct_id")) + "</b>",
                styles["ReportBody"],
            ),
            Paragraph(
                safe(trial.get("title")),
                styles["ReportBody"],
            ),
            Paragraph(
                "<b>Status:</b> "
                + safe(trial.get("status"))
                + " | <b>Phases:</b> "
                + safe(", ".join(trial.get("phases", []))),
                styles["ReportBody"],
            ),
            Paragraph(
                "<b>Source:</b> "
                + safe(trial.get("url")),
                styles["ReportBody"],
            ),
            Spacer(1, 0.3 * cm),
        ]

        story.append(KeepTogether(block))

    # LITERATURE
    section("5. Scientific literature")

    for publication in publications:
        paragraph(
            "<b>" + safe(publication.get("title")) + "</b>"
        )

        paragraph(
            "<b>PMID:</b> "
            + safe(publication.get("pmid"))
        )

        paragraph(
            "<b>Publication types:</b> "
            + safe(", ".join(
                publication.get("publication_types", [])
            ))
        )

        paragraph(
            "<b>Source:</b> "
            + safe(publication.get("url"))
        )

        paragraph(
            "<b>Abstract:</b> "
            + safe(publication.get("abstract") or "Unavailable")
        )

    # LIMITATIONS
        story.append(Spacer(1, 0.2 * cm))
    section("6. Scientific limitations")

    for limitation in report.get(
        "scientific_limitations", []
    ):
        paragraph("- " + safe(limitation))

    
    # SCIENTIFIC EVIDENCE ASSESSMENT
    section("7. Scientific evidence assessment")

    experimental = evidence["experimental_evidence"]
    clinical_evidence = evidence["clinical_evidence"]
    literature_evidence = evidence["literature_evidence"]

    paragraph(
        "<b>Experimental evidence:</b> "
        + safe(experimental["classification"])
    )

    paragraph(
        "<b>Clinical evidence:</b> "
        + safe(clinical_evidence["classification"])
    )

    paragraph(
        "<b>Clinical efficacy conclusion:</b> "
        + safe(clinical_evidence["efficacy_conclusion"])
    )

    paragraph(
        "<b>Literature evidence:</b> "
        + safe(literature_evidence["classification"])
    )

    paragraph(
        "<b>Overall assessment:</b> "
        + safe(evidence["overall_assessment"])
    )

    # RESEARCH GAP ANALYSIS
    section("8. Research gap analysis")

    paragraph(
        "<b>Gap categories identified:</b> "
        + str(gap_analysis["gaps_identified"])
    )

    for gap in gap_analysis["research_gaps"]:
        paragraph(
            "<b>" + safe(gap["category"]) + "</b>"
            + " — " + safe(gap["description"])
        )

    paragraph(
        "<b>Interpretation:</b> "
        + safe(gap_analysis["interpretation"])
    )

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            A4[0] - 2 * cm,
            1.2 * cm,
            f"NeuroScope.AI | Page {document.page}",
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return output_path


if __name__ == "__main__":
    reports_directory = Path("reports")
    
    json_files = sorted(
        [
            path
            for path in reports_directory.glob(
                "research_report_*.json"
            )
            if not path.stem.endswith("_analysis")
        ],
        key=lambda path: path.stat().st_mtime,
    )

    if not json_files:
        raise FileNotFoundError(
            "No JSON research report found."
        )

    output = generate_pdf_report(json_files[-1])

    print("\nPDF REPORT GENERATED")
    print(f"File: {output.resolve()}")
