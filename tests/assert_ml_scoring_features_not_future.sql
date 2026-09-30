select *

from {{ ref('ml_player_market_value_scoring') }}

where feature_last_appearance_date > prediction_as_of_date
    or previous_market_value_date > prediction_as_of_date
    or prediction_as_of_date != current_date()
