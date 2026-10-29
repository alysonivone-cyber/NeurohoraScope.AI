"""Static offline tests that do not require the MCP SDK or network access."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageStructureTests(unittest.TestCase):
    def test_mcp_tool_registration_is_preserved(self):
        tree = ast.parse((ROOT / 'src/mcp/server.py').read_text(encoding='utf8'))
        found = set()
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                if any(isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                       and dec.func.attr == 'tool' and isinstance(dec.func.value, ast.Name)
                       and dec.func.value.id == 'mcp' for dec in node.decorator_list):
                    found.add(node.name)
        expected = {
            'search_neuroscience_literature', 'search_diseases',
            'get_disease_molecules', 'search_clinical_trials',
            'research_molecule', 'search_molecule_chembl',
            'get_molecule_mechanisms', 'get_biological_target',
            'get_molecule_bioactivities', 'generate_pharmacology_report',
            'generate_integrated_research_report',
            "analyze_scientific_evidence_with_gemini",
        }
        self.assertEqual(found, expected)

    def test_all_internal_absolute_src_imports_resolve(self):
        modules = {'.'.join(p.relative_to(ROOT).with_suffix('').parts)
                   for p in ROOT.rglob('*.py') if '__pycache__' not in p.parts}
        for path in ROOT.rglob('*.py'):
            if '__pycache__' in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding='utf8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('src.'):
                    with self.subTest(file=str(path.relative_to(ROOT)), module=node.module):
                        self.assertTrue(any(m == node.module or m.startswith(node.module + '.') for m in modules))


if __name__ == '__main__':
    unittest.main()
