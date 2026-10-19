-- RESEARCH-ONLY, READ-ONLY diagnostics. Requires an explicitly authorized
-- BigQuery/dbt profile and fresh governed source tables; no live claim is made.
-- Reconciles population/key grains, temporal source leakage and coverage.
--
-- Example (only after permission/cost review):
--   dbt compile --select ml_player_market_value_training ml_player_market_value_scoring
--   dbt show --inline "$(cat analyses/audit_ml_feature_lineage_20261019.sql)"
--
-- Do not publish counts from a stale feature table as current model statistics.
with training as (
    select
        'historical_training' as population,
        count(*) as row_count,
        count(distinct training_row_key) as distinct_keys,
        count(distinct player_id) as distinct_players,
        min(season) as earliest_season,
        max(season) as latest_season,
        min(target_market_value_date) as earliest_target_or_asof_date,
        max(target_market_value_date) as latest_target_or_asof_date,
        countif(target_market_value_eur is null or target_market_value_eur <= 0)
            as nonpositive_or_missing_targets,
        countif(feature_last_appearance_date >= target_market_value_date)
            as invalid_appearance_timestamps,
        countif(previous_market_value_date >= target_market_value_date)
            as invalid_prior_valuation_timestamps,
        countif(previous_market_value_eur < 0) as negative_prior_values,
        countif(previous_market_value_eur is null) as missing_prior_values,
        countif(prior_valuation_count < 0) as negative_valuation_counts
    from {{ ref('ml_player_market_value_training') }}
),
scoring as (
    select
        'current_scoring' as population,
        count(*) as row_count,
        count(distinct scoring_row_key) as distinct_keys,
        count(distinct player_id) as distinct_players,
        min(season) as earliest_season,
        max(season) as latest_season,
        min(prediction_as_of_date) as earliest_target_or_asof_date,
        max(prediction_as_of_date) as latest_target_or_asof_date,
        cast(null as int64) as nonpositive_or_missing_targets,
        countif(feature_last_appearance_date > prediction_as_of_date)
            as invalid_appearance_timestamps,
        countif(previous_market_value_date > prediction_as_of_date)
            as invalid_prior_valuation_timestamps,
        countif(previous_market_value_eur < 0) as negative_prior_values,
        countif(previous_market_value_eur is null) as missing_prior_values,
        countif(prior_valuation_count < 0) as negative_valuation_counts
    from {{ ref('ml_player_market_value_scoring') }}
)
select * from training
union all
select * from scoring
