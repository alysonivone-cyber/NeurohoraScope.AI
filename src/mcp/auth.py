"""Authentification Bearer du serveur MCP NeurohoraScope.AI."""

import hmac
import os

from mcp.server.auth.provider import AccessToken, TokenVerifier


class NeurohoraTokenVerifier(TokenVerifier):
    """Valide un jeton statique configure dans l'environnement."""

    async def verify_token(self, token: str) -> AccessToken | None:
        expected_token = os.getenv("MCP_ACCESS_TOKEN", "")
        resource_url = os.getenv("MCP_PUBLIC_URL", "")

        if not expected_token or not resource_url or not token:
            return None

        if not hmac.compare_digest(token, expected_token):
            return None

        return AccessToken(
            token=token,
            client_id="neurohorascope-client",
            scopes=["mcp:tools"],
            resource=resource_url,
        )
