"""Guard win-rate scale compatibility between warehouse, production PBIP and demo.

This source-only test cannot verify that a connected BigQuery refresh succeeds.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMDL = ("FootballPlayerAnalysis/Model/definition/tables/"
        "fct_club_performance.tmdl")


class ClubWinRateScaleTests(unittest.TestCase):
    def test_warehouse_emits_percentage_points(self):
        sql = (ROOT / "models" / "intermediate" /
               "int_club_performance_summary.sql").read_text(encoding="utf-8-sig")
        self.assertIn("safe_divide(", sql.lower())
        self.assertRegex(
            sql.lower(),
            r"\)\s*\*\s*100\s*,\s*2\s*\)\s+as\s+win_rate",
            "BigQuery source contract must be updated if upstream switches to ratios",
        )

    def test_production_normalizes_only_win_rate_for_percent_display(self):
        source = (ROOT / "powerbi" / "workspace" / TMDL).read_text(
            encoding="utf-8-sig")
        self.assertIn("formatString: 0.0%", source)
        self.assertIn("GoogleBigQuery.Database([UseStorageApi=false])", source)
        self.assertIn('fct_club_performance_Table = football_mart_Schema{[Name="fct_club_performance",Kind="Table"]}[Data],', source)
        self.assertEqual(source.count("Table.TransformColumns("), 1)
        self.assertIn('{"win_rate", each if _ = null then null else Number.From(_) / 100, type nullable number}', source)
        self.assertIn('in\n\t\t\t\t    #"Win Rate Fraction"', source)
        self.assertEqual(40.0 / 100, 0.4)

    def test_demo_rows_are_already_fractions_and_must_not_be_rescaled(self):
        source = (ROOT / "powerbi" / "offline-demo" / TMDL).read_text(
            encoding="utf-8-sig")
        self.assertIn("formatString: 0.0%", source)
        self.assertIn("#table(", source)
        self.assertNotIn("Win Rate Fraction", source)
        rows = [line.strip() for line in source.splitlines()
                if re.match(r'^\{\d+,\s*"Demo ', line.strip())]
        self.assertEqual(len(rows), 6)
        for row in rows:
            cols = row.strip(" {},").split(",")
            matches, wins, ratio = int(cols[3]), int(cols[4]), float(cols[10])
            self.assertGreater(matches, 0)
            self.assertGreaterEqual(ratio, 0)
            self.assertLessEqual(ratio, 1)
            self.assertAlmostEqual(ratio, wins / matches, places=4)


if __name__ == "__main__":
    unittest.main()
