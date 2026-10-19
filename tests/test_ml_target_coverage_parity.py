"""Offline source parity and synthetic target-date conflict tests.

These are no substitute for compiled dbt and actual BigQuery sampling.
"""
from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sql_file(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").lower()


class MLTargetCoverageParity(unittest.TestCase):
    def test_training_coverage_and_audit_use_unambiguous_latest_date(self):
        paths = (
            "models/ml/ml_player_market_value_training.sql",
            "tests/assert_ml_training_row_coverage.sql",
            "analyses/audit_ml_valuation_event_grain_20261019.sql",
        )
        for path in paths:
            with self.subTest(path=path):
                source = sql_file(path)
                self.assertIn("count(distinct", source)
                self.assertIn("target_market_value_date desc", source)
                self.assertIn("target_market_value_eur", source)
                self.assertIn("season_market_value > 0", source)

    def test_coverage_requires_matching_canonical_player_date_and_eur(self):
        model = sql_file("models/ml/ml_player_market_value_training.sql")
        coverage = sql_file("tests/assert_ml_training_row_coverage.sql")
        self.assertIn("target.target_market_value_eur = valuations.market_value_in_eur", model)
        self.assertIn("t.target.target_market_value_eur = v.market_value_in_eur", coverage)
        self.assertIn("having count(distinct market_value_in_eur) = 1", coverage)
        self.assertIn("except distinct", coverage)
        self.assertIn("ml_player_market_value_training", coverage)

    def test_synthetic_latest_date_conflict_not_filled_from_older_date(self):
        with sqlite3.connect(":memory:") as db:
            db.execute(
                "create table target(player_id integer, season integer, "
                "target_date text, eur integer)"
            )
            db.executemany(
                "insert into target values (?,?,?,?)",
                [
                    (1, 2024, "2024-01-01", 100000),
                    (1, 2024, "2024-06-01", 200000),
                    (1, 2024, "2024-06-01", 300000),
                    (2, 2024, "2024-06-01", 250000),
                    (2, 2024, "2024-06-01", 250000),
                    (3, 2024, "2024-06-01", 0),
                ],
            )
            # Same COUNT(DISTINCT) and latest-date selection as BigQuery;
            # SQLite's ROW_NUMBER is used instead of BigQuery ARRAY_AGG.
            query = """
                with per_date as (
                    select player_id, season, target_date,
                      case when count(distinct eur) = 1 then max(eur) end
                        as target_eur
                    from target where eur > 0 group by 1,2,3
                ),
                latest as (
                    select *, row_number() over (
                        partition by player_id, season order by target_date desc
                    ) as rn
                    from per_date
                )
                select player_id, target_date, target_eur
                from latest where rn = 1 order by player_id
            """
            rows = db.execute(query).fetchall()
            self.assertEqual(
                rows,
                [(1, "2024-06-01", None), (2, "2024-06-01", 250000)],
            )
            # An earlier valid date must NOT silently stand in for
            # the most recent date whose EUR source observations conflict.

    def test_audit_reports_explicit_latest_date_conflicts(self):
        audit = sql_file("analyses/audit_ml_valuation_event_grain_20261019.sql")
        self.assertIn("conflicted_latest_player_season_targets", audit)
        self.assertIn("excluded_ambiguous_or_unmatched_targets", audit)


if __name__ == "__main__":
    unittest.main()
