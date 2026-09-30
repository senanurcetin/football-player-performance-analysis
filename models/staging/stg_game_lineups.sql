select

    trim(game_lineups_id) as game_lineups_id,

    date as lineup_date,

    game_id,

    player_id,

    club_id,

    trim(player_name) as player_name,

    lower(trim(type)) as lineup_type,

    nullif(upper(trim(position)), '') as position,

    trim(number) as squad_number,

    team_captain

from {{ source('football_raw', 'game_lineups') }}

where game_lineups_id is not null
