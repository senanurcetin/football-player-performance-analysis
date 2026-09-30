select
    player_id,
    season,
    competition_id

from {{ ref('fct_player_career_timeline') }}

group by
    player_id,
    season,
    competition_id

having count(*) > 1
