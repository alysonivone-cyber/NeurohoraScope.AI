
"""Point d'entrée du serveur MCP NeurohoraScope.AI."""

import os

from src.mcp.server import mcp


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "streamable-http":
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8000"))

        mcp.settings.host = host
        mcp.settings.port = port

        print(
            f"NeurohoraScope.AI MCP HTTP: {host}:{port}",
            flush=True,
        )

        mcp.run(transport="streamable-http")

    elif transport == "stdio":
        mcp.run(transport="stdio")

    else:
        raise ValueError(
            f"Transport MCP non pris en charge : {transport}"
        )


if __name__ == "__main__":
    main()
