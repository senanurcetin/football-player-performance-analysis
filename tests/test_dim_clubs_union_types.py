"""Ensure historical club UNION values preserve BigQuery types."""
from pathlib import Path
import re
import unittest

SQL = (Path(__file__).resolve().parents[1] / "models" / "marts" / "dim_clubs.sql").read_text(encoding="utf8")
HISTORICAL = SQL.split("combined_clubs as (", 1)[1].split("from historical_clubs", 1)[0]


class TestDimClubsUnionTypes(unittest.TestCase):
    def test_numeric_historical_fallbacks_are_typed(self):
        expected = {
            "total_market_value": "float64",
            "squad_size": "int64",
            "average_age": "float64",
            "foreigners_number": "int64",
            "foreigners_percentage": "float64",
            "national_team_players": "int64",
            "stadium_seats": "int64",
        }
        for column, datatype in expected.items():
            with self.subTest(column=column):
                self.assertIn(f"cast(null as {datatype}) as {column}", HISTORICAL)

    def test_never_cast_numeric_market_value_to_string(self):
        self.assertNotIn("cast(null as string) as total_market_value", HISTORICAL)

    def test_powerbi_club_column_order_unchanged(self):
        expected = [
            "club_code", "domestic_competition_id", "total_market_value",
            "squad_size", "average_age", "foreigners_number",
            "foreigners_percentage", "national_team_players", "stadium_name",
            "stadium_seats", "net_transfer_record",
        ]
        aliases = re.findall(
            r"(?m)^\s*cast\(null as [a-z0-9]+\) as ([a-z_]+),?\s*$",
            HISTORICAL,
        )
        self.assertEqual(aliases, expected)
        self.assertIn("'historical_reference' as club_record_type", HISTORICAL)


if __name__ == "__main__":
    unittest.main()
