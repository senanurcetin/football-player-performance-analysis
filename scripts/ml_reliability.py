"""Offline, audit-friendly football market-value evaluation helpers.

Input is a caller-supplied frame; this module does not access Google Cloud,
Kaggle, local credentials or model artifacts. Reported metrics are descriptive
on the supplied observations and do not establish causal effects.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_origin_season_splits(
    frame: pd.DataFrame,
    *,
    season_column: str = "season",
    min_train_seasons: int = 4,
    test_seasons: list[int] | None = None,
) -> list[tuple[int, np.ndarray, np.ndarray]]:
    """Return (test season, earlier train row indices, test row indices).

    These are **candidate** folds. The model, tuning and interval calibration
    must each be performed strictly within the fold's training rows, never the
    held-out season. Does not train or score a model.
    """
    if min_train_seasons < 1:
        raise ValueError("min_train_seasons must be positive")
    if season_column not in frame:
        raise ValueError(f"Missing season column: {season_column}")
    values = pd.to_numeric(frame[season_column], errors="coerce").to_numpy(dtype=float)
    if len(values) == 0 or not np.isfinite(values).all() or np.any(values != np.floor(values)):
        raise ValueError("Seasons must be present and finite whole numbers")
    years = np.sort(np.unique(values.astype(int)))
    if len(years) <= min_train_seasons:
        raise ValueError("Not enough distinct seasons for rolling-origin evaluation")
    eligible = set(int(year) for year in years[min_train_seasons:])
    requested = sorted(eligible) if test_seasons is None else sorted(set(test_seasons))
    if not requested or any(year not in eligible for year in requested):
        raise ValueError("Requested test seasons are not chronologically eligible")
    folds = []
    for test_year in requested:
        train_idx = np.flatnonzero(values < test_year)
        test_idx = np.flatnonzero(values == test_year)
        if len(np.unique(values[train_idx])) < min_train_seasons or len(test_idx) == 0:
            raise ValueError("Invalid rolling-origin fold population")
        folds.append((int(test_year), train_idx, test_idx))
    return folds


def grouped_mae_skill_bootstrap(
    frame: pd.DataFrame,
    *,
    player_column: str = "player_id",
    target_column: str = "target_market_value_eur",
    model_column: str = "predicted_market_value_eur",
    baseline_column: str = "baseline_prediction_eur",
    replicates: int = 500,
    confidence: float = 0.95,
    seed: int = 42,
) -> dict[str, float | int]:
    """Confidence interval for MAE improvement (%) via player-cluster bootstrap.

    Sampling units are players, *not* player-seasons. With historical serial or
    temporal drift, this bootstrap is descriptive uncertainty conditional on the
    observed period and should not be interpreted as future-season coverage.
    """
    if not isinstance(replicates, int) or replicates < 100:
        raise ValueError("At least 100 bootstrap replicates are required")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between zero and one")
    required = [player_column, target_column, model_column, baseline_column]
    missing = [col for col in required if col not in frame]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if frame.empty or frame[player_column].isna().any():
        raise ValueError("Player-group bootstrap requires complete player identifiers")
    numeric = frame[[target_column, model_column, baseline_column]].apply(
        pd.to_numeric, errors="coerce"
    ).to_numpy(dtype=float)
    if not np.isfinite(numeric).all() or (numeric[:, 0] <= 0).any() or (numeric[:, 1:] < 0).any():
        raise ValueError("Target and predictions must be finite, with positive targets")
    groups = pd.factorize(frame[player_column], sort=True)[0]
    group_count = int(groups.max()) + 1
    if group_count < 2:
        raise ValueError("At least two distinct players are required")
    error_model = np.abs(numeric[:, 0] - numeric[:, 1])
    error_baseline = np.abs(numeric[:, 0] - numeric[:, 2])
    baseline_group_sums = np.bincount(groups, weights=error_baseline, minlength=group_count)
    model_group_sums = np.bincount(groups, weights=error_model, minlength=group_count)
    baseline_total = float(baseline_group_sums.sum())
    if baseline_total <= 0:
        raise ValueError("Baseline error is zero; relative skill is undefined")
    observed_skill_pct = float(100 * (1 - model_group_sums.sum() / baseline_total))
    rng = np.random.default_rng(seed)
    bootstrap_scores = np.empty(replicates, dtype=float)
    # Bound working memory even when there are many distinct players.
    for start in range(0, replicates, 128):
        end = min(start + 128, replicates)
        sample_ids = rng.integers(0, group_count, size=(end - start, group_count))
        sampled_baseline = baseline_group_sums[sample_ids].sum(axis=1)
        sampled_model = model_group_sums[sample_ids].sum(axis=1)
        valid = sampled_baseline > 0
        if not valid.all():
            raise ValueError("A bootstrap sample has zero baseline error")
        bootstrap_scores[start:end] = 100 * (1 - sampled_model / sampled_baseline)
    alpha = (1 - confidence) / 2
    low, high = np.quantile(bootstrap_scores, [alpha, 1 - alpha])
    return {
        "player_groups": group_count,
        "rows": int(len(frame)),
        "replicates": replicates,
        "confidence_level_pct": float(confidence * 100),
        "mae_skill_vs_persistence_pct": observed_skill_pct,
        "bootstrap_ci_lower_pct": float(low),
        "bootstrap_ci_upper_pct": float(high),
    }


def interval_coverage_by_group(
    frame: pd.DataFrame,
    *,
    group_column: str = "season",
    target_column: str = "target_market_value_eur",
    lower_column: str = "prediction_lower_eur",
    upper_column: str = "prediction_upper_eur",
    min_rows: int = 30,
) -> pd.DataFrame:
    """Return observed interval coverage and width; suppress small group rates."""
    if not isinstance(min_rows, int) or min_rows < 1:
        raise ValueError("min_rows must be a positive integer")
    columns = [group_column, target_column, lower_column, upper_column]
    missing = [col for col in columns if col not in frame]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if frame.empty:
        raise ValueError("Cannot estimate interval coverage on an empty sample")
    values = frame[[target_column, lower_column, upper_column]].apply(
        pd.to_numeric, errors="coerce"
    ).to_numpy(dtype=float)
    if (
        not np.isfinite(values).all()
        or (values[:, 0] <= 0).any()
        or (values[:, 1:] < 0).any()
        or (values[:, 1] > values[:, 2]).any()
    ):
        raise ValueError("Invalid actual values or interval boundaries")
    working = pd.DataFrame({
        "group": frame[group_column].astype(object).where(frame[group_column].notna(), "unavailable").astype(str),
        "is_covered": (values[:, 0] >= values[:, 1]) & (values[:, 0] <= values[:, 2]),
        "width_eur": values[:, 2] - values[:, 1],
    })
    rows = []
    for group, sample in working.groupby("group", sort=True):
        meets_minimum = len(sample) >= min_rows
        rows.append({
            "segment_type": group_column,
            "segment_value": group,
            "row_count": len(sample),
            "minimum_rows": min_rows,
            "meets_minimum_rows": meets_minimum,
            "interval_coverage_pct": float(sample["is_covered"].mean() * 100)
            if meets_minimum else np.nan,
            "median_interval_width_eur": float(sample["width_eur"].median())
            if meets_minimum else np.nan,
        })
    return pd.DataFrame(rows)
