# NeuroScope.AI

Computational neuropharmacology research prototype combining **ChEMBL**, **PubMed**, **ClinicalTrials.gov**, scientific evidence summaries, **Gemini** interpretation, and an **MCP server**.

**Research use only.** IC50 measurements, publication counts and trial registrations do **not** establish comparative clinical efficacy, safety or treatment recommendations. Comparisons across assays require explicit experimental comparability checks.

## Installation (Windows / PowerShell)

From the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The included `requirements.txt` was converted from a Windows UTF-16 export to UTF-8. Some pinned versions may need adjusting for your Python version. `google-genai`, `reportlab`, and `PyMuPDF` were added for modules already present in the project.

To use Gemini, create a local `.env` (do **not** commit it):

```text
GEMINI_API_KEY=YOUR_KEY_HERE
GEMINI_MODEL=gemini-3.1-flash-lite
```

## Run MCP

From the project root:

```powershell
.\.venv\Scripts\python.exe mcp_server.py
```

Default transport is stdio. To start streamable HTTP, set `MCP_TRANSPORT=streamable-http` in the process environment and run the same entry point. The standard MCP path is typically `/mcp`; verify actual host, port, routing, and public accessibility before sharing a URL. **This archive has not been deployed.**

## Gemini processing

```powershell
.\.venv\Scripts\python.exe -m src.ai.gemini_config
.\.venv\Scripts\python.exe -m src.ai.gemini_scientific_processor
```

Gemini output is checked against source experimental records (molecule, target, assay and IC50) before writing its report. The natural-language interpretation still requires human scientific review. API usage requires a valid key and internet access.

## Offline tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe -m compileall -q src main.py mcp_server.py
```

Historical interactive/network test scripts are retained under `tests/legacy/` as `manual_test_*.py`. They are **not** automatically run by the offline test command; several make real network calls or require a running MCP server.

## Project layout

- `src/analysis/`: evidence assessment, molecule and assay comparisons, pharmacological research.
- `src/clients/`: ChEMBL, PubMed, ClinicalTrials.gov clients.
- `src/ai/`: Gemini configuration, processor and deterministic source-data validation.
- `src/storage/`: SQLite helpers, ChEMBL cache and versioning.
- `src/provenance/`: source tracking, change logs and integrity audits.
- `src/reporting/`: PDF, Markdown and research exports.
- `src/mcp/server.py`: canonical MCP tools; `mcp_server.py` is a compatible root launcher.
- `main.py`: existing standalone entry point; `database.py`: compatibility import wrapper.
- `tests/`: offline regression tests and manual legacy scripts.
- `reports/`, `cache/`, `data/`: preserved scientific outputs and datasets supplied with the archive.

Run scripts using `python -m src.<package>.<module>` from the project root. Paths to `reports/` and `cache/` are currently relative to the working directory.

For further details see `docs/architecture.md`, `docs/scientific_methodology.md`, and `docs/mcp_tools.md`.

## Scope and remaining work

This is a **structural refactor**, not a finished production deployment. Local Python compilation and offline regression tests have been performed, but live MCP protocol sessions, ChEMBL/PubMed/ClinicalTrials.gov calls, Gemini API calls, and remote deployment need to be verified in the target environment. A Gemini-powered MCP tool has **not yet** been registered; the processor remains a separate validated workflow.
