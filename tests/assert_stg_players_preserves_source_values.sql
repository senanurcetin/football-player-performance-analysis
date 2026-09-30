select
    staging.player_id

from {{ ref('stg_players') }} staging

inner join {{ source('football_raw', 'players') }} raw
    on staging.player_id = raw.player_id

where staging.current_club_id is distinct from raw.current_club_id
    or staging.last_season is distinct from raw.last_season
    or staging.highest_market_value_in_eur is distinct from raw.highest_market_value_in_eur
