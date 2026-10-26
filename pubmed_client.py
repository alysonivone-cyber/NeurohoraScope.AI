
import requests
import xml.etree.ElementTree as ET
import logging
import requests
import xml.etree.ElementTree as ET

from database import initialize_database, save_publications, count_publications


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

HEADERS = {
    "User-Agent": "NeuroScopeAI/0.1 (educational research prototype)"
}


def search_pubmed(query, max_results=10):
    """Recherche des publications PubMed et récupère leurs résumés."""

    max_results = max(1, min(int(max_results), 50))

    logging.getLogger(__name__).info(
    "PubMed search: %s", query
)

    search_response = requests.get(
        f"{BASE_URL}/esearch.fcgi",
        params={
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
        },
        headers=HEADERS,
        timeout=30,
    )

    search_response.raise_for_status()

    search_data = search_response.json()

    pmids = search_data.get(
        "esearchresult", {}
    ).get("idlist", [])

    if not pmids:
        logging.getLogger(__name__).info(
    "No PubMed publications found."
)
        return []

    fetch_response = requests.get(
        f"{BASE_URL}/efetch.fcgi",
        params={
            "db": "pubmed",
            "id": ",".join(pmids),
            "rettype": "abstract",
            "retmode": "xml",
        },
        headers=HEADERS,
        timeout=30,
    )

    fetch_response.raise_for_status()

    root = ET.fromstring(fetch_response.content)

    publications = []

    for article in root.findall(".//PubmedArticle"):

        pmid = article.findtext(
            ".//MedlineCitation/PMID"
        )

        title_element = article.find(".//ArticleTitle")

        title = (
            "".join(title_element.itertext()).strip()
            if title_element is not None
            else "Titre indisponible"
        )

        abstract_parts = []

        for section in article.findall(
            ".//MedlineCitation/Article/Abstract/AbstractText"
        ):

            section_text = "".join(
                section.itertext()
            ).strip()

            section_label = section.attrib.get("Label")

            if section_text:

                if section_label:
                    abstract_parts.append(
                        f"{section_label}: {section_text}"
                    )
                else:
                    abstract_parts.append(section_text)

        
        abstract = "\n".join(abstract_parts)

        publication_types = [
            element.text.strip()
            for element in article.findall(
                ".//MedlineCitation/Article/PublicationTypeList/PublicationType"
            )
            if element.text and element.text.strip()
        ]

        if pmid:
            publications.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "publication_types": publication_types,
            })

    return publications


if __name__ == "__main__":

    disease = input(
        "\n🧠 Quelle maladie souhaites-tu explorer ? "
    ).strip()

    if not disease:
        print("Veuillez saisir une maladie.")
        raise SystemExit(0)

    query = f'("{disease}"[Title/Abstract]) AND neuroprotection'

    try:

        # 1. Recherche des publications sur PubMed
        results = search_pubmed(
            query,
            max_results=10
        )

        # 2. Initialisation de la base SQLite
        initialize_database()

        # 3. Enregistrement des publications
        save_publications(results)

        print("\n💾 Publications synchronisées avec SQLite.")

        print(
            f"📚 Total dans la bibliothèque : {count_publications()}"
        )

        print(
            f"\n📚 Publications récupérées : {len(results)}"
        )

        # 4. Affichage des résultats
        for index, publication in enumerate(results, start=1):

            print(f"\n{'=' * 60}")

            print(f"📄 ARTICLE {index}")

            print(f"🧬 {publication['title']}")

            print(f"🔗 {publication['url']}")

            if publication["abstract"]:

                print(
                    f"\nRésumé : {publication['abstract'][:500]}..."
                )

            else:
                print("\nRésumé indisponible.")

    except requests.RequestException as error:

        print(
            f"\n❌ Erreur de connexion PubMed : {error}"
        )

    except ET.ParseError as error:

        print(
            f"\n❌ Erreur de lecture XML : {error}"
        )
