"""Train and evaluate a leakage-safe player market value regression model."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from google.oauth2 import service_account
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


NUMERIC_FEATURES = [
    "season",
    "height_in_cm",
    "age_at_target_date",
    "matches_before_target",
    "competitions_played_before_target",
    "minutes_before_target",
    "goals_before_target",
    "assists_before_target",
    "yellow_cards_before_target",
    "red_cards_before_target",
    "goals_per_90_before_target",
    "assists_per_90_before_target",
    "previous_market_value_eur",
    "days_since_previous_market_value",
    "prior_valuation_count",
    "prior_highest_market_value_eur",
]

CATEGORICAL_FEATURES = [
    "position",
    "sub_position",
    "preferred_foot",
    "country_of_citizenship",
    "competition_id",
    "competition_type",
    "competition_country_name",
    "confederation",
]

TARGET = "target_market_value_eur"
MODEL_NAME = "player_market_value_hgbr"
MODEL_VERSION = "v5"
PREDICTION_QUALITY_STATUSES = ["high", "medium", "limited"]
PREDICTION_QUALITY_BLEND_WEIGHT_OVERRIDES = {"limited": 0.0}
METADATA_COLUMNS = [
    "position",
    "sub_position",
    "age_at_target_date",
    "competition_country_name",
]
BLOCKING_GATE_THRESHOLDS = {
    "mae_improvement_vs_baseline_pct": 0.0,
    "wape_pct": 15.0,
    "r2": 0.95,
    "overall_interval_coverage_pct": 85.0,
    "elite_interval_coverage_pct": 80.0,
    "champion_mae_regression_pct": 2.0,
    "quality_segment_mae_improvement_vs_baseline_pct": 0.0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--dataset", default="football_ml")
    parser.add_argument("--table", default="ml_player_market_value_training")
    parser.add_argument("--score-table", default="ml_player_market_value_scoring")
    parser.add_argument("--credentials")
    parser.add_argument("--test-seasons", type=int, default=2)
    parser.add_argument("--max-rows", type=int)
    parser.add_argument("--output-dir", default="artifacts/player_market_value")
    parser.add_argument(
        "--publish-predictions-table",
        help="Optional BigQuery table name in the selected dataset, written with WRITE_TRUNCATE.",
    )
    parser.add_argument(
        "--publish-current-predictions-table",
        help="Optional BigQuery table name for current active-player predictions.",
    )
    parser.add_argument(
        "--publish-evaluation-metrics-table",
        help="Optional BigQuery table name for overall and segment evaluation metrics.",
    )
    parser.add_argument(
        "--publish-drift-table",
        help="Optional BigQuery table name for current-scoring feature drift metrics.",
    )
    parser.add_argument(
        "--publish-model-registry-table",
        help="Optional BigQuery table name for append-only model-run metadata.",
    )
    parser.add_argument(
        "--publish-feature-importance-table",
        help="Optional BigQuery table name for held-out permutation importance.",
    )
    parser.add_argument(
        "--publish-quality-gates-table",
        help="Optional BigQuery table name for model release quality gates.",
    )
    return parser.parse_args()


def bigquery_client(args: argparse.Namespace) -> bigquery.Client:
    credentials = None
    if args.credentials:
        credentials = service_account.Credentials.from_service_account_file(
            args.credentials
        )
    return bigquery.Client(project=args.project_id, credentials=credentials)


def load_training_data(args: argparse.Namespace) -> pd.DataFrame:
    client = bigquery_client(args)
    selected_columns = [
        "training_row_key",
        "player_id",
        "player_name",
        "target_market_value_date",
        TARGET,
        *NUMERIC_FEATURES,
        *CATEGORICAL_FEATURES,
    ]
    selected_columns = list(dict.fromkeys(selected_columns))
    limit = f"limit {args.max_rows}" if args.max_rows else ""
    query = f"""
        select {", ".join(selected_columns)}
        from `{args.project_id}.{args.dataset}.{args.table}`
        where {TARGET} > 0
        order by target_market_value_date, training_row_key
        {limit}
    """
    frame = client.query(query).to_dataframe(create_bqstorage_client=False)
    for column in NUMERIC_FEATURES + [TARGET]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype(float)
    for column in CATEGORICAL_FEATURES:
        frame[column] = frame[column].astype(object).where(frame[column].notna(), np.nan)
    return frame


def load_scoring_data(args: argparse.Namespace) -> pd.DataFrame:
    client = bigquery_client(args)
    selected_columns = [
        "scoring_row_key",
        "player_id",
        "player_name",
        "prediction_as_of_date",
        *NUMERIC_FEATURES,
        *CATEGORICAL_FEATURES,
    ]
    selected_columns = list(dict.fromkeys(selected_columns))
    query = f"""
        select {", ".join(selected_columns)}
        from `{args.project_id}.{args.dataset}.{args.score_table}`
        order by scoring_row_key
    """
    frame = client.query(query).to_dataframe(create_bqstorage_client=False)
    for column in NUMERIC_FEATURES:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype(float)
    for column in CATEGORICAL_FEATURES:
        frame[column] = frame[column].astype(object).where(frame[column].notna(), np.nan)
    return frame


def load_latest_approved_model(args: argparse.Namespace) -> dict[str, object] | None:
    destination = (
        f"{args.project_id}.{args.dataset}."
        f"{args.publish_model_registry_table or 'ml_player_market_value_model_registry'}"
    )
    query = f"""
        select model_version, test_mae_eur
        from `{destination}`
        where release_status in ('approved', 'approved_with_monitoring')
        order by model_generated_at_utc desc
        limit 1
    """
    try:
        rows = list(bigquery_client(args).query(query, location="EU").result())
    except NotFound:
        return None
    return dict(rows[0].items()) if rows else None


def validate_input_frame(frame: pd.DataFrame, frame_type: str) -> None:
    if frame_type not in {"training", "scoring"}:
        raise ValueError(f"Unknown frame type: {frame_type}.")

    key_column = "training_row_key" if frame_type == "training" else "scoring_row_key"
    required_columns = {
        key_column,
        "player_id",
        "season",
        *NUMERIC_FEATURES,
        *CATEGORICAL_FEATURES,
    }
    if frame_type == "training":
        required_columns.add(TARGET)

    missing_columns = sorted(required_columns.difference(frame.columns))
    if missing_columns:
        raise ValueError(f"{frame_type} frame is missing columns: {missing_columns}.")
    if frame.empty:
        raise ValueError(f"{frame_type} frame is empty.")
    if frame[key_column].isna().any() or frame[key_column].duplicated().any():
        raise ValueError(f"{frame_type} frame has invalid keys in {key_column}.")
    if frame["player_id"].isna().any() or frame["season"].isna().any():
        raise ValueError(f"{frame_type} frame has missing player_id or season.")

    numeric_columns = [*NUMERIC_FEATURES]
    if frame_type == "training":
        numeric_columns.append(TARGET)
    numeric_values = frame[numeric_columns].to_numpy(dtype=float)
    if np.isinf(numeric_values).any():
        raise ValueError(f"{frame_type} frame contains infinite numeric values.")
    if frame_type == "training" and (frame[TARGET] <= 0).any():
        raise ValueError("Training frame contains a non-positive target.")


def feature_contract() -> dict[str, object]:
    return {
        "target": TARGET,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "prediction_quality_statuses": PREDICTION_QUALITY_STATUSES,
        "blend_strategy": "tuning_season_quality_status_weights",
        "blend_weight_overrides": PREDICTION_QUALITY_BLEND_WEIGHT_OVERRIDES,
        "prediction_interval_bands": [
            "under_1m",
            "1m_to_5m",
            "5m_to_20m",
            "20m_plus",
        ],
    }


def feature_contract_hash() -> str:
    serialized = json.dumps(feature_contract(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def runtime_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }


def git_commit_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_by_season(
    frame: pd.DataFrame, test_seasons: int
) -> tuple[pd.DataFrame, pd.DataFrame, list[int]]:
    seasons = sorted(int(season) for season in frame["season"].dropna().unique())
    if len(seasons) <= test_seasons:
        raise ValueError("Not enough distinct seasons for the requested time split.")

    held_out_seasons = seasons[-test_seasons:]
    train = frame[~frame["season"].isin(held_out_seasons)].copy()
    test = frame[frame["season"].isin(held_out_seasons)].copy()
    if train.empty or test.empty:
        raise ValueError("Time split produced an empty train or test dataset.")
    return train, test, held_out_seasons


def build_pipeline() -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median", add_indicator=True))]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    encoded_missing_value=-1,
                ),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        verbose_feature_names_out=False,
    )
    model = HistGradientBoostingRegressor(
        learning_rate=0.07,
        max_iter=300,
        max_leaf_nodes=31,
        min_samples_leaf=30,
        l2_regularization=1.0,
        random_state=42,
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def regression_metrics(
    actual: np.ndarray, predicted: np.ndarray
) -> dict[str, float | None]:
    absolute_error = np.abs(actual - predicted)
    return {
        "mae_eur": float(mean_absolute_error(actual, predicted)),
        "rmse_eur": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)) if len(actual) >= 2 else None,
        "wape_pct": float(absolute_error.sum() / actual.sum() * 100),
        "median_absolute_percentage_error_pct": float(
            np.median(absolute_error / actual) * 100
        ),
        "mean_error_eur": float(np.mean(predicted - actual)),
        "within_25_pct": float(np.mean(absolute_error / actual <= 0.25) * 100),
    }


def select_blend_weight(
    actual: np.ndarray, model_prediction: np.ndarray, baseline_prediction: np.ndarray
) -> float:
    candidates = np.linspace(0, 1, 21)
    return float(
        min(
            candidates,
            key=lambda weight: mean_absolute_error(
                actual,
                weight * model_prediction + (1 - weight) * baseline_prediction,
            ),
        )
    )


def select_blend_weights_by_quality_status(
    frame: pd.DataFrame,
    actual: np.ndarray,
    model_prediction: np.ndarray,
    baseline_prediction: np.ndarray,
    minimum_segment_rows: int = 100,
) -> dict[str, float]:
    statuses = prediction_quality_status(frame)
    weights = {
        "default": select_blend_weight(actual, model_prediction, baseline_prediction)
    }
    for status in PREDICTION_QUALITY_STATUSES:
        mask = statuses.eq(status).to_numpy()
        weights[status] = (
            select_blend_weight(
                actual[mask],
                model_prediction[mask],
                baseline_prediction[mask],
            )
            if mask.sum() >= minimum_segment_rows
            else weights["default"]
        )
    weights.update(PREDICTION_QUALITY_BLEND_WEIGHT_OVERRIDES)
    return weights


def apply_blend_weights_by_quality_status(
    frame: pd.DataFrame,
    model_prediction: np.ndarray,
    baseline_prediction: np.ndarray,
    blend_weights: dict[str, float],
) -> tuple[np.ndarray, np.ndarray]:
    selected_weights = (
        prediction_quality_status(frame)
        .map(blend_weights)
        .fillna(blend_weights["default"])
        .to_numpy(dtype=float)
    )
    predictions = (
        selected_weights * model_prediction
        + (1 - selected_weights) * baseline_prediction
    )
    return predictions, selected_weights


def prediction_quality_status(frame: pd.DataFrame) -> pd.Series:
    high = (
        frame["previous_market_value_eur"].notna()
        & frame["age_at_target_date"].notna()
        & frame["competition_id"].notna()
        & frame["minutes_before_target"].ge(450)
    )
    medium = (
        frame["previous_market_value_eur"].notna()
        & frame["age_at_target_date"].notna()
        & frame["minutes_before_target"].gt(0)
    )
    return pd.Series(
        np.select([high, medium], ["high", "medium"], default="limited"),
        index=frame.index,
    )


def validate_predictions(
    predictions: pd.DataFrame, key_column: str, prediction_column: str
) -> None:
    if predictions[key_column].duplicated().any():
        raise ValueError(f"Duplicate prediction keys found in {key_column}.")
    values = predictions[prediction_column].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError(f"Invalid values found in {prediction_column}.")
    interval_columns = {
        "prediction_interval_band",
        "prediction_interval_eur",
        "prediction_lower_eur",
        "prediction_upper_eur",
    }
    if interval_columns.issubset(predictions.columns):
        interval_widths = predictions["prediction_interval_eur"].to_numpy(dtype=float)
        lower = predictions["prediction_lower_eur"].to_numpy(dtype=float)
        upper = predictions["prediction_upper_eur"].to_numpy(dtype=float)
        if (
            not np.isfinite(interval_widths).all()
            or (interval_widths <= 0).any()
            or predictions["prediction_interval_band"].isna().any()
            or (lower < 0).any()
            or (lower > values).any()
            or (upper < values).any()
        ):
            raise ValueError("Invalid prediction intervals found.")


def value_band(values: pd.Series) -> pd.Series:
    return pd.cut(
        values,
        bins=[0, 1_000_000, 5_000_000, 20_000_000, np.inf],
        labels=["under_1m", "1m_to_5m", "5m_to_20m", "20m_plus"],
        include_lowest=True,
        right=False,
    ).astype(str)


def calibrate_prediction_intervals(
    actual: np.ndarray, predicted: np.ndarray, quantile: float = 0.9
) -> tuple[float, dict[str, float]]:
    absolute_error = np.abs(actual - predicted)
    default_interval = float(np.quantile(absolute_error, quantile, method="higher"))
    predicted_bands = value_band(pd.Series(predicted)).to_numpy()
    interval_by_band = {
        band: float(
            np.quantile(absolute_error[predicted_bands == band], quantile, method="higher")
        )
        for band in np.unique(predicted_bands)
    }
    return default_interval, interval_by_band


def prediction_interval_widths(
    predicted: np.ndarray,
    default_interval: float,
    interval_by_band: dict[str, float],
) -> tuple[np.ndarray, np.ndarray]:
    bands = value_band(pd.Series(predicted))
    widths = bands.map(interval_by_band).fillna(default_interval).to_numpy(dtype=float)
    return bands.to_numpy(), widths


def evaluation_metrics(predictions: pd.DataFrame, model_version: str) -> pd.DataFrame:
    frame = predictions.copy()
    frame["value_band"] = value_band(frame[TARGET])
    frame["has_previous_market_value"] = frame["previous_market_value_eur"].notna()
    frame["age_band"] = pd.cut(
        frame["age_at_target_date"],
        bins=[0, 21, 24, 28, 32, np.inf],
        labels=["under_21", "21_to_23", "24_to_27", "28_to_31", "32_plus"],
        include_lowest=True,
        right=False,
    ).astype(str)

    segments = [("overall", None)]
    for column in [
        "season",
        "position",
        "sub_position",
        "age_band",
        "competition_id",
        "competition_country_name",
        "value_band",
        "has_previous_market_value",
        "prediction_quality_status",
    ]:
        segments.extend(
            (column, value) for value in frame[column].dropna().drop_duplicates()
        )

    rows: list[dict[str, object]] = []
    for segment_type, segment_value in segments:
        segment = (
            frame
            if segment_type == "overall"
            else frame[frame[segment_type] == segment_value]
        )
        actual = segment[TARGET].to_numpy(dtype=float)
        predicted = segment["predicted_market_value_eur"].to_numpy(dtype=float)
        baseline = segment["baseline_prediction_eur"].to_numpy(dtype=float)
        model_metrics = regression_metrics(actual, predicted)
        baseline_metrics = regression_metrics(actual, baseline)
        rows.append(
            {
                "model_version": model_version,
                "segment_type": segment_type,
                "segment_value": "all" if segment_value is None else str(segment_value),
                "row_count": len(segment),
                "minimum_sample_size": 30,
                "meets_minimum_sample_size": len(segment) >= 30,
                **model_metrics,
                "baseline_mae_eur": baseline_metrics["mae_eur"],
                "mae_improvement_vs_baseline_pct": (
                    (baseline_metrics["mae_eur"] - model_metrics["mae_eur"])
                    / baseline_metrics["mae_eur"]
                    * 100
                    if baseline_metrics["mae_eur"]
                    else 0
                ),
                "interval_coverage_pct": float(
                    (
                        (segment[TARGET] >= segment["prediction_lower_eur"])
                        & (segment[TARGET] <= segment["prediction_upper_eur"])
                    ).mean()
                    * 100
                ),
            }
        )
    return pd.DataFrame(rows)


def feature_importance_report(
    pipeline: Pipeline,
    test: pd.DataFrame,
    model_version: str,
) -> pd.DataFrame:
    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    result = permutation_importance(
        pipeline,
        test[features],
        test[TARGET],
        scoring="neg_mean_absolute_error",
        n_repeats=3,
        random_state=42,
        n_jobs=-1,
    )
    report = pd.DataFrame(
        {
            "model_version": model_version,
            "feature": features,
            "feature_type": [
                "numeric" if feature in NUMERIC_FEATURES else "categorical"
                for feature in features
            ],
            "mae_increase_eur_mean": result.importances_mean,
            "mae_increase_eur_std": result.importances_std,
        }
    ).sort_values("mae_increase_eur_mean", ascending=False)
    report["importance_rank"] = np.arange(1, len(report) + 1)
    return report


def quality_gate_report(
    metrics: dict[str, object],
    segment_metrics: pd.DataFrame,
    model_version: str,
    generated_at: datetime,
    champion: dict[str, object] | None = None,
    current_predictions: pd.DataFrame | None = None,
    drift: pd.DataFrame | None = None,
) -> pd.DataFrame:
    ensemble = metrics["ensemble_model"]
    baseline = metrics["previous_value_baseline"]
    overall_interval_coverage = float(
        segment_metrics.loc[
            segment_metrics["segment_type"].eq("overall"),
            "interval_coverage_pct",
        ].iloc[0]
    )
    elite_rows = segment_metrics[
        segment_metrics["segment_type"].eq("value_band")
        & segment_metrics["segment_value"].eq("20m_plus")
    ]
    elite_interval_coverage = (
        float(elite_rows["interval_coverage_pct"].iloc[0])
        if not elite_rows.empty
        else 0.0
    )
    mae_improvement = (
        (baseline["mae_eur"] - ensemble["mae_eur"]) / baseline["mae_eur"] * 100
    )

    rows: list[dict[str, object]] = []

    def add_gate(
        gate_name: str,
        actual_value: float,
        threshold_operator: str,
        threshold_value: float,
        passed: bool,
        severity: str,
        details: str,
    ) -> None:
        rows.append(
            {
                "model_version": model_version,
                "model_generated_at_utc": generated_at,
                "gate_name": gate_name,
                "actual_value": float(actual_value),
                "threshold_operator": threshold_operator,
                "threshold_value": float(threshold_value),
                "passed": bool(passed),
                "severity": severity,
                "details": details,
            }
        )

    add_gate(
        "mae_improvement_vs_baseline_pct",
        mae_improvement,
        ">",
        BLOCKING_GATE_THRESHOLDS["mae_improvement_vs_baseline_pct"],
        mae_improvement > BLOCKING_GATE_THRESHOLDS["mae_improvement_vs_baseline_pct"],
        "blocking",
        "The ensemble must improve held-out MAE versus the previous-value baseline.",
    )
    add_gate(
        "held_out_wape_pct",
        ensemble["wape_pct"],
        "<=",
        BLOCKING_GATE_THRESHOLDS["wape_pct"],
        ensemble["wape_pct"] <= BLOCKING_GATE_THRESHOLDS["wape_pct"],
        "blocking",
        "Held-out WAPE must remain within the production error budget.",
    )
    add_gate(
        "held_out_r2",
        ensemble["r2"],
        ">=",
        BLOCKING_GATE_THRESHOLDS["r2"],
        ensemble["r2"] >= BLOCKING_GATE_THRESHOLDS["r2"],
        "blocking",
        "Held-out R2 must meet the minimum explanatory-performance threshold.",
    )
    add_gate(
        "overall_interval_coverage_pct",
        overall_interval_coverage,
        ">=",
        BLOCKING_GATE_THRESHOLDS["overall_interval_coverage_pct"],
        overall_interval_coverage
        >= BLOCKING_GATE_THRESHOLDS["overall_interval_coverage_pct"],
        "blocking",
        "Overall held-out prediction interval coverage must remain reliable.",
    )
    add_gate(
        "elite_interval_coverage_pct",
        elite_interval_coverage,
        ">=",
        BLOCKING_GATE_THRESHOLDS["elite_interval_coverage_pct"],
        elite_interval_coverage
        >= BLOCKING_GATE_THRESHOLDS["elite_interval_coverage_pct"],
        "blocking",
        "Actual EUR 20M+ player interval coverage must remain reliable.",
    )
    quality_segments = segment_metrics[
        segment_metrics["segment_type"].eq("prediction_quality_status")
    ]
    worst_quality_segment_improvement = (
        float(quality_segments["mae_improvement_vs_baseline_pct"].min())
        if not quality_segments.empty
        else -100.0
    )
    add_gate(
        "worst_quality_segment_mae_improvement_vs_baseline_pct",
        worst_quality_segment_improvement,
        ">=",
        BLOCKING_GATE_THRESHOLDS[
            "quality_segment_mae_improvement_vs_baseline_pct"
        ],
        worst_quality_segment_improvement
        >= BLOCKING_GATE_THRESHOLDS[
            "quality_segment_mae_improvement_vs_baseline_pct"
        ],
        "blocking",
        "No prediction-quality segment may underperform its previous-value baseline.",
    )
    if champion is not None:
        champion_mae_regression_pct = (
            (ensemble["mae_eur"] - champion["test_mae_eur"])
            / champion["test_mae_eur"]
            * 100
        )
        add_gate(
            "champion_mae_regression_pct",
            champion_mae_regression_pct,
            "<=",
            BLOCKING_GATE_THRESHOLDS["champion_mae_regression_pct"],
            champion_mae_regression_pct
            <= BLOCKING_GATE_THRESHOLDS["champion_mae_regression_pct"],
            "blocking",
            f"Candidate MAE must not regress materially versus {champion['model_version']}.",
        )

    if current_predictions is not None:
        limited_pct = float(
            current_predictions["prediction_quality_status"].eq("limited").mean() * 100
        )
        add_gate(
            "current_limited_prediction_pct",
            limited_pct,
            "<=",
            25.0,
            limited_pct <= 25.0,
            "warning",
            "A high limited-quality share requires analyst review before BI refresh.",
        )
    if drift is not None:
        significant_drift_count = int(drift["drift_status"].eq("significant").sum())
        add_gate(
            "significant_drift_feature_count",
            significant_drift_count,
            "<=",
            0.0,
            significant_drift_count == 0,
            "warning",
            "Significant feature drift requires analyst review but does not auto-reject.",
        )
    return pd.DataFrame(rows)


def release_status(quality_gates: pd.DataFrame) -> str:
    blocking_failed = (
        quality_gates["severity"].eq("blocking") & ~quality_gates["passed"]
    ).any()
    warning_failed = (
        quality_gates["severity"].eq("warning") & ~quality_gates["passed"]
    ).any()
    if blocking_failed:
        return "rejected"
    return "approved_with_monitoring" if warning_failed else "approved"


def assert_blocking_quality_gates(quality_gates: pd.DataFrame) -> None:
    failed = quality_gates[
        quality_gates["severity"].eq("blocking") & ~quality_gates["passed"]
    ]
    if not failed.empty:
        gate_names = ", ".join(failed["gate_name"].tolist())
        raise ValueError(f"Blocking model quality gates failed: {gate_names}.")


def population_stability_index(
    reference: pd.Series, current: pd.Series, numeric: bool
) -> float:
    epsilon = 1e-6
    if numeric:
        reference_numeric = pd.to_numeric(reference, errors="coerce")
        current_numeric = pd.to_numeric(current, errors="coerce")
        quantiles = np.unique(
            reference_numeric.dropna().quantile(np.linspace(0, 1, 11)).to_numpy()
        )
        if len(quantiles) < 2:
            return 0.0
        quantiles[0], quantiles[-1] = -np.inf, np.inf
        reference_counts = pd.cut(reference_numeric, quantiles).value_counts(
            sort=False, normalize=True
        )
        current_counts = pd.cut(current_numeric, quantiles).value_counts(
            sort=False, normalize=True
        )
    else:
        reference_counts = (
            reference.fillna("__missing__").astype(str).value_counts(normalize=True)
        )
        current_counts = (
            current.fillna("__missing__").astype(str).value_counts(normalize=True)
        )
        categories = reference_counts.index.union(current_counts.index)
        reference_counts = reference_counts.reindex(categories, fill_value=0)
        current_counts = current_counts.reindex(categories, fill_value=0)

    reference_distribution = np.clip(reference_counts.to_numpy(), epsilon, None)
    current_distribution = np.clip(current_counts.to_numpy(), epsilon, None)
    return float(
        np.sum(
            (current_distribution - reference_distribution)
            * np.log(current_distribution / reference_distribution)
        )
    )


def feature_drift_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    model_version: str,
) -> pd.DataFrame:
    rows = []
    reference_season_min = int(reference["season"].min())
    reference_season_max = int(reference["season"].max())
    current_season_min = int(current["season"].min())
    current_season_max = int(current["season"].max())
    for feature, feature_type in [
        *((feature, "numeric") for feature in NUMERIC_FEATURES),
        *((feature, "categorical") for feature in CATEGORICAL_FEATURES),
    ]:
        psi = population_stability_index(
            reference[feature], current[feature], numeric=feature_type == "numeric"
        )
        rows.append(
            {
                "model_version": model_version,
                "feature": feature,
                "feature_type": feature_type,
                "psi": psi,
                "drift_status": (
                    "stable" if psi < 0.1 else "monitor" if psi < 0.25 else "significant"
                ),
                "reference_row_count": len(reference),
                "current_row_count": len(current),
                "reference_season_min": reference_season_min,
                "reference_season_max": reference_season_max,
                "current_season_min": current_season_min,
                "current_season_max": current_season_max,
                "reference_missing_pct": float(reference[feature].isna().mean() * 100),
                "current_missing_pct": float(current[feature].isna().mean() * 100),
            }
        )
    return pd.DataFrame(rows)


def publish_predictions(
    args: argparse.Namespace,
    predictions: pd.DataFrame,
    table_name: str | None,
    write_disposition: str = bigquery.WriteDisposition.WRITE_TRUNCATE,
) -> str | None:
    if not table_name:
        return None

    destination = f"{args.project_id}.{args.dataset}.{table_name}"
    job_config = bigquery.LoadJobConfig(write_disposition=write_disposition)
    if write_disposition == bigquery.WriteDisposition.WRITE_APPEND:
        job_config.schema_update_options = [
            bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
        ]
    bigquery_client(args).load_table_from_dataframe(
        predictions, destination, job_config=job_config
    ).result()
    return destination


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frame = load_training_data(args)
    validate_input_frame(frame, "training")
    contract_hash = feature_contract_hash()
    source_commit_sha = git_commit_sha()
    package_versions = runtime_versions()
    champion = (
        load_latest_approved_model(args) if args.publish_model_registry_table else None
    )
    train, test, held_out_seasons = split_by_season(frame, args.test_seasons)
    pre_test_seasons = sorted(int(season) for season in train["season"].unique())
    if len(pre_test_seasons) < 3:
        raise ValueError("At least three pre-test seasons are required.")
    tuning_season = pre_test_seasons[-2]
    calibration_season = pre_test_seasons[-1]
    development = train[train["season"] < tuning_season].copy()
    tuning = train[train["season"] == tuning_season].copy()
    calibration_training = train[train["season"] <= tuning_season].copy()
    calibration = train[train["season"] == calibration_season].copy()
    if development.empty or tuning.empty or calibration.empty:
        raise ValueError("Tuning or calibration split produced an empty dataset.")

    tuning_pipeline = build_pipeline()
    tuning_pipeline.fit(
        development[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
        development[TARGET],
    )
    tuning_model_prediction = np.maximum(
        tuning_pipeline.predict(tuning[NUMERIC_FEATURES + CATEGORICAL_FEATURES]),
        0,
    )
    tuning_baseline_fill = float(development[TARGET].median())
    tuning_baseline_prediction = (
        tuning["previous_market_value_eur"]
        .fillna(tuning_baseline_fill)
        .to_numpy()
    )
    blend_weights = select_blend_weights_by_quality_status(
        tuning,
        tuning[TARGET].to_numpy(),
        tuning_model_prediction,
        tuning_baseline_prediction,
    )

    calibration_pipeline = build_pipeline()
    calibration_pipeline.fit(
        calibration_training[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
        calibration_training[TARGET],
    )
    calibration_model_prediction = np.maximum(
        calibration_pipeline.predict(
            calibration[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        ),
        0,
    )
    calibration_baseline = (
        calibration["previous_market_value_eur"]
        .fillna(float(calibration_training[TARGET].median()))
        .to_numpy()
    )
    calibration_prediction, _ = apply_blend_weights_by_quality_status(
        calibration,
        calibration_model_prediction,
        calibration_baseline,
        blend_weights,
    )
    conformal_interval_eur, conformal_interval_by_predicted_value_band = (
        calibrate_prediction_intervals(
            calibration[TARGET].to_numpy(),
            calibration_prediction,
        )
    )

    generated_at = datetime.now(timezone.utc)
    version_input = (
        f"{generated_at.isoformat()}-{len(frame)}-{frame[TARGET].sum()}-"
        f"{tuning_season}-{calibration_season}-"
        f"{json.dumps(blend_weights, sort_keys=True)}-{contract_hash}"
    )
    model_version = (
        f"{MODEL_NAME}_{MODEL_VERSION}_"
        f"{generated_at:%Y%m%dT%H%M%SZ}_"
        f"{hashlib.sha256(version_input.encode()).hexdigest()[:8]}"
    )

    pipeline = build_pipeline()
    pipeline.fit(train[NUMERIC_FEATURES + CATEGORICAL_FEATURES], train[TARGET])
    model_prediction = np.maximum(
        pipeline.predict(test[NUMERIC_FEATURES + CATEGORICAL_FEATURES]),
        0,
    )
    baseline_fill = float(train[TARGET].median())
    baseline_prediction = (
        test["previous_market_value_eur"].fillna(baseline_fill).to_numpy()
    )
    predicted, test_blend_weights = apply_blend_weights_by_quality_status(
        test,
        model_prediction,
        baseline_prediction,
        blend_weights,
    )
    prediction_interval_band, prediction_interval_eur = prediction_interval_widths(
        predicted,
        conformal_interval_eur,
        conformal_interval_by_predicted_value_band,
    )
    actual = test[TARGET].to_numpy()

    metrics = {
        "training_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_season_min": int(train["season"].min()),
        "train_season_max": int(train["season"].max()),
        "tuning_season": tuning_season,
        "calibration_season": calibration_season,
        "held_out_test_seasons": held_out_seasons,
        "target_transform": "none",
        "selected_ml_blend_weight": blend_weights["default"],
        "selected_ml_blend_weights_by_quality_status": blend_weights,
        "conformal_prediction_interval_eur_90": conformal_interval_eur,
        "conformal_prediction_interval_by_predicted_value_band_eur_90": (
            conformal_interval_by_predicted_value_band
        ),
        "model_version": model_version,
        "feature_contract_hash": contract_hash,
        "source_commit_sha": source_commit_sha,
        "runtime_versions": package_versions,
        "champion_model_version": champion["model_version"] if champion else None,
        "champion_test_mae_eur": champion["test_mae_eur"] if champion else None,
        "ensemble_model": regression_metrics(actual, predicted),
        "ml_only_model": regression_metrics(actual, model_prediction),
        "previous_value_baseline": regression_metrics(actual, baseline_prediction),
    }

    predictions = test[
        [
            "training_row_key",
            "player_id",
            "player_name",
            "season",
            "competition_id",
            "target_market_value_date",
            TARGET,
            "previous_market_value_eur",
            *METADATA_COLUMNS,
        ]
    ].copy()
    predictions["ml_only_prediction_eur"] = model_prediction.round(0)
    predictions["baseline_prediction_eur"] = baseline_prediction.round(0)
    predictions["predicted_market_value_eur"] = predicted.round(0)
    predictions["absolute_error_eur"] = np.abs(actual - predicted).round(0)
    predictions["prediction_interval_band"] = prediction_interval_band
    predictions["prediction_interval_eur"] = prediction_interval_eur.round(0)
    predictions["prediction_lower_eur"] = np.maximum(
        predicted - prediction_interval_eur, 0
    ).round(0)
    predictions["prediction_upper_eur"] = (predicted + prediction_interval_eur).round(0)
    predictions["prediction_quality_status"] = prediction_quality_status(test)
    predictions["selected_ml_blend_weight"] = test_blend_weights
    predictions["model_version"] = model_version
    predictions["model_generated_at_utc"] = generated_at
    validate_predictions(
        predictions, "training_row_key", "predicted_market_value_eur"
    )
    segment_metrics = evaluation_metrics(predictions, model_version)
    feature_importance = feature_importance_report(pipeline, test, model_version)

    final_pipeline = build_pipeline()
    final_pipeline.fit(
        frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
        frame[TARGET],
    )

    current_predictions = None
    drift = None
    should_score_current = any(
        [
            args.publish_current_predictions_table,
            args.publish_drift_table,
            args.publish_quality_gates_table,
        ]
    )
    if should_score_current:
        current_predictions = load_scoring_data(args)
        validate_input_frame(current_predictions, "scoring")
        scoring_ml_prediction = np.maximum(
            final_pipeline.predict(
                current_predictions[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
            ),
            0,
        )
        scoring_baseline = (
            current_predictions["previous_market_value_eur"]
            .fillna(float(frame[TARGET].median()))
            .to_numpy()
        )
        current_predictions["ml_only_prediction_eur"] = scoring_ml_prediction.round(0)
        current_predictions["baseline_prediction_eur"] = scoring_baseline.round(0)
        scoring_prediction, scoring_blend_weights = (
            apply_blend_weights_by_quality_status(
                current_predictions,
                scoring_ml_prediction,
                scoring_baseline,
                blend_weights,
            )
        )
        current_predictions["predicted_market_value_eur"] = scoring_prediction.round(0)
        scoring_interval_band, scoring_interval_eur = prediction_interval_widths(
            current_predictions["predicted_market_value_eur"].to_numpy(dtype=float),
            conformal_interval_eur,
            conformal_interval_by_predicted_value_band,
        )
        current_predictions["prediction_interval_band"] = scoring_interval_band
        current_predictions["prediction_interval_eur"] = scoring_interval_eur.round(0)
        current_predictions["prediction_lower_eur"] = np.maximum(
            current_predictions["predicted_market_value_eur"] - scoring_interval_eur, 0
        ).round(0)
        current_predictions["prediction_upper_eur"] = (
            current_predictions["predicted_market_value_eur"] + scoring_interval_eur
        ).round(0)
        current_predictions["prediction_delta_vs_previous_eur"] = (
            current_predictions["predicted_market_value_eur"]
            - current_predictions["previous_market_value_eur"]
        ).round(0)
        current_predictions["prediction_delta_vs_previous_pct"] = (
            current_predictions["prediction_delta_vs_previous_eur"]
            / current_predictions["previous_market_value_eur"].replace(0, np.nan)
            * 100
        ).round(2)
        current_predictions["prediction_quality_status"] = prediction_quality_status(
            current_predictions
        )
        current_predictions["kalite_etiketi_tr"] = (
            current_predictions["prediction_quality_status"]
            .map({"high": "Yüksek", "medium": "Orta", "limited": "Sınırlı"})
            .fillna(current_predictions["prediction_quality_status"])
        )
        current_predictions["pozisyon_tr"] = (
            current_predictions["position"]
            .map({
                "Attack": "Forvet",
                "Defender": "Defans",
                "Goalkeeper": "Kaleci",
                "Midfield": "Orta Saha",
                "Missing": "Bilinmiyor",
            })
            .fillna("Bilinmiyor")
        )
        current_predictions["prediction_is_out_of_time"] = (
            current_predictions["season"] > frame["season"].max()
        )
        current_predictions["selected_ml_blend_weight"] = scoring_blend_weights
        current_predictions["model_version"] = model_version
        current_predictions["model_generated_at_utc"] = generated_at
        validate_predictions(
            current_predictions, "scoring_row_key", "predicted_market_value_eur"
        )
        drift_reference = frame[frame["season"] == frame["season"].max()]
        drift = feature_drift_report(
            drift_reference,
            current_predictions,
            model_version,
        )

    quality_gates = quality_gate_report(
        metrics,
        segment_metrics,
        model_version,
        generated_at,
        champion=champion,
        current_predictions=current_predictions,
        drift=drift,
    )
    status = release_status(quality_gates)
    metrics["release_status"] = status
    metrics["blocking_quality_gates_passed"] = bool(
        (
            quality_gates.loc[
                quality_gates["severity"].eq("blocking"),
                "passed",
            ]
        ).all()
    )
    metrics["warning_quality_gates_failed"] = int(
        (
            quality_gates["severity"].eq("warning")
            & ~quality_gates["passed"]
        ).sum()
    )

    model_bundle = {
        "pipeline": final_pipeline,
        "evaluation_pipeline": pipeline,
        "selected_ml_blend_weight": blend_weights["default"],
        "selected_ml_blend_weights_by_quality_status": blend_weights,
        "baseline_fill_value_eur": float(frame[TARGET].median()),
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "held_out_test_seasons": held_out_seasons,
        "conformal_prediction_interval_eur_90": conformal_interval_eur,
        "conformal_prediction_interval_by_predicted_value_band_eur_90": (
            conformal_interval_by_predicted_value_band
        ),
        "model_name": MODEL_NAME,
        "model_version": model_version,
        "release_status": status,
        "feature_contract": feature_contract(),
        "feature_contract_hash": contract_hash,
        "blocking_gate_thresholds": BLOCKING_GATE_THRESHOLDS,
        "runtime_versions": package_versions,
        "source_commit_sha": source_commit_sha,
        "model_generated_at_utc": generated_at.isoformat(),
    }
    model_path = output_dir / "model.joblib"
    joblib.dump(model_bundle, model_path)
    model_artifact_sha256 = file_sha256(model_path)
    metrics["model_artifact_sha256"] = model_artifact_sha256

    predictions.to_csv(output_dir / "test_predictions.csv", index=False)
    segment_metrics.to_csv(output_dir / "evaluation_metrics.csv", index=False)
    feature_importance.to_csv(output_dir / "feature_importance.csv", index=False)
    quality_gates.to_csv(output_dir / "quality_gates.csv", index=False)
    if current_predictions is not None:
        current_predictions.to_csv(output_dir / "current_predictions.csv", index=False)
    if drift is not None:
        drift.to_csv(output_dir / "feature_drift.csv", index=False)
    (output_dir / "feature_contract.json").write_text(
        json.dumps(feature_contract(), indent=2), encoding="utf-8"
    )
    artifact_manifest = {
        "model_name": MODEL_NAME,
        "model_version": model_version,
        "release_status": status,
        "model_generated_at_utc": generated_at.isoformat(),
        "model_artifact_sha256": model_artifact_sha256,
        "feature_contract_hash": contract_hash,
        "source_commit_sha": source_commit_sha,
        "runtime_versions": package_versions,
        "production_training_rows": len(frame),
        "production_train_season_min": int(frame["season"].min()),
        "production_train_season_max": int(frame["season"].max()),
    }
    (output_dir / "artifact_manifest.json").write_text(
        json.dumps(artifact_manifest, indent=2), encoding="utf-8"
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    assert_blocking_quality_gates(quality_gates)

    metrics["published_predictions_table"] = publish_predictions(
        args, predictions, args.publish_predictions_table
    )
    metrics["published_evaluation_metrics_table"] = publish_predictions(
        args, segment_metrics, args.publish_evaluation_metrics_table
    )
    metrics["published_current_predictions_table"] = publish_predictions(
        args, current_predictions, args.publish_current_predictions_table
    )
    metrics["published_drift_table"] = publish_predictions(
        args, drift, args.publish_drift_table
    )
    metrics["published_feature_importance_table"] = publish_predictions(
        args, feature_importance, args.publish_feature_importance_table
    )
    metrics["published_quality_gates_table"] = publish_predictions(
        args, quality_gates, args.publish_quality_gates_table
    )

    registry = pd.DataFrame(
        [
            {
                "model_name": MODEL_NAME,
                "model_version": model_version,
                "model_generated_at_utc": generated_at,
                "release_status": status,
                "blocking_quality_gates_passed": metrics[
                    "blocking_quality_gates_passed"
                ],
                "warning_quality_gates_failed": metrics[
                    "warning_quality_gates_failed"
                ],
                "model_artifact_sha256": model_artifact_sha256,
                "feature_contract_hash": contract_hash,
                "source_commit_sha": source_commit_sha,
                "runtime_versions": json.dumps(package_versions, sort_keys=True),
                "training_rows": len(train),
                "test_rows": len(test),
                "train_season_min": int(train["season"].min()),
                "train_season_max": int(train["season"].max()),
                "evaluation_training_rows": len(train),
                "production_training_rows": len(frame),
                "evaluation_train_season_min": int(train["season"].min()),
                "evaluation_train_season_max": int(train["season"].max()),
                "production_train_season_min": int(frame["season"].min()),
                "production_train_season_max": int(frame["season"].max()),
                "tuning_season": tuning_season,
                "calibration_season": calibration_season,
                "test_seasons": ",".join(str(season) for season in held_out_seasons),
                "selected_ml_blend_weight": blend_weights["default"],
                "selected_ml_blend_weights_by_quality_status": json.dumps(
                    blend_weights,
                    sort_keys=True,
                ),
                "conformal_prediction_interval_eur_90": conformal_interval_eur,
                "conformal_prediction_interval_by_predicted_value_band_eur_90": (
                    json.dumps(
                        conformal_interval_by_predicted_value_band,
                        sort_keys=True,
                    )
                ),
                **{
                    f"test_{key}": value
                    for key, value in metrics["ensemble_model"].items()
                },
            }
        ]
    )
    metrics["published_model_registry_table"] = publish_predictions(
        args,
        registry,
        args.publish_model_registry_table,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
