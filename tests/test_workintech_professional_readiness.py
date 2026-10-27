"""Workintech PBIP/source risk gates (offline; no Desktop screenshots)."""
from __future__ import annotations
from pathlib import Path
import importlib.util
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"audit_workintech_semantic_model.py"
PBIP=ROOT/"powerbi"/"workintech-20261027"/"FootballPlayerAnalysis"


def load_module():
    spec=importlib.util.spec_from_file_location("audit_workintech_semantic_model",SCRIPT)
    module=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class TestWorkintechProfessionalReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=load_module().assess(PBIP)

    def test_governed_sources_and_layout_are_preserved(self):
        self.assertEqual(self.audit["governed_table_count"],31)
        self.assertEqual(self.audit["pages"],13)
        self.assertEqual(self.audit["visuals"],308)
        self.assertEqual(self.audit["structural_errors"],[])

    def test_duplicate_physical_tables_are_flagged_not_removed(self):
        self.assertEqual(self.audit["duplicate_physical_source_import_count"],31)
        self.assertEqual(self.audit["additional_unique_import_count"],3)
        self.assertEqual(self.audit["all_bigquery_import_count"],65)
        self.assertEqual(len(self.audit["extra_tables"]),34)
        self.assertEqual(self.audit["status"],"RELEASE_HOLD_SEMANTIC_CONSOLIDATION")
        self.assertTrue(all(not x["safe_to_delete_automatically"]
                            for x in self.audit["extra_tables"]))

    def test_extras_reference_existing_relationships(self):
        self.assertGreaterEqual(self.audit["extra_imports_referenced_by_relationships"],28)
        self.assertIn(
            "EXTRA_IMPORTS_HAVE_RELATIONSHIPS",
            {f["code"] for f in self.audit["findings"]},
        )

    def test_future_transfers_not_used_as_completed_outcomes(self):
        src=(ROOT/"models"/"marts"/"fct_transfer_fixed_horizon_outcomes.sql").read_text("utf8")
        annotated=(ROOT/"models"/"marts"/"fct_transfer_market_value_analysis.sql").read_text("utf8")
        self.assertIn("where not is_future_transfer",src.lower())
        self.assertIn("transfer_date > current_date() as is_future_transfer",annotated.lower())
        success=(ROOT/"models"/"marts"/"fct_transfer_success_labels.sql").read_text("utf8")
        self.assertIn("from {{ ref('fct_transfer_fixed_horizon_outcomes') }}",success)

    def test_ml_positive_targets_enforced_at_source(self):
        training=(ROOT/"models"/"ml"/"ml_player_market_value_training.sql").read_text("utf8")
        self.assertIn("market_value_in_eur > 0",training)
        self.assertIn("when count(distinct market_value_in_eur) = 1",training)

    def test_quality_tools_are_read_only(self):
        q=(ROOT/"scripts"/"profile_workintech_source_quality.py").read_text("utf8")
        self.assertIn('duckdb.connect(":memory:")',q)
        self.assertNotIn("gcloud",q)
        self.assertNotIn("Start-Process",q)
        self.assertNotIn("Get-Process",q)


if __name__=="__main__":
    unittest.main()
