# SPEC-001 — Architecture générale et exigences du système

**Projet :** NeurohoraScope.AI
**Domaine :** Neuropharmacologie computationnelle
**Version documentaire :** 1.0
**Date :** 29 octobre 2026
**Statut :** Architecture identifiée — validation fonctionnelle partielle

## 1. Objectif

NeurohoraScope.AI est une application Python destinée à la recherche et à l'analyse de données scientifiques en neurosciences et en pharmacologie.

Elle vise à faciliter la consultation, l'organisation, la comparaison et l'interprétation de données provenant de sources biomédicales.

Le projet associe des méthodes d'analyse déterministes, des outils de traçabilité scientifique, des fonctionnalités de reporting et une assistance par intelligence artificielle.

Il constitue un outil de recherche et non un dispositif de diagnostic ou de décision thérapeutique.

## 2. Périmètre fonctionnel

Le système comprend les domaines fonctionnels suivants :

- Acquisition de données scientifiques externes.
- Consultation de données locales sur les maladies et les molécules.
- Analyse des activités pharmacologiques.
- Étude de la comparabilité expérimentale.
- Évaluation et organisation des preuves scientifiques.
- Traçabilité des données et des transformations.
- Production de rapports scientifiques.
- Analyse assistée par Google Gemini.
- Exposition de fonctionnalités via le Model Context Protocol (MCP).

La présence des modules correspondants dans le dépôt est confirmée. Leur niveau de validation doit être documenté individuellement.

## 3. Architecture logicielle

Le code principal est organisé dans le package `src/`.

### 3.1. Acquisition des données — `src/clients/`

Ce package contient les clients d'accès à :

- PubMed.
- ChEMBL.
- ClinicalTrials.gov.

### 3.2. Analyse scientifique — `src/analysis/`

Ce package regroupe notamment les modules consacrés :

- Aux activités pharmacologiques.
- Aux essais expérimentaux.
- À la comparabilité des mesures.
- À la sélectivité moléculaire.
- À l'évaluation des preuves.
- Aux rapports de recherche intégrés.
- À l'identification de lacunes dans les données scientifiques.

### 3.3. Intelligence artificielle — `src/ai/`

Ce package contient :

- La configuration de Gemini.
- Le traitement des analyses scientifiques générées.
- La validation déterministe et certains contrôles sémantiques.

### 3.4. Stockage — `src/storage/`

Ce package comprend notamment :

- Les fonctions de stockage SQLite.
- L'importation de Medicodex.
- La gestion du cache ChEMBL.
- Le suivi des versions et de la fraîcheur des caches.

### 3.5. Traçabilité — `src/provenance/`

Ce package regroupe des modules de provenance, de journalisation des modifications scientifiques et d'audit d'intégrité.

### 3.6. Production documentaire — `src/reporting/`

Ce package comprend des modules de génération et d'exportation de rapports scientifiques, notamment aux formats Markdown et PDF.

### 3.7. Serveur MCP — `src/mcp/`

L'implémentation principale est située dans :

`src/mcp/server.py`

Le point d'entrée compatible avec les différents transports est :

`mcp_server.py`

Le serveur expose actuellement 12 outils MCP.

## 4. Points d'entrée

- `main.py` : point d'entrée autonome existant.
- `mcp_server.py` : lanceur du serveur MCP.
- `src/mcp/server.py` : définition des outils MCP.

L'application doit être exécutée depuis la racine du dépôt afin de préserver la résolution des imports et des chemins relatifs.

## 5. Exigences générales

**SYS-001 :** Le système doit conserver une architecture modulaire permettant de séparer les responsabilités.

**SYS-002 :** Les modules internes doivent utiliser des imports cohérents avec l'organisation du package `src`.

**SYS-003 :** Les données expérimentales originales doivent rester distinctes des interprétations générées par intelligence artificielle.

**SYS-004 :** Les informations scientifiques doivent conserver, lorsque disponibles, leurs identifiants et leur provenance.

**SYS-005 :** Les comparaisons pharmacologiques doivent tenir compte des limites liées aux conditions expérimentales.

**SYS-006 :** Le système ne doit pas présenter une activité in vitro comme une preuve d'efficacité clinique.

**SYS-007 :** Les secrets et clés API ne doivent pas être intégrés directement au code source ni publiés dans le dépôt.

**SYS-008 :** Le serveur MCP doit permettre la découverte et l'invocation des outils enregistrés.

**SYS-009 :** Les fonctionnalités critiques doivent disposer de tests automatisés adaptés.

**SYS-010 :** Les documents de spécification doivent être mis à jour lorsque les interfaces, comportements ou exigences évoluent.

## 6. Contraintes scientifiques

Les résultats doivent distinguer :

1. Les observations expérimentales issues des sources.
2. Les traitements et comparaisons déterministes.
3. Les interprétations générées par intelligence artificielle.
4. Les hypothèses scientifiques nécessitant une vérification supplémentaire.

Une valeur IC50 ne constitue pas, à elle seule, une démonstration d'efficacité thérapeutique.

Les données issues de différentes conditions expérimentales ne doivent pas être considérées automatiquement comme directement comparables.

## 7. Contraintes techniques

- Langage principal : Python.
- Organisation : packages Python sous `src/`.
- Stockage local : SQLite et fichiers de cache.
- Intelligence artificielle : Google Gemini.
- Interface d'intégration : MCP avec FastMCP 1.30.0.
- Transports MCP : `stdio` et `streamable-http`.
- Tests automatisés : `unittest`.

Les paramètres de configuration sensibles doivent être gérés séparément du code.

## 8. État des validations au 29 octobre 2026

### Vérifications réussies

- [x] Compilation du serveur MCP.
- [x] Importation de l'instance FastMCP.
- [x] Enregistrement des 12 outils.
- [x] Exécution de 15 tests automatisés sans échec.
- [x] Initialisation d'une session MCP via HTTP local.
- [x] Découverte des 12 outils depuis un client HTTP.
- [x] Invocation HTTP d'un outil avec validation d'un paramètre invalide.
- [x] Protection DNS rebinding activée dans la configuration locale.

### Vérifications complémentaires

- [ ] Audit fonctionnel détaillé de tous les modules scientifiques.
- [ ] Vérification complète du contrat de réponse Gemini après restauration.
- [ ] Tests d'intégration des sources externes dans l'environnement cible.
- [ ] Authentification des clients MCP distants.
- [ ] Tests de sécurité et de limitation des requêtes.
- [ ] Déploiement HTTPS et validation depuis un client distant.

## 9. Documentation associée

- `SPEC-002` : acquisition, stockage et traçabilité.
- `SPEC-003` : analyse pharmacologique et rapports scientifiques.
- `SPEC-004` : analyse scientifique assistée par Gemini.
- `SPEC-005` : architecture et fonctionnement du serveur MCP.
- `docs/architecture.md`
- `docs/mcp_tools.md`
- `docs/scientific_methodology.md`

## 10. Critères d'acceptation finale

SPEC-001 pourra être considérée comme entièrement validée lorsque :

- L'architecture documentée correspondra au code effectivement livré.
- Les exigences fonctionnelles critiques auront été vérifiées.
- Les contrôles scientifiques seront opérationnels et testés.
- Les interfaces MCP seront conformes à leurs contrats.
- Les mesures de sécurité nécessaires au mode de déploiement retenu auront été validées.
- Les SPECS associées seront cohérentes avec cette spécification générale.

**Conclusion :** NeurohoraScope.AI dispose d'une architecture modulaire identifiable et d'un serveur MCP local testé. La validation complète du système et son déploiement distant restent des étapes distinctes.