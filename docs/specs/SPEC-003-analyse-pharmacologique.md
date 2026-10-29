# SPEC-003 — Analyse pharmacologique, comparabilité expérimentale et rapports scientifiques

**Projet :** NeurohoraScope.AI
**Domaine :** Neuropharmacologie computationnelle
**Version documentaire :** 1.0
**Date :** 29 octobre 2026
**Statut :** Architecture implémentée — validation fonctionnelle partielle

## 1. Objectif

Définir les exigences scientifiques et techniques des fonctionnalités d'analyse pharmacologique de NeurohoraScope.AI.

Le système vise à organiser, filtrer, comparer et interpréter des observations expérimentales issues notamment de ChEMBL, en tenant compte de leurs conditions de production et de leurs limites.

Il doit également permettre la production de rapports scientifiques structurés et traçables.

L'objectif n'est pas de prédire directement l'efficacité clinique d'une molécule, mais de soutenir l'exploration et l'évaluation critique des données pharmacologiques disponibles.

## 2. Périmètre scientifique

Les fonctionnalités identifiées dans le dépôt concernent :

- L'identification et l'organisation des activités pharmacologiques.
- L'extraction de mesures expérimentales.
- L'analyse des cibles biologiques.
- La comparaison de molécules.
- L'évaluation de la sélectivité moléculaire.
- La classification des essais expérimentaux.
- L'analyse de la comparabilité des observations.
- L'évaluation des preuves scientifiques.
- L'identification de lacunes dans les données.
- La synthèse des informations pharmacologiques, bibliographiques et cliniques.
- La génération de rapports scientifiques.

Ces domaines sont représentés par des modules Python existants. Leur couverture fonctionnelle et leur validation doivent être confirmées individuellement.

## 3. Analyse des activités pharmacologiques

### 3.1. Sources expérimentales

Les données pharmacologiques sont notamment récupérées depuis ChEMBL.

Les informations nécessaires à leur interprétation peuvent comprendre :

- L'identifiant de la molécule.
- L'identifiant de la cible biologique.
- L'identifiant de l'essai expérimental.
- Le type de mesure, notamment IC50.
- La valeur expérimentale.
- L'unité de mesure.
- La relation expérimentale.
- Les métadonnées disponibles concernant l'essai.

### 3.2. Extraction des mesures

**Module :** `src/analysis/exact_activity_matcher.py`

L'architecture comprend un module consacré à l'identification de correspondances expérimentales exactes.

Les critères précis de sélection doivent être vérifiés dans son implémentation.

La méthodologie existante décrit notamment une routine d'extraction BTK qui sélectionne les observations IC50 positives, exprimées en nM, avec la relation `=` et la cible `Tyrosine-protein kinase BTK`.

Cette règle concerne cette routine particulière et ne doit pas être généralisée automatiquement à toutes les analyses.

### 3.3. Conservation des observations

Une observation expérimentale sélectionnée ne doit pas être modifiée silencieusement.

Les transformations éventuelles doivent être explicites et documentées.

Les mesures originales doivent rester distinguables des valeurs calculées et des interprétations.

## 4. Comparabilité expérimentale

### 4.1. Principe scientifique

Deux valeurs pharmacologiques ne sont pas nécessairement directement comparables lorsqu'elles proviennent d'essais différents.

Les conditions expérimentales, les cibles, les méthodes et les contextes de mesure peuvent influencer les résultats.

Le système doit donc éviter de présenter une comparaison numérique comme une conclusion scientifique définitive lorsque la comparabilité n'est pas suffisamment établie.

### 4.2. Modules concernés

- `src/analysis/assay_classifier.py`
- `src/analysis/assay_comparability.py`
- `src/analysis/assay_metadata.py`
- `src/analysis/comparability_summary.py`
- `src/analysis/comparison_reliability.py`
- `src/analysis/experimental_comparability.py`
- `src/analysis/experimental_context.py`
- `src/analysis/experimental_matrix.py`

