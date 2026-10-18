"""Deterministic credential-free unit tests for temporal and statistical audits."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ml_reliability import (  # noqa: E402
    grouped_mae_skill_bootstrap,
    interval_coverage_by_group,
    rolling_origin_season_splits,
)


class RollingOriginContract(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({"season": [2019, 2021, 2020, 2021, 2022, 2023, 2024]})

    def test_expanding_window_never_includes_test_or_future(self):
        folds = rolling_origin_season_splits(self.frame, min_train_seasons=3)
        self.assertEqual([year for year, _, _ in folds], [2022, 2023, 2024])
        for year, train, test in folds:
            self.assertTrue((self.frame.iloc[train]["season"] < year).all())
            self.assertTrue((self.frame.iloc[test]["season"] == year).all())
            self.assertFalse(set(train).intersection(test))

    def test_explicit_test_seasons_are_subset_only(self):
        folds = rolling_origin_season_splits(
            self.frame, min_train_seasons=3, test_seasons=[2024, 2022, 2022]
        )
        self.assertEqual([year for year, _, _ in folds], [2022, 2024])

    def test_invalid_seasons_and_ineligible_folds_rejected(self):
        bad_frames = [
            pd.DataFrame({"season": [2021, 2022, None, 2023, 2024]}),
            pd.DataFrame({"season": [2021, 2022, 2022.5, 2023, 2024]}),
            pd.DataFrame({"season": [2022] * 5}),
        ]
        for frame in bad_frames:
            with self.subTest(frame=frame.to_dict()):
                with self.assertRaises(ValueError):
                    rolling_origin_season_splits(frame, min_train_seasons=2)
        with self.assertRaises(ValueError):
            rolling_origin_season_splits(self.frame, min_train_seasons=3, test_seasons=[2021])
        with self.assertRaises(ValueError):
            rolling_origin_season_splits(self.frame, min_train_seasons=0)


class PlayerGroupedBootstrap(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({
            "player_id": [1, 1, 1, 2, 2, 3, 3, 4],
            "target_market_value_eur": [100, 130, 140, 200, 210, 300, 310, 400],
            "predicted_market_value_eur": [105, 130, 143, 208, 200, 305, 310, 392],
            "baseline_prediction_eur": [90, 115, 120, 180, 205, 280, 298, 385],
        })

    def test_reproducible_player_bootstrap_and_direction(self):
        a = grouped_mae_skill_bootstrap(self.frame, replicates=300, seed=23)
        b = grouped_mae_skill_bootstrap(self.frame, replicates=300, seed=23)
        self.assertEqual(a, b)
        self.assertEqual(a["player_groups"], 4)
        self.assertEqual(a["rows"], 8)
        self.assertGreater(a["mae_skill_vs_persistence_pct"], 0)
        self.assertLessEqual(a["bootstrap_ci_lower_pct"], a["bootstrap_ci_upper_pct"])

    def test_invalid_replicates_and_one_player_rejected(self):
        with self.assertRaises(ValueError):
            grouped_mae_skill_bootstrap(self.frame, replicates=30)
        with self.assertRaises(ValueError):
            grouped_mae_skill_bootstrap(self.frame.assign(player_id=1))

    def test_corrupt_inputs_rejected(self):
        variants = [
            self.frame.assign(player_id=[None, 1, 1, 2, 2, 3, 3, 4]),
            self.frame.assign(target_market_value_eur=np.nan),
            self.frame.assign(predicted_market_value_eur=np.inf),
            self.frame.assign(baseline_prediction_eur=-2),
            self.frame.assign(baseline_prediction_eur=self.frame.target_market_value_eur),
        ]
        for frame in variants:
            with self.subTest():
                with self.assertRaises(ValueError):
                    grouped_mae_skill_bootstrap(frame)


class IntervalCoverage(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({
            "season": [2024, 2024, 2024, 2025],
            "target_market_value_eur": [100, 200, 300, 400],
            "prediction_lower_eur": [90, 205, 290, 390],
            "prediction_upper_eur": [110, 220, 310, 410],
        })

    def test_observed_coverage_and_sample_size_suppression(self):
        result = interval_coverage_by_group(self.frame, min_rows=2)
        y2024 = result.loc[result.segment_value.eq("2024")].iloc[0]
        y2025 = result.loc[result.segment_value.eq("2025")].iloc[0]
        self.assertAlmostEqual(y2024.interval_coverage_pct, 200/3)
        self.assertEqual(y2024.median_interval_width_eur, 20)
        self.assertTrue(np.isnan(y2025.interval_coverage_pct))
        self.assertFalse(y2025.meets_minimum_rows)

    def test_invalid_intervals_rejected(self):
        for column, value in [
            ("prediction_lower_eur", -1),
            ("prediction_lower_eur", 500),
            ("prediction_upper_eur", np.inf),
            ("target_market_value_eur", np.nan),
        ]:
            with self.subTest(column=column, value=value):
                frame = self.frame.astype({"target_market_value_eur": float, "prediction_lower_eur": float, "prediction_upper_eur": float}).copy()
                frame.loc[0, column] = value
                with self.assertRaises(ValueError):
                    interval_coverage_by_group(frame, min_rows=1)

    def test_minimum_population_validation(self):
        with self.assertRaises(ValueError):
            interval_coverage_by_group(self.frame, min_rows=0)
        with self.assertRaises(ValueError):
            interval_coverage_by_group(self.frame.iloc[0:0])


if __name__ == "__main__":
    unittest.main()
