select *

from {{ ref('ml_player_market_value_training') }}

where feature_last_appearance_date >= target_market_value_date
    or previous_market_value_date >= target_market_value_date
    or target_market_value_eur <= 0
    or target_market_value_date > current_date()
