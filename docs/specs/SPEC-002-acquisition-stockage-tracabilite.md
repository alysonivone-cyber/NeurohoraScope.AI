# SPEC-002 — Acquisition, stockage et traçabilité scientifique

**Projet :** NeurohoraScope.AI
**Domaine :** Neuropharmacologie computationnelle
**Version documentaire :** 1.2
**Date :** 4 novembre 2026 (mise à jour ; état historique du 29 octobre conservé)
**Statut :** Acquisition externe et Medicodex testés — stockage/cache/provenance à auditer

## 1. Objectif

Définir les exigences techniques et scientifiques relatives à l'acquisition, au stockage, à la conservation et à la traçabilité des données utilisées par NeurohoraScope.AI.

Le système doit permettre de consulter plusieurs sources biomédicales tout en préservant l'identité des observations expérimentales et les informations nécessaires à leur interprétation.

Les données sources doivent rester distinctes des traitements analytiques et des interprétations produites par intelligence artificielle.

## 2. Sources de données

### 2.1. PubMed

**Module :** `src/clients/pubmed_client.py`

PubMed est utilisé pour rechercher des publications biomédicales.

Les informations exploitées par l'outil MCP de recherche comprennent notamment :

- Identifiant PMID.
- Titre de publication.
- Résumé, lorsqu'il est disponible.
- URL de la publication.
- Types de publications, lorsqu'ils sont disponibles.

**Exigence :** les publications doivent rester identifiables par leur source et ne pas être présentées automatiquement comme des preuves d'efficacité thérapeutique.

### 2.2. ChEMBL

**Module :** `src/clients/chembl_client.py`

ChEMBL constitue une source de données pharmacologiques concernant notamment les molécules, les cibles biologiques et les activités expérimentales.

Les informations pertinentes comprennent :

- Identifiants ChEMBL.
- Identité des molécules.
- Identité des cibles biologiques.
- Identifiants des essais expérimentaux.
- Types de mesures pharmacologiques.
- Valeurs, unités et relations expérimentales.

Une observation IC50 doit conserver les informations nécessaires à son interprétation.

### 2.3. ClinicalTrials.gov

**Module :** `src/clients/clinical_trials_client.py`

Cette source permet de consulter des études cliniques enregistrées.

Les recherches peuvent notamment être filtrées selon :

- La maladie.
- Le type d'intervention.
- La phase de l'étude.
- Le statut de recrutement ou de réalisation.

L'enregistrement d'une étude clinique ne constitue pas, à lui seul, une preuve d'efficacité.

### 2.4. Medicodex

**Module :** `src/storage/medicodex_import.py`

Medicodex est une source locale utilisée pour organiser des associations entre maladies et molécules.

Le fichier de données identifié dans la documentation technique est :

`data/medicodex.json`

Ces associations doivent être interprétées comme des informations de recherche, et non comme des recommandations thérapeutiques validées.

## 3. Architecture d'acquisition

Les clients externes sont regroupés dans :

`src/clients/`

Cette séparation vise à distinguer la récupération des données de leur traitement scientifique.

Les modules d'analyse doivent exploiter les résultats des clients sans modifier silencieusement les observations expérimentales originales.

Les erreurs réseau, les réponses incomplètes et les données absentes doivent être gérées explicitement.

## 4. Stockage local

### 4.1. SQLite

**Module :** `src/storage/database.py`

Le système utilise SQLite pour certaines données locales, notamment les publications et les associations scientifiques.

Les opérations de stockage doivent préserver l'intégrité des informations et éviter les duplications non souhaitées.

### 4.2. Cache ChEMBL

**Modules concernés :**

- `src/storage/chembl_cache.py`
- `src/storage/cache_freshness.py`
- `src/storage/cache_versioning.py`
- `src/storage/cache_version_comparator.py`

Ces modules constituent l'architecture de gestion du cache et de son suivi temporel.

Les règles exactes d'expiration, de comparaison et d'invalidation devront être confirmées par un audit du code et des tests dédiés.

