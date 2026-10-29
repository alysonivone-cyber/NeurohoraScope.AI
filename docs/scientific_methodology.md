# NeurohoraScope.AI — Méthodologie scientifique et garanties d'intégrité

**Version :** 1.1
**Mise à jour :** 29 octobre 2026
**Domaine :** neuropharmacologie computationnelle
**Statut :** contrôles méthodologiques partiellement implémentés ; validation scientifique exhaustive en attente

## 1. Objectif

NeurohoraScope.AI soutient la recherche exploratoire en neuropharmacologie computationnelle par l'acquisition de données biomédicales, l'analyse pharmacologique, l'organisation des preuves, la production de rapports et l'interprétation assistée par IA.

La plateforme ne vise ni à établir directement l'efficacité clinique d'une intervention ni à produire des recommandations thérapeutiques personnalisées.

Ce document décrit les principes scientifiques et les limites méthodologiques applicables aux résultats.

## 2. Sources scientifiques

### 2.1. PubMed

PubMed permet de retrouver des publications biomédicales. La présence d'une publication dans les résultats de recherche ne garantit pas sa qualité méthodologique ni la force des preuves qu'elle apporte.

### 2.2. ChEMBL

ChEMBL fournit des informations sur les molécules, les cibles biologiques, les essais et les activités expérimentales. Chaque mesure doit être interprétée selon son type, son unité, sa cible et son contexte expérimental.

### 2.3. ClinicalTrials.gov

ClinicalTrials.gov renseigne sur les études cliniques enregistrées. Une étude enregistrée n'est pas nécessairement achevée, et son enregistrement ne démontre pas l'efficacité d'une intervention.

### 2.4. Medicodex

Medicodex fournit des associations locales entre maladies et molécules. Ces associations ne doivent pas être automatiquement interprétées comme des indications thérapeutiques validées.

## 3. Mesures pharmacologiques

### 3.1. IC50

L'IC50 correspond à la concentration associée à 50 % d'inhibition dans les conditions d'un essai expérimental donné.

Une IC50 plus faible peut indiquer une puissance inhibitrice apparente plus importante **dans un contexte expérimental suffisamment comparable**. Elle ne démontre pas à elle seule une meilleure efficacité clinique, une sécurité supérieure ou un intérêt thérapeutique accru.

### 3.2. Métadonnées nécessaires

Les informations pertinentes comprennent notamment :

- L'identité de la molécule.
- La cible biologique.
- L'identifiant de l'essai.
- Le type de mesure.
- La valeur et son unité.
- La relation expérimentale (`=`, `<`, `>` notamment).
- La description et les conditions de l'essai, lorsqu'elles sont disponibles.

La conservation de ces informations facilite la reproductibilité et l'interprétation critique.

## 4. Extraction d'activités exactes

La méthodologie existante décrit une routine particulière d'extraction des activités BTK utilisant les critères suivants :

- **Cible :** `Tyrosine-protein kinase BTK`.
- **Mesure :** `IC50`.
- **Unité :** `nM`.
- **Relation :** `=`.
- **Valeur :** numérique et strictement positive.

Ces critères concernent cette routine et ne doivent pas être étendus automatiquement à toutes les analyses ChEMBL.

Dans cette extraction, les observations exprimées par des inégalités ou dans des unités non prises en charge ne sont pas traitées comme des mesures exactes. Les observations originales doivent rester distinctes des résultats filtrés ou calculés.

## 5. Comparabilité expérimentale

Des mesures issues de deux essais différents ne sont pas nécessairement directement comparables. Les résultats peuvent varier selon :

- La méthode de mesure.
- Les conditions expérimentales.
- Le système biologique utilisé.
- Les constructions ou variantes de la cible.
- Les techniques de détection.
- Les protocoles d'essai.

Un classement purement numérique de molécules testées dans des essais hétérogènes peut donc être trompeur.

NeurohoraScope.AI possède des modules de classification des essais, d'analyse du contexte expérimental, de comparabilité et de fiabilité. Leurs règles détaillées et leur couverture nécessitent encore des tests ciblés.

## 6. Sélectivité moléculaire

L'étude de la sélectivité exige d'identifier les cibles et de vérifier la comparabilité des conditions de mesure.

Des valeurs d'activité différentes contre deux cibles ne permettent pas automatiquement de conclure à une sélectivité fiable si les essais sont trop hétérogènes. Les observations doivent être séparées des conclusions dérivées.

## 7. Évaluation des preuves

Les sources de preuves peuvent inclure les mesures pharmacologiques, les travaux précliniques, les publications biomédicales, les études cliniques enregistrées, les résultats cliniques publiés et les synthèses de littérature.

Ces sources n'ont ni le même rôle ni les mêmes limites. Le nombre de publications, le nombre d'essais ou la présence d'associations dans une base de données ne constituent pas des mesures directes de la qualité des preuves.

L'absence de résultats retrouvés lors d'une recherche ne prouve pas nécessairement l'absence d'activité biologique ou de potentiel thérapeutique.

## 8. Interprétation scientifique assistée par Gemini

### 8.1. Rôle de Gemini

Le processeur `src/ai/gemini_scientific_processor.py` structure et interprète des observations pharmacologiques sélectionnées.

Ses instructions demandent de préserver les molécules, cibles, valeurs IC50 et identifiants ChEMBL, de ne pas inventer de références, d'éviter les affirmations cliniques injustifiées et de ne pas classer des composés provenant d'essais non comparables.

