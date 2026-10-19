-- Singular, read-only dbt test: return ONLY invalid current scoring rows.
-- Scoring features must be known on or before prediction_as_of_date.
-- Source freshness is separately audited; a zero-row result alone does not
-- prove that upstream data was refreshed or real-time predictions exist.
select
    scoring_row_key,
    player_id,
    season,
    prediction_as_of_date,
    feature_last_appearance_date,
    previous_market_value_date,
    previous_market_value_eur,
    prior_valuation_count,
    days_since_previous_market_value
from {{ ref('ml_player_market_value_scoring') }}
where prediction_as_of_date is null
    or feature_last_appearance_date > prediction_as_of_date
    or previous_market_value_date > prediction_as_of_date
    or previous_market_value_eur < 0
    or prior_valuation_count < 0
    or days_since_previous_market_value < 0
    or (has_previous_market_value and previous_market_value_eur is null)
    or (not has_previous_market_value and previous_market_value_eur is not null)
