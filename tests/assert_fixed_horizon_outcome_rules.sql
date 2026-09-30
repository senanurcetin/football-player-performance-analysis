select transfer_key

from {{ ref('fct_transfer_fixed_horizon_outcomes') }}

where (has_90d_outcome and abs(date_diff(valuation_90d_date, target_90d_date, day)) > 30)
    or (has_180d_outcome and abs(date_diff(valuation_180d_date, target_180d_date, day)) > 30)
    or (has_365d_outcome and abs(date_diff(valuation_365d_date, target_365d_date, day)) > 30)
    or has_90d_outcome != (valuation_90d_date is not null and market_value_baseline is not null)
    or has_180d_outcome != (valuation_180d_date is not null and market_value_baseline is not null)
    or has_365d_outcome != (valuation_365d_date is not null and market_value_baseline is not null)
    or market_value_change_90d is distinct from market_value_90d - market_value_baseline
    or market_value_change_180d is distinct from market_value_180d - market_value_baseline
    or market_value_change_365d is distinct from market_value_365d - market_value_baseline
    or outcome_90d_status not in ('observed', 'missing_baseline', 'not_yet_observable', 'missing_followup')
    or outcome_180d_status not in ('observed', 'missing_baseline', 'not_yet_observable', 'missing_followup')
    or outcome_365d_status not in ('observed', 'missing_baseline', 'not_yet_observable', 'missing_followup')
    or (market_value_baseline is null and outcome_90d_status != 'missing_baseline')
    or (market_value_baseline is null and outcome_180d_status != 'missing_baseline')
    or (market_value_baseline is null and outcome_365d_status != 'missing_baseline')
    or pre_180d_appearances < 0
    or post_180d_appearances < 0
