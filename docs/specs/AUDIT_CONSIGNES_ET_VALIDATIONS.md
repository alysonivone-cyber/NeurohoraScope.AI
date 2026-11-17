# Audit des SPEC — NeurohoraScope.AI (mis à jour le 17 novembre 2026)

## Exigences explicites du professeur

- Trois parties : collecte de données externes ; traitement structurant avec un service IA externe ; serveur MCP utilisé par un client IA.
- Sources : API ou datasets publics. Langage : Python ou JavaScript/TypeScript.
- Déploiement en ligne du MCP, sans exigence de design.
- Livrables explicitement cités : code sur un dépôt Git et URL publique MCP.
- Échéance : 17 novembre 2026 à 23:59 CET.
- **Aucune capture d'écran obligatoire n'est mentionnée.**

## État vérifié

| Point | Statut | Preuve disponible |
|---|---|---|
| Dépôt Git | Confirmé | `main`, commit `1909ae3` (17 nov. ; `1f7216f` le 4 nov.) |
| Serveur HTTPS Render | Confirmé | `/mcp`, déploiement Live du 17 novembre (commit `1909ae3`) |
| Client Claude distant | Confirmé | Recherche PubMed : trois publications avec PMID et URL |
| Outils MCP | 12 découverts | 12 outils exécutés le 17 nov. ; l'outil Gemini appelle Gemini en direct (`mode: live`) avec repli sur des données enregistrées |
| IA externe Gemini | Confirmé localement | HTTP 200, `status: success`, deux observations BTK |
| Données structurées par Gemini servies à Claude | Confirmé (17 nov.) | 55 publications enregistrées (11 maladies) ; `status: precomputed` en repli |
| Appel Gemini **en direct** par Claude sur Render | Confirmé (17 nov.) | `status: success`, `mode: live` pour Parkinson et la sclérose en plaques ; borné (30/jour, 3 publications, cache 1 h) |
| Authentification du MCP public | Non | Mode démonstration sans authentification |
| Tests exhaustifs de sécurité et scientifique | Non démontrés | À distinguer des scénarios réussis |

## Mise à jour du 17 novembre 2026

- Medicodex : 18 maladies et 261 associations (dont Parkinson, ajouté manuellement, et neuf maladies issues de ClinicalTrials.gov), champ `Source` par enregistrement, fichier de déploiement `deploy_data/medicodex.json`. Voir SPEC-002, section 14.
- Les affirmations « huit maladies / 195 associations » et « Parkinson absent » datent du 4 novembre et sont **historiques**.
- Clé Gemini remplacée ; ancienne clé révoquée.
- Étape IA ajoutée : Gemini structure des résumés PubMed, d'abord hors ligne (55 publications, 11 maladies enregistrées), puis en direct depuis le serveur MCP avec garde-fous (SPEC-004, section 15). Le schéma du professeur (données brutes, IA, données structurées, MCP, client) est suivi, y compris l'appel de l'IA depuis le serveur déployé.

## Attention à la lecture des SPEC

Les sections de tests datées du 29 octobre sont conservées comme **historique**. Les nouvelles sections « Mise à jour — 4 novembre 2026 » font foi pour les événements récents. Les cinq fichiers ne prétendent pas que tous les modules ont été testés : seuls les scénarios effectivement observés sont qualifiés de réussis.

## Liens du rendu

- Dépôt : https://github.com/alysonivone-cyber/NeurohoraScope.AI
- Endpoint MCP : https://neurohorascope-ai.onrender.com/mcp

## Point d'attention pédagogique

Le schéma du professeur montre un flux collecte → IA → MCP → client. Le 17 novembre, Gemini a été appelé en direct par le serveur MCP déployé à la demande de Claude (`mode: live`), avec repli sur les données enregistrées. Les limites (plafond quotidien, 11 maladies, 3 publications par appel) sont documentées dans SPEC-004, section 15.
