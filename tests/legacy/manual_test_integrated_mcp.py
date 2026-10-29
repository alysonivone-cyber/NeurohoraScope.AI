
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
    )

    async with stdio_client(server_params) as (
        read,
        write,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "generate_integrated_research_report",
                arguments={
                    "molecule_name": "Orelabrutinib",
                    "disease": "Multiple Sclerosis",
                    "max_activities": 5,
                    "max_trials": 5,
                },
            )

            if result.isError:
                raise RuntimeError(
                    "MCP returned a tool error."
                )

            if result.structuredContent:
                report = result.structuredContent
            else:
                text_blocks = [
                    block.text
                    for block in result.content
                    if block.type == "text"
                ]

                if not text_blocks:
                    raise RuntimeError(
                        "No MCP report content returned."
                    )

                report = json.loads(text_blocks[0])

            # Some MCP versions wrap structured
            # tool results in a 'result' field.
            if (
                isinstance(report, dict)
                and "result" in report
                and isinstance(report["result"], dict)
            ):
                report = report["result"]

            
            print("\n=== MCP RESPONSE DIAGNOSTIC ===")
            print("Report type:", type(report).__name__)

            if isinstance(report, dict):
                print("Report keys:", list(report.keys()))

            print(
                json.dumps(
                    report,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )[:5000]
            )

            print("=== END DIAGNOSTIC ===\n")

            required_sections = [
                "pharmacology",
                "clinical_trials",
                "literature",
            ]

            for section in required_sections:
                assert section in report, (
                    f"Missing section: {section}"
                )

            assert (
                report["pharmacology"]["status"]
                == "success"
            )

            assert isinstance(
                report["clinical_trials"]["studies"],
                list,
            )

            assert isinstance(
                report["literature"]["publications"],
                list,
            )

            print(
                "\nNEUROSCOPE.AI - INTEGRATED MCP TEST\n"
            )

            print("MCP connection: OK")
            print("ChEMBL: OK")
            print("ClinicalTrials.gov: OK")
            print("PubMed: OK")

            print(
                "Clinical studies:",
                report["clinical_trials"]["relevant_count"],
            )

            print(
                "PubMed publications:",
                report["literature"]["returned_count"],
            )

            print(
                "\nSUCCESS: Three-source MCP report validated."
            )


if __name__ == "__main__":
    asyncio.run(main())
