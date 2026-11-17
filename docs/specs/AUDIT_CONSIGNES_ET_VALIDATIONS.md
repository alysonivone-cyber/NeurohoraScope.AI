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
| Dépôt Git | Confirmé | `main`, commit `5db4f9a` (17 nov. ; `1f7216f` le 4 nov.) |
| Serveur HTTPS Render | Confirmé | `/mcp`, déploiement Live du 17 novembre (commit `5db4f9a`) |
| Client Claude distant | Confirmé | Recherche PubMed : trois publications avec PMID et URL |
| Outils MCP | 12 découverts | 11 outils exécutés (revérifiés le 17 nov.), 1 outil Gemini volontairement désactivé en public |
| IA externe Gemini | Confirmé localement | HTTP 200, `status: success`, deux observations BTK |
| Gemini appelé par Claude sur Render | Non démontré | Désactivé par `MCP_PUBLIC_DEMO=true` |
| Authentification du MCP public | Non | Mode démonstration sans authentification |
| Tests exhaustifs de sécurité et scientifique | Non démontrés | À distinguer des scénarios réussis |

## Mise à jour du 17 novembre 2026

- Medicodex : 18 maladies et 261 associations (dont Parkinson, ajouté manuellement, et neuf maladies issues de ClinicalTrials.gov), champ `Source` par enregistrement, fichier de déploiement `deploy_data/medicodex.json`. Voir SPEC-002, section 14.
- Les affirmations « huit maladies / 195 associations » et « Parkinson absent » datent du 4 novembre et sont **historiques**.
- Clé Gemini remplacée ; ancienne clé à révoquer.

## Attention à la lecture des SPEC

Les sections de tests datées du 29 octobre sont conservées comme **historique**. Les nouvelles sections « Mise à jour — 4 novembre 2026 » font foi pour les événements récents. Les cinq fichiers ne prétendent pas que tous les modules ont été testés : seuls les scénarios effectivement observés sont qualifiés de réussis.

## Liens du rendu

- Dépôt : https://github.com/alysonivone-cyber/NeurohoraScope.AI
- Endpoint MCP : https://neurohorascope-ai.onrender.com/mcp

## Point d'attention pédagogique

Le schéma du professeur montre un flux collecte → IA → MCP → client. Le traitement Gemini et le MCP public sont chacun démontrés, **mais pas comme un appel Gemini de bout en bout depuis Claude**. Ne pas prétendre l'inverse. Si le professeur exige ce scénario exact, il faudra prévoir une démonstration contrôlée ou clarifier l'interprétation de la consigne.
