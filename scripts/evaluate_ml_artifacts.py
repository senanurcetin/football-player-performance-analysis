"""Offline reliability report for existing football market-value backtest CSVs.

Consumes evaluation predictions only. It does not retrain, score, query BigQuery,
access Kaggle, invoke Power BI or change the production release state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ml_reliability import grouped_mae_skill_bootstrap, interval_coverage_by_group

TARGET = "target_market_value_eur"
PRED = "predicted_market_value_eur"
BASE = "baseline_prediction_eur"
LOWER = "prediction_lower_eur"
UPPER = "prediction_upper_eur"
REQUIRED = (
    "training_row_key", "player_id", "season", "position",
    "prediction_quality_status", "model_version", TARGET, PRED, BASE, LOWER, UPPER,
)
GROUP_COLUMNS = ("season", "position", "prediction_quality_status", "actual_value_band")


def validate_evaluation_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Fail closed on incomplete or internally inconsistent historical predictions."""
    missing = sorted(set(REQUIRED).difference(frame.columns))
    if missing:
        raise ValueError(f"Evaluation CSV is missing columns: {missing}")
    if frame.empty:
        raise ValueError("Evaluation CSV is empty")
    if frame["training_row_key"].isna().any() or frame["training_row_key"].duplicated().any():
        raise ValueError("Evaluation keys must be nonnull and unique")
    if frame["player_id"].isna().any() or frame["season"].isna().any():
        raise ValueError("Player and season cannot be null")
    versions = frame["model_version"].dropna().astype(str).unique()
    if len(versions) != 1 or frame["model_version"].isna().any() or not versions[0].strip():
        raise ValueError("Expected exactly one nonempty model version")
    numeric_cols = [TARGET, PRED, BASE, LOWER, UPPER, "season"]
    clean = frame.copy()
    for col in numeric_cols:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    arr = clean[numeric_cols].to_numpy(dtype=float)
    if not np.isfinite(arr).all():
        raise ValueError("Evaluation metrics require finite numeric fields")
    if ((clean[TARGET] <= 0) | (clean[[PRED, BASE, LOWER, UPPER]] < 0).any(axis=1)).any():
        raise ValueError("Market-value targets must be positive; estimates/bounds nonnegative")
    if ((clean[LOWER] > clean[PRED]) | (clean[PRED] > clean[UPPER])).any():
        raise ValueError("Prediction cannot fall outside its published interval")
    if not (clean["season"] == np.floor(clean["season"])).all():
        raise ValueError("Season must be an integer")
    clean["season"] = clean["season"].astype(int)
    clean["actual_value_band"] = pd.cut(
        clean[TARGET], bins=[0, 1e6, 5e6, 20e6, np.inf],
        labels=["under_1m", "1m_to_5m", "5m_to_20m", "20m_plus"],
        include_lowest=True, right=False,
    ).astype(str)
    return clean


def validate_evaluation_provenance(
    frame: pd.DataFrame, metadata: dict[str, object]
) -> dict[str, object]:
    """Check self-consistency of the exported predictions and model metrics.

    These checks establish *artifact coherence*, not authenticated warehouse
    provenance. Independent source freshness and feature lineage still require
    an authorized data connection.
    """
    clean = validate_evaluation_frame(frame)
    if not isinstance(metadata, dict):
        raise ValueError("Evaluation metrics JSON must contain an object")
    version = str(clean["model_version"].iloc[0])
    if metadata.get("model_version") != version:
        raise ValueError("Predictions and metrics reference different model versions")
    def whole_number(field: str) -> int:
        value = metadata.get(field)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"Metrics field {field} must be an integer")
        return value
    train_end = whole_number("train_season_max")
    train_rows = whole_number("training_rows")
    test_rows = whole_number("test_rows")
    tuning = whole_number("tuning_season")
    calibration = whole_number("calibration_season")
    seasons = metadata.get("held_out_test_seasons")
    if (
        not isinstance(seasons, list)
        or not seasons
        or any(isinstance(year, bool) or not isinstance(year, int) for year in seasons)
        or len(set(seasons)) != len(seasons)
    ):
        raise ValueError("Held-out season provenance must be unique whole years")
    observed_seasons = sorted(int(year) for year in clean["season"].unique())
    if (
        sorted(seasons) != observed_seasons
        or not (tuning < calibration <= train_end < min(seasons))
        or test_rows != len(clean)
        or train_rows <= 0
    ):
        raise ValueError("Artifact train/tune/calibration/holdout provenance mismatch")
    return {
        "model_version": version,
        "source_commit_sha": metadata.get("source_commit_sha"),
        "feature_contract_hash": metadata.get("feature_contract_hash"),
        "declared_train_season_max": train_end,
        "declared_test_seasons": observed_seasons,
        "declared_test_rows": test_rows,
        "artifact_pair_consistent": True,
        "warehouse_freshness_verified": False,
        "training_lineage_independently_verified": False,
    }


