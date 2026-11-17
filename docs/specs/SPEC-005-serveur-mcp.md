# SPEC-005 — Serveur MCP, sécurité et déploiement

**Projet :** NeurohoraScope.AI
**Domaine :** Neuropharmacologie computationnelle
**Version documentaire :** 1.2
**Date :** 17 novembre 2026 (mise à jour ; états historiques conservés)
**Statut :** Serveur MCP HTTPS Live et testé avec Claude — mode public non authentifié

## 1. Objectif

Exposer les fonctionnalités scientifiques de NeurohoraScope.AI à des clients compatibles avec le Model Context Protocol (MCP).

Le serveur doit permettre la découverte et l'invocation d'outils de recherche biomédicale, d'analyse pharmacologique, de génération de rapports et d'analyse assistée par intelligence artificielle.

L'accès distant doit être sécurisé avant toute exposition publique.

## 2. Architecture technique

**Langage :** Python
**Framework MCP :** FastMCP, package `mcp` version 1.30.0

**Point d'entrée :** `mcp_server.py`
**Implémentation principale :** `src/mcp/server.py`

Le serveur s'appuie notamment sur :

- `src/clients/` : récupération des données externes.
- `src/analysis/` : traitements scientifiques.
- `src/ai/` : intégration Gemini et validation.
- `src/storage/` : stockage local.
- `src/provenance/` : traçabilité.
- `src/reporting/` : génération de rapports.

## 3. Outils MCP

Le serveur expose actuellement 12 outils :

1. `search_neuroscience_literature`
2. `search_diseases`
3. `get_disease_molecules`
4. `search_clinical_trials`
5. `research_molecule`
6. `search_molecule_chembl`
7. `get_molecule_mechanisms`
8. `get_biological_target`
9. `get_molecule_bioactivities`
10. `generate_pharmacology_report`
11. `generate_integrated_research_report`
12. `analyze_scientific_evidence_with_gemini`

Ces outils ont été confirmés par une session de découverte MCP.

Leur présence ne constitue pas une validation fonctionnelle exhaustive de chacun d'eux.

## 4. Transports pris en charge

### 4.1. stdio

Transport destiné à la communication locale entre un client MCP et un processus serveur.

**Statut :** testé localement.

### 4.2. Streamable HTTP

Transport HTTP utilisé pour permettre les échanges MCP sur un endpoint réseau.

**Endpoint local :** `http://127.0.0.1:8000/mcp`

**Statut :** testé avec succès en environnement local.

Les tests ont confirmé :

- La disponibilité du serveur HTTP.
- L'initialisation d'une session MCP.
- La découverte des 12 outils.
- L'invocation d'un outil.
- Le rejet contrôlé d'un paramètre invalide.

Le déploiement distant n'a pas encore été réalisé.

## 5. Configuration du serveur

Le lanceur `mcp_server.py` utilise les variables d'environnement suivantes :

| Variable | Fonction | Valeur locale par défaut |
|---|---|---|
| `MCP_TRANSPORT` | Choix du transport | `stdio` |
| `MCP_HOST` | Adresse d'écoute HTTP | `127.0.0.1` |
| `PORT` | Port HTTP | `8000` |

Le transport HTTP est activé lorsque :

`MCP_TRANSPORT=streamable-http`

La configuration locale doit conserver une adresse d'écoute limitée à la machine de développement.

## 6. Fonctionnement du protocole

Un client MCP compatible doit pouvoir :

1. Établir une connexion au serveur.
2. Initialiser une session MCP.
3. Découvrir les outils disponibles.
4. Transmettre des paramètres structurés.
5. Invoquer un outil.
6. Recevoir une réponse conforme au protocole.

Une erreur métier retournée dans le contenu d'un outil doit être distinguée d'une erreur du protocole MCP.

## 7. Sécurité actuelle

L'inspection locale de FastMCP 1.30.0 a confirmé :

**Protection DNS rebinding :** activée.

**Hôtes autorisés :**

- `127.0.0.1:*`
- `localhost:*`
- `[::1]:*`

**Origines autorisées :**

- `http://127.0.0.1:*`
- `http://localhost:*`
- `http://[::1]:*`

**Chemin HTTP :** `/mcp`

**Sessions :** avec état (`stateless_http=False`).

**Réponses JSON directes :** désactivées (`json_response=False`).

### Authentification

Aucun fournisseur d'authentification ni vérificateur de jetons n'est actuellement configuré.

La version installée de FastMCP expose les paramètres :

- `auth`
- `auth_server_provider`
- `token_verifier`

Leur disponibilité a été vérifiée, mais aucune configuration d'authentification n'a encore été implémentée ni testée.

Les protections d'hôtes et d'origines ne remplacent pas une authentification.

## 8. Exigences de sécurité pour le déploiement

**SEC-001 :** Exiger HTTPS pour les connexions distantes.

