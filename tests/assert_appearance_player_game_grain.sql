select
    player_id,
    game_id

from {{ ref('stg_appearances') }}

group by
    player_id,
    game_id

having count(*) > 1
