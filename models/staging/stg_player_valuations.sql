select

    player_id,

    date as valuation_date,

    market_value_in_eur,

    trim(current_club_name) as current_club_name,

    current_club_id,

    player_club_domestic_competition_id

from {{ source('football_raw', 'player_valuations') }}

where player_id is not null