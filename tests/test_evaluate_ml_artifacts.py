"""Fully offline evaluation artifact and lineage tests, all data synthetic."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_ml_artifacts import (  # noqa: E402
    evaluate_predictions, main, summarize_segments, validate_evaluation_frame,
    validate_evaluation_provenance,
)


def synthetic_predictions() -> pd.DataFrame:
    return pd.DataFrame({
        "training_row_key": ["a", "b", "c", "d", "e", "f"],
        "player_id": [1, 1, 2, 2, 3, 3],
        "season": [2024, 2025, 2024, 2025, 2024, 2025],
        "position": ["Defender", "Defender", "Attack", "Attack", "Midfield", "Midfield"],
        "prediction_quality_status": ["high", "high", "medium", "medium", "limited", "limited"],
        "model_version": ["model_v5_test"] * 6,
        "target_market_value_eur": [100, 110, 200, 210, 300, 310],
        "predicted_market_value_eur": [102, 109, 198, 212, 303, 309],
        "baseline_prediction_eur": [92, 100, 180, 190, 275, 280],
        "prediction_lower_eur": [90, 100, 180, 190, 275, 290],
        "prediction_upper_eur": [110, 120, 210, 230, 320, 320],
    })


def synthetic_metrics() -> dict[str, object]:
    return {
        "model_version": "model_v5_test",
        "source_commit_sha": "synthetic-fixture-sha",
        "feature_contract_hash": "synthetic-contract-hash",
        "train_season_max": 2023,
        "training_rows": 120,
        "test_rows": 6,
        "tuning_season": 2022,
        "calibration_season": 2023,
        "held_out_test_seasons": [2024, 2025],
    }


class EvaluationArtifactContract(unittest.TestCase):
    def test_valid_predictions_retained_and_group_labels_preserved(self):
        frame = synthetic_predictions()
        clean = validate_evaluation_frame(frame)
        self.assertEqual(len(clean), 6)
        self.assertEqual(set(clean.actual_value_band), {"under_1m"})

    def test_fails_on_mixed_model_versions(self):
        frame = synthetic_predictions()
        frame.loc[0, "model_version"] = "other_model"
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate_evaluation_frame(frame)

    def test_fails_on_missing_duplicate_key(self):
        for invalid in [None, "b"]:
            with self.subTest(invalid=invalid):
                frame = synthetic_predictions()
                frame.loc[0, "training_row_key"] = invalid
                with self.assertRaises(ValueError):
                    validate_evaluation_frame(frame)

    def test_fails_on_corrupt_money_and_bounds(self):
        for column, value in [
            ("target_market_value_eur", np.nan),
            ("target_market_value_eur", 0),
            ("target_market_value_eur", -1),
            ("predicted_market_value_eur", np.inf),
            ("baseline_prediction_eur", -1),
            ("prediction_lower_eur", -2),
            ("prediction_lower_eur", 105),
            ("prediction_upper_eur", 101),
        ]:
            with self.subTest(col=column, invalid=value):
                f = synthetic_predictions()
                f[column] = f[column].astype(float)
                f.loc[0, column] = value
                with self.assertRaises(ValueError):
                    validate_evaluation_frame(f)

    def test_missing_columns_and_fractional_seasons(self):
        with self.assertRaises(ValueError):
            validate_evaluation_frame(synthetic_predictions().drop(columns=["position"]))
        frame = synthetic_predictions()
        frame["season"] = frame["season"].astype(float)
        frame.loc[0, "season"] = 2024.5
        with self.assertRaisesRegex(ValueError, "integer"):
            validate_evaluation_frame(frame)

    def test_summary_skill_coverage_and_temporal_scope(self):
        frame = synthetic_predictions()
        summary, segments = evaluate_predictions(frame, min_rows=2, replicates=200, seed=17)
        self.assertEqual(summary["model_version"], "model_v5_test")
        self.assertEqual(summary["min_test_season"], 2024)
        self.assertEqual(summary["max_test_season"], 2025)
        self.assertGreater(summary["cluster_bootstrap_mae_skill"]["mae_skill_vs_persistence_pct"], 0)
        self.assertEqual(set(segments["segment_type"]), {
            "season", "position", "prediction_quality_status", "actual_value_band"
        })
        self.assertEqual(int(segments["row_count"].sum()), 24)

    def test_small_sample_suppression_is_missing_not_zero(self):
        segments = summarize_segments(synthetic_predictions(), min_rows=3)
        pos = segments.loc[segments.segment_type.eq("position")]
        self.assertTrue(pos.model_mae_eur.isna().all())
        self.assertTrue(pos.observed_interval_coverage_pct.isna().all())
        self.assertTrue((pos.row_count == 2).all())
        self.assertTrue(segments.meets_minimum_rows.any())

    def test_categorical_null_does_not_merge_literal_nan_segment(self):
        frame = synthetic_predictions()
        frame["position"] = pd.Categorical([
            "nan", None, "Attack", "Attack", "Defender", "Defender"
        ])
        groups = summarize_segments(frame, min_rows=1)
        position = groups.loc[groups.segment_type.eq("position")]
        self.assertIn("nan", set(position.segment_value))
        self.assertIn("unavailable", set(position.segment_value))
        self.assertEqual(position.row_count.sum(), len(frame))

    def test_empty_and_zero_baseline_error_fails(self):
        with self.assertRaises(ValueError):
            validate_evaluation_frame(synthetic_predictions().iloc[:0])
        frame = synthetic_predictions()
        frame["baseline_prediction_eur"] = frame["target_market_value_eur"]
        with self.assertRaisesRegex(ValueError, "Baseline error"):
            evaluate_predictions(frame, min_rows=2, replicates=100)

    def test_provenance_rejects_mismatched_model_and_chronology(self):
        frame = synthetic_predictions()
        verified = validate_evaluation_provenance(frame, synthetic_metrics())
        self.assertTrue(verified["artifact_pair_consistent"])
        self.assertFalse(verified["warehouse_freshness_verified"])
        for name, invalid in [
            ("model_version", "different-model"),
            ("train_season_max", 2024),
            ("test_rows", 5),
            ("calibration_season", 2024),
            ("calibration_season", 2022),  # Pre-calibration fitting leak: not final training season
            ("held_out_test_seasons", [2024, 2024]),
            ("held_out_test_seasons", [2025]),
            ("training_rows", 0),
            ("tuning_season", 2023),
        ]:
            with self.subTest(field=name, invalid=invalid):
                metadata = synthetic_metrics()
                metadata[name] = invalid
                with self.assertRaises(ValueError):
                    validate_evaluation_provenance(frame, metadata)

    def test_provenance_rejects_malformed_types(self):
        for name, invalid in [
            ("train_season_max", "2023"),
            ("test_rows", True),
            ("held_out_test_seasons", ["2024", "2025"]),
            ("held_out_test_seasons", None),
        ]:
            with self.subTest(field=name):
                metadata = synthetic_metrics()
                metadata[name] = invalid
                with self.assertRaises(ValueError):
                    validate_evaluation_provenance(synthetic_predictions(), metadata)

    def test_sparse_baseline_error_is_explicitly_unestimable_not_an_exception(self):
        frame = synthetic_predictions()
        frame["baseline_prediction_eur"] = frame["target_market_value_eur"]
        frame.loc[0, "baseline_prediction_eur"] -= 10
        summary, segments = evaluate_predictions(frame, min_rows=2, replicates=200, seed=42)
        bootstrap = summary["cluster_bootstrap_mae_skill"]
        self.assertEqual(bootstrap["bootstrap_ci_status"], "not_estimable_undefined_resamples")
        self.assertGreater(bootstrap["undefined_bootstrap_resamples"], 0)
        self.assertIsNone(bootstrap["bootstrap_ci_lower_pct"])
        self.assertIsNone(bootstrap["bootstrap_ci_upper_pct"])
        json.dumps(summary, allow_nan=False)
        self.assertEqual(segments["row_count"].sum(), 4 * len(frame))

    def test_cli_never_overwrites_prediction_or_metrics_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            predictions = output / "segment_metrics.csv"
            metadata = output / "meta.json"
            predictions.write_text("input-sentinel", encoding="utf-8")
            metadata.write_text("metrics-sentinel", encoding="utf-8")
            with self.assertRaises(SystemExit):
                main(["--input", str(predictions), "--metrics", str(metadata),
                      "--output-dir", str(output)])
            self.assertEqual(predictions.read_text(encoding="utf-8"), "input-sentinel")

            predictions = output / "safe_predictions.csv"
            predictions.write_text("new-input-sentinel", encoding="utf-8")
            metrics = output / "reliability_summary.json"
            metrics.write_text("metadata-sentinel", encoding="utf-8")
            with self.assertRaises(SystemExit):
                main(["--input", str(predictions), "--metrics", str(metrics),
                      "--output-dir", str(output)])
            self.assertEqual(metrics.read_text(encoding="utf-8"), "metadata-sentinel")

    def test_cli_writes_hashed_only_aggregate_outputs(self):
        frame = synthetic_predictions()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "test_predictions.csv"
            metrics = Path(tmp) / "metrics.json"
            output = Path(tmp) / "report"
            frame.to_csv(source, index=False)
            metrics.write_text(json.dumps(synthetic_metrics()), encoding="utf-8")
            exit_code = main(["--input", str(source), "--metrics", str(metrics),
                              "--output-dir", str(output),
                              "--min-rows", "2", "--replicates", "100", "--seed", "5"])
            self.assertEqual(exit_code, 0)
            summary = json.loads((output / "reliability_summary.json").read_text())
            self.assertEqual(len(summary["input_sha256"]), 64)
            self.assertEqual(len(summary["metrics_sha256"]), 64)
            self.assertEqual(summary["model_version"], "model_v5_test")
            self.assertTrue(summary["artifact_provenance"]["artifact_pair_consistent"])
            saved = pd.read_csv(output / "segment_metrics.csv")
            self.assertEqual(len(saved), 9)
            self.assertTrue(source.is_file())


if __name__ == "__main__":
    unittest.main()
