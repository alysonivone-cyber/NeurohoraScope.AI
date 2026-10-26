
from pubmed_client import search_pubmed
from scientific_analyzer import detect_mechanisms
from database import (
    initialize_database,
    save_publications,
    count_publications,
)


def research_disease(disease, max_results=10):
    """Recherche et analyse la littérature sur une maladie."""

    disease = disease.strip()

    if not disease:
        print("❌ Le nom de la maladie est obligatoire.")
        return []

    query = f'("{disease}"[Title/Abstract]) AND neuroprotection'

    print("\n" + "=" * 65)
    print("🧠 NEUROSCOPE.AI — RESEARCH ENGINE")
    print(f"🔎 Maladie étudiée : {disease}")
    print("=" * 65)

    publications = search_pubmed(
        query,
        max_results=max_results
    )

    initialize_database()
    save_publications(publications)

    print(f"\n📚 Bibliothèque : {count_publications()} publications")
    print(f"🔬 Résultats de cette recherche : {len(publications)}")

    analyzed_results = []

    for publication in publications:

        text = (
            publication["title"]
            + " "
            + publication.get("abstract", "")
        )

        mechanisms = detect_mechanisms(text)
        publication_types = publication.get(
            "publication_types", []
        )

        result = {
            "pmid": publication["pmid"],
            "title": publication["title"],
            "url": publication["url"],
            "mechanisms": mechanisms,
            "publication_types": publication_types,
        }

        analyzed_results.append(result)

        print("\n" + "-" * 65)
        print(f"📄 {result['title']}")
        print(f"🔗 {result['url']}")

        print(
            "📖 Types PubMed : "
            + (
                ", ".join(publication_types)
                if publication_types
                else "Non renseignés"
            )
        )

        print(
            "🧬 Thèmes détectés : "
            + (
                ", ".join(mechanisms)
                if mechanisms
                else "Aucun thème reconnu"
            )
        )

    return analyzed_results


if __name__ == "__main__":

    disease = input(
        "\n🧠 Quelle maladie neurologique souhaites-tu explorer ? "
    )

    research_disease(disease, max_results=10)
