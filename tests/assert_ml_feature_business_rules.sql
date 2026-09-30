select
    'training' as model_name,
    training_row_key as row_key

from {{ ref('ml_player_market_value_training') }}

where matches_before_target < 0
    or competitions_played_before_target < 0
    or minutes_before_target < 0
    or goals_before_target < 0
    or assists_before_target < 0
    or yellow_cards_before_target < 0
    or red_cards_before_target < 0
    or target_market_value_eur <= 0
    or (age_at_target_date is not null and age_at_target_date not between 10 and 60)
    or has_previous_market_value != (previous_market_value_eur is not null)
    or (previous_market_value_eur is null) != (previous_market_value_date is null)
    or (has_previous_market_value and days_since_previous_market_value <= 0)
    or (has_previous_market_value and prior_valuation_count < 1)
    or previous_market_value_eur > prior_highest_market_value_eur
    or goals_per_90_before_target is distinct from round(
        safe_divide(goals_before_target, nullif(minutes_before_target, 0)) * 90,
        4
    )
    or assists_per_90_before_target is distinct from round(
        safe_divide(assists_before_target, nullif(minutes_before_target, 0)) * 90,
        4
    )

union all

select
    'scoring' as model_name,
    scoring_row_key as row_key

from {{ ref('ml_player_market_value_scoring') }}

where matches_before_target <= 0
    or competitions_played_before_target <= 0
    or minutes_before_target < 0
    or goals_before_target < 0
    or assists_before_target < 0
    or yellow_cards_before_target < 0
    or red_cards_before_target < 0
    or (age_at_target_date is not null and age_at_target_date not between 10 and 60)
    or has_previous_market_value != (previous_market_value_eur is not null)
    or (previous_market_value_eur is null) != (previous_market_value_date is null)
    or (has_previous_market_value and days_since_previous_market_value < 0)
    or (has_previous_market_value and prior_valuation_count < 1)
    or previous_market_value_eur > prior_highest_market_value_eur
    or goals_per_90_before_target is distinct from round(
        safe_divide(goals_before_target, nullif(minutes_before_target, 0)) * 90,
        4
    )
    or assists_per_90_before_target is distinct from round(
        safe_divide(assists_before_target, nullif(minutes_before_target, 0)) * 90,
        4
    )
