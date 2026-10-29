
import re
import sqlite3

from src.storage.database import DATABASE_NAME


EVIDENCE_PATTERNS = {
    "Meta-analysis": [
        r"\bmeta-analysis\b",
        r"\bmeta analysis\b",
    ],
    "Systematic review": [
        r"\bsystematic review\b",
    ],
    "Clinical trial": [
        r"\brandomized controlled trial\b",
        r"\brandomised controlled trial\b",
        r"\bphase [iIvVxX0-9]+\b",
        r"\bclinical trial\b",
    ],
    "Animal study": [
        r"\bmouse models?\b",
        r"\bmice\b",
        r"\brats?\b",
        r"\bpreclinical animal\b",
    ],
    "Cellular study": [
        r"\bin vitro\b",
        r"\bcell cultures?\b",
        r"\bcell lines?\b",
    ],
    "Review": [
        r"\breview article\b",
        r"\bnarrative review\b",
        r"\bthis review\b",
        r"\breview of\b",
    ],
}


def detect_evidence_indicators(text):
    """Détecte des indices textuels du type d'étude."""

    detected = []

    for category, patterns in EVIDENCE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(category)
                break

    return detected


def analyze_evidence():
    """Explore les indices méthodologiques dans SQLite."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        publications = connection.execute("""
            SELECT pmid, title, abstract
            FROM publications
            ORDER BY collected_at DESC
        """).fetchall()

    print("\n🧠 NEUROSCOPE.AI — EVIDENCE ANALYZER")
    print(f"📚 Publications examinées : {len(publications)}")

    for pmid, title, abstract in publications:
        text = f"{title} {abstract or ''}"

        indicators = detect_evidence_indicators(text)

        print("\n" + "=" * 60)
        print(f"📄 {title}")
        print(f"🔗 https://pubmed.ncbi.nlm.nih.gov/{pmid}/")

        if indicators:
            print("\n🔬 Indices méthodologiques :")

            for indicator in indicators:
                print(f"  • {indicator}")
        else:
            print("\n⚪ Type d'étude non déterminé.")


if __name__ == "__main__":
    analyze_evidence()