Ces modules constituent l'architecture identifiée pour l'analyse des essais et de leur comparabilité.

Les règles exactes de classification et les critères de fiabilité devront être audités avant validation complète.

## 5. Comparaison et sélectivité moléculaires

**Modules concernés :**

- `src/analysis/molecular_comparison.py`
- `src/analysis/molecular_selectivity.py`
- `src/analysis/pharmacology_comparison.py`
- `src/analysis/target_matrix.py`

Ces modules sont destinés à organiser les comparaisons entre molécules, activités et cibles biologiques.

Les comparaisons doivent distinguer les observations directement comparables de celles présentant des limites méthodologiques.

Une différence entre deux valeurs IC50 ne démontre pas, à elle seule, une supériorité thérapeutique.

## 6. Évaluation des preuves scientifiques

**Modules concernés :**

- `src/analysis/evidence_analyzer.py`
- `src/analysis/evidence_assessment.py`
- `src/analysis/research_gap_detector.py`
- `src/analysis/trial_relevance.py`
- `src/analysis/molecule_literature.py`

L'architecture comprend des modules consacrés à l'organisation des preuves, à l'analyse de la littérature, à la pertinence des essais et à l'identification de lacunes scientifiques.

Les résultats doivent distinguer :

1. Les observations expérimentales.
2. Les publications retrouvées.
3. Les études cliniques enregistrées.
4. Les analyses dérivées.
5. Les hypothèses nécessitant des recherches supplémentaires.

Le nombre de publications ou d'études retrouvées ne doit pas être assimilé à une mesure directe de la qualité des preuves.

## 7. Rapports pharmacologiques

### 7.1. Rapport pharmacologique

**Module :** `src/analysis/pharmacology_report.py`

Le serveur MCP expose l'outil :

`generate_pharmacology_report`

Cet outil permet de demander la génération d'un rapport à partir du nom d'une molécule et d'un nombre maximal d'activités.

### 7.2. Rapport de recherche intégré

**Module :** `src/analysis/integrated_research_report.py`

Le serveur MCP expose :

`generate_integrated_research_report`

Les paramètres identifiés comprennent :

- `molecule_name`
- `disease`
- `max_activities`
- `max_trials`

Ce rapport vise à réunir plusieurs catégories d'informations scientifiques.

La structure exacte des résultats doit être vérifiée par des tests fonctionnels ciblés.

## 8. Production et exportation documentaire

Le package `src/reporting/` comprend notamment :

- `markdown_report.py`
- `pdf_report.py`
- `pharmacology_dossier.py`
- `comparison_pdf.py`
- `comparability_report_pdf.py`
- `experimental_matrix_pdf.py`
- `export_research_report.py`
- `export_comparability_summary.py`

Ces modules représentent les capacités de production documentaire identifiées dans le dépôt.

La conformité des fichiers générés, leur lisibilité et leur contenu scientifique devront être vérifiés.

## 9. Exigences fonctionnelles

**ANA-001 :** Permettre l'organisation des activités pharmacologiques par molécule et cible biologique.

**ANA-002 :** Préserver les identifiants des observations et essais expérimentaux.

**ANA-003 :** Conserver les valeurs, unités et relations expérimentales originales.

**ANA-004 :** Appliquer des critères explicites de sélection des observations.

**ANA-005 :** Distinguer les mesures exactes des observations comportant des inégalités ou des unités non prises en charge.

**ANA-006 :** Évaluer la comparabilité des observations avant toute conclusion comparative.

**ANA-007 :** Signaler les limites méthodologiques des comparaisons entre essais.

**ANA-008 :** Permettre l'organisation des informations de sélectivité moléculaire.

**ANA-009 :** Distinguer les résultats expérimentaux des conclusions cliniques.

**ANA-010 :** Produire des rapports pharmacologiques structurés.

