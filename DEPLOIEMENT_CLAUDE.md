# NeurohoraScope.AI — connexion Claude / Render

## Correctif de structure
Le ZIP d’origine ne contenait pas `src/mcp/server.py` (seulement `server.py.txt`). Ce fichier a été restauré.

## Option A — Démonstration Claude.ai sans jeton (la plus simple)
Dans **Render > Environment**, configurer :
- `MCP_PUBLIC_DEMO=true`
- `MCP_PUBLIC_URL=https://neurohorascope-ai.onrender.com/mcp`
- `MCP_REQUIRE_AUTH=false` (le mode démo le force aussi en mémoire)

Enregistrer et déployer le commit corrigé. Dans Claude.ai, ajouter un connecteur MCP distant HTTP Streamable vers `https://neurohorascope-ai.onrender.com/mcp` avec **Authentication: None**. La disponibilité des connecteurs dépend du compte Claude.

**Attention : mode public non authentifié.** Toute personne connaissant l’URL peut appeler les outils scientifiques, y compris des recherches externes. L'outil Gemini est désactivé dans ce mode pour protéger la clé et les quotas. N’utiliser que temporairement pour une démonstration contrôlée. Éviter les données privées. Pour la production, préférer OAuth ou un contrôle d'accès compatible avec le client.

## Option B — Bearer (mode sécurisé conservé)
Dans Render : `MCP_PUBLIC_DEMO=false`, `MCP_REQUIRE_AUTH=true`, `MCP_ACCESS_TOKEN=<secret long>`, `MCP_PUBLIC_URL=https://neurohorascope-ai.onrender.com/mcp`. Ce mode exige un client qui envoie le header Authorization. Claude.ai ne propose pas nécessairement ce champ.

## Test de la connexion
Une fois le déploiement Live, vérifier via un client MCP `initialize` puis `tools/list`, puis appeler `search_diseases` et `search_neuroscience_literature`. Une requête GET dans le navigateur n’est pas un test MCP fiable. Un 401 en mode public indique que l’ancien déploiement ou une autre couche d’authentification est toujours active.

## Sécurité
Le ZIP d'origine contenait `.env` : il a été exclu. Si ce ZIP a été partagé ou commité publiquement, faire tourner les clés concernées et vérifier l’historique Git. Le dossier `.venv` a aussi été exclu.
