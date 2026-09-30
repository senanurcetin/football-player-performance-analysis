select

    appearance_id,

    game_id,
    player_id,

    player_club_id,
    nullif(player_current_club_id, -1) as player_current_club_id,

    date as appearance_date,

    trim(player_name) as player_name,

    competition_id,

    yellow_cards,
    red_cards,
    goals,
    assists,
    minutes_played

from {{ source('football_raw', 'appearances') }}

where appearance_id is not null