### 4.3. Surveillance des changements

**Module :** `src/storage/multi_assay_change_monitor.py`

Le système comporte un module consacré à la surveillance des changements portant sur plusieurs essais expérimentaux.

La couverture fonctionnelle de ce module reste à vérifier.

## 5. Traçabilité scientifique

Les modules identifiés sont :

- `src/provenance/activity_provenance.py`
- `src/provenance/data_provenance.py`
- `src/provenance/scientific_change_log.py`
- `src/provenance/scientific_integrity_audit.py`

L'objectif est de permettre l'identification des sources, le suivi des transformations et l'audit de l'intégrité des données.

Une analyse reproductible doit pouvoir être reliée, lorsque les informations sont disponibles, à la source, à l'identifiant de l'observation, aux critères de sélection et à la date de récupération.

## 6. Intégrité des mesures expérimentales

Pour les routines d'extraction BTK décrites dans la méthodologie scientifique existante, les observations IC50 admissibles doivent respecter les critères suivants :

- Valeur numérique strictement positive.
- Unité `nM`.
- Relation expérimentale `=`.
- Cible `Tyrosine-protein kinase BTK`.

Les valeurs exprimées dans d'autres unités ou accompagnées d'une relation d'inégalité sont exclues par cette routine particulière.

Cette règle ne doit pas être généralisée sans vérification à l'ensemble des traitements ChEMBL.

Les observations exclues ne doivent pas être converties silencieusement en mesures exactes.

## 7. Exigences fonctionnelles

**DATA-001 :** Permettre la récupération de publications scientifiques depuis PubMed.

**DATA-002 :** Permettre la consultation de données moléculaires et pharmacologiques depuis ChEMBL.

**DATA-003 :** Permettre la recherche d'études enregistrées sur ClinicalTrials.gov.

**DATA-004 :** Permettre l'exploitation des données locales Medicodex.

**DATA-005 :** Préserver les identifiants et métadonnées disponibles des observations expérimentales.

**DATA-006 :** Séparer les données sources des résultats dérivés et des interprétations générées par IA.

**DATA-007 :** Conserver les unités et relations expérimentales utilisées dans les mesures pharmacologiques.

**DATA-008 :** Prévoir des mécanismes de gestion des erreurs et d'indisponibilité des sources externes.

**DATA-009 :** Permettre le suivi de la fraîcheur et des versions des caches.

**DATA-010 :** Faciliter l'identification des transformations et modifications scientifiques.

**DATA-011 :** Éviter de présenter des associations locales maladie-molécule comme des indications thérapeutiques établies.

**DATA-012 :** Permettre une vérification de provenance adaptée aux résultats scientifiques exportés.

## 8. Exigences non fonctionnelles

### 8.1. Reproductibilité

Les traitements scientifiques doivent documenter, lorsque cela est possible :

- La source utilisée.
- La date de récupération.
- Les paramètres de recherche.
- Les filtres appliqués.
- Les identifiants des observations.
- Les versions de cache pertinentes.

### 8.2. Confidentialité

Les clés API et les secrets ne doivent pas être intégrés aux rapports ni aux fichiers publiés.

Les bases locales, caches privés et données de recherche ne doivent pas être rendus publics sans contrôle préalable.

### 8.3. Robustesse

Une indisponibilité temporaire d'une source externe doit produire une erreur identifiable plutôt qu'un résultat scientifique fabriqué.

### 8.4. Séparation des responsabilités

L'acquisition, le stockage, l'analyse et la présentation doivent rester organisés dans des modules distincts.

## 9. Tests d'acceptation

### Éléments déjà constatés

- [x] Présence des trois clients scientifiques externes dans le dépôt.
- [x] Présence du module d'importation Medicodex.
- [x] Présence du module SQLite.
- [x] Présence des modules de cache et de provenance.
- [x] Enregistrement des outils MCP d'accès aux sources scientifiques.
- [x] Exécution globale de 15 tests automatisés sans échec.

