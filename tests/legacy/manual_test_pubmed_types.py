
from src.clients.pubmed_client import search_pubmed


def main():
    print("\n🧠 NEUROSCOPE.AI — PUBMED METADATA TEST")

    publications = search_pubmed(
        'Alzheimer disease AND neuroprotection',
        max_results=5
    )

    for publication in publications:
        print("\n" + "=" * 60)
        print(f"📄 {publication['title']}")
        print(f"🔗 {publication['url']}")

        types = publication.get("publication_types", [])

        if types:
            print("🔬 Types PubMed :", ", ".join(types))
        else:
            print("⚪ Aucun type PubMed renseigné.")


if __name__ == "__main__":
    main()
