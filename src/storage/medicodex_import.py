
import json
import sqlite3
from pathlib import Path

from src.storage.database import DATABASE_NAME, initialize_database

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCAL_DATA_FILE = PROJECT_ROOT / "data" / "medicodex.json"
DEPLOY_DATA_FILE = PROJECT_ROOT / "deploy_data" / "medicodex.json"

DATA_FILE = (
    LOCAL_DATA_FILE
    if LOCAL_DATA_FILE.is_file()
    else DEPLOY_DATA_FILE
)

def import_medicodex():
    """Importe les maladies et molécules depuis un export JSON."""

    if not DATA_FILE.exists():
        print("❌ Fichier Medicodex introuvable.")
        return

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = data.get("records", [])
    imported_diseases = 0
    imported_associations = 0

    initialize_database()

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        for record in records:
            fields = record.get("fields", {})

            name = fields.get("Disease Name EN", "").strip()
            definition = fields.get("Definition EN", "")
            umls_cui = fields.get("UMLS CUI", "")

            if not name:
                continue

            seo_data = {}
            seo_raw = fields.get("SEO:JSON-LD EN", "")

            if seo_raw:
                try:
                    seo_data = json.loads(seo_raw)
                except json.JSONDecodeError:
                    print(f"⚠️ JSON-LD invalide : {name}")

            source_url = ""

            for item in seo_data.get("@graph", []):
                if item.get("@type") == "MedicalWebPage":
                    source_url = item.get("url", "")
                    break

            connection.execute("""
                INSERT INTO diseases
                    (name, definition, umls_cui, source, source_url)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name, source) DO UPDATE SET
                    definition = excluded.definition,
                    umls_cui = excluded.umls_cui,
                    source_url = excluded.source_url
            """, (
                name,
                definition,
                umls_cui,
                "Medicodex",
                source_url,
            ))

            disease_id = connection.execute("""
                SELECT id FROM diseases
                WHERE name = ? AND source = ?
            """, (name, "Medicodex")).fetchone()[0]

            imported_diseases += 1

            for item in seo_data.get("@graph", []):
                if item.get("@type") != "MedicalWebPage":
                    continue

                for mention in item.get("mentions", []):
                    if mention.get("@type") != "ItemList":
                        continue

                    for entry in mention.get("itemListElement", []):
                        molecule_name = (
                            entry.get("item", {}).get("name", "").strip()
                        )

                        if not molecule_name:
                            continue

                        connection.execute("""
                            INSERT OR IGNORE INTO molecules (name)
                            VALUES (?)
                        """, (molecule_name,))

                        molecule_id = connection.execute("""
                            SELECT id FROM molecules WHERE name = ?
                        """, (molecule_name,)).fetchone()[0]

                        cursor = connection.execute("""
                            INSERT OR IGNORE INTO disease_molecules
                                (disease_id, molecule_id, source)
                            VALUES (?, ?, ?)
                        """, (
                            disease_id,
                            molecule_id,
                            "Medicodex",
                        ))

                        imported_associations += cursor.rowcount

    print("\n🧬 IMPORT MEDICODEX TERMINÉ")
    print(f"✅ Maladies traitées : {imported_diseases}")
    print(f"✅ Nouvelles associations : {imported_associations}")


if __name__ == "__main__":
    import_medicodex()