### Vérifications complémentaires

- [ ] Vérifier les réponses réelles de chaque source externe.
- [ ] Tester les erreurs réseau et les réponses incomplètes.
- [ ] Vérifier les règles de déduplication SQLite.
- [ ] Tester les politiques d'expiration des caches.
- [ ] Vérifier les mécanismes de suivi des changements.
- [ ] Auditer les informations de provenance effectivement conservées.
- [ ] Tester la reproductibilité des extractions sur des jeux de données contrôlés.

La réussite globale des tests existants ne constitue pas une validation individuelle de tous les modules mentionnés.

## 10. Contraintes scientifiques

NeurohoraScope.AI doit respecter les principes suivants :

1. Une mesure expérimentale doit rester associée à son contexte.
2. Une observation in vitro ne prouve pas une efficacité clinique.
3. Des mesures provenant d'essais différents ne sont pas nécessairement comparables.
4. Une publication retrouvée ne constitue pas automatiquement une preuve scientifique de haute qualité.
5. Une étude clinique enregistrée ne démontre pas automatiquement l'efficacité d'une intervention.
6. Une interprétation générée par IA ne doit pas remplacer les données sources.

## 11. Documentation associée

- `SPEC-001` : architecture générale.
- `SPEC-003` : analyse pharmacologique et rapports.
- `SPEC-004` : Gemini et validation scientifique.
- `SPEC-005` : serveur MCP.
- `docs/architecture.md`
- `docs/scientific_methodology.md`

## 12. Critères de validation finale

SPEC-002 pourra être considérée comme entièrement validée lorsque :

- Les interfaces d'acquisition auront été vérifiées.
- Les règles de stockage auront été documentées et testées.
- Les mécanismes de cache auront été audités.
- La traçabilité des observations sera démontrée sur des exemples reproductibles.
- Les données sources et les résultats dérivés resteront clairement séparés.
- Les erreurs des services externes seront correctement prises en charge.

**Conclusion :** l'architecture d'acquisition, de stockage et de provenance est présente dans NeurohoraScope.AI. La validation complète de son comportement nécessite des tests ciblés supplémentaires.

---

## 13. Mise à jour des vérifications — 4 novembre 2026

### Scénarios fonctionnels observés

- **PubMed :** `search_neuroscience_literature` invoqué depuis Claude via le MCP public après le déploiement `1f7216f` ; trois publications sur Parkinson, avec titres, PMID `38598580`, `31295812`, `41152735` et URL PubMed.
- **ChEMBL :** consultation de Levodopa (`CHEMBL1009`), de mécanismes annotés, de la cible DRD3 (`CHEMBL234`) et de résultats d'activité ; les annotations de mécanisme ne doivent pas être confondues avec une preuve mécanistique ou clinique définitive.
- **ClinicalTrials.gov :** recherche d'essais sur Parkinson et sur Levodopa fonctionnelle dans les scénarios testés ; les réponses sont limitées/filtrées et ne représentent pas nécessairement l'ensemble des études.
- **Medicodex :** base locale consultable ; huit maladies et 195 associations maladie-molécule observées lors des contrôles précédents. La recherche `Alzheimer` renvoie une entrée ; Parkinson ne figure pas dans le jeu de huit maladies examiné. L'absence de résultat n'est donc pas une panne de recherche.
- **Données pour Gemini :** `reports/exact_activity_matches.json` et `deploy_data/exact_activity_matches.json` présents localement, chacun avec sept observations au moment du contrôle. Le processeur sélectionne le fichier local en priorité.

### Limites de validation

Les tests confirment l'accès et des réponses réelles pour ces cas, **pas** l'exhaustivité des clients, la fraîcheur et la déduplication SQLite, l'invalidation des caches, la provenance complète ni les scénarios de panne réseau. Les cases historiques du 29 octobre restent des instantanés et ne doivent pas être interprétées comme le statut final du 4 novembre.
