"""Smoke-test the player market value preprocessing and model pipeline."""

import numpy as np
import pandas as pd

from train_player_market_value import (
    CATEGORICAL_FEATURES,
    METADATA_COLUMNS,
    NUMERIC_FEATURES,
    TARGET,
    apply_blend_weights_by_quality_status,
    assert_blocking_quality_gates,
    build_pipeline,
    calibrate_prediction_intervals,
    evaluation_metrics,
    feature_contract_hash,
    feature_drift_report,
    prediction_interval_widths,
    prediction_quality_status,
    quality_gate_report,
    regression_metrics,
    release_status,
    select_blend_weight,
    select_blend_weights_by_quality_status,
    validate_input_frame,
    validate_predictions,
)

required_evaluation_metadata = {
    "position",
    "sub_position",
    "age_at_target_date",
    "competition_country_name",
}
if not required_evaluation_metadata.issubset(METADATA_COLUMNS):
    raise SystemExit("ML evaluation publishing contract omits required segment metadata.")


rng = np.random.default_rng(42)
row_count = 500

frame = pd.DataFrame(
    {
        feature: rng.normal(size=row_count)
        for feature in NUMERIC_FEATURES
    }
)
for feature in CATEGORICAL_FEATURES:
    frame[feature] = rng.choice(["a", "b", None], size=row_count)

frame[TARGET] = np.exp(rng.normal(14, 1, size=row_count))
frame["training_row_key"] = np.arange(row_count).astype(str)
frame["player_id"] = np.arange(row_count)
frame["player_name"] = "Synthetic Player"
frame["target_market_value_date"] = pd.Timestamp("2025-01-01")
frame["previous_market_value_eur"] = frame["previous_market_value_eur"].abs()
frame["season"] = rng.choice([2022, 2023, 2024], size=row_count)
frame.loc[::20, "height_in_cm"] = np.nan
validate_input_frame(frame, "training")

if len(feature_contract_hash()) != 64:
    raise SystemExit("ML feature contract hash is invalid.")

pipeline = build_pipeline()
pipeline.fit(frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES], frame[TARGET])
prediction = np.maximum(
    pipeline.predict(frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES]),
    0,
)

if not np.isfinite(prediction).all():
    raise SystemExit("ML smoke test produced non-finite predictions.")

baseline = np.full(row_count, frame[TARGET].median())
weight = select_blend_weight(frame[TARGET].to_numpy(), prediction, baseline)
if not 0 <= weight <= 1:
    raise SystemExit("ML smoke test selected an invalid ensemble weight.")

segment_test = frame.iloc[:6].copy()
segment_test["previous_market_value_eur"] = [1, 1, 1, np.nan, np.nan, np.nan]
segment_test["age_at_target_date"] = 25
segment_test["competition_id"] = ["a", "a", "a", None, None, None]
segment_test["minutes_before_target"] = [900, 900, 900, 0, 0, 0]
segment_actual = np.array([10, 20, 30, 40, 50, 60], dtype=float)
segment_model = np.array([10, 20, 30, 400, 500, 600], dtype=float)
segment_baseline = np.array([100, 200, 300, 40, 50, 60], dtype=float)
segment_weights = select_blend_weights_by_quality_status(
    segment_test,
    segment_actual,
    segment_model,
    segment_baseline,
    minimum_segment_rows=1,
)
segment_prediction, selected_weights = apply_blend_weights_by_quality_status(
    segment_test,
    segment_model,
    segment_baseline,
    segment_weights,
)
if segment_weights["high"] != 1 or segment_weights["limited"] != 0:
    raise SystemExit("ML smoke test selected incorrect quality-segment weights.")
if not np.allclose(segment_prediction, segment_actual):
    raise SystemExit("ML smoke test applied incorrect quality-segment weights.")
if not set(selected_weights).issubset(set(segment_weights.values())):
    raise SystemExit("ML smoke test emitted an unknown quality-segment weight.")

metrics = regression_metrics(frame[TARGET].to_numpy(), prediction)
if not all(np.isfinite(value) for value in metrics.values()):
    raise SystemExit("ML smoke test produced non-finite metrics.")

frame["predicted_market_value_eur"] = prediction
frame["baseline_prediction_eur"] = frame["previous_market_value_eur"]
default_interval, interval_by_band = calibrate_prediction_intervals(
    frame[TARGET].to_numpy(),
    prediction,
)
frame["prediction_interval_band"], interval_widths = prediction_interval_widths(
    prediction,
    default_interval,
    interval_by_band,
)
frame["prediction_interval_eur"] = interval_widths
frame["prediction_lower_eur"] = np.maximum(prediction - interval_widths, 0)
frame["prediction_upper_eur"] = prediction + interval_widths
frame["prediction_quality_status"] = prediction_quality_status(frame)
validate_predictions(frame, "training_row_key", "predicted_market_value_eur")

segment_metrics = evaluation_metrics(frame, "synthetic")
if segment_metrics.empty:
    raise SystemExit("ML smoke test produced no segment metrics.")
required_segment_types = {
    "overall",
    "position",
    "sub_position",
    "age_band",
    "competition_id",
    "competition_country_name",
    "value_band",
    "prediction_quality_status",
}
if not required_segment_types.issubset(set(segment_metrics["segment_type"])):
    raise SystemExit("ML smoke test did not produce all governed segment metrics.")
if segment_metrics["meets_minimum_sample_size"].isna().any():
    raise SystemExit("ML smoke test produced invalid segment sample-size governance.")

drift = feature_drift_report(frame.iloc[:250], frame.iloc[250:], "synthetic")
if drift.empty or not np.isfinite(drift["psi"]).all():
    raise SystemExit("ML smoke test produced invalid drift metrics.")

quality_gates = quality_gate_report(
    {
        "ensemble_model": metrics,
        "previous_value_baseline": regression_metrics(
            frame[TARGET].to_numpy(),
            frame["baseline_prediction_eur"].to_numpy(),
        ),
    },
    segment_metrics,
    "synthetic",
    pd.Timestamp("2026-01-01", tz="UTC").to_pydatetime(),
    current_predictions=frame,
    drift=drift,
)
if quality_gates.empty or release_status(quality_gates) not in {
    "approved",
    "approved_with_monitoring",
    "rejected",
}:
    raise SystemExit("ML smoke test produced invalid quality gates.")
if not quality_gates["gate_name"].eq(
    "worst_quality_segment_mae_improvement_vs_baseline_pct"
).any():
    raise SystemExit("ML smoke test did not produce the quality-segment gate.")

blocking_failure = quality_gates.copy()
blocking_failure.loc[
    blocking_failure["severity"].eq("blocking"), "passed"
] = False
try:
    assert_blocking_quality_gates(blocking_failure)
except ValueError:
    pass
else:
    raise SystemExit("ML smoke test did not reject failed blocking gates.")

print("ML pipeline smoke test passed.")
