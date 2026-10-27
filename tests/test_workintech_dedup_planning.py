"""Regression tests for Workintech duplicate-import migration planning.

The tests do not alter the repository PBIP or need a Power BI screenshot.
"""
from pathlib import Path
import importlib.util
import unittest

ROOT=Path(__file__).resolve().parents[1]
PBIP=ROOT/"powerbi"/"workintech-20261027"/"FootballPlayerAnalysis"

def load(name):
    path=ROOT/"scripts"/name
    spec=importlib.util.spec_from_file_location(name.removesuffix(".py"),path)
    module=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module

class WorkintechDedupPlanningRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.migration=load("plan_workintech_relationship_migration.py").plan(PBIP)

    def test_no_relationships_lost_from_classification(self):
        c=self.migration["counts"]
        self.assertEqual(c["all_relationships"],158)
        self.assertEqual(c["duplicate_source_related_relationships"],80)
        self.assertEqual(c["unaffected_relationships"],78)
        self.assertEqual(
            c["identical_pair_and_attributes"]+
            c["same_pair_different_attributes"]+
            c["extra_local_date_relationships"]+
            c["novel_non_date_relationships"],80)

    def test_conflicting_filter_directions_are_never_auto_merged(self):
        self.assertEqual(self.migration["counts"]["same_pair_different_attributes"],2)
        self.assertTrue(
            all("crossFilteringBehavior" in x["attribute_differences"]
                for x in self.migration["same_pair_different_attributes"]))
        self.assertTrue(self.migration["policy"]["never_discard_filter_direction_disagreement"])

    def test_local_date_and_novel_relationships_are_preserved_for_review(self):
        self.assertEqual(self.migration["counts"]["extra_local_date_relationships"],40)
        self.assertEqual(self.migration["counts"]["novel_non_date_relationships"],9)
        self.assertTrue(self.migration["policy"]["bulk_delete_automated"] is False)

    def test_three_isolated_candidate_tables_have_equal_physical_source_and_schema(self):
        pilot=load("pilot_workintech_safe_dedup.py")
        _,relationships,layout,hashes,check=pilot.profile(PBIP)
        self.assertEqual(len(check),3)
        self.assertTrue(all(x["relationship_references"]==0 and x["other_file_references"]==0 for x in check))
        self.assertTrue(all(x["matching_column_count"]>=17 for x in check))
        self.assertIn("relationship ",relationships)
        self.assertIn("diagrams",layout)
        self.assertIn("Model/definition/model.tmdl",hashes)

    def test_no_active_pbip_rewrite_enabled(self):
        policy=self.migration["policy"]
        self.assertTrue(policy["never_rewrite_active_owner_pbip_from_this_report"])
        self.assertFalse(policy["request_user_screenshots"])
        self.assertTrue(policy["require_actual_runtime_model_acceptance_before_production_promotion"])

if __name__=="__main__":
    unittest.main()
