
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


def build_data_provenance(matrix, source_path):
    records = []

    for measurement in matrix.get("matrix", []):
        assay_id = measurement.get(
            "assay_chembl_id"
        )

        records.append({
            "molecule": measurement.get("molecule"),
            "target": measurement.get("target"),
            "ic50_nM": measurement.get("ic50_nM"),
            "assay_chembl_id": assay_id,
            "source_database": "ChEMBL",
            "assay_url": (
                f"https://www.ebi.ac.uk/chembl/"
                f"assay_report_card/{assay_id}/"
                if assay_id else None
            ),
            "assay_format": measurement.get(
                "assay_format"
            ),
            "assay_description": measurement.get(
                "assay_description"
            ),
        })

    source_bytes = Path(source_path).read_bytes()

    return {
        "analysis_type": "scientific_data_provenance",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_file": Path(source_path).name,
        "source_sha256": hashlib.sha256(
            source_bytes
        ).hexdigest(),
        "record_count": len(records),
        "records": records,
        "limitations": (
            "Provenance is based on retrieved ChEMBL "
            "assay identifiers and the local source "
            "JSON. This does not establish original "
            "publication provenance or experimental "
            "reproducibility."
        ),
    }


if __name__ == "__main__":
    reports_dir = Path("reports")

    files = sorted(
        reports_dir.glob("experimental_matrix_*.json"),
        key=lambda p: p.stat().st_mtime,
    )

    if not files:
        raise FileNotFoundError(
            "No experimental matrix JSON found."
        )

    source_path = files[-1]

    matrix = json.loads(
        source_path.read_text(encoding="utf-8")
    )

    provenance = build_data_provenance(
        matrix,
        source_path,
    )

    output_path = reports_dir / (
        "scientific_data_provenance.json"
    )

    output_path.write_text(
        json.dumps(
            provenance,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nSCIENTIFIC DATA PROVENANCE GENERATED")
    print("Records:", provenance["record_count"])
    print("SHA256:", provenance["source_sha256"])
    print("File:", output_path.resolve())