**SEC-002 :** Authentifier les clients autorisés avant l'accès aux outils.

**SEC-003 :** Refuser les requêtes non authentifiées.

**SEC-004 :** Limiter les origines et hôtes autorisés à la configuration du déploiement.

**SEC-005 :** Protéger les clés API et secrets par des variables d'environnement ou un gestionnaire de secrets.

**SEC-006 :** Ne jamais publier le fichier `.env`.

**SEC-007 :** Prévoir des limites de requêtes et des protections contre les abus.

**SEC-008 :** Éviter de divulguer des informations sensibles dans les journaux.

**SEC-009 :** Tester les erreurs d'authentification et les tentatives d'accès non autorisées.

**SEC-010 :** Vérifier que les contrôles scientifiques restent actifs dans l'environnement distant.

## 9. Exigences fonctionnelles

**MCP-001 :** Permettre l'initialisation d'une session MCP.

**MCP-002 :** Permettre la découverte des outils.

**MCP-003 :** Exposer les 12 outils scientifiques actuellement enregistrés.

**MCP-004 :** Accepter des paramètres structurés.

**MCP-005 :** Rejeter les paramètres invalides selon les règles des outils.

**MCP-006 :** Retourner des réponses compatibles MCP.

**MCP-007 :** Préserver les validations scientifiques lors des traitements Gemini.

**MCP-008 :** Permettre une configuration sécurisée des services externes.

**MCP-009 :** Prendre en charge le transport Streamable HTTP.

**MCP-010 :** Permettre une configuration d'authentification adaptée au déploiement.

**MCP-011 :** Maintenir la compatibilité du transport stdio.

**MCP-012 :** Permettre des tests d'intégration depuis un client MCP.

## 10. Tests d'acceptation

### Vérifications réussies

- [x] Compilation Python du serveur.
- [x] Importation de l'instance FastMCP.
- [x] Découverte des 12 outils.
- [x] Réussite de 15 tests automatisés.
- [x] Initialisation d'une session MCP HTTP.
- [x] Découverte des outils via HTTP.
- [x] Invocation d'un outil via HTTP.
- [x] Rejet de `max_records=0` sans appel Gemini.
- [x] Vérification de la configuration locale du serveur.
- [x] Vérification de la protection DNS rebinding.
- [x] Vérification de la disponibilité des paramètres d'authentification FastMCP.

### Vérifications restantes

- [ ] Authentification des clients distants.
- [ ] Refus vérifié des connexions non autorisées.
- [ ] Tests des limites de requêtes.
- [ ] Tests de sécurité des origines et des hôtes.
- [ ] Invocation valide de Gemini via MCP HTTP après restauration.
- [ ] Déploiement sur une infrastructure HTTPS.
- [ ] Validation depuis un client MCP distant.
- [ ] Vérification de la protection des secrets en production.
- [ ] Vérification des journaux et de la gestion des erreurs.

## 11. Résultats des tests locaux

**Date :** 4 novembre 2026 (mise à jour ; état historique du 29 octobre conservé)

**Tests automatisés :** 15 exécutés, 15 réussis.

**Outils MCP découverts :** 12.

**Transport HTTP :** Streamable HTTP.

**Adresse locale :** `127.0.0.1:8000`.

**Endpoint :** `/mcp`.

**Initialisation de session :** réussie.

**Découverte des outils :** réussie.

**Invocation HTTP :** réussie.

**Paramètre testé :** `max_records=0`.

**Résultat applicatif :** rejet attendu du paramètre invalide.

**Erreur protocolaire :** aucune lors de l'invocation MCP valide.

## 12. Stratégie de déploiement

Le déploiement devra être effectué progressivement :

1. Conserver la version locale validée.
2. Choisir une solution d'authentification compatible.
3. Ajouter les tests d'accès autorisé et refusé.
4. Préparer la configuration de production.
5. Déployer derrière HTTPS.
6. Configurer les variables d'environnement et les secrets.
7. Vérifier les restrictions réseau.
8. Tester les outils depuis un client distant.
9. Contrôler les journaux et les erreurs.
10. Confirmer la préservation des validations scientifiques.

Aucune URL publique ne doit être considérée comme opérationnelle avant validation réelle.

## 13. Documentation associée

- `SPEC-001` : architecture générale.
- `SPEC-002` : acquisition, stockage et traçabilité.
- `SPEC-003` : analyse pharmacologique.
- `SPEC-004` : Gemini et validation scientifique.
- `docs/architecture.md`
- `docs/mcp_tools.md`
- `docs/scientific_methodology.md`

## 14. Critères de validation finale

SPEC-005 sera considérée comme entièrement validée lorsque :

- Le serveur sera accessible via HTTPS.
- Les accès seront authentifiés et contrôlés.
- Les clients non autorisés seront rejetés.
- Les outils fonctionneront depuis un client distant.
- Les données et secrets seront protégés.
- Les validations scientifiques resteront actives.
- Les tests d'intégration et de sécurité auront été exécutés avec succès.

