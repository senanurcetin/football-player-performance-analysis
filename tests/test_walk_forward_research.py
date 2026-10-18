"""Offline synthetic tests for research-only chronological model refitting."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

import walk_forward_research as m


def example_frame() -> pd.DataFrame:
    rows = []
    for year in range(2015, 2024):
        for athlete in range(24):
            base = 80_000 + year * 6 + athlete * 700
            rows.append({
                "season": year,
                "player_id": athlete,
                "target_market_value_eur": base + 500,
                "previous_market_value_eur": base,
                "age": 20 + athlete % 5,
                "position": ["Attack", "Defender", "Midfield"][athlete % 3],
            })
    return pd.DataFrame(rows)


class FoldResearchTests(unittest.TestCase):
    def setUp(self):
        self.frame = example_frame()
        self.numeric = ["age", "previous_market_value_eur"]
        self.categorical = ["position"]

    def test_known_finite_sample_conformal_residual_rank(self):
        actual = np.arange(1, 11, dtype=float)
        predicted = actual - np.arange(10, dtype=float)
        self.assertEqual(m.finite_sample_radius(actual, predicted), 9.0)
        self.assertEqual(m.finite_sample_radius(np.array([3.0] * 10), np.array([3.0] * 10)), 0.0)

    def test_insufficient_calibration_and_bad_quantiles(self):
        with self.assertRaisesRegex(ValueError, "Insufficient"):
            m.finite_sample_radius(np.ones(3), np.zeros(3), alpha=0.1)
        for alpha in [-1, 0, 1, 2]:
            with self.subTest(alpha=alpha):
                with self.assertRaises(ValueError):
                    m.finite_sample_radius(np.ones(10), np.ones(10), alpha=alpha)
        with self.assertRaises(ValueError):
            m.finite_sample_radius(np.ones(10), np.zeros(5))

    def test_full_walk_forward_splits_and_cohort_comparisons(self):
        results = m.run_walk_forward(self.frame, self.numeric, self.categorical, max_iter=5)
        self.assertEqual(results.test_season.tolist(), [2020, 2021, 2022, 2023])
        self.assertTrue((results.development_season_max < results.tuning_season).all())
        self.assertTrue((results.tuning_season < results.training_season_max + 1).all())
        self.assertTrue((results.training_season_max < results.calibration_season).all())
        self.assertTrue((results.calibration_season < results.test_season).all())
        self.assertEqual(results.test_rows.tolist(), [24] * 4)
        self.assertTrue((results.interval_radius_eur >= 0).all())
        self.assertTrue(np.isfinite(results.model_mae_eur).all())

    def test_calibration_and_test_share_same_fitted_estimator(self):
        original = m.build_model
        call_count = 0
        def wrapped(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return original(*args, **kwargs)
        with patch.object(m, "build_model", wrapped):
            result = m.run_walk_forward(self.frame, self.numeric, self.categorical, max_iter=2)
        self.assertEqual(call_count, 2 * len(result), "tuning and calibrating fits only")

    def test_future_target_changing_does_not_change_earlier_fold(self):
        original = m.run_walk_forward(self.frame, self.numeric, self.categorical, max_iter=3)
        altered = self.frame.copy()
        altered.loc[altered.season == 2023, "target_market_value_eur"] *= 100
        changed = m.run_walk_forward(altered, self.numeric, self.categorical, max_iter=3)
        pd.testing.assert_series_equal(
            original.iloc[0].drop(labels=["test_season"]),
            changed.iloc[0].drop(labels=["test_season"]), check_names=False,
        )

    def test_unknown_position_uses_past_only_median(self):
        ref = self.frame[self.frame.season == 2015].copy()
        example = ref.iloc[:2].copy()
        example["position"] = ["Unknown", None]
        predicted = m.position_median_predict(ref, example)
        self.assertTrue(np.all(predicted == float(ref.target_market_value_eur.median())))

    def test_missing_target_noninteger_seasons_and_infinity_fail(self):
        for column, invalid in [
            ("target_market_value_eur", np.nan),
            ("target_market_value_eur", -1.0),
            ("season", 2023.5),
            ("previous_market_value_eur", np.inf),
        ]:
            with self.subTest(column=column, invalid=invalid):
                frame = self.frame.copy()
                frame[column] = frame[column].astype(float)
                frame.loc[0, column] = invalid
                with self.assertRaises(ValueError):
                    m.prepare_research_frame(frame, self.numeric, self.categorical)

    def test_missing_feature_columns_and_insufficient_seasons_fail(self):
        with self.assertRaises(ValueError):
            m.run_walk_forward(self.frame, ["not_in_data"], ["position"], max_iter=2)
        with self.assertRaises(ValueError):
            m.run_walk_forward(self.frame[self.frame.season < 2018], self.numeric, self.categorical, max_iter=2)

    def test_target_or_identity_as_feature_rejected(self):
        for feature in ["target_market_value_eur", "player_id", "target_market_value_date"]:
            with self.subTest(feature=feature):
                with self.assertRaisesRegex(ValueError, "leakage"):
                    m.prepare_research_frame(self.frame, self.numeric + [feature], self.categorical)

    def test_cli_outputs_hashed_research_only_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "history.csv"
            contract_path = Path(tmp) / "feature_contract.json"
            output = Path(tmp) / "audit.csv"
            self.frame.to_csv(source, index=False)
            contract_path.write_text(json.dumps({
                "target": m.TARGET,
                "numeric_features": self.numeric,
                "categorical_features": self.categorical,
            }), encoding="utf-8")
            self.assertEqual(m.main(["--input", str(source), "--feature-contract", str(contract_path),
                                     "--output", str(output), "--max-iter", "3"]), 0)
            self.assertEqual(len(pd.read_csv(output)), 4)
            metadata = json.loads(output.with_suffix(".manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["folds"], 4)
            self.assertFalse(metadata["production_model_v5_results"])
            self.assertEqual(len(metadata["raw_input_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()