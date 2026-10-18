"""Research-only chronological market value backtesting on exported features.

This script neither accesses BigQuery nor promotes or publishes any model.
It fits distinct historical models to prior seasons only and compares them to
past-only position-median and previous-market-value persistence benchmarks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


TARGET = "target_market_value_eur"


def finite_sample_radius(y_true: np.ndarray, y_pred: np.ndarray, alpha: float = 0.1) -> float:
    """Conservative finite-sample split conformal residual quantile.

    Applies marginal-exchangeability logic only; chronological shift can break
    nominal coverage and must be checked empirically on the held-out season.
    """
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    if not (0 < alpha < 1) or y_true.ndim != 1 or y_pred.shape != y_true.shape:
        raise ValueError("Invalid calibration alpha or residual arrays")
    if len(y_true) == 0 or not np.isfinite(y_true).all() or not np.isfinite(y_pred).all():
        raise ValueError("Calibration data must be nonempty and finite")
    n = len(y_true)
    rank = int(np.ceil((n + 1) * (1 - alpha)))
    if rank > n:
        raise ValueError("Insufficient calibration rows for finite nontrivial interval")
    return float(np.partition(np.abs(y_true - y_pred), rank - 1)[rank - 1])


def prepare_research_frame(frame: pd.DataFrame, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    """Enforce provided historical feature contract; never impute the target."""
    if not numeric or len(set(numeric + categorical)) != len(numeric + categorical):
        raise ValueError("Feature contract must contain distinct nonempty numeric features")
    forbidden = {
        TARGET, "training_row_key", "player_id", "player_name",
        "target_market_value_date", "current_market_value_in_eur",
        "future_market_value_eur", "transfer_fee_eur",
    }
    if forbidden.intersection(numeric + categorical):
        raise ValueError("Feature contract contains target or potential leakage fields")
    required = {"season", "player_id", TARGET, "previous_market_value_eur", "position", *numeric, *categorical}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing feature-contract fields: {missing}")
    if frame.empty:
        raise ValueError("Training features are empty")
    clean = frame.copy()
    for column in set(numeric + [TARGET, "season"]):
        clean[column] = pd.to_numeric(clean[column], errors="coerce")
    if clean["player_id"].isna().any():
        raise ValueError("A player identifier is missing")
    targets = clean[TARGET].to_numpy(dtype=float)
    seasons = clean["season"].to_numpy(dtype=float)
    if (not np.isfinite(targets).all() or (targets <= 0).any()
        or not np.isfinite(seasons).all() or (seasons != np.floor(seasons)).any()):
        raise ValueError("Targets must be positive and seasons whole, finite years")
    if np.isinf(clean[numeric].to_numpy(dtype=float)).any():
        raise ValueError("Infinity is not a valid numeric feature")
    clean["season"] = clean["season"].astype(int)
    for col in categorical:
        clean[col] = clean[col].astype(object).where(clean[col].notna(), np.nan)
    return clean


def build_model(numeric: list[str], categorical: list[str], *, max_iter: int = 150) -> Pipeline:
    numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median", add_indicator=True))])
    category_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
    ])
    pre = ColumnTransformer([
        ("numeric", numeric_pipeline, numeric),
        ("categorical", category_pipeline, categorical),
    ])
    return Pipeline([
        ("preprocessing", pre),
        ("model", HistGradientBoostingRegressor(max_iter=max_iter, max_leaf_nodes=15,
                                               min_samples_leaf=10, random_state=42)),
    ])


def position_median_predict(reference: pd.DataFrame, other: pd.DataFrame) -> np.ndarray:
    """Position baselines are computed solely from past-season observations."""
    if reference.empty or other.empty:
        raise ValueError("Reference and evaluation populations must be nonempty")
    median = float(reference[TARGET].median())
    by_position = reference.groupby("position", dropna=False)[TARGET].median()
    return np.array([
        float(by_position.get(pos, median)) if pd.notna(pos) else median
        for pos in other["position"]
    ])


def run_walk_forward(
    frame: pd.DataFrame,
    numeric: list[str],
    categorical: list[str],
    *,
    min_development_seasons: int = 3,
    max_iter: int = 150,
    alpha: float = 0.1,
) -> pd.DataFrame:
    """Execute independent train/tune/calibrate/test chronologies by test season.

    For each test season Y: tuning is Y's third-most-recent observed historical
    season, calibration is the last prior season, and development consists of
    seasons before tuning. Never tunes, trains, or calibrates on test year Y.
    """
    clean = prepare_research_frame(frame, numeric, categorical)
    years = sorted(clean["season"].unique().tolist())
    min_train = min_development_seasons + 2
    if min_development_seasons < 1 or len(years) <= min_train:
        raise ValueError("At least development+tuning+calibration+test seasons required")
    features = numeric + categorical
    records = []
    for test_year in years[min_train:]:
        prior = [year for year in years if year < test_year]
        tune_year, calibration_year = prior[-2:]
        development = clean[clean["season"] < tune_year]
        tuning = clean[clean["season"] == tune_year]
        pre_calibration = clean[clean["season"] <= tune_year]
        calibration = clean[clean["season"] == calibration_year]
        training = clean[clean["season"] < test_year]
        test = clean[clean["season"] == test_year]
        if any(x.empty for x in [development, tuning, pre_calibration, calibration, training, test]):
            raise ValueError("A chronological research segment is empty")
        if not (development.season.max() < tune_year < calibration_year < test_year):
            raise AssertionError("Temporal leakage detected in evaluation split")
        model_tune = build_model(numeric, categorical, max_iter=max_iter)
        model_tune.fit(development[features], development[TARGET])
        tuning_ml = np.maximum(model_tune.predict(tuning[features]), 0)
        prior_fallback = float(development[TARGET].median())
        tuning_persist = tuning["previous_market_value_eur"].fillna(prior_fallback).to_numpy(float)
        weights = np.linspace(0, 1, 21)
        weight = float(min(weights, key=lambda w: mean_absolute_error(
            tuning[TARGET], w * tuning_ml + (1 - w) * tuning_persist)))
        model_cal = build_model(numeric, categorical, max_iter=max_iter)
        model_cal.fit(pre_calibration[features], pre_calibration[TARGET])
        cal_ml = np.maximum(model_cal.predict(calibration[features]), 0)
        cal_persist = calibration["previous_market_value_eur"].fillna(
            float(pre_calibration[TARGET].median())).to_numpy(float)
        cal_pred = weight * cal_ml + (1 - weight) * cal_persist
        radius = finite_sample_radius(calibration[TARGET].to_numpy(float), cal_pred, alpha)
        # Use the *same fitted model* for calibration and held-out inference.
        # Refitting on the calibration season would invalidate split-conformal
        # residual comparability, even though it is a past season.
        test_ml = np.maximum(model_cal.predict(test[features]), 0)
        test_persist = test["previous_market_value_eur"].fillna(
            float(pre_calibration[TARGET].median())).to_numpy(float)
        test_pred = weight * test_ml + (1 - weight) * test_persist
        cohort_pred = position_median_predict(pre_calibration, test)
        actual = test[TARGET].to_numpy(float)
        total_abs = float(np.abs(actual - test_pred).sum())
        baseline_abs = float(np.abs(actual - test_persist).sum())
        coverage = float(((actual >= np.maximum(test_pred - radius, 0)) &
                          (actual <= test_pred + radius)).mean() * 100)
        records.append({
            "test_season": int(test_year),
            "development_season_max": int(development["season"].max()),
            "tuning_season": int(tune_year),
            "calibration_season": int(calibration_year),
            "training_season_max": int(pre_calibration["season"].max()),
            "latest_available_prior_season": int(training["season"].max()),
            "train_rows": len(pre_calibration),
            "test_rows": len(test),
            "unique_test_players": int(test["player_id"].nunique()),
            "selected_ml_blend_weight": weight,
            "model_mae_eur": float(total_abs / len(test)),
            "persistence_mae_eur": float(baseline_abs / len(test)),
            "position_median_mae_eur": float(np.abs(actual - cohort_pred).mean()),
            "model_wape_pct": float(100 * total_abs / actual.sum()),
            "mae_skill_vs_persistence_pct": float(100 * (1 - total_abs / baseline_abs))
            if baseline_abs > 0 else np.nan,
            "observed_90pct_interval_coverage_pct": coverage,
            "interval_radius_eur": radius,
        })
    return pd.DataFrame(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--feature-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-iter", type=int, default=150)
    parser.add_argument("--min-development-seasons", type=int, default=3)
    args = parser.parse_args(argv)
    if args.max_iter < 1 or args.max_iter > 300:
        parser.error("--max-iter must be in [1, 300]")
    if args.input.resolve() == args.output.resolve():
        parser.error("Output path cannot overwrite input")
    if args.feature_contract.resolve() == args.output.resolve():
        parser.error("Output path cannot overwrite feature contract")
    contract = json.loads(args.feature_contract.read_text(encoding="utf-8"))
    if contract.get("target") != TARGET:
        parser.error("Unexpected target in exported feature contract")
    numeric, categorical = contract.get("numeric_features"), contract.get("categorical_features")
    if not isinstance(numeric, list) or not isinstance(categorical, list):
        parser.error("Feature lists must be provided in the contract")
    results = run_walk_forward(
        pd.read_csv(args.input), numeric, categorical, max_iter=args.max_iter,
        min_development_seasons=args.min_development_seasons,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)
    manifest = {
        "report_type": "research_only_refitted_seasonal_backtest",
        "raw_input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "feature_contract_sha256": hashlib.sha256(args.feature_contract.read_bytes()).hexdigest(),
        "folds": len(results),
        "min_test_season": int(results.test_season.min()),
        "max_test_season": int(results.test_season.max()),
        "data_provenance": "caller_supplied_export_not_independently_authenticated",
        "production_model_v5_results": False,
        "production_changes": False,
    }
    args.output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} historical research folds to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())