
import json
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
    LongTable,
    TableStyle,
    KeepTogether,
)


def generate_experimental_pdf(json_path):
    json_path = Path(json_path)

    data = json.loads(
        json_path.read_text(encoding="utf-8")
    )

    output_path = json_path.with_suffix(".pdf")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitleCustom",
        parent=styles["Title"],
        fontSize=17,
        leading=21,
        spaceAfter=14,
        textColor=colors.HexColor("#163A63"),
    ))

    styles.add(ParagraphStyle(
        name="SmallCellCustom",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    ))

    styles.add(ParagraphStyle(
        name="SectionCustom",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=13,
        spaceAfter=8,
        textColor=colors.HexColor("#163A63"),
    ))

    cell_style = styles["SmallCellCustom"]
    story = []

    def paragraph(value):
        return Paragraph(
            escape(str(value if value is not None else "—")),
            cell_style,
        )

    story.append(Paragraph(
        "NeuroScope.AI",
        styles["ReportTitleCustom"],
    ))

    story.append(Paragraph(
        "Experimental Pharmacology Matrix",
        styles["Heading1"],
    ))

    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        f"<b>Molecules:</b> "
        f"{escape(str(data.get('molecule_a')))} and "
        f"{escape(str(data.get('molecule_b')))}",
        styles["Normal"],
    ))

    story.append(Paragraph(
        f"<b>Measurements:</b> "
        f"{data.get('total_measurements', 0)}",
        styles["Normal"],
    ))

    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph(
        "1. Experimental measurements",
        styles["SectionCustom"],
    ))

    rows = [[
        paragraph("Molecule"),
        paragraph("Target"),
        paragraph("IC50 (nM)"),
        paragraph("Assay format"),
    ]]

    for item in data.get("matrix", []):
        rows.append([
            paragraph(item.get("molecule")),
            paragraph(item.get("target")),
            paragraph(item.get("ic50_nM")),
            paragraph(item.get("assay_format")),
        ])

    table = LongTable(
        rows,
        colWidths=[
            3.1 * cm,
            5.5 * cm,
            2.2 * cm,
            3.8 * cm,
        ],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#E6EEF6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1),
         0.3, colors.lightgrey),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(
        "2. Experimental protocols",
        styles["SectionCustom"],
    ))

    for item in data.get("matrix", []):
        heading = (
            f"{item.get('molecule')} — "
            f"{item.get('target')}"
        )

        block = [
            Paragraph(
                escape(heading),
                styles["Heading3"],
            ),
            Paragraph(
                "<b>Assay:</b> "
                + escape(str(
                    item.get("assay_chembl_id")
                )),
                styles["Normal"],
            ),
            Paragraph(
                escape(str(
                    item.get("assay_description")
                    or "Description unavailable."
                )),
                styles["Normal"],
            ),
            Spacer(1, 0.25 * cm),
        ]

        story.append(KeepTogether(block))

    story.append(Paragraph(
        "3. Scientific limitations",
        styles["SectionCustom"],
    ))

    story.append(Paragraph(
        escape(data.get(
            "interpretation",
            "No interpretation provided."
        )),
        styles["Normal"],
    ))

    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph(
        "The displayed records are a limited "
        "sample of retrieved ChEMBL bioactivities. "
        "These data do not establish clinical "
        "efficacy, neuroprotection, or comparative "
        "molecular superiority.",
        styles["Normal"],
    ))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            A4[0] - 1.6 * cm,
            1 * cm,
            f"Page {document.page}",
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return output_path


if __name__ == "__main__":
    reports_dir = Path("reports")

    files = sorted(
        reports_dir.glob("experimental_matrix_*.json"),
        key=lambda path: path.stat().st_mtime,
    )

    if not files:
        raise FileNotFoundError(
            "No experimental matrix JSON found."
        )

    latest_json = files[-1]

    print("Reading:", latest_json)

    pdf_path = generate_experimental_pdf(
        latest_json
    )

    print("EXPERIMENTAL PDF GENERATED")
    print("File:", pdf_path.resolve())
