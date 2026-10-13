"""Clubs offline M fixture must use numeric literals matching its typed columns.

Six quoted numeric literals for average_age and another six for
foreigners_percentage were producing six per-row Power Query conversion
errors on the synthetic dim_clubs import.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "powerbi/offline-demo/FootballPlayerAnalysis/Model/definition/tables/dim_clubs.tmdl"


class ClubFixtureTests(unittest.TestCase):
    def test_six_rows_have_numeric_age_and_foreigners_percentage(self):
        text = FILE.read_text(encoding="utf-8-sig")
        self.assertIn('#"average_age" = number', text)
        self.assertIn('#"foreigners_percentage" = number', text)
        lines = [line.strip() for line in text.splitlines() if re.match(r'^\s*\{\d+, "DCL-', line)]
        self.assertEqual(len(lines), 6)
        for line in lines:
            self.assertNotRegex(line, r'"\d+\.\d+"')
            values = re.findall(r',\s*(\d+\.\d+)\s*,', line)
            self.assertGreaterEqual(len(values), 1)
            self.assertIn('"current_profile"', line)


if __name__ == "__main__":
    unittest.main()
