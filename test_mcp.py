
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_tool(session, name, arguments):
    print("\n" + "=" * 60)
    print(f"TEST : {name}")
    print("=" * 60)

    try:
        result = await session.call_tool(
            name,
            arguments=arguments,
        )

        for content in result.content:
            if content.type == "text":
                print(content.text[:5000])

        if result.isError:
            print("\nERREUR : cet outil a échoué.")
        else:
            print("\nSUCCÈS : appel MCP terminé.")

    except Exception as error:
        print(f"\nERREUR : {error}")


async def main():
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        env=environment,
    )

    print("\nNEUROSCOPE.AI — MCP INTEGRATION TEST")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\nConnexion MCP réussie.")

            tools = await session.list_tools()

            print(f"\nOutils disponibles : {len(tools.tools)}")

            for tool in tools.tools:
                print(f" - {tool.name}")

            await test_tool(
                session,
                "search_diseases",
                {"keyword": "Alzheimer"},
            )

            await test_tool(
                session,
                "get_disease_molecules",
                {"disease_id": 1},
            )

            await test_tool(
                session,
                "search_neuroscience_literature",
                {
                    "disease": "Parkinson",
                    "max_results": 3,
                },
            )
             
            await test_tool(
                session,
                "search_clinical_trials",
                {
                    "disease": "Multiple Sclerosis",
                    "max_results": 5,
                    "intervention_type": "DRUG",
                    "phase": "PHASE3",
                    "status": "RECRUITING",
                },
            )

            await test_tool(
                session,
                "research_molecule",
                {
                    "molecule": "Orelabrutinib",
                    "disease": "Multiple Sclerosis",
                    "max_results": 5,
                },
            )  
            
            await test_tool(
                session,
                "search_molecule_chembl",
                {
                    "molecule": "Orelabrutinib",
                    "max_results": 5,
                },
            )

            await test_tool(
                session,
                "get_molecule_mechanisms",
                {
                    "chembl_id": "CHEMBL4650321",
                },
            )

            await test_tool(
                session,
                "get_biological_target",
                {
                    "target_chembl_id": "CHEMBL5251",
                },
            )

            await test_tool(
                session,
                "get_molecule_bioactivities",
                {
                    "molecule_chembl_id": "CHEMBL4650321",
                    "max_results": 5,
                },
            )

            await test_tool(
                session,
                "generate_pharmacology_report",
                {
                    "molecule_name": "Orelabrutinib",
                    "max_activities": 5,
                },
            )

            
            await test_tool(
                session,
                "generate_integrated_research_report",
                {
                    "molecule_name": "Orelabrutinib",
                    "disease": "Multiple Sclerosis",
                    "max_activities": 5,
                    "max_trials": 5,
                },
            )

if __name__ == "__main__":
    asyncio.run(main())
