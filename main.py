
import requests
import xml.etree.ElementTree as ET
from src.storage.database import initialize_database, save_publications, count_publications

# NeuroScope.AI - Scientific Research Engine
# Phase 2: Collecte des publications et abstracts

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def search_pubmed(query, max_results=5):
    print(f"\n🔬 Recherche scientifique : {query}\n")

    response = requests.get(
        BASE_URL + "esearch.fcgi",
        params={
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
            "sort": "pub_date",
            "tool": "NeuroScopeAI",
        },
        timeout=20,
    )
    response.raise_for_status()

    article_ids = response.json()["esearchresult"]["idlist"]

    if not article_ids:
        print("Aucune publication trouvée.")
        return []

    response = requests.get(
        BASE_URL + "efetch.fcgi",
        params={
            "db": "pubmed",
            "id": ",".join(article_ids),
            "retmode": "xml",
            "tool": "NeuroScopeAI",
        },
        timeout=30,
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    publications = []

    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//MedlineCitation/PMID", "")

        title_element = article.find(".//ArticleTitle")
        title = (
            "".join(title_element.itertext()).strip()
            if title_element is not None
            else ""
        )

        abstract_parts = []

        for section in article.findall(".//Abstract/AbstractText"):
            section_text = "".join(section.itertext()).strip()
            label = section.get("Label")

            if section_text:
                if label:
                    section_text = f"{label}: {section_text}"
                abstract_parts.append(section_text)

        abstract = "\n".join(abstract_parts)

        publication = {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        }

        publications.append(publication)

        print("=" * 70)
        print(f"📖 {title}")
        print(f"🔗 {publication['url']}")
        print("\n🧠 ABSTRACT :\n")
        print(abstract if abstract else "Résumé non disponible.")
        print()

    return publications

if __name__ == "__main__":
    try:
        initialize_database()

        publications = search_pubmed(
            "Parkinson disease AND neuroprotection",
            max_results=3,
        )

        save_publications(publications)

        print(
            f"\n🧠 Total dans NeuroScope.AI : "
            f"{count_publications()} publications"
        )

    except requests.RequestException as error:
        print(f"Erreur de connexion à PubMed : {error}")

    except ET.ParseError as error:
        print(f"Erreur de lecture XML : {error}")

    except (KeyError, ValueError) as error:
        print(f"Erreur de traitement : {error}")
