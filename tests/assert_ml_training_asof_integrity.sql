-- Singular, read-only dbt test: return ONLY invalid historical training rows.
-- Training model features must predate the supervised valuation event.
-- This query does not update BigQuery or run without a separately authorized
-- dbt test against the governed warehouse.
select
    training_row_key,
    player_id,
    season,
    target_market_value_date,
    feature_last_appearance_date,
    previous_market_value_date,
    previous_market_value_eur,
    prior_valuation_count,
    days_since_previous_market_value
from {{ ref('ml_player_market_value_training') }}
where target_market_value_eur is null
    or target_market_value_eur <= 0
    or feature_last_appearance_date >= target_market_value_date
    or previous_market_value_date >= target_market_value_date
    or previous_market_value_eur < 0
    or prior_valuation_count < 0
    or days_since_previous_market_value < 1
    or (has_previous_market_value and previous_market_value_eur is null)
    or (not has_previous_market_value and previous_market_value_eur is not null)
