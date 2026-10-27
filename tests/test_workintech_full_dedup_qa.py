"""Static regression tests for isolated full Workintech PBIP deduplication.

The sandbox is optional: if absent on a new checkout, tests skip rather than
touching the owner's Power BI installation. Regenerate the sandbox using the
documented two-step recovery scripts before accepting a clean-model release.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util,json,unittest

ROOT=Path(__file__).resolve().parents[1]
RECOVERY=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027")
CANONICAL=ROOT/"powerbi/workintech-20261027/FootballPlayerAnalysis"
QA=RECOVERY/"powerbi-full-dedup-qa-20261028/FootballPlayerAnalysis"
AUDIT=RECOVERY/"powerbi-full-dedup-qa-20261028/full_dedup_static_audit.json"

def module():
    p=ROOT/"scripts/migrate_workintech_full_dedup_qa.py"
    spec=importlib.util.spec_from_file_location("full_dedup_qa",p)
    obj=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(obj)
    return obj

class FullDedupStaticQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine=module()
        if not QA.is_dir() or not AUDIT.is_file():
            raise unittest.SkipTest("Isolated Windows QA PBIP not available: runtime acceptance NOT implied.")
        cls.audit=json.loads(AUDIT.read_text("utf8"))
        cls.model=QA/"Model/definition"

    def test_fully_eliminated_redundant_physical_imports(self):
        files=list((self.model/"tables").glob("*.tmdl"))
        bq=[f for f in files if 'GoogleBigQuery.Database(' in f.read_text("utf8")]
        self.assertEqual(len(bq),34)
        self.assertFalse(any(f.stem.endswith(" (2)") for f in bq))
        self.assertEqual(self.audit["removed_in_earlier_sandbox"],3)
        self.assertEqual(self.audit["removed_in_this_sandbox"],28)
        self.assertEqual(self.audit["exclusive_autodate_tables_removed"],40)

    def test_all_87_relationships_reference_existing_columns_and_compatible_types(self):
        schema={f.stem:self.engine.cols(f.read_text("utf8"))
                for f in (self.model/"tables").glob("*.tmdl")}
        chunks=self.engine.REL_RE.findall((self.model/"relationships.tmdl").read_text("utf8"))
        self.assertEqual(len(chunks),87)
        ids=[]
        for chunk in chunks:
            (a,x),(b,y),opts=self.engine.pair(chunk)
            with self.subTest(from_table=a,to_table=b):
                self.assertIn(x,schema[a])
                self.assertIn(y,schema[b])
                self.assertEqual(schema[a][x],schema[b][y])
            ids.append(chunk.splitlines()[0])
        self.assertEqual(len(ids),len(set(ids)))

    def test_9_novel_business_relations_survive(self):
        self.assertEqual(self.audit["novel_business_relations_preserved_and_remapped"],9)
        self.assertEqual(self.audit["relations_before"],158)
        self.assertEqual(self.audit["relations_after"],87)
        self.assertEqual(self.audit["redundant_relations_removed"],31)
        self.assertEqual(self.audit["exclusive_autodate_relations_removed"],40)

    def test_report_pages_and_visuals_preserved(self):
        pages=QA/"Report/definition/pages"
        self.assertEqual(len(list(pages.glob("*/page.json"))),13)
        self.assertEqual(len(list(pages.rglob("visual.json"))),308)
        self.assertTrue(self.audit["other_file_hashes_identical"])

    def test_original_governed_measure_and_data_source_tmdls_unchanged(self):
        original=CANONICAL/"Model/definition/tables"
        after=self.model/"tables"
        for p in original.glob("*.tmdl"):
            if p.stem.endswith(" (2)") or p.stem.startswith("LocalDateTable_"):
                continue
            q=after/p.name
            self.assertTrue(q.exists(),p.name)
            self.assertEqual(p.read_bytes(),q.read_bytes(),p.name)
        self.assertFalse(self.audit["existing_dax_measure_definitions_changed"])

    def test_release_hold_and_no_screenshot_requirement(self):
        self.assertFalse(self.audit["powerbi_desktop_runtime_tested"])
        self.assertFalse(self.audit["owner_active_pbip_changed"])
        self.assertFalse(self.audit["canonical_repo_pbip_changed"])
        self.assertEqual(self.audit["screenshot_requests"],0)
        self.assertFalse(self.audit["status"].endswith("_RUNTIME_VERIFIED"))

if __name__=="__main__":
    unittest.main()