Ces instructions textuelles ne suffisent pas, à elles seules, à garantir la justesse des réponses.

### 8.2. Validation déterministe des observations

**Fonction :** `validate_gemini_records`
**Module :** `src/ai/validation.py`

Cette fonction compare les observations sources avec celles produites par Gemini selon :

- L'identité de la molécule.
- L'identité de la cible.
- L'identifiant de l'essai ChEMBL.
- La valeur IC50.
- Le nombre d'occurrences de chaque observation.

La comparaison utilise `Counter` pour détecter les ajouts, suppressions, duplications et modifications. Les IC50 sont converties en `Decimal`, et les valeurs non numériques, non finies ou non positives sont rejetées.

**Limite :** cette vérification protège les champs expérimentaux comparés ; elle ne valide pas l'exactitude scientifique des explications rédigées par Gemini. Elle ne vérifie pas non plus tous les champs possibles des observations sources.

### 8.3. Validation sémantique ciblée

**Fonction :** `validate_potency_descriptions`

Cette fonction détecte certaines utilisations incorrectes de l'expression anglaise « sub-nanomolar ».

Une IC50 ne peut être qualifiée de subnanomolaire que si :

**IC50 < 1 nM**

| Valeur IC50 | Formulation | Résultat du contrôle |
|---|---|---|
| 0,5 nM | « sub-nanomolar » | Acceptée |
| 1,0 nM | « sub-nanomolar » | Rejetée |
| 1,6 nM | « sub-nanomolar » | Rejetée |
| 1,6 nM | « low-nanomolar » | Non rejetée par cette règle |

La dernière ligne ne signifie pas que toute l'interprétation a été validée. Le contrôle sémantique actuel est limité à une famille de formulations et ne couvre pas toutes les contradictions scientifiques possibles.

## 9. Limites des interprétations

NeurohoraScope.AI ne doit pas :

- Assimiler une activité *in vitro* à une efficacité clinique.
- Présenter une association expérimentale comme une recommandation thérapeutique.
- Inventer des mesures ou des références manquantes.
- Considérer une interprétation IA comme une preuve indépendante.
- Supposer que tous les essais sont directement comparables.
- Présenter l'enregistrement d'un essai clinique comme une démonstration de succès thérapeutique.
- Transformer une hypothèse en conclusion établie sans preuve suffisante.

Les incertitudes et limites méthodologiques doivent être explicites.

## 10. Provenance et reproductibilité

Les résultats doivent préserver, lorsque disponibles :

- La source des données.
- Les identifiants d'origine.
- Les identifiants des essais.
- Les valeurs et unités expérimentales.
- Les critères de sélection.
- Les métadonnées de récupération et de traitement pertinentes.

Le projet comporte des modules de provenance, de journalisation des changements et d'audit d'intégrité. Leur couverture opérationnelle complète reste à vérifier.

## 11. Principes de production des rapports

Les rapports scientifiques doivent distinguer clairement :

1. Les observations originales.
2. Les critères de sélection et les traitements.
3. Les calculs dérivés.
4. Les interprétations produites par IA.
5. Les limites scientifiques.
6. Les questions nécessitant de nouvelles recherches.

Les rapports ne doivent pas modifier silencieusement les mesures sources. La présence de modules d'exportation ne garantit pas que chaque document produit a été vérifié indépendamment.

## 12. État des validations au 29 octobre 2026

| Élément | État |
|---|---|
| Tests automatisés Python | 15 réussis |
| Validation déterministe Gemini | Implémentée |
| Validation sémantique ciblée | Implémentée |
| Tests de validation sémantique | 4 réussis |
| Outils MCP découverts | 12 |
| Streamable HTTP local | Testé |
| Validation scientifique exhaustive | Non réalisée |

La suite actuelle ne constitue pas une validation exhaustive de la méthodologie scientifique.

## 13. Vérifications scientifiques restantes

- Tester les extractions sur des jeux de données ChEMBL contrôlés.
- Vérifier les critères de comparabilité des essais.
- Valider les calculs de sélectivité moléculaire.
- Auditer les méthodes d'évaluation des preuves.
- Tester les données incomplètes ou contradictoires.
- Étendre les contrôles sémantiques au-delà de « sub-nanomolar ».
- Vérifier l'exactitude et la provenance des rapports.
- Comparer les interprétations IA aux sources scientifiques originales.
- Tester les traitements complets après déploiement.

## 14. Documentation associée

- `docs/architecture.md`
- `docs/mcp_tools.md`
- `docs/specs/SPEC-001-architecture-generale.md`
- `docs/specs/SPEC-002-acquisition-stockage-tracabilite.md`
- `docs/specs/SPEC-003-analyse-pharmacologique.md`
- `docs/specs/SPEC-004-gemini-mcp.md`
- `docs/specs/SPEC-005-serveur-mcp.md`

## 15. Conclusion

NeurohoraScope.AI combine récupération de données biomédicales, analyses pharmacologiques, rapports scientifiques et interprétation assistée par Gemini. Sa validation déterministe protège certains champs expérimentaux, tandis qu'un contrôle sémantique ciblé détecte une catégorie précise d'erreurs de formulation.

Ces protections renforcent l'intégrité des traitements, sans remplacer l'expertise scientifique, la vérification indépendante des sources ni une validation complète des workflows.
