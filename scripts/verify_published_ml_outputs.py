"""Verify the published BigQuery player market value ML outputs."""

from __future__ import annotations

import argparse

from google.cloud import bigquery
from google.oauth2 import service_account


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--dataset", default="football_ml")
    parser.add_argument("--credentials")
    return parser.parse_args()


def bigquery_client(args: argparse.Namespace) -> bigquery.Client:
    credentials = None
    if args.credentials:
        credentials = service_account.Credentials.from_service_account_file(
            args.credentials
        )
    return bigquery.Client(project=args.project_id, credentials=credentials)


def main() -> None:
    args = parse_args()
    prefix = f"`{args.project_id}.{args.dataset}"
    query = f"""
        with latest as (
            select model_version, release_status
            from {prefix}.ml_player_market_value_model_registry`
            order by model_generated_at_utc desc
            limit 1
        )

        select
            latest.model_version,
            latest.release_status,
            (
                select count(*)
                from {prefix}.ml_player_market_value_quality_gates`
                where severity = 'blocking' and not passed
            ) as blocking_gate_failures,
            (
                select count(*)
                from {prefix}.ml_player_market_value_current_predictions`
            ) as current_prediction_rows,
            (
                select count(*)
                from {prefix}.ml_player_market_value_current_predictions`
                where model_version != latest.model_version
                    or predicted_market_value_eur < 0
                    or prediction_interval_eur <= 0
                    or prediction_lower_eur > predicted_market_value_eur
                    or prediction_upper_eur < predicted_market_value_eur
                    or selected_ml_blend_weight not between 0 and 1
                    or (
                        prediction_quality_status = 'limited'
                        and selected_ml_blend_weight != 0
                    )
            ) as invalid_current_predictions,
            (
                select count(*)
                from {prefix}.ml_player_market_value_evaluation_predictions`
                where predicted_market_value_eur < 0
                    or prediction_interval_eur <= 0
                    or prediction_lower_eur > predicted_market_value_eur
                    or prediction_upper_eur < predicted_market_value_eur
                    or selected_ml_blend_weight not between 0 and 1
                    or (
                        prediction_quality_status = 'limited'
                        and selected_ml_blend_weight != 0
                    )
            ) as invalid_evaluation_predictions,
            (
                select count(*)
                from {prefix}.ml_player_market_value_evaluation_predictions`
                where model_version != latest.model_version
            ) as evaluation_version_mismatches,
            (
                select count(*)
                from {prefix}.ml_player_market_value_evaluation_metrics`
                where model_version != latest.model_version
            ) as metric_version_mismatches,
            (
                select count(*)
                from {prefix}.ml_player_market_value_evaluation_metrics`
                where row_count <= 0
                    or minimum_sample_size != 30
                    or meets_minimum_sample_size != (row_count >= minimum_sample_size)
            ) as invalid_segment_metrics,
            (
                select count(*)
                from {prefix}.ml_player_market_value_feature_drift`
                where model_version != latest.model_version
            ) as drift_version_mismatches,
            (
                select count(*)
                from {prefix}.ml_player_market_value_feature_importance`
                where model_version != latest.model_version
            ) as importance_version_mismatches,
            (
                select count(*)
                from {prefix}.ml_player_market_value_quality_gates`
                where model_version != latest.model_version
            ) as gate_version_mismatches

        from latest
    """
    rows = list(bigquery_client(args).query(query, location="EU").result())
    if len(rows) != 1:
        raise ValueError("Published ML verification could not identify one latest model.")

    result = dict(rows[0].items())
    if result["release_status"] == "rejected":
        raise ValueError("Latest published model is rejected.")
    if result["current_prediction_rows"] <= 0:
        raise ValueError("Published current predictions are empty.")

    failure_fields = [
        "blocking_gate_failures",
        "invalid_current_predictions",
        "invalid_evaluation_predictions",
        "evaluation_version_mismatches",
        "metric_version_mismatches",
        "invalid_segment_metrics",
        "drift_version_mismatches",
        "importance_version_mismatches",
        "gate_version_mismatches",
    ]
    failures = {
        field: result[field]
        for field in failure_fields
        if result[field] != 0
    }
    if failures:
        raise ValueError(f"Published ML verification failed: {failures}.")

    print(
        f"Published ML outputs verified: {result['model_version']} "
        f"({result['release_status']})."
    )


if __name__ == "__main__":
    main()
