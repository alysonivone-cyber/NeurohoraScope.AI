"""Application HTTP securisee pour NeurohoraScope.AI."""

import os

from starlette.middleware.authentication import AuthenticationMiddleware

from mcp.server.auth.middleware.auth_context import AuthContextMiddleware
from mcp.server.auth.middleware.bearer_auth import (
    BearerAuthBackend,
    RequireAuthMiddleware,
)

# Activer la protection HTTP avant tout import du package MCP.
os.environ["MCP_EXTERNAL_AUTH"] = "true"

from src.mcp.auth import NeurohoraTokenVerifier


def create_app():
    if os.getenv("MCP_REQUIRE_AUTH", "").lower() != "true":
        raise RuntimeError("Authentification MCP obligatoire.")

    token = os.getenv("MCP_ACCESS_TOKEN", "")

    if len(token) < 32:
        raise RuntimeError(
            "MCP_ACCESS_TOKEN doit contenir au moins 32 caracteres."
        )

    # Le serveur MCP existant est importe sans configuration OAuth.
    # Sa protection HTTP est appliquee par les middlewares ci-dessous.
    os.environ["MCP_EXTERNAL_AUTH"] = "true"
    from src.mcp.server import mcp

    app = mcp.streamable_http_app()

    # Protection explicite de la route MCP.
    for route in app.routes:
        if getattr(route, "path", None) == "/mcp":
            route.app = RequireAuthMiddleware(
                route.app,
                required_scopes=["mcp:tools"],
            )

    app.add_middleware(AuthContextMiddleware)
    app.add_middleware(
        AuthenticationMiddleware,
        backend=BearerAuthBackend(
            NeurohoraTokenVerifier()
        ),
    )

    return app


app = create_app()
