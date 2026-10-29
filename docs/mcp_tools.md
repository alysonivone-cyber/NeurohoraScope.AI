# NeurohoraScope.AI — Référence des outils MCP

**Version :** 1.1
**Mise à jour :** 29 octobre 2026
**Statut :** enregistrement des outils et transports locaux vérifiés ; validation individuelle partielle

## 1. Présentation

NeurohoraScope.AI expose ses fonctionnalités de recherche scientifique au moyen du **Model Context Protocol (MCP)**. Le serveur permet à un client compatible d'interroger des sources biomédicales, de rechercher des molécules et des essais cliniques, de générer des rapports et de solliciter une analyse Gemini.

Le serveur enregistre actuellement **12 outils MCP**.

- **Implémentation principale :** `src/mcp/server.py`
- **Lanceur racine :** `mcp_server.py`

## 2. Registre des 12 outils

### 2.1. `search_neuroscience_literature`

Recherche des publications biomédicales liées aux neurosciences et aux domaines connexes.

**Source principale :** PubMed.

### 2.2. `search_diseases`

Recherche des maladies dans les données locales disponibles.

**Source principale :** Medicodex.

### 2.3. `get_disease_molecules`

Récupère les associations disponibles entre une maladie et des molécules.

**Source principale :** Medicodex.

Une association documentaire ne doit pas être présentée automatiquement comme une indication thérapeutique établie.

### 2.4. `search_clinical_trials`

Recherche des informations sur les études cliniques enregistrées.

**Source principale :** ClinicalTrials.gov.

L'enregistrement d'un essai ne constitue pas une preuve d'efficacité.

### 2.5. `research_molecule`

Organise des informations scientifiques disponibles pour soutenir la recherche sur une molécule. Le contenu exact de la réponse dépend du traitement implémenté et doit être vérifié lors de tests ciblés.

### 2.6. `search_molecule_chembl`

Recherche des molécules dans ChEMBL.

### 2.7. `get_molecule_mechanisms`

Récupère les informations disponibles sur les mécanismes d'action moléculaires.

**Source principale :** ChEMBL.

### 2.8. `get_biological_target`

Récupère des informations sur les cibles biologiques.

**Source principale :** ChEMBL.

### 2.9. `get_molecule_bioactivities`

Récupère des observations expérimentales de bioactivité moléculaire.

**Source principale :** ChEMBL.

Les mesures doivent être interprétées en conservant leurs unités, leurs conditions expérimentales et les informations de provenance disponibles.

### 2.10. `generate_pharmacology_report`

Demande la génération d'un rapport de recherche pharmacologique structuré.

**Module associé :** `src/analysis/pharmacology_report.py`.

### 2.11. `generate_integrated_research_report`

Demande la génération d'un rapport scientifique intégrant plusieurs catégories d'informations biomédicales disponibles.

**Module associé :** `src/analysis/integrated_research_report.py`.

### 2.12. `analyze_scientific_evidence_with_gemini`

Soumet des observations pharmacologiques sélectionnées à Google Gemini, avec des contrôles déterministes et sémantiques ciblés.

**Modules associés :**

- `src/ai/gemini_scientific_processor.py`
- `src/ai/validation.py`

**Paramètre identifié :** `max_records`, entier compris entre 1 et 20, valeur par défaut 7.

**Source locale utilisée :** `reports/exact_activity_matches.json`.

Les observations produites par Gemini sont comparées aux données d'origine afin de détecter les modifications, ajouts, omissions ou duplications des mesures contrôlées. Un second contrôle rejette certaines utilisations erronées de « sub-nanomolar » pour une IC50 supérieure ou égale à 1 nM.

Ces validations ne garantissent pas l'exactitude de toutes les interprétations rédigées par l'IA.

## 3. Transports MCP

### 3.1. `stdio`

Transport de communication locale entre un client MCP et le processus serveur. **Statut : testé.**

### 3.2. Streamable HTTP

**Endpoint local :** `http://127.0.0.1:8000/mcp`

Un client compatible a réussi à initialiser une session, à découvrir les 12 outils et à invoquer l'outil Gemini avec `max_records=0`. La réponse de validation attendue a été reçue sans erreur de protocole MCP.

Ce test ne constitue pas une nouvelle invocation valide de l'API Gemini après la restauration du serveur.

## 4. Appels et gestion des erreurs

Le client doit initialiser une session MCP conforme avant de solliciter les outils. Les paramètres sont validés par les implémentations concernées.

Une entrée invalide doit conduire à une réponse explicite plutôt qu'à un résultat scientifique inventé. Il faut distinguer une erreur métier renvoyée par un outil d'une erreur du protocole MCP lui-même.

## 5. Intégrité scientifique

Les outils doivent préserver les protections assurées par leurs modules sous-jacents :

- Ne pas modifier silencieusement les mesures expérimentales.
- Ne pas confondre activité *in vitro* et efficacité clinique.
- Tenir compte des limites de comparaison entre essais.
- Conserver les informations de provenance lorsqu'elles sont disponibles.
- Séparer observations originales et interprétations IA.
- Ne pas inventer les données manquantes.

## 6. Sécurité

Le transport HTTP actuel est configuré pour le développement local. L'interface de boucle locale et la protection contre le DNS rebinding sont activées.

Aucun fournisseur d'authentification ni vérificateur de jeton n'est actuellement configuré. L'endpoint ne doit donc pas être rendu public sans authentification, HTTPS, restrictions réseau et tests de sécurité adaptés.

## 7. État des vérifications au 29 octobre 2026

| Contrôle | Résultat |
|---|---|
| Suite de tests Python | 15 tests réussis |
| Découverte des outils MCP | 12 outils découverts |
| Communication locale `stdio` | Testée |
| Streamable HTTP local | Testé |
| Initialisation de session HTTP | Réussie |
| Liste des outils via HTTP | Obtenue |
| Invocation d'un outil via HTTP | Réussie |
| Paramètre Gemini invalide | Rejet attendu |
| Requête Gemini valide via HTTP après restauration | À tester |
| Authentification distante | Non implémentée |
| Déploiement public HTTPS | Non réalisé |

Ces résultats ne prouvent pas que tous les traitements scientifiques des 12 outils ont été validés individuellement.

## 8. Vérifications complémentaires

- Confirmer les schémas d'entrée et de sortie de chaque outil.
- Ajouter des tests ciblés pour les différents traitements scientifiques.
- Tester les défaillances des API externes et les réponses incomplètes.
- Vérifier une invocation Gemini valide via HTTP.
- Tester l'authentification et les restrictions d'accès.
- Effectuer des tests de bout en bout après déploiement.

## 9. Documentation associée

- `docs/architecture.md`
- `docs/scientific_methodology.md`
- `docs/specs/SPEC-001-architecture-generale.md`
- `docs/specs/SPEC-002-acquisition-stockage-tracabilite.md`
- `docs/specs/SPEC-003-analyse-pharmacologique.md`
- `docs/specs/SPEC-004-gemini-mcp.md`
- `docs/specs/SPEC-005-serveur-mcp.md`

## 10. Conclusion

NeurohoraScope.AI expose 12 outils scientifiques par MCP. Les échanges locaux via `stdio` et Streamable HTTP ont été testés. La validation détaillée des traitements, l'authentification distante et le déploiement sécurisé restent à réaliser.
