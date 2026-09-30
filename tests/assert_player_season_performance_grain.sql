select
    player_id,
    season,
    competition_id

from {{ ref('int_player_season_performance') }}

group by
    player_id,
    season,
    competition_id

having count(*) > 1
