# SPEC-004 — Analyse scientifique avec Gemini et MCP

**Projet :** NeurohoraScope.AI
**Domaine :** Neuropharmacologie computationnelle
**Version documentaire :** 1.1
**Date :** 29 octobre 2026
**Statut :** Implémentation locale testée — validation scientifique partielle — déploiement distant non réalisé

## 1. Objectif

Développer une fonctionnalité d'analyse scientifique assistée par Google Gemini, accessible notamment à travers le Model Context Protocol (MCP).

Le système doit permettre d'interpréter des observations pharmacologiques structurées provenant de ChEMBL, sans modifier les mesures expérimentales originales.

L'intelligence artificielle intervient comme outil d'assistance à la recherche. Ses interprétations ne doivent pas être confondues avec des résultats expérimentaux validés.

## 2. Architecture technique

### 2.1. Configuration Gemini

**Module :** `src/ai/gemini_config.py`

Ce module est destiné à la configuration du service Gemini.

Le processeur scientifique charge également sa configuration depuis les variables d'environnement.

### 2.2. Processeur scientifique

**Module :** `src/ai/gemini_scientific_processor.py`

**Fonction :** `analyze_scientific_data(records)`

Cette fonction :

1. Vérifie que les données d'entrée constituent une liste non vide.
2. Vérifie la présence de la clé API Gemini.
3. Transmet les observations au modèle.
4. Demande une réponse structurée au format JSON.
5. Vérifie la structure générale de la réponse.
6. Applique la validation déterministe des observations.
7. Applique le contrôle sémantique ciblé.
8. Retourne l'analyse uniquement si ces contrôles réussissent.

### 2.3. Validation scientifique

**Module :** `src/ai/validation.py`

Fonctions principales :

- `validate_gemini_records`
- `validate_potency_descriptions`

Ces fonctions réalisent des contrôles indépendants de l'interprétation du modèle.

### 2.4. Interface MCP

**Module :** `src/mcp/server.py`

**Outil :** `analyze_scientific_evidence_with_gemini`

Cet outil expose l'analyse scientifique à un client MCP compatible.

## 3. Données d'entrée

### 3.1. Paramètre MCP

`max_records`

Nombre maximal d'observations à analyser.

**Valeur par défaut :** 7
**Intervalle accepté :** de 1 à 20 inclus.

Une valeur hors de cet intervalle doit être rejetée avant tout appel à Gemini.

### 3.2. Source expérimentale

`reports/exact_activity_matches.json`

Ce fichier contient les observations pharmacologiques sélectionnées pour l'analyse.

Le processeur attend une liste JSON non vide.

Les observations doivent conserver leurs informations expérimentales originales.

## 4. Configuration du modèle

Le processeur utilise la variable d'environnement :

`GEMINI_MODEL`

**Valeur par défaut configurée :** `gemini-3.1-flash-lite`

La clé d'accès est fournie par :

`GEMINI_API_KEY`

Aucune clé API ne doit être intégrée directement au code source, à la documentation ou aux rapports.

## 5. Format de réponse

### 5.1. Réponse du processeur Gemini

Le processeur attend un objet JSON contenant notamment :

- `research_domain`
- `records`
- `scientific_limitations`

Chaque observation interprétée doit comprendre :

- `molecule`
- `target`
- `ic50_nm`
- `assay_id`
- `interpretation`

Les informations expérimentales doivent correspondre aux observations sources.

### 5.2. Réponse de l'outil MCP

L'implémentation actuelle construit une réponse comprenant :

- `status`
- `project`
- `source`
- `records_analyzed`
- `scientific_analysis`
- `scientific_note`

Les champs `model` et `measurement_validation`, décrits dans une version antérieure, ne sont pas actuellement ajoutés explicitement par l'outil MCP restauré.

Leur éventuel rétablissement constitue une amélioration de traçabilité à examiner séparément.

## 6. Validation déterministe

La fonction `validate_gemini_records` compare les observations originales et les observations produites par Gemini.

Les champs contrôlés comprennent :

- L'identité de la molécule.
- L'identité de la cible.
- L'identifiant de l'essai ChEMBL.
- La valeur IC50.

La comparaison utilise un comptage des observations afin de détecter les ajouts, suppressions, modifications et duplications.

Les valeurs IC50 sont comparées numériquement à l'aide du type `Decimal`.

Les valeurs non numériques, non finies ou non positives sont rejetées.

Cette validation ne garantit ni la qualité des données sources ni l'exactitude des interprétations scientifiques rédigées par Gemini.

## 7. Validation sémantique ciblée

La fonction `validate_potency_descriptions` contrôle certaines formulations scientifiques produites par Gemini.

### 7.1. Règle subnanomolaire

Une valeur IC50 peut être qualifiée de subnanomolaire uniquement si elle est strictement inférieure à 1 nM.

Par conséquent :

- IC50 = 0,5 nM : formulation subnanomolaire admissible.
- IC50 = 1,0 nM : formulation subnanomolaire rejetée.
- IC50 = 1,6 nM : formulation subnanomolaire rejetée.