def summarize_segments(frame: pd.DataFrame, *, min_rows: int = 30) -> pd.DataFrame:
    """Produce observed skill and calibrated-interval diagnostics per segment."""
    if not isinstance(min_rows, int) or min_rows < 1:
        raise ValueError("min_rows must be a positive integer")
    frame = validate_evaluation_frame(frame)
    rows: list[dict[str, object]] = []
    for column in GROUP_COLUMNS:
        coverage = interval_coverage_by_group(frame, group_column=column, min_rows=min_rows)
        coverage_lookup = {str(row.segment_value): row for row in coverage.itertuples()}
        for group, sample in frame.assign(
            __group=frame[column].astype(object).where(frame[column].notna(), "unavailable").astype(str)
        ).groupby("__group", sort=True):
            n = len(sample)
            observed = n >= min_rows
            a = sample[TARGET].to_numpy(dtype=float)
            p = sample[PRED].to_numpy(dtype=float)
            b = sample[BASE].to_numpy(dtype=float)
            model_mae = float(np.abs(a - p).mean())
            baseline_mae = float(np.abs(a - b).mean())
            c = coverage_lookup[group]
            rows.append({
                "segment_type": column,
                "segment_value": str(group),
                "row_count": n,
                "unique_players": int(sample["player_id"].nunique()),
                "meets_minimum_rows": observed,
                "model_mae_eur": model_mae if observed else np.nan,
                "baseline_mae_eur": baseline_mae if observed else np.nan,
                "mae_skill_vs_persistence_pct": (
                    100 * (1 - model_mae / baseline_mae)
                    if observed and baseline_mae > 0 else np.nan
                ),
                "model_wape_pct": float(100 * np.abs(a - p).sum() / a.sum()) if observed else np.nan,
                "observed_interval_coverage_pct": c.interval_coverage_pct,
                "median_interval_width_eur": c.median_interval_width_eur,
            })
    return pd.DataFrame(rows)


def evaluate_predictions(
    frame: pd.DataFrame, *, min_rows: int = 30, replicates: int = 500, seed: int = 42
) -> tuple[dict[str, object], pd.DataFrame]:
    """Return one auditable summary and all eligible / suppressed segments."""
    clean = validate_evaluation_frame(frame)
    metrics = grouped_mae_skill_bootstrap(clean, replicates=replicates, seed=seed)
    actual = clean[TARGET].to_numpy(dtype=float)
    pred = clean[PRED].to_numpy(dtype=float)
    base = clean[BASE].to_numpy(dtype=float)
    summary: dict[str, object] = {
        "model_version": str(clean["model_version"].iloc[0]),
        "evaluation_scope": "unverified_input_declared_holdout",
        "min_test_season": int(clean["season"].min()),
        "max_test_season": int(clean["season"].max()),
        "model_mae_eur": float(np.abs(actual - pred).mean()),
        "baseline_mae_eur": float(np.abs(actual - base).mean()),
        "model_wape_pct": float(np.abs(actual - pred).sum() / actual.sum() * 100),
        "baseline_wape_pct": float(np.abs(actual - base).sum() / actual.sum() * 100),
        "empirical_interval_coverage_pct": float(
            ((actual >= clean[LOWER].to_numpy()) & (actual <= clean[UPPER].to_numpy())).mean() * 100
        ),
        "median_interval_width_eur": float((clean[UPPER] - clean[LOWER]).median()),
        "cluster_bootstrap_mae_skill": metrics,
        "limitations": [
            "The target is a historical Transfermarkt estimate, not a transaction price.",
            "Player-group bootstrap intervals do not account for temporal distribution shift.",
            "Empirical retrospective interval coverage is not a future coverage guarantee.",
            "Suppressed segment metrics are missing, not zero.",
        ],
    }
    return summary, summarize_segments(clean, min_rows=min_rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("artifacts/player_market_value/test_predictions.csv"))
    parser.add_argument("--metrics", type=Path, default=Path("artifacts/player_market_value/metrics.json"), help="Required model metadata to verify holdout chronology and model version")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/player_market_value/offline_reliability"))
    parser.add_argument("--min-rows", type=int, default=30)
    parser.add_argument("--replicates", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    if args.input.resolve() == (args.output_dir / "segment_metrics.csv").resolve():
        parser.error("Input must not overlap a generated output")
    if args.metrics.resolve() == args.input.resolve():
        parser.error("Predictions CSV and metrics JSON must be separate files")
    frame = pd.read_csv(args.input)
    metadata = json.loads(args.metrics.read_text(encoding="utf-8"))
    provenance = validate_evaluation_provenance(frame, metadata)
    summary, segments = evaluate_predictions(
        frame, min_rows=args.min_rows, replicates=args.replicates, seed=args.seed
    )
    summary["evaluation_scope"] = "metadata_coherent_historical_holdout"
    summary["artifact_provenance"] = provenance
    summary["input_sha256"] = hashlib.sha256(args.input.read_bytes()).hexdigest()
    summary["metrics_sha256"] = hashlib.sha256(args.metrics.read_bytes()).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "reliability_summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    segments.to_csv(args.output_dir / "segment_metrics.csv", index=False)
    print(f"Offline reliability report saved for {summary['model_version']}: {len(segments)} segments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
