"""Guard the Workintech SQL test and snapshot-before-test sequencing."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027")


class TestMlCoverageAndSnapshotSequence(unittest.TestCase):
    def test_canonical_valuation_does_not_shadow_source_name(self):
        sql = (ROOT / "tests" / "assert_ml_training_row_coverage.sql").read_text("utf8")
        self.assertIn("max(market_value_in_eur) as canonical_market_value_eur", sql)
        self.assertIn("having count(distinct market_value_in_eur) = 1", sql)
        self.assertIn("v.canonical_market_value_eur", sql)
        self.assertNotIn("max(market_value_in_eur) as market_value_in_eur", sql)

    def test_snapshot_models_target_the_new_namespace(self):
        for name in ("snap_player_profiles.sql", "snap_club_profiles.sql"):
            with self.subTest(name=name):
                sql = (ROOT / "snapshots" / name).read_text("utf8")
                self.assertIn("target_schema=target.schema ~ '_snapshots'", sql)
                self.assertIn("strategy='check'", sql)

    def test_authorized_operator_script_runs_snapshots_before_all_tests(self):
        p = RECOVERY / "Start-WorkintechWarehouse.ps1"
        if not p.is_file():
            self.skipTest("Operator-local PowerShell recovery is not part of GitHub clone")
        script = p.read_text("utf-8-sig")
        self.assertLess(script.index("& $Dbt snapshot @Common"), script.index("& $Dbt test @Common"))
        self.assertIn("dbt focused regression tests", script)
        self.assertIn("if ($Phase -eq 'Verify') { $Layers=@() }", script)


if __name__ == "__main__":
    unittest.main()
