# NeurohoraScope.AI

Serveur MCP de neuropharmacologie computationnelle — projet IA de **Alyson ISABELLA VALENZI** (Bachelor Développement Web & Intelligence Artificielle, CREA Genève), rendu le 17 novembre 2026.

Il combine **PubMed**, **ClinicalTrials.gov**, **ChEMBL**, une base locale de maladies, une étape de structuration par **Gemini** (IA externe) et un **serveur MCP** déployé en ligne, utilisable depuis Claude.

**Usage de recherche uniquement.** Une valeur d'activité, une publication ou l'enregistrement d'un essai clinique ne démontrent ni l'efficacité ni la sécurité d'un traitement et ne constituent pas une recommandation thérapeutique.

## 1. Liens

| Élément | Adresse |
|---|---|
| Serveur MCP public (à ajouter dans Claude) | `https://neurohorascope-ai.onrender.com/mcp` |
| Code source (dépôt GitHub) | `https://github.com/alysonivone-cyber/NeurohoraScope.AI` |
| Document de présentation | le PDF `NeurohoraScopeAIRenduFINAL17novAlysonISABELLAVALENZI.pdf` du dépôt (son contenu est repris dans ce README) |

**Pour ajouter le connecteur dans Claude :** ajouter un connecteur MCP personnalisé (HTTP, « Streamable HTTP ») avec l'adresse ci-dessus et **Authentication : None**. La disponibilité des connecteurs personnalisés dépend du type de compte Claude. Après l'ajout, ouvrir une **nouvelle conversation** pour que les outils apparaissent.

**À savoir avant de tester :** le serveur est hébergé sur l'offre gratuite de Render et s'endort après un moment d'inactivité. **Le premier appel peut prendre 50 secondes ou plus** ; les appels suivants sont rapides. L'outil Gemini appelle Gemini en direct depuis le serveur (avec des limites, voir section 8) ; son premier appel peut durer 10 à 30 secondes.

## 2. Présentation du projet

Le projet suit les trois parties demandées :