**ANA-011 :** Permettre la production de rapports intégrant plusieurs sources scientifiques.

**ANA-012 :** Préserver la provenance des données dans les résultats lorsque les métadonnées nécessaires sont disponibles.

**ANA-013 :** Éviter toute présentation trompeuse de la puissance, de la sélectivité ou de l'efficacité d'une molécule.

**ANA-014 :** Signaler les données insuffisantes ou les limites empêchant une conclusion fiable.

## 10. Exigences non fonctionnelles

### 10.1. Reproductibilité

Les résultats doivent pouvoir être reliés aux données et critères utilisés pour les produire.

### 10.2. Fiabilité

Les comparaisons doivent respecter les limites des observations expérimentales.

### 10.3. Lisibilité

Les rapports doivent distinguer clairement les données sources, les analyses et les limites scientifiques.

### 10.4. Robustesse

Les données manquantes, incompatibles ou insuffisantes doivent être signalées plutôt que remplacées par des résultats inventés.

### 10.5. Traçabilité

Les identifiants des molécules, cibles et essais doivent être conservés lorsque disponibles.

## 11. Tests d'acceptation

### Vérifications déjà constatées

- [x] Présence des modules d'analyse pharmacologique.
- [x] Présence des modules de comparabilité expérimentale.
- [x] Présence des modules de sélectivité moléculaire.
- [x] Présence des modules d'évaluation des preuves.
- [x] Présence des modules de reporting.
- [x] Enregistrement des deux outils MCP de génération de rapports.
- [x] Réussite globale de la suite de 15 tests automatisés.

### Vérifications complémentaires

- [ ] Vérifier les critères d'extraction des mesures sur des données contrôlées.
- [ ] Auditer les classifications d'essais expérimentaux.
- [ ] Tester les règles de comparabilité entre observations.
- [ ] Vérifier les calculs et conclusions de sélectivité.
- [ ] Tester les rapports pharmacologiques avec des données réelles et synthétiques.
- [ ] Vérifier les rapports intégrés et la gestion des sources absentes.
- [ ] Contrôler la validité des fichiers Markdown et PDF générés.
- [ ] Tester les erreurs, données manquantes et cas limites.
- [ ] Vérifier la traçabilité des observations dans les exports.

La réussite de la suite actuelle ne garantit pas que tous les modules ci-dessus disposent de tests individuels.

## 12. Contraintes scientifiques

Le système ne doit pas :

- Assimiler une activité in vitro à une efficacité clinique.
- Présenter automatiquement deux essais différents comme comparables.
- Déduire une recommandation thérapeutique personnalisée.
- Inventer des mesures, des essais ou des références.
- Transformer une hypothèse en conclusion expérimentale établie.
- Présenter les interprétations de l'IA comme des observations originales.

Les résultats doivent permettre une lecture critique des preuves disponibles.

## 13. Documentation associée

- `SPEC-001` : architecture générale.
- `SPEC-002` : acquisition, stockage et traçabilité.
- `SPEC-004` : Gemini et validation scientifique.
- `SPEC-005` : serveur MCP.
- `docs/scientific_methodology.md`
- `docs/architecture.md`

## 14. Critères de validation finale

SPEC-003 pourra être considérée comme entièrement validée lorsque :

- Les règles de sélection et de comparaison auront été vérifiées.
- Les résultats scientifiques seront reproductibles sur des jeux de données contrôlés.
- Les rapports générés préserveront la provenance et les limites des observations.
- Les erreurs et données insuffisantes seront correctement gérées.
- Les fonctionnalités critiques disposeront de tests adaptés.
- Les conclusions respecteront les contraintes scientifiques définies.

**Conclusion :** NeurohoraScope.AI dispose d'une architecture étendue d'analyse pharmacologique et de reporting. Une validation fonctionnelle détaillée reste nécessaire avant de considérer l'ensemble de ces capacités comme scientifiquement vérifiées.