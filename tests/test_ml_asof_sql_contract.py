"""Credential-free source checks for dbt's historical as-of integrity gates.

These tests inspect SQL contracts only. They never execute BigQuery and do
not replace running the two singular dbt tests against governed source tables.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AsOfIntegritySqlContracts(unittest.TestCase):
    def test_training_reference_and_temporal_constraints(self):
        sql = (ROOT / "tests/assert_ml_training_asof_integrity.sql").read_text(
            encoding="utf-8"
        ).lower()
        self.assertIn("ref('ml_player_market_value_training')", sql)
        for term in (
            "feature_last_appearance_date >= target_market_value_date",
            "previous_market_value_date >= target_market_value_date",
            "target_market_value_eur <= 0",
            "previous_market_value_eur < 0",
            "prior_valuation_count < 0",
            "days_since_previous_market_value < 1",
        ):
            with self.subTest(term=term):
                self.assertIn(term, sql)

    def test_scoring_reference_and_temporal_constraints(self):
        sql = (ROOT / "tests/assert_ml_scoring_asof_integrity.sql").read_text(
            encoding="utf-8"
        ).lower()
        self.assertIn("ref('ml_player_market_value_scoring')", sql)
        for term in (
            "prediction_as_of_date is null",
            "feature_last_appearance_date > prediction_as_of_date",
            "previous_market_value_date > prediction_as_of_date",
            "previous_market_value_eur < 0",
            "prior_valuation_count < 0",
            "days_since_previous_market_value < 0",
        ):
            with self.subTest(term=term):
                self.assertIn(term, sql)

    def test_both_singular_tests_are_read_only(self):
        for path in (
            ROOT / "tests/assert_ml_training_asof_integrity.sql",
            ROOT / "tests/assert_ml_scoring_asof_integrity.sql",
        ):
            with self.subTest(path=path.name):
                sql = re.sub(r"--[^\n]*", "", path.read_text(encoding="utf-8"))
                self.assertRegex(sql.lower(), r"\bselect\b")
                self.assertNotRegex(
                    sql.lower(),
                    r"\b(create|drop|alter|truncate|delete\s+from|"
                    r"insert\s+into|merge\s+into|update\s+)\b",
                )


if __name__ == "__main__":
    unittest.main()