1. **Base du projet sans IA, à partir de données externes publiques :** PubMed (publications), ClinicalTrials.gov (essais cliniques), ChEMBL (molécules, mécanismes, cibles, activités) et une base locale de 18 maladies avec leurs molécules associées.
2. **Manipulation des données avec un service externe :** Gemini (SDK officiel `google-genai`) transforme des résumés de publications PubMed en données structurées (type d'étude, molécules citées, résultat principal, limites), en direct à la demande de Claude. 55 publications déjà structurées sont enregistrées en secours.
3. **Serveur MCP :** 12 outils (SDK Python officiel `mcp`) exposés en HTTP, déployés automatiquement sur Render à partir du dépôt GitHub.

Les clés API ne sont pas dans le dépôt : elles sont définies dans les variables d'environnement de l'hébergeur.

Scénario type : installer le MCP dans Claude, poser une question (par exemple « Quelles sont les molécules associées à la maladie de Parkinson ? »), le MCP renvoie des données structurées (titres, identifiants, liens), puis Claude répond à partir de ces données.

## 3. Les 12 outils du serveur

| Outil | Rôle | Source |
|---|---|---|
| `search_diseases` | Cherche une maladie dans la base locale (par mot-clé, sans tenir compte de la casse) | Base locale |
| `get_disease_molecules` | Liste les molécules associées à une maladie, à partir de son identifiant | Base locale |
| `search_neuroscience_literature` | Recherche des publications ; la requête PubMed est complétée automatiquement par « neuroprotection » | PubMed |
| `search_clinical_trials` | Recherche des essais cliniques pour une maladie (phase, statut, interventions, lien) | ClinicalTrials.gov |
| `research_molecule` | Recherche des essais cliniques qui impliquent une molécule | ClinicalTrials.gov |
| `search_molecule_chembl` | Identifiant ChEMBL, nom, poids moléculaire, AlogP, SMILES, phase clinique maximale | ChEMBL |
| `get_molecule_mechanisms` | Mécanismes d'action annotés d'une molécule | ChEMBL |
| `get_biological_target` | Fiche d'une cible biologique (nom, type, organisme, accession) | ChEMBL |
| `get_molecule_bioactivities` | Mesures expérimentales d'activité d'une molécule | ChEMBL |
| `generate_pharmacology_report` | Rapport pharmacologique : propriétés, mécanismes, cibles, activités | ChEMBL |
| `generate_integrated_research_report` | Rapport intégré : pharmacologie, essais cliniques, publications et limites scientifiques | ChEMBL, ClinicalTrials.gov, PubMed |
| `analyze_scientific_evidence_with_gemini` | Appelle Gemini en direct pour structurer des résumés PubMed d'une maladie neurologique ; repli sur des données enregistrées | Gemini + PubMed |

## 4. Exemples de requêtes à tester dans Claude

- « Cherche "Parkinson" dans les maladies de NeurohoraScope.AI, puis donne-moi les molécules associées à cette maladie. »
- « Cherche "sclerosis" dans les maladies de NeurohoraScope.AI, puis donne-moi les molécules de la sclérose en plaques. »
- « Utilise NeurohoraScope.AI pour trouver 3 publications sur la maladie de Parkinson, avec leurs PMID et leurs liens PubMed. »
- « Cherche des essais cliniques sur la maladie de Huntington avec NeurohoraScope.AI et donne-moi leur identifiant NCT, leur statut et leur phase. »
- « Cherche la molécule Levodopa dans ChEMBL, puis donne-moi ses mécanismes d'action et sa cible biologique. »
- « Génère un rapport de recherche intégré sur la Levodopa dans le contexte de la maladie de Parkinson. »
- « Utilise l'outil Gemini de NeurohoraScope.AI pour la maladie de Parkinson et donne-moi, pour chaque publication, le titre, le type d'étude, les molécules citées et le lien. »

## 5. Base locale de maladies

La base locale contient **18 maladies** (261 associations maladie-molécule). Les 11 premières lignes sont neurologiques (neurodégénératives, neuro-immunitaires ou neuromusculaires). Les molécules d'Alzheimer viennent des données Medicodex d'origine. Celles de Parkinson et des 9 autres maladies neurologiques ont été ajoutées à partir des essais cliniques renvoyés par le serveur le 17 novembre 2026.

| Id | Maladie | Molécules | Source |
|---|---|---|---|
| 1 | Alzheimer Disease | 10 | Medicodex |
| 9 | Parkinson Disease | 5 | Saisie manuelle (NeurohoraScope.AI) |
| 10 | Multiple Sclerosis | 8 | Essais cliniques |
| 11 | Amyotrophic Lateral Sclerosis | 12 | Essais cliniques |
| 12 | Huntington Disease | 10 | Essais cliniques |
| 13 | Lewy Body Disease | 3 | Essais cliniques |
| 14 | Frontotemporal Dementia | 6 | Essais cliniques |
| 15 | Progressive Supranuclear Palsy | 4 | Essais cliniques |
| 16 | Multiple System Atrophy | 6 | Essais cliniques |
| 17 | Friedreich Ataxia | 6 | Essais cliniques |
| 18 | Spinal Muscular Atrophy | 6 | Essais cliniques |
| 2 | Cardiovascular Diseases | 2 | Medicodex |
| 3 | Diabetes Mellitus, Type 2 | 36 | Medicodex |
| 4 | Endometriosis | 11 | Medicodex |
| 5 | Hypertension | 94 | Medicodex |
| 6 | Leukemia | 12 | Medicodex |
| 7 | Lyme Disease | 3 | Medicodex |
| 8 | Melanoma | 27 | Medicodex |

Règle appliquée aux molécules issues des essais : médicaments étudiés ou comparateurs actifs, avec leur nom tel qu'il figure dans l'essai. Ont été exclus le placebo, la prémédication (corticoïdes, antihistaminiques, etc.), les produits de diagnostic (radiotraceurs), les procédures simulées, les essais sur volontaires sains et les médicaments donnés pour une autre indication. Ce sont des associations issues d'essais, **pas une liste de traitements validée** ; certains noms sont des codes de développement ou des noms commerciaux. Les identifiants UMLS des 9 maladies ajoutées à partir des essais sont vides ; l'ataxie spinocérébelleuse n'a pas été ajoutée, car la recherche n'a renvoyé aucun essai retenu par le filtre.

## 6. Molécules des maladies neurologiques

| Maladie | Molécules associées |
|---|---|
| Alzheimer Disease (id 1) | Aducanumab, Benzgalantamine, Donepezil, Galantamine, Memantine, Rivastigmine, Selegiline, Tacrine, Tocopherol / vit E, Valproic acid |
| Parkinson Disease (id 9) | Entacapone, Istradefylline, Levodopa, Rotigotine, Tolcapone |
| Multiple Sclerosis (id 10) | Alemtuzumab, Dimethyl fumarate, Fenebrutinib, GW-1000-02, Glatiramer acetate, Interferon beta-1a, Ocrelizumab, Ozanimod |
| Amyotrophic Lateral Sclerosis (id 11) | ABBV-CLS-7262, CNM-Au8, DNL343, Dexpramipexole, Levosimendan, MediCabilis CBD Oil, Minocycline, NUZ-001, Pridopidine, SLS-005 Trehalose, Verdiperstat, Zilucoplan |
| Huntington Disease (id 12) | Dimebon (latrepirdine), Minocycline, Olanzapine, Pridopidine, RO7234292 (RG6042), Riluzole, SKY-0515, Tiapridal, Votoplam, Xenazine |
| Lewy Body Disease (id 13) | Donanemab, Donepezil, Galantamine |
| Frontotemporal Dementia (id 14) | ARO-MAPT-SC, ET-STEM, Galantamine, Memantine, PBFT02, Syntocinon |
| Progressive Supranuclear Palsy (id 15) | FNP-223, GV1001, Salsalate, Valproic acid |
| Multiple System Atrophy (id 16) | 3-N-butylphthalide, Fluoxétine, Foralumab, TAK-341, TEV-56286, Tllsh2910 |
| Friedreich Ataxia (id 17) | CTI-1601, Idebenone, MIN-102, Nomlabofusp, Omaveloxolone, Vatiquinone |
| Spinal Muscular Atrophy (id 18) | Apitegromab, Hydroxyurea, Levocarnitine, Nusinersen, Salanersen, Valproate |

## 7. Vérifications effectuées le 17 novembre 2026

Les 12 outils ont été appelés depuis Claude sur le serveur déployé et ont tous répondu sans erreur (dernier commit au moment du rendu : `2273ab7`).

| Outil | Résultat observé |
|---|---|
| `search_diseases` | « Parkinson » → id 9 ; « sclerosis » → ids 10 et 11 |
| `get_disease_molecules` | Ids 10 : 8 molécules ; 12 : 10 ; 18 : 6 ; 9 : 5 |
| `search_neuroscience_literature` | Publications renvoyées avec PMID et lien PubMed |
| `search_clinical_trials` | Parkinson : 1 136 essais trouvés ; échantillon renvoyé |
| `research_molecule` | Levodopa et Parkinson : 457 essais trouvés ; essais renvoyés |
| `search_molecule_chembl` | CHEMBL1009 (LEVODOPA), poids moléculaire 197,19 |
| `get_molecule_mechanisms` | Agoniste du récepteur D3 (cible CHEMBL234) |
| `get_biological_target` | D(3) dopamine receptor, accession P35462 |
| `get_molecule_bioactivities` | CHEMBL1009 : 1 277 mesures au total ; échantillon renvoyé |
| `generate_pharmacology_report` | Rapport complet : molécule, mécanisme, cible, activités |
| `generate_integrated_research_report` | Rapport complet avec 6 limites scientifiques |
| `analyze_scientific_evidence_with_gemini` | « success / live » : 3 publications structurées par Gemini en direct (Parkinson, sclérose en plaques, Alzheimer) ; maladie non couverte : repli « precomputed » |

## 8. Limites et précautions

- **Premier appel lent :** sur l'offre gratuite de Render, le serveur s'endort après un moment d'inactivité. La première requête peut prendre 50 secondes ou plus.
- **Dépendance aux API externes :** les outils ChEMBL, PubMed et ClinicalTrials.gov interrogent des API publiques en direct. Leur disponibilité ne dépend pas de ce projet : en cas d'indisponibilité temporaire (par exemple une erreur 500 côté EMBL-EBI, observée le 17 novembre 2026 vers 16 h 30), l'outil concerné renvoie un message d'erreur clair et les autres outils continuent de fonctionner.
- **Gemini en direct, avec limites :** quand Claude appelle l'outil avec une maladie, le serveur récupère 3 résumés PubMed, les envoie à Gemini avec la clé stockée dans les variables d'environnement de l'hébergeur (jamais dans le dépôt), valide la réponse (titres et liens repris de la source, molécules rejetées si elles ne figurent pas dans le texte) et la renvoie avec `mode: live`. Pour protéger la clé, l'outil est limité à 11 maladies neurologiques, 30 appels par jour et un cache d'une heure. En cas de limite atteinte, de maladie non couverte ou d'erreur, il renvoie 55 publications déjà structurées par Gemini et enregistrées dans `deploy_data/gemini_structured_literature.json` (`status: precomputed`). Ce sont des données générées par une IA à partir de résumés, pas des conclusions scientifiques validées ; pour les maladies rares, PubMed renvoie parfois des articles peu spécifiques, et la liste « molécules citées » peut contenir des gènes ou des cytokines.
- **Mode démo sans authentification :** toute personne qui connaît l'adresse peut appeler les outils. Ce mode est destiné à une démonstration ponctuelle. Un mode avec jeton est déjà codé (`src/mcp/auth.py`).
- **Base locale limitée :** une maladie absente du tableau de la section 5 (par exemple l'ataxie spinocérébelleuse) n'est pas trouvée par `search_diseases`. Les outils PubMed, ClinicalTrials.gov et ChEMBL restent utilisables pour n'importe quelle maladie.
- **Résultats partiels :** les outils renvoient un échantillon (limité par un paramètre), pas la totalité des publications ou des essais. Les publications sont renvoyées sans date ni revue. Les données ClinicalTrials.gov sont en direct : les totaux peuvent varier légèrement d'un jour à l'autre.
- **Valeur scientifique :** une valeur d'activité, une publication ou l'enregistrement d'un essai ne démontrent ni l'efficacité ni la sécurité d'un traitement. Les rapports le rappellent dans leurs notes de limites. Usage de recherche uniquement.
- **Maintenance de l'hébergeur :** Render a annoncé une maintenance de son infrastructure le 18 novembre à 3 h (heure de Genève), pendant laquelle le service peut être indisponible.

## 9. Organisation du code

- `src/mcp/` : serveur MCP (`server.py`, les 12 outils) et authentification (`auth.py`) ;
- `src/clients/` : accès à ChEMBL, PubMed et ClinicalTrials.gov ;
- `src/analysis/` : analyses, rapports, filtrage de pertinence des essais ;
- `src/storage/` : base SQLite, import des données (Medicodex), cache ;
- `src/ai/` : traitement Gemini (analyse ChEMBL et structuration des résumés PubMed) et validation par les données sources ;
- `src/provenance/` : suivi des sources et journal des changements ;
- `deploy_data/` : données utilisées au déploiement (base locale, données structurées par Gemini) ;
- `render.yaml`, `start_render.py`, `render_app.py` : configuration et démarrage sur Render (la base SQLite est reconstruite au démarrage à partir de `deploy_data/medicodex.json`) ;
- `docs/specs/` : spécifications SPEC-001 à SPEC-005 et fichier d'audit, mis à jour le 17 novembre 2026 (18 maladies, 261 associations, vérification des 12 outils) ;
- `tests/` : tests de régression hors ligne et scripts manuels historiques.

Documentation complémentaire : `docs/architecture.md`, `docs/scientific_methodology.md`, `docs/mcp_tools.md`.

## 10. Installation et lancement en local (Windows / PowerShell)

Depuis la racine du dépôt :

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Pour utiliser Gemini en local, créer un fichier `.env` (**ne pas le publier**) :

```text
GEMINI_API_KEY=VOTRE_CLE
GEMINI_MODEL=gemini-3.1-flash-lite
```

Lancer le serveur MCP (transport stdio par défaut) :

```powershell
.\.venv\Scripts\python.exe mcp_server.py
```

Pour le mode HTTP, définir `MCP_TRANSPORT=streamable-http` dans l'environnement du processus (chemin `/mcp`). Sur Render, le démarrage passe par `start_render.py`.

Régénérer les données structurées par Gemini (étape hors ligne, nécessite la clé) :

```powershell
.\.venv\Scripts\python.exe -m src.ai.gemini_structure_literature
```

Tests hors ligne :

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Les scripts de test manuels sont dans `tests/legacy/` (`manual_test_*.py`) ; ils ne sont pas exécutés automatiquement car plusieurs font de vrais appels réseau.
