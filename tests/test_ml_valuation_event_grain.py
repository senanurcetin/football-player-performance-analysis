"""Run actual canonical valuation CTE against SQLite synthetic fixtures.

Credential-free; this does not compile BigQuery or assert warehouse execution.
The same BigQuery-independent CASE/COUNT DISTINCT/GROUP BY semantics can be
executed by SQLite, catching accidental source-grain regressions.
"""
from __future__ import annotations

import re
import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRAINING = ROOT / "models/ml/ml_player_market_value_training.sql"
SCORING = ROOT / "models/ml/ml_player_market_value_scoring.sql"
REF = "{{ ref('stg_player_valuations') }}"


def canonical_cte(path: Path) -> str:
    sql = path.read_text(encoding="utf-8")
    match = re.search(
        r"valuation_events as \((.*?)\n\),\s*unambiguous_valuation_events as \((.*?)\n\),",
        sql,
        flags=re.S,
    )
    if match is None:
        raise AssertionError(f"Canonical player-date valuation CTE missing in {path}")
    if REF not in match.group(1):
        raise AssertionError(f"Canonical CTE must read staged valuation source: {path}")
    return (
        "with valuation_events as ("
        + match.group(1).replace(REF, "player_valuations")
        + "\n), unambiguous_valuation_events as ("
        + match.group(2)
        + "\n)"
    )


class ValuationEventGrain(unittest.TestCase):
    def setUp(self) -> None:
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.execute(
            "create table player_valuations("
            "player_id integer, valuation_date text, market_value_in_eur integer, "
            "player_club_domestic_competition_id text)"
        )

    def add(self, *rows: tuple[object, ...]) -> None:
        self.db.executemany(
            "insert into player_valuations values (?, ?, ?, ?)", rows
        )

    def actual_events(self) -> list[tuple[object, ...]]:
        query = canonical_cte(TRAINING) + (
            "\n select player_id, valuation_date, market_value_in_eur, "
            "player_club_domestic_competition_id "
            "from unambiguous_valuation_events order by player_id, valuation_date"
        )
        return self.db.execute(query).fetchall()

    def test_scoring_and_training_share_same_canonical_source_rules(self) -> None:
        self.assertEqual(canonical_cte(TRAINING), canonical_cte(SCORING))
        training = TRAINING.read_text(encoding="utf-8")
        scoring = SCORING.read_text(encoding="utf-8")
        self.assertIn("inner join unambiguous_valuation_events valuations", training)
        self.assertIn(
            "timeline_targets.target.target_market_value_eur = valuations.market_value_in_eur",
            training,
        )
        self.assertIn("left join unambiguous_valuation_events valuations", training)
        self.assertIn("left join unambiguous_valuation_events valuations", scoring)

    def test_exact_duplicates_collapse_to_one_valid_event(self) -> None:
        self.add((1, "2024-01-01", 120000, "D1"), (1, "2024-01-01", 120000, "D1"))
        self.assertEqual(self.actual_events(), [(1, "2024-01-01", 120000, "D1")])

    def test_conflicting_market_values_are_not_chosen_arbitrarily(self) -> None:
        self.add((1, "2024-02-01", 100000, "D1"),
                 (1, "2024-02-01", 200000, "D1"),
                 (1, "2024-01-01", 50000, "D1"))
        self.assertEqual(self.actual_events(), [(1, "2024-01-01", 50000, "D1")])

    def test_ambiguous_competition_is_null_but_value_remains(self) -> None:
        self.add((5, "2023-03-01", 700000, "D1"),
                 (5, "2023-03-01", 700000, "D2"))
        self.assertEqual(self.actual_events(), [(5, "2023-03-01", 700000, None)])

    def test_invalid_valuations_are_not_prior_baselines(self) -> None:
        self.add((2, "2023-01-01", None, "D1"),
                 (2, "2023-02-01", 0, "D1"),
                 (2, "2023-03-01", -10, "D1"),
                 (2, None, 200, "D1"),
                 (2, "2023-04-01", 300, "D1"))
        self.assertEqual(self.actual_events(), [(2, "2023-04-01", 300, "D1")])

    def test_training_target_match_has_exactly_one_join_row(self) -> None:
        self.add((1, "2022-08-01", 100000, "D1"),
                 (1, "2022-08-01", 100000, "D1"),
                 (1, "2023-08-01", 120000, "D1"),
                 (1, "2023-08-01", 150000, "D2"))
        self.db.execute(
            "create table targets(player_id integer, season integer, "
            "target_market_value_date text, target_market_value_eur integer)"
        )
        self.db.executemany(
            "insert into targets values (?, ?, ?, ?)",
            [(1, 2022, "2022-08-01", 100000),
             (1, 2023, "2023-08-01", 120000)],
        )
        query = canonical_cte(TRAINING) + """
        select t.player_id, t.season, t.target_market_value_eur
        from targets t
        inner join unambiguous_valuation_events v
          on t.player_id = v.player_id
          and t.target_market_value_date = v.valuation_date
          and t.target_market_value_eur = v.market_value_in_eur
        """
        self.assertEqual(self.db.execute(query).fetchall(), [(1, 2022, 100000)])


if __name__ == "__main__":
    unittest.main()
