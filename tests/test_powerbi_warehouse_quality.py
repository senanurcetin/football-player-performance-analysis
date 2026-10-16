"""Unit tests for opt-in, read-only BigQuery mart reconciliation.

Tests use injected output; they do not call BigQuery or require credentials.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "check_powerbi_warehouse_quality.py"
SPEC = importlib.util.spec_from_file_location("warehouse_quality", MODULE)
assert SPEC and SPEC.loader
quality = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quality)


def good_result():
    return {
        "club_performance": {
            "n": "3270", "unique_clubs": "3270", "invalid_matches": "0",
            "win_rate_mismatch": "0", "invalid_win_rate": "0",
            "min_win_rate": "0.0", "max_win_rate": "100.0",
        },
        "club_risk": {
            "n": "5714", "unique_clubs": "5714", "negative_transfers": "0",
            "fee_coverage_outside_pct": "0", "outcome_coverage_outside_pct": "0",
            "success_outside_pct": "0", "outcome_exceeds_population": "0",
        },
        "quality_audit": {
            "audit_rows": "17", "latest_audit_utc": "2026-06-21 10:50:30.267+00"
        },
    }


class BigQueryReadOnlyWarehouseContract(unittest.TestCase):
    def test_all_sql_is_fixed_select_and_has_exact_project_scoping(self):
        self.assertEqual(set(quality.QUERIES), {"club_performance", "club_risk", "quality_audit"})
        for name, sql in quality.QUERIES.items():
            with self.subTest(name=name):
                self.assertTrue(sql.startswith("SELECT "))
                self.assertIn("FROM " + chr(96) + "data-analiz-490513.football_mart.", sql)
                self.assertNotRegex(sql, r"(?i)\b(INSERT|MERGE|DELETE|UPDATE|DROP|CREATE|TRUNCATE|ALTER|CALL|EXPORT)\b")
        self.assertEqual(quality.LOCATION, "EU")
        self.assertEqual(quality.MAX_BYTES_BILLED, 10_485_760)

    def test_cli_uses_billing_ceiling_without_shell_and_hides_stderr(self):
        fake = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps([good_result()["club_performance"]]),
            stderr="token or local path warning"
        )
        with patch.object(quality.subprocess, "run", return_value=fake) as runner:
            result = quality.run_query(quality.QUERIES["club_performance"], "bq.cmd")
            self.assertEqual(result["n"], "3270")
            cmd = runner.call_args.args[0]
            self.assertIn("--maximum_bytes_billed=10485760", cmd)
            self.assertIn("--use_legacy_sql=false", cmd)
            self.assertIn("--format=json", cmd)
            self.assertEqual(cmd[0], "bq.cmd")
            self.assertFalse(runner.call_args.kwargs["check"])
            self.assertNotIn("shell", runner.call_args.kwargs)
        fake.returncode = 1
        fake.stderr = "private user token must not be leaked"
        with patch.object(quality.subprocess, "run", return_value=fake):
            with self.assertRaises(RuntimeError) as caught:
                quality.run_query(quality.QUERIES["club_risk"], "bq.cmd")
            self.assertNotIn("private user token", str(caught.exception))

    def test_verified_2026_historical_data_yields_warning_not_failure(self):
        report = quality.assess(
            good_result(), datetime(2026, 10, 16, 15, tzinfo=timezone.utc)
        )
        self.assertEqual(report["status"], "WARN")
        self.assertEqual(report["blocking_findings"], [])
        self.assertGreater(report["latest_audit_age_days"], 90)
        self.assertIn("historical", report["warnings"][0])
        self.assertEqual(report["portfolio_release"], "HOLD")
        self.assertEqual(report["desktop_refresh"], "NOT_VERIFIED")

    def test_fresh_audit_passes_without_misrepresenting_desktop(self):
        report = quality.assess(
            good_result(), datetime(2026, 6, 22, tzinfo=timezone.utc)
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["desktop_kpi_reconciliation"], "NOT_VERIFIED")

    def test_bad_club_rates_are_explicit_release_blockers(self):
        record = good_result()
        record["club_performance"]["win_rate_mismatch"] = "5"
        record["club_risk"]["success_outside_pct"] = "2"
        record["club_risk"]["unique_clubs"] = "5713"
        report = quality.assess(record, datetime(2026, 10, 16, tzinfo=timezone.utc))
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["blocking_findings"]), 3)

    def test_null_audit_has_explicit_coverage_warning(self):
        record = good_result()
        record["quality_audit"] = {"audit_rows": "0", "latest_audit_utc": None}
        report = quality.assess(record, datetime(2026, 10, 16, tzinfo=timezone.utc))
        self.assertEqual(report["status"], "WARN")
        self.assertIsNone(report["latest_audit_age_days"])

    def test_unparseable_audit_timestamp_is_rejected(self):
        record = good_result()
        record["quality_audit"]["latest_audit_utc"] = "not a timestamp"
        with self.assertRaises(ValueError):
            quality.assess(record, datetime(2026, 10, 16, tzinfo=timezone.utc))


if __name__ == "__main__":
    unittest.main()
