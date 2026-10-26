
import json
import re

from pubmed_client import search_pubmed


def safe_pubmed_term(value):
    """
    Prepare a user-provided term for a
    PubMed Title/Abstract phrase search.
    """

    value = value.strip()

    if not value:
        raise ValueError("Search term cannot be empty.")

    # Avoid inserting PubMed query syntax
    # through molecule or disease names.
    value = re.sub(r'["\[\]()]', " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    if not value:
        raise ValueError("Invalid search term.")

    return f'"{value}"[Title/Abstract]'


def research_molecule_literature(
    molecule_name,
    disease=None,
    max_results=10,
):
    """
    Search PubMed for publications mentioning
    a molecule and optionally a disease.

    Search results are bibliographic matches,
    not validated evidence of efficacy.
    """

    molecule_name = molecule_name.strip()

    if not molecule_name:
        raise ValueError("Molecule name is required.")

    max_results = max(1, min(int(max_results), 20))

    molecule_term = safe_pubmed_term(molecule_name)

    disease = disease.strip() if disease else None

    if disease:
        disease_term = safe_pubmed_term(disease)

        query = (
            f"{molecule_term} AND {disease_term}"
        )
    else:
        query = molecule_term

    publications = search_pubmed(
        query=query,
        max_results=max_results,
    )

    return {
        "molecule": molecule_name,
        "disease": disease,
        "pubmed_query": query,
        "returned_count": len(publications),
        "publications": publications,
        "scientific_note": (
            "Publications are retrieved using "
            "Title/Abstract search terms. "
            "A bibliographic match does not "
            "establish treatment efficacy, "
            "safety, or causal mechanisms. "
            "The search is not exhaustive."
        ),
    }


if __name__ == "__main__":
    report = research_molecule_literature(
        molecule_name="Orelabrutinib",
        disease="Multiple Sclerosis",
        max_results=10,
    )

    print(
        "\nNEUROSCOPE.AI - MOLECULE LITERATURE\n"
    )

    print(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
    )
