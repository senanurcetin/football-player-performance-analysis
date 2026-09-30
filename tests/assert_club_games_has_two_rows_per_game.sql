select
    game_id

from {{ ref('stg_club_games') }}

group by game_id

having count(*) != 2
