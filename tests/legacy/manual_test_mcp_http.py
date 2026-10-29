
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():
    print("\nNEUROSCOPE.AI — HTTP MCP TEST")

    async with streamable_http_client(SERVER_URL) as (
        read,
        write,
        _,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\nConnexion HTTP MCP réussie !")

            tools = await session.list_tools()

            print(f"\nOutils disponibles : {len(tools.tools)}")

            for tool in tools.tools:
                print(f" - {tool.name}")

            result = await session.call_tool(
                "search_diseases",
                arguments={"keyword": "Alzheimer"},
            )

            print("\nRésultat de la recherche :")

            for content in result.content:
                if content.type == "text":
                    print(content.text)

            if result.isError:
                print("\nERREUR : appel MCP échoué.")
            else:
                print("\nSUCCÈS : outil MCP accessible par HTTP.")


if __name__ == "__main__":
    asyncio.run(main())
