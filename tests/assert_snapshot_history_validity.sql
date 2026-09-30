with invalid_player_history as (
    select player_id
    from {{ ref('snap_player_profiles') }}
    group by player_id
    having countif(dbt_valid_to is null) != 1
        or countif(dbt_valid_to is not null and dbt_valid_to <= dbt_valid_from) > 0
),

invalid_club_history as (
    select club_id
    from {{ ref('snap_club_profiles') }}
    group by club_id
    having countif(dbt_valid_to is null) != 1
        or countif(dbt_valid_to is not null and dbt_valid_to <= dbt_valid_from) > 0
)

select cast(player_id as string) as invalid_key, 'player' as snapshot_type
from invalid_player_history

union all

select cast(club_id as string), 'club'
from invalid_club_history
