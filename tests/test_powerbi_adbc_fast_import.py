"""Genuine BigQuery ADBC v2 fast portfolio model source contract.

The 31-table version was checked on a separate authenticated Desktop QA clone.
This test checks source integrity; screenshots remain separately gated.
"""
from __future__ import annotations
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"scripts"/"optimize_powerbi_adbc_import.py"
spec=importlib.util.spec_from_file_location("pbi_fast_import",SRC)
assert spec and spec.loader
fast=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fast)

class FastPowerBIPBIP(unittest.TestCase):
    def test_no_broken_references_or_unused_two_million_row_tables(self):
        for edition in fast.EDITIONS:
            project=ROOT/"powerbi"/edition/"FootballPlayerAnalysis"
            definitions=project/"Model"/"definition"
            model=(definitions/"model.tmdl").read_text(encoding="utf-8-sig")
            relations=(definitions/"relationships.tmdl").read_text(encoding="utf-8-sig")
            with self.subTest(edition=edition):
                for table in fast.ALL_REMOVED:
                    self.assertFalse((definitions/"tables"/(table+".tmdl")).exists())
                    self.assertNotIn("ref table "+table,model)
                    self.assertNotRegex(relations,r"\b"+table+r"\.")
                self.assertEqual(len(json.loads(re.search(r"(?m)^annotation PBI_QueryOrder = (\[.*\])$",model).group(1))),31)
                self.assertEqual(fast.transform_project(project,apply=False)["adbc_v2_partitions_modified"],0)

    def test_31_production_bigquery_adbc_v2_imports_remain_real(self):
        tables=ROOT/"powerbi"/"workspace"/"FootballPlayerAnalysis"/"Model"/"definition"/"tables"
        imports=[]
        for file in tables.glob("*.tmdl"):
            text=file.read_text(encoding="utf-8-sig")
            if "GoogleBigQuery.Database" in text:
                imports.append(file.stem)
                self.assertIn(fast.ADBC,text)
                self.assertNotIn("UseStorageApi=true",text)
                self.assertIn("data-analiz-490513",text)
                self.assertIn("mode: import",text)
                self.assertNotIn("#table(",text)
        self.assertEqual(len(imports),31)

    def test_synthetic_test_fixture_separate_and_13_pages_unchanged(self):
        production=ROOT/"powerbi"/"workspace"/"FootballPlayerAnalysis"
        fixture=ROOT/"powerbi"/"offline-demo"/"FootballPlayerAnalysis"
        for project in (production,fixture):
            pages=project/"Report"/"definition"/"pages"
            self.assertEqual(len(list(pages.glob("*/page.json"))),13)
        for file in (fixture/"Model"/"definition"/"tables").glob("*.tmdl"):
            self.assertNotIn("GoogleBigQuery.Database",file.read_text(encoding="utf-8-sig"))
        self.assertIn("GoogleBigQuery.Database",(production/"Model"/"definition"/"tables"/"dim_players.tmdl").read_text())

if __name__=="__main__":
    unittest.main()
