
import sqlite3

from database import DATABASE_NAME


def search_diseases(keyword):
    """Recherche des maladies dans la base NeuroScope.AI."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.row_factory = sqlite3.Row

        diseases = connection.execute("""
            SELECT id, name, definition, umls_cui, source
            FROM diseases
            WHERE name LIKE ? COLLATE NOCASE
            ORDER BY name
        """, (f"%{keyword}%",)).fetchall()

        return [dict(disease) for disease in diseases]


def get_disease_molecules(disease_id):
    """Récupère les molécules associées à une maladie."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.row_factory = sqlite3.Row

        molecules = connection.execute("""
            SELECT m.name, dm.source
            FROM molecules m
            JOIN disease_molecules dm
                ON m.id = dm.molecule_id
            WHERE dm.disease_id = ?
            ORDER BY m.name
        """, (disease_id,)).fetchall()

        return [dict(molecule) for molecule in molecules]


def search_publications(keyword):
    """Recherche dans les titres et abstracts PubMed."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.row_factory = sqlite3.Row

        publications = connection.execute("""
            SELECT pmid, title, abstract, url
            FROM publications
            WHERE title LIKE ? COLLATE NOCASE
               OR abstract LIKE ? COLLATE NOCASE
            ORDER BY collected_at DESC
        """, (f"%{keyword}%", f"%{keyword}%")).fetchall()

        return [dict(publication) for publication in publications]


if __name__ == "__main__":
    keyword = input("\n🧠 NeuroScope.AI — Recherche : ").strip()

    if not keyword:
        print("Veuillez saisir un mot-clé.")
        raise SystemExit(0)

    diseases = search_diseases(keyword)
    publications = search_publications(keyword)

    print(f"\n🔬 RÉSULTATS POUR : {keyword}")

    print(f"\n🧬 Maladies trouvées : {len(diseases)}")

    for disease in diseases:
        print(f"\n📖 {disease['name']}")
        print(f"Source : {disease['source']}")
        print(f"UMLS : {disease['umls_cui']}")

        molecules = get_disease_molecules(disease["id"])

        print(f"Molécules associées : {len(molecules)}")

        for molecule in molecules[:10]:
            print(f"  • {molecule['name']}")

    print(f"\n📚 Publications trouvées : {len(publications)}")

    for publication in publications:
        print(f"\n📄 {publication['title']}")
        print(f"🔗 {publication['url']}")
