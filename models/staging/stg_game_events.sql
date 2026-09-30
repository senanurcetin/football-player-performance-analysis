select

    trim(game_event_id) as game_event_id,

    date as event_date,

    game_id,

    nullif(minute, -1) as minute,

    lower(trim(type)) as event_type,

    club_id,

    trim(club_name) as club_name,

    player_id,

    nullif(trim(description), '') as event_description,

    player_in_id,

    player_assist_id

from {{ source('football_raw', 'game_events') }}

where game_event_id is not null
