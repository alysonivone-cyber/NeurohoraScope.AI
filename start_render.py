"""Demarrage de NeurohoraScope.AI sur Render."""

import os

import uvicorn


def main():
    if os.getenv("MCP_REQUIRE_AUTH", "").lower() != "true":
        raise RuntimeError(
            "Authentification obligatoire sur Render."
        )

    if len(os.getenv("MCP_ACCESS_TOKEN", "")) < 32:
        raise RuntimeError(
            "MCP_ACCESS_TOKEN doit contenir au moins 32 caracteres."
        )

    from src.storage.medicodex_import import DATA_FILE, import_medicodex

    if DATA_FILE.is_file():
        print("Initialisation des donnees Medicodex...", flush=True)
        import_medicodex()
    else:
        print(
            "Medicodex absent : demarrage sans import Medicodex.",
            flush=True,
        )

    print("Demarrage du serveur MCP HTTP securise...", flush=True)

    # L'application est chargee apres les verifications.
    from render_app import app

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