Le contrôle reconnaît certaines variantes textuelles de l'expression anglaise *sub-nanomolar*.

### 7.2. Limites

Cette validation est ciblée.

Elle ne vérifie pas toutes les interprétations scientifiques possibles, notamment les conclusions mécanistiques complexes, les comparaisons entre essais ou les affirmations cliniques.

La validation sémantique générale reste donc une évolution future.

## 8. Exigences fonctionnelles

**GEM-001 :** Accepter entre 1 et 20 observations pour l'outil MCP.

**GEM-002 :** Préserver l'identité des molécules et des cibles.

**GEM-003 :** Préserver les identifiants des essais ChEMBL.

**GEM-004 :** Préserver les valeurs IC50 originales.

**GEM-005 :** Rejeter les observations ajoutées, supprimées, dupliquées ou modifiées.

**GEM-006 :** Exiger une réponse Gemini structurée au format JSON.

**GEM-007 :** Distinguer les données expérimentales des interprétations de l'IA.

**GEM-008 :** Ne pas présenter une activité in vitro comme une preuve d'efficacité clinique.

**GEM-009 :** Rejeter les descriptions subnanomolaires incompatibles avec la valeur IC50.

**GEM-010 :** Ne pas écraser les données sources par les résultats de l'IA.

**GEM-011 :** Gérer les erreurs de configuration, de réponse et de validation.

**GEM-012 :** Préserver la traçabilité des analyses scientifiques générées.

## 9. Anomalie scientifique historique

Une analyse antérieure de l'Orelabrutinib ciblant BTK a décrit une valeur IC50 de 1,6 nM comme *sub-nanomolar*.

Cette description était incorrecte, car 1,6 nM est supérieur à 1 nM.

Un contrôle sémantique ciblé a depuis été implémenté pour détecter ce type de contradiction.

Cette correction ne constitue pas une validation exhaustive de toutes les formulations scientifiques produites par Gemini.

## 10. Tests d'acceptation

### Tests réussis

- [x] Enregistrement de l'outil Gemini parmi les 12 outils MCP.
- [x] Tests antérieurs de connexion réelle à Gemini.
- [x] Analyse antérieure de sept observations ChEMBL.
- [x] Validation déterministe des mesures expérimentales.
- [x] Quatre tests automatisés de validation sémantique.
- [x] Rejet d'une description subnanomolaire pour IC50 = 1,6 nM.
- [x] Rejet à la limite IC50 = 1,0 nM.
- [x] Acceptation de la formulation pour IC50 = 0,5 nM.
- [x] Initialisation d'une session MCP via Streamable HTTP local.
- [x] Découverte des 12 outils depuis un client HTTP.
- [x] Invocation HTTP de l'outil Gemini avec rejet attendu de `max_records = 0`.
- [x] Réussite de la suite globale de 15 tests automatisés.

### Tests restant à effectuer

- [ ] Réexécuter une analyse Gemini valide après restauration du serveur MCP.
- [ ] Vérifier les erreurs et réponses malformées de l'API Gemini.
- [ ] Vérifier le contrat de réponse complet de l'outil MCP.
- [ ] Tester davantage de contradictions sémantiques.
- [ ] Vérifier le comportement avec des observations expérimentales atypiques.
- [ ] Valider l'outil depuis un serveur MCP distant sécurisé.

## 11. Sécurité scientifique

Le système doit :

- Préserver les données expérimentales originales.
- Rejeter les modifications non autorisées des observations.
- Éviter les références scientifiques inventées.
- Signaler les limites des analyses.
- Ne pas formuler de recommandations thérapeutiques personnalisées.
- Distinguer les résultats observés des hypothèses.
- Ne pas considérer les sorties de l'IA comme des preuves scientifiques indépendantes.

## 12. Évolutions prévues

1. Renforcement de la validation sémantique.
2. Tests automatisés des erreurs de l'API Gemini.
3. Harmonisation du contrat de réponse MCP.
4. Amélioration de la traçabilité du modèle et des analyses.
5. Extension des analyses à plusieurs molécules et sources.
6. Intégration scientifique plus poussée des données PubMed et ClinicalTrials.gov.
7. Déploiement distant sécurisé du serveur MCP.

## 13. Critères de validation finale

SPEC-004 sera considérée comme entièrement validée lorsque :

- Les mesures expérimentales seront préservées dans tous les scénarios couverts.
- Les règles de validation déterministe et sémantique seront testées.
- Les erreurs Gemini seront gérées de manière contrôlée.
- Le contrat de réponse MCP sera stable et documenté.
- Les limites scientifiques seront explicites.
- L'outil aura été vérifié dans l'environnement de déploiement retenu.

**Conclusion :** l'intégration Gemini-MCP est fonctionnelle dans les scénarios locaux testés. La validation déterministe et un contrôle sémantique ciblé sont implémentés. La validation scientifique exhaustive et le déploiement distant restent hors du périmètre actuellement vérifié.