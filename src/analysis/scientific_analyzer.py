
import sqlite3
from src.storage.database import DATABASE_NAME


MECHANISMS = {
    "Neuroinflammation": [
        "neuroinflammation",
        "microglia",
        "microglial",
        "inflammatory",
        "inflammasome",
    ],
    "Oxidative stress": [
        "oxidative stress",
        "reactive oxygen species",
        "free radicals",
        "antioxidant",
    ],
    "Mitochondrial dysfunction": [
        "mitochondrial dysfunction",
        "mitochondria",
        "mitochondrial",
    ],
    "Protein aggregation": [
        "amyloid",
        "tau protein",
        "alpha-synuclein",
        "protein aggregation",
    ],
    "Neuroprotection": [
        "neuroprotection",
        "neuroprotective",
        "neuronal survival",
        "neuronal protection",
    ],
    "Neuroplasticity": [
        "neuroplasticity",
        "synaptic plasticity",
        "neurogenesis",
    ],
}


def detect_mechanisms(text):
    """Repère des termes associés à des mécanismes biologiques."""

    text = text.lower()
    detected = []

    for mechanism, keywords in MECHANISMS.items():
        if any(keyword in text for keyword in keywords):
            detected.append(mechanism)

    return detected


def analyze_publications():
    """Analyse les publications présentes dans SQLite."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        publications = connection.execute("""
            SELECT pmid, title, abstract
            FROM publications
            ORDER BY collected_at DESC
        """).fetchall()

    print("\n🧠 NEUROSCOPE.AI — SCIENTIFIC ANALYZER")
    print(f"📚 Publications à analyser : {len(publications)}")

    for pmid, title, abstract in publications:
        text = f"{title} {abstract or ''}"
        mechanisms = detect_mechanisms(text)

        print("\n" + "=" * 60)
        print(f"📄 {title}")
        print(f"🔗 https://pubmed.ncbi.nlm.nih.gov/{pmid}/")

        if mechanisms:
            print("\n🔬 Thèmes biologiques détectés :")

            for mechanism in mechanisms:
                print(f"  • {mechanism}")
        else:
            print("\nAucun thème reconnu.")


if __name__ == "__main__":
    analyze_publications()
