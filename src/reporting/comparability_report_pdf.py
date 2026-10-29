
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    LongTable,
    TableStyle,
    KeepTogether,
)


def generate_comparability_pdf(json_path):
    json_path = Path(json_path)

    data = json.loads(
        json_path.read_text(encoding="utf-8")
    )

    output_path = json_path.with_suffix(".pdf")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="NeuroTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#163A63"),
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name="NeuroSection",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#163A63"),
        spaceBefore=14,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="NeuroCell",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    ))

    story = []

    def cell(value):
        return Paragraph(
            escape(str(
                value if value is not None else "—"
            )),
            styles["NeuroCell"],
        )

    story.append(Paragraph(
        "NeuroScope.AI",
        styles["NeuroTitle"],
    ))

    story.append(Paragraph(
        "Scientific Comparability Report",
        styles["Heading1"],
    ))

    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "<b>Molecules:</b> "
        + escape(str(data.get("molecule_a")))
        + " and "
        + escape(str(data.get("molecule_b"))),
        styles["Normal"],
    ))

    story.append(Paragraph(
        "<b>Generated (UTC):</b> "
        + escape(str(
            data.get("generated_at_utc", "Unknown")
        )),
        styles["Normal"],
    ))

    story.append(Paragraph(
        "<b>Source:</b> "
        + escape(str(
            data.get("source_file", "Unknown")
        )),
        styles["Normal"],
    ))

    story.append(Paragraph(
        "1. Comparison overview",
        styles["NeuroSection"],
    ))

    overview = [
        ("Total cross-molecule comparisons",
         data.get("total_comparisons", 0)),
        ("Same-target pairs",
         data.get("same_target_pairs", 0)),
        ("Same-target, same-format pairs",
         data.get(
             "same_target_same_format_pairs", 0
         )),
    ]

    for label, value in overview:
        story.append(Paragraph(
            f"<b>{escape(label)}:</b> "
            f"{escape(str(value))}",
            styles["Normal"],
        ))

    story.append(Paragraph(
        "2. Status distribution",
        styles["NeuroSection"],
    ))

    status_rows = [
        [cell("Classification"), cell("Count")]
    ]

    for status, count in (
        data.get("status_distribution") or {}
    ).items():
        status_rows.append([
            cell(status),
            cell(count),
        ])

    status_table = LongTable(
        status_rows,
        colWidths=[11 * cm, 3 * cm],
        repeatRows=1,
    )

    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#E6EEF6")),
        ("GRID", (0, 0), (-1, -1),
         0.3, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(status_table)

    story.append(Paragraph(
        "3. Pairs requiring methodological review",
        styles["NeuroSection"],
    ))

    candidates = data.get("review_candidates") or []

    if not candidates:
        story.append(Paragraph(
            "No same-target, same-format pairs "
            "were identified.",
            styles["Normal"],
        ))

    for index, item in enumerate(candidates, 1):
        block = [
            Paragraph(
                f"Candidate {index}: "
                + escape(str(item.get("target_a"))),
                styles["Heading3"],
            ),
            Paragraph(
                "<b>"
                + escape(str(item.get("molecule_a")))
                + ":</b> "
                + escape(str(item.get("ic50_a_nM")))
                + " nM — "
                + escape(str(item.get("assay_a"))),
                styles["Normal"],
            ),
            Paragraph(
                "<b>"
                + escape(str(item.get("molecule_b")))
                + ":</b> "
                + escape(str(item.get("ic50_b_nM")))
                + " nM — "
                + escape(str(item.get("assay_b"))),
                styles["Normal"],
            ),
            Paragraph(
                "<b>Format:</b> "
                + escape(str(item.get("format_a")))
                + " / "
                + escape(str(item.get("format_b"))),
                styles["Normal"],
            ),
            Spacer(1, 0.3 * cm),
        ]

        story.append(KeepTogether(block))

    story.append(Paragraph(
        "4. Scientific recommendations",
        styles["NeuroSection"],
    ))

    for recommendation in (
        data.get("scientific_recommendations") or []
    ):
        story.append(Paragraph(
            "• " + escape(str(recommendation)),
            styles["Normal"],
        ))

        story.append(Spacer(1, 0.15 * cm))

    story.append(Paragraph(
        "5. Interpretation and limitations",
        styles["NeuroSection"],
    ))

    story.append(Paragraph(
        "This report summarizes a limited set of "
        "ChEMBL bioactivity records. Matching target "
        "and assay format does not establish "
        "experimental equivalence. Assay conditions, "
        "biological models and readouts must be "
        "reviewed before quantitative comparisons. "
        "No clinical efficacy or molecular superiority "
        "is inferred.",
        styles["Normal"],
    ))

    def page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            A4[0] - 1.7 * cm,
            1 * cm,
            f"Page {document.page}",
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=page_number,
        onLaterPages=page_number,
    )

    return output_path


if __name__ == "__main__":
    reports_dir = Path("reports")

    files = sorted(
        reports_dir.glob("comparability_summary_*.json"),
        key=lambda p: p.stat().st_mtime,
    )

    if not files:
        raise FileNotFoundError(
            "No comparability summary JSON found."
        )

    latest_file = files[-1]

    print("Reading:", latest_file)

    pdf_path = generate_comparability_pdf(
        latest_file
    )

    print("\nCOMPARABILITY PDF GENERATED")
    print("File:", pdf_path.resolve())
