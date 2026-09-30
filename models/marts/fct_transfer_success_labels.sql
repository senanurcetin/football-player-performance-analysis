{{ config(
    partition_by={"field": "transfer_date", "data_type": "date", "granularity": "year"},
    cluster_by=["to_club_id", "position", "transfer_year"]
) }}

select
    outcomes.transfer_key,
    outcomes.player_id,
    outcomes.player_name,
    outcomes.position,
    outcomes.age_at_transfer,
    outcomes.transfer_date,
    outcomes.transfer_year,
    outcomes.transfer_season,
    outcomes.from_club_id,
    outcomes.from_club_name,
    outcomes.to_club_id,
    outcomes.to_club_name,
    outcomes.transfer_fee,
    outcomes.has_known_transfer_fee,
    outcomes.market_value_baseline,
    outcomes.fee_market_value_difference_pct,
    365 as label_horizon_days,
    outcomes.valuation_365d_date as outcome_valuation_date,
    outcomes.market_value_365d as outcome_market_value,
    outcomes.market_value_change_365d_pct as market_value_change_at_horizon_pct,
    outcomes.outcome_365d_status as label_status,
    20 as success_threshold_pct,
    if(outcomes.market_value_change_365d_pct >= 20, 1, 0) as is_successful_transfer

from {{ ref('fct_transfer_fixed_horizon_outcomes') }} outcomes

where outcomes.has_365d_outcome
