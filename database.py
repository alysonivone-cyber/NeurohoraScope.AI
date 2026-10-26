
import sqlite3

DATABASE_NAME = "neuroscope.db"


def initialize_database():
    """Initialise les tables scientifiques de NeuroScope.AI."""

    with sqlite3.connect(DATABASE_NAME) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS publications (
                pmid TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                abstract TEXT,
                url TEXT NOT NULL,
                collected_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                definition TEXT,
                umls_cui TEXT,
                source TEXT NOT NULL,
                source_url TEXT,
                UNIQUE(name, source)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS molecules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS disease_molecules (
                disease_id INTEGER NOT NULL,
                molecule_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                PRIMARY KEY (disease_id, molecule_id, source),
                FOREIGN KEY (disease_id) REFERENCES diseases(id),
                FOREIGN KEY (molecule_id) REFERENCES molecules(id)
            )
        """)

    print("🧠 Base de données NeuroScope.AI initialisée.")


def save_publications(publications):
    """Enregistre les publications PubMed."""

    with sqlite3.connect(DATABASE_NAME) as connection:

        for publication in publications:
            connection.execute("""
                INSERT INTO publications
                    (pmid, title, abstract, url)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(pmid) DO UPDATE SET
                    title = excluded.title,
                    abstract = excluded.abstract,
                    url = excluded.url
            """, (
                publication["pmid"],
                publication["title"],
                publication["abstract"],
                publication["url"]
            ))

    print(f"✅ {len(publications)} publications enregistrées.")


def count_publications():
    """Compte les publications enregistrées."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        result = connection.execute(
            "SELECT COUNT(*) FROM publications"
        ).fetchone()

    return result[0]
