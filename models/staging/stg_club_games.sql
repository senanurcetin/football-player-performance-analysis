select

    game_id,

    club_id,

    own_goals,

    own_position,

    trim(own_manager_name) as own_manager_name,

    opponent_id,

    opponent_goals,

    opponent_position,

    trim(opponent_manager_name) as opponent_manager_name,

    trim(hosting) as hosting,

    is_win

from {{ source('football_raw', 'club_games') }}

where game_id is not null