# NeurohoraScope.AI — Architecture logicielle

**Version :** 1.1
**Mise à jour :** 29 octobre 2026
**Statut :** architecture locale vérifiée ; déploiement distant en attente

## 1. Présentation du projet

NeurohoraScope.AI est une application Python de recherche exploratoire en neuropharmacologie computationnelle. Elle rassemble la recherche bibliographique, les données pharmacologiques moléculaires, les informations relatives aux essais cliniques, les analyses scientifiques, les rapports et l'interprétation assistée par intelligence artificielle.

Le projet distingue les observations expérimentales, les analyses dérivées et les interprétations produites par IA. Il ne constitue ni un dispositif de décision clinique ni un système de recommandation thérapeutique.

## 2. Organisation modulaire

```text
NeurohoraScope.AI/
├── src/
│   ├── ai/
│   ├── analysis/
│   ├── clients/
│   ├── mcp/
│   ├── provenance/
│   ├── reporting/
│   └── storage/
├── tests/
├── docs/
│   └── specs/
├── data/
├── reports/
├── main.py
└── mcp_server.py
```

### 2.1. Acquisition des données — `src/clients/`

Ce package regroupe les interfaces de récupération des données de PubMed, ChEMBL et ClinicalTrials.gov.

### 2.2. Analyse scientifique — `src/analysis/`

Les modules identifiés concernent les activités pharmacologiques, les cibles biologiques, les comparaisons moléculaires, la sélectivité, la classification des essais, leur comparabilité, l'évaluation des preuves, les lacunes documentaires et les rapports intégrés. Leur présence dans le dépôt ne signifie pas que chaque traitement a été validé individuellement.

### 2.3. Intelligence artificielle — `src/ai/`

Ce package contient l'intégration Gemini et les contrôles de cohérence scientifique. Le processeur applique une comparaison déterministe des observations expérimentales et une validation sémantique ciblée des formulations « sub-nanomolar ». Ces contrôles ne garantissent pas l'exactitude de toutes les interprétations générées.

### 2.4. Stockage — `src/storage/`

Ce package contient notamment la gestion SQLite, l'importation Medicodex, le cache ChEMBL, le suivi de fraîcheur et des versions du cache, ainsi que des modules de surveillance des modifications de données.

### 2.5. Provenance — `src/provenance/`

Les modules concernent la provenance des activités et des données, le journal des modifications scientifiques et l'audit d'intégrité. Leur couverture opérationnelle complète reste à vérifier.

### 2.6. Rapports — `src/reporting/`

Ce package rassemble les modules de production et d'exportation de rapports scientifiques, notamment aux formats Markdown et PDF. Les résultats produits nécessitent des vérifications ciblées.

### 2.7. Serveur MCP — `src/mcp/server.py`

Ce module constitue l'implémentation principale du serveur FastMCP. Le fichier racine `mcp_server.py` sert de lanceur et de point d'entrée de compatibilité. Le serveur enregistre actuellement **12 outils MCP**.

## 3. Points d'entrée

- **`main.py` :** point d'entrée principal de l'application.
- **`mcp_server.py` :** lanceur du serveur MCP, avec transports `stdio` et `streamable-http`.
- **`src/ai/gemini_scientific_processor.py` :** processeur scientifique Gemini pouvant lire `reports/exact_activity_matches.json` et produire `reports/gemini_scientific_analysis.json`.

## 4. Imports et responsabilités

Les imports internes doivent rester cohérents avec l'organisation en packages, notamment sous la forme `from src.analysis...`. La logique principale doit rester dans les packages de `src/`, sans duplication dans les lanceurs de compatibilité.

## 5. Interface MCP

Les 12 outils couvrent la littérature biomédicale, les maladies, les associations maladie-molécule, les essais cliniques, les recherches moléculaires ChEMBL, les mécanismes d'action, les cibles, les bioactivités, les rapports pharmacologiques, les rapports intégrés et l'analyse Gemini.

Le registre détaillé figure dans `docs/mcp_tools.md`.

## 6. Transports et tests locaux

### 6.1. `stdio`

Transport de communication entre un client MCP local et le processus serveur. **Statut : testé localement.**

### 6.2. Streamable HTTP

**Adresse locale :** `http://127.0.0.1:8000/mcp`

Un client MCP compatible a pu initialiser une session, découvrir les 12 outils et invoquer un outil en recevant la réponse de validation attendue pour un paramètre invalide. **Statut : testé localement.**

Ces résultats ne constituent pas une validation d'un déploiement distant.

## 7. Sécurité

La configuration locale utilise l'interface de boucle locale et active la protection contre le DNS rebinding. Aucun fournisseur d'authentification ni vérificateur de jeton n'est actuellement configuré.

Le serveur ne doit pas être exposé publiquement dans cet état. Un déploiement distant nécessitera HTTPS, une authentification appropriée, des restrictions d'accès, la protection des secrets et des tests de sécurité.

## 8. Garanties et limites scientifiques

Le système doit préserver les mesures expérimentales d'origine, séparer les observations des interprétations IA, éviter d'assimiler l'activité *in vitro* à une efficacité clinique et signaler les limites des comparaisons entre essais différents.

La validation Gemini vérifie certains champs expérimentaux et une catégorie précise de formulation trompeuse. Elle ne remplace ni l'examen critique des sources ni la validation scientifique indépendante.

## 9. État des vérifications au 29 octobre 2026

| Vérification | Résultat |
|---|---|
| Suite automatisée Python | 15 tests réussis |
| Outils MCP enregistrés | 12 outils découverts |
| Communication MCP locale `stdio` | Testée |
| Initialisation d'une session Streamable HTTP | Réussie |
| Découverte des outils via HTTP | Réussie |
| Invocation d'un outil via HTTP | Réussie |
| Validation sémantique Gemini ciblée | 4 tests réussis |
| Authentification distante | Non configurée |
| Déploiement public HTTPS | Non réalisé |

La réussite des tests existants ne démontre pas une couverture exhaustive de tous les modules.

## 10. Travaux restants

- Vérifier individuellement les traitements scientifiques critiques.
- Étendre les tests d'intégration et de gestion des erreurs.
- Contrôler les rapports et leurs informations de provenance.
- Réexécuter une requête Gemini valide via le serveur HTTP restauré.
- Implémenter l'authentification et les contrôles d'accès distants.
- Effectuer les tests de sécurité avant tout déploiement public.

## 11. Documents associés

- `docs/mcp_tools.md`
- `docs/scientific_methodology.md`
- `docs/specs/SPEC-001-architecture-generale.md`
- `docs/specs/SPEC-002-acquisition-stockage-tracabilite.md`
- `docs/specs/SPEC-003-analyse-pharmacologique.md`
- `docs/specs/SPEC-004-gemini-mcp.md`
- `docs/specs/SPEC-005-serveur-mcp.md`

## 12. Conclusion

NeurohoraScope.AI possède une architecture Python modulaire combinant acquisition biomédicale, analyse pharmacologique, rapports scientifiques, interprétation Gemini et interopérabilité MCP. Le fonctionnement local du serveur et la découverte de ses outils ont été vérifiés. La validation scientifique exhaustive et la sécurisation d'un déploiement distant restent à réaliser.
