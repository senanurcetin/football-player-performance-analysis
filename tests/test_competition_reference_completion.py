"""Regression safeguards for incompletely covered Transfermarkt competition IDs.

The 2026-10-27 publisher archive has 65 reference rows, while 88,958 games
use five additional IDs. Enrich only these IDs with explicitly missing
metadata, rather than deleting 1,214 games or inventing competition facts.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "staging" / "stg_competitions.sql"


class TestCompetitionReferenceCompletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = MODEL.read_text(encoding="utf-8").lower()

    def test_publisher_is_still_authoritative_for_existing_rows(self):
        self.assertIn("{{ source('football_raw', 'competitions') }}", self.sql)
        self.assertIn("select * from publisher_competitions", self.sql)
        self.assertIn("union all", self.sql)

    def test_missing_ids_come_from_observed_games_not_a_hardcoded_list(self):
        self.assertIn("{{ ref('stg_games') }}", self.sql)
        self.assertIn("select distinct", self.sql)
        self.assertIn("publisher.competition_id is null", self.sql)
        self.assertIn("games.competition_id is not null", self.sql)

    def test_no_fabricated_country_subtype_or_club_counts(self):
        for field in ("competition_sub_type", "competition_type",
                      "country_name", "domestic_league_code", "confederation"):
            self.assertRegex(self.sql, r"cast\(null as string\) as " + re.escape(field))
        for field in ("country_id", "total_clubs"):
            self.assertRegex(self.sql, r"cast\(null as int64\) as " + re.escape(field))
        self.assertIn("unmapped competition", self.sql)

    def test_existing_powerbi_ten_column_contract_not_expanded(self):
        expected = ["competition_id", "competition_code", "competition_name",
                    "competition_sub_type", "competition_type", "country_id",
                    "country_name", "domestic_league_code", "confederation",
                    "total_clubs"]
        block = self.sql.split("union all")[-1]
        names = re.findall(r"(?m)^\s*(?:cast\(.+?\)|.+?)\s+as\s+([a-z_]+),?\s*$", block)
        self.assertEqual(names, expected[1:])
        self.assertIn("\n    competition_id,", block)


if __name__ == "__main__":
    unittest.main()