**Conclusion :** le serveur MCP de NeurohoraScope.AI est fonctionnel et testé localement avec les transports stdio et Streamable HTTP. Son exposition distante nécessite encore une authentification, des contrôles de sécurité et une validation en production.

---

## 15. Déploiement et validation distante — 4 novembre 2026

### Infrastructure effectivement déployée

- Dépôt : `https://github.com/alysonivone-cyber/NeurohoraScope.AI` ; branche `main` ; commit `1f7216f`.
- Hébergement : Render Free, Python 3.13.17 ; `start_render.py` importe `render_app.py`, application ASGI exécutée par Uvicorn.
- URL publique du MCP : **`https://neurohorascope-ai.onrender.com/mcp`** ; transport **Streamable HTTP sur HTTPS**.
- Déploiement `1f7216f` : **Deploy succeeded | Live**, 4 novembre 2026, 11:35:18 GMT+1 ; journaux « Application startup complete » et « Your service is live ».
- La racine `/` peut retourner HTTP 404 sans anomalie : le chemin fonctionnel est `/mcp`.
- Le service gratuit peut s'endormir et nécessiter plus de 50 secondes pour se réveiller.

### Tests réellement observés

1. Session MCP initialisée à distance via un client Python, `list_tools()` retourne **12 outils**.
2. Connecteur personnalisé Claude.ai configuré avec l'URL `/mcp`, transport HTTP Streamable, sans authentification ; connexion effective.
3. Les 12 outils ont été invoqués au niveau protocolaire : **11 exécutés**, tandis que `analyze_scientific_evidence_with_gemini` a renvoyé intentionnellement `status: disabled` en mode public.
4. Après le déploiement `1f7216f`, Claude a invoqué `search_neuroscience_literature` et reçu **trois publications** Parkinson avec titres, PMID et URL. Le serveur a donc été revalidé après le dernier déploiement.

### Sécurité réellement en place et écarts

- Configuration du mode démonstration : `MCP_PUBLIC_DEMO=true`, `MCP_REQUIRE_AUTH=false`. L'endpoint est **public et non authentifié** ; ne pas le décrire comme protégé par OAuth ou jeton Bearer.
- Gemini est **désactivé sur l'endpoint public** pour protéger le quota API. Le traitement Gemini a été testé séparément **en local**, avec une clé stockée en variable d'environnement.
- Le mode public répond au besoin pédagogique d'une URL MCP accessible à Claude, mais **ne satisfait pas SEC-002, SEC-003 et SEC-009** tels qu'énoncés pour un déploiement authentifié. Ces exigences doivent être qualifiées de *non applicables au mode démonstration public* ou *à réaliser pour un mode de production restreint*, sans les marquer comme réussies.
- Les limitations de débit, l'anti-abus, la revue des journaux et les contrôles d'accès du mode privé ne sont pas démontrés par les tests disponibles. Une exposition publique sans authentification nécessite une vigilance particulière sur l'abus des API publiques et la disponibilité.

### Critères d'acceptation du rendu pédagogique

- **Confirmé :** code dans un dépôt Git ; URL publique MCP ; serveur HTTP accessible ; découverte des outils ; appel réel depuis Claude ; données structurées (titre et URL).
- **Confirmé séparément :** analyse de données ChEMBL avec l'API Gemini en local, réponse validée.
- **À expliciter :** le flux « Gemini exécuté par Claude via le MCP distant » n'est pas démontré dans le mode public actuel. Le sujet du professeur représente une chaîne de traitement IA vers MCP ; le degré d'intégration attendu entre ces étapes devra être confirmé si une démonstration bout-en-bout est exigée.
- **Livrables explicitement demandés dans le PDF :** dépôt Git et URL publique du MCP, avant le 17 novembre 2026 à 23:59 CET. Aucune capture d'écran n'y est exigée.

---

## Mise à jour — 17 novembre 2026

- Le serveur public `https://neurohorascope-ai.onrender.com/mcp` reste en mode démonstration (`MCP_PUBLIC_DEMO=true`, `MCP_REQUIRE_AUTH=false`) ; le README le mentionne désormais comme démonstration publique.
- Dernier déploiement : commit `5db4f9a`, Live ; journaux : 18 maladies et 261 associations chargées.
- Les **12 outils** ont été réexécutés via le connecteur Claude : `analyze_scientific_evidence_with_gemini` renvoie toujours `status: disabled` en mode public, comme attendu. Les 11 autres ont répondu.
- La clé Gemini a été remplacée ; elle ne doit exister que dans les variables d'environnement Render, jamais dans le dépôt.
- Le premier appel après une période d'inactivité peut dépasser 50 secondes (offre gratuite Render).
- Inchangé : aucune authentification, appel Gemini de bout en bout depuis Claude non démontré.
