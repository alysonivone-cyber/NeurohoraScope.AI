
from pathlib import Path
import fitz


def find_latest_pdf(folder, prefix):
    files = list(folder.glob(f"{prefix}*.pdf"))

    if not files:
        raise FileNotFoundError(
            f"No PDF found for: {prefix}"
        )

    return max(
        files,
        key=lambda p: p.stat().st_mtime,
    )


def build_pharmacology_dossier():
    reports_dir = Path("reports")

    experimental_pdf = find_latest_pdf(
        reports_dir,
        "experimental_matrix_",
    )

    comparability_pdf = find_latest_pdf(
        reports_dir,
        "comparability_summary_",
    )

    output_path = reports_dir / (
        "NeuroScope_Experimental_Pharmacology_Dossier.pdf"
    )

    dossier = fitz.open()

    for pdf_path in [
        experimental_pdf,
        comparability_pdf,
    ]:
        with fitz.open(pdf_path) as source:
            print(
                f"Reading {pdf_path.name}: "
                f"{len(source)} pages"
            )
            dossier.insert_pdf(source)

    if len(dossier) != 3:
        raise ValueError(
            f"Expected 3 pages, found {len(dossier)}"
        )

    for index, page in enumerate(dossier, 1):
        width = page.rect.width
        height = page.rect.height

        # Remove the old footer region.
        footer = fitz.Rect(
            0,
            height - 65,
            width,
            height,
        )

        page.add_redact_annot(
            footer,
            fill=(1, 1, 1),
        )

        page.apply_redactions()

        # Add continuous page numbering.
        page.insert_text(
            (width - 85, height - 30),
            f"Page {index}",
            fontsize=9,
            fontname="helv",
            color=(0.2, 0.2, 0.2),
        )

    dossier.set_metadata({
        "title": (
            "NeuroScope.AI - "
            "Experimental Pharmacology Dossier"
        ),
        "author": "NeuroScope.AI",
        "subject": (
            "Experimental pharmacology "
            "and scientific comparability"
        ),
    })

    dossier.save(
        output_path,
        garbage=4,
        deflate=True,
    )

    dossier.close()

    with fitz.open(output_path) as check:
        print("\nPHARMACOLOGY DOSSIER GENERATED")
        print("Total pages:", len(check))

        for index, page in enumerate(check, 1):
            footer_text = page.get_text(
                clip=fitz.Rect(
                    0,
                    page.rect.height - 65,
                    page.rect.width,
                    page.rect.height,
                )
            )
            print(
                f"Page {index} footer:",
                footer_text.strip(),
            )

    print("File:", output_path.resolve())


if __name__ == "__main__":
    build_pharmacology_dossier()
