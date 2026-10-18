"""Credential-free regression tests for market-value ML numeric safety.

Uses synthetic rows only; importing the module does not initialize BigQuery.
Run: python -m unittest discover -s tests -p 'test_ml_numeric_contract.py' -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from train_player_market_value import (  # noqa: E402
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET,
    calibrate_prediction_intervals,
    validate_input_frame,
    validate_predictions,
)


def synthetic_features(kind: str = "training") -> pd.DataFrame:
    """Minimal synthetic feature rows, never real football observations."""
    values: dict[str, object] = {
        feature: [1.0, 2.0, 3.0] for feature in NUMERIC_FEATURES
    }
    values.update({feature: ["a", "b", "c"] for feature in CATEGORICAL_FEATURES})
    values["season"] = [2022, 2023, 2024]
    values["player_id"] = [101, 102, 103]
    if kind == "training":
        values["training_row_key"] = ["a", "b", "c"]
        values[TARGET] = [100_000.0, 200_000.0, 300_000.0]
        values["target_market_value_date"] = ["2022-01-01", "2023-01-01", "2024-01-01"]
    else:
        values["scoring_row_key"] = ["a", "b", "c"]
        values["prediction_as_of_date"] = ["2025-01-01"] * 3
    return pd.DataFrame(values)


def synthetic_predictions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "training_row_key": ["a", "b"],
            "predicted_market_value_eur": [100.0, 200.0],
            "prediction_interval_band": ["under_1m", "under_1m"],
            "prediction_interval_eur": [25.0, 25.0],
            "prediction_lower_eur": [75.0, 175.0],
            "prediction_upper_eur": [125.0, 225.0],
        }
    )


class MarketValueNumericContract(unittest.TestCase):
    def test_valid_training_and_scoring_rows(self) -> None:
        validate_input_frame(synthetic_features("training"), "training")
        scoring = synthetic_features("scoring")
        scoring.loc[0, "height_in_cm"] = np.nan  # Optional feature missingness is allowed.
        validate_input_frame(scoring, "scoring")

    def test_invalid_training_target_is_rejected(self) -> None:
        for invalid in [np.nan, np.inf, -np.inf, 0.0, -1.0]:
            with self.subTest(invalid=invalid):
                frame = synthetic_features()
                frame.loc[0, TARGET] = invalid
                with self.assertRaises(ValueError):
                    validate_input_frame(frame, "training")

    def test_infinite_scoring_features_are_rejected(self) -> None:
        for invalid in [np.inf, -np.inf]:
            with self.subTest(invalid=invalid):
                frame = synthetic_features("scoring")
                frame.loc[0, "height_in_cm"] = invalid
                with self.assertRaises(ValueError):
                    validate_input_frame(frame, "scoring")

    def test_valid_complete_intervals_and_clipped_lower_bound(self) -> None:
        predictions = synthetic_predictions()
        validate_predictions(predictions, "training_row_key", "predicted_market_value_eur")
        predictions.loc[0, "prediction_lower_eur"] = 0.0
        validate_predictions(predictions, "training_row_key", "predicted_market_value_eur")

    def test_predictions_without_optional_intervals_remain_valid(self) -> None:
        predictions = synthetic_predictions()[
            ["training_row_key", "predicted_market_value_eur"]
        ]
        validate_predictions(predictions, "training_row_key", "predicted_market_value_eur")

    def test_missing_prediction_keys_are_rejected(self) -> None:
        predictions = synthetic_predictions()
        predictions.loc[0, "training_row_key"] = None
        with self.assertRaises(ValueError):
            validate_predictions(predictions, "training_row_key", "predicted_market_value_eur")

    def test_duplicate_prediction_keys_are_rejected(self) -> None:
        predictions = synthetic_predictions()
        predictions.loc[1, "training_row_key"] = "a"
        with self.assertRaises(ValueError):
            validate_predictions(predictions, "training_row_key", "predicted_market_value_eur")

    def test_incomplete_interval_column_set_is_rejected(self) -> None:
        for missing in [
            "prediction_interval_band",
            "prediction_interval_eur",
            "prediction_lower_eur",
            "prediction_upper_eur",
        ]:
            with self.subTest(missing=missing):
                predictions = synthetic_predictions().drop(columns=[missing])
                with self.assertRaises(ValueError):
                    validate_predictions(
                        predictions, "training_row_key", "predicted_market_value_eur"
                    )

    def test_nonfinite_interval_boundaries_are_rejected(self) -> None:
        for column in ["prediction_lower_eur", "prediction_upper_eur"]:
            for invalid in [np.nan, np.inf, -np.inf]:
                with self.subTest(column=column, invalid=invalid):
                    predictions = synthetic_predictions()
                    predictions.loc[0, column] = invalid
                    with self.assertRaises(ValueError):
                        validate_predictions(
                            predictions, "training_row_key", "predicted_market_value_eur"
                        )

    def test_invalid_interval_widths_and_ordering_are_rejected(self) -> None:
        cases = [
            ("prediction_interval_eur", 0.0),
            ("prediction_interval_eur", -1.0),
            ("prediction_interval_eur", np.nan),
            ("prediction_interval_eur", np.inf),
            ("prediction_lower_eur", 101.0),
            ("prediction_upper_eur", 99.0),
            ("prediction_interval_band", None),
        ]
        for column, invalid in cases:
            with self.subTest(column=column, invalid=invalid):
                predictions = synthetic_predictions()
                predictions.loc[0, column] = invalid
                with self.assertRaises(ValueError):
                    validate_predictions(
                        predictions, "training_row_key", "predicted_market_value_eur"
                    )

    def test_interval_calibration_accepts_valid_arrays(self) -> None:
        absolute, per_band = calibrate_prediction_intervals(
            np.array([100.0, 200.0, 300.0]),
            np.array([90.0, 210.0, 280.0]),
        )
        self.assertEqual(absolute, 20.0)
        self.assertGreaterEqual(len(per_band), 1)

    def test_interval_calibration_rejects_invalid_quantiles(self) -> None:
        for quantile in [-0.1, 0.0, 1.0, 1.1]:
            with self.subTest(quantile=quantile):
                with self.assertRaises(ValueError):
                    calibrate_prediction_intervals(
                        np.array([100.0]), np.array([90.0]), quantile=quantile
                    )

    def test_interval_calibration_rejects_invalid_arrays(self) -> None:
        cases = [
            (np.array([]), np.array([])),
            (np.array([100.0]), np.array([90.0, 20.0])),
            (np.array([np.nan]), np.array([90.0])),
            (np.array([np.inf]), np.array([90.0])),
            (np.array([-100.0]), np.array([90.0])),
            (np.array([100.0]), np.array([np.nan])),
            (np.array([100.0]), np.array([-90.0])),
        ]
        for actual, predicted in cases:
            with self.subTest(actual=actual, predicted=predicted):
                with self.assertRaises(ValueError):
                    calibrate_prediction_intervals(actual, predicted)


if __name__ == "__main__":
    unittest.main()
