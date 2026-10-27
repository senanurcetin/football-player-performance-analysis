"""Read-only verification for the 34-source Workintech QA model's PBIR bindings."""
from pathlib import Path
import importlib.util
import json
import unittest

REPO=Path(__file__).resolve().parents[1]
AUDIT=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-full-dedup-qa-20261028\qa_field_and_filter_path_report.json")
SANDBOX=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-full-dedup-qa-20261028\FootballPlayerAnalysis")
def imported():
    script=REPO/"scripts/check_workintech_qa_visual_bindings.py"
    spec=importlib.util.spec_from_file_location("nexus_visual_bindings",script)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class TestWorkintechDedupVisualBindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not AUDIT.is_file() or not SANDBOX.is_dir():
            raise unittest.SkipTest("Isolated workintech static QA model unavailable")
        cls.data=json.loads(AUDIT.read_text("utf-8"))
    def test_report_all_visual_references_resolve(self):
        self.assertEqual(self.data["status"],"VISUAL_BINDINGS_PASS_FILTER_RUNTIME_STILL_REQUIRED")
        self.assertEqual(self.data["validated_visual_column_measure_refs"],243)
        self.assertEqual(self.data["distinct_bindings"],101)
        self.assertEqual(self.data["missing_table_or_field_references"],[])
    def test_qa_is_reduced_and_preserves_all_report_pages(self):
        self.assertEqual(self.data["model_tables"],77)
        pages=SANDBOX/"Report/definition/pages"
        self.assertEqual(len(list(pages.glob("*/page.json"))),13)
        self.assertEqual(len(list(pages.rglob("visual.json"))),308)
    def test_filter_graph_is_declared_but_not_runtime_certified(self):
        self.assertGreaterEqual(self.data["business_filter_graph_nodes"],25)
        self.assertGreaterEqual(self.data["business_filter_graph_components"],1)
        self.assertTrue(any("semantic engine" in s for s in self.data["limitations"]))
        self.assertTrue(any("new screenshots" in s for s in self.data["limitations"]))
if __name__=="__main__":
    unittest.main()
