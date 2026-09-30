select
    player_id,
    valuation_date

from {{ ref('fct_market_value_history') }}

group by
    player_id,
    valuation_date

having count(*) > 1
