select

    game_id,

    competition_id,

    season,

    trim(round) as round,

    date as game_date,

    home_club_id,
    away_club_id,

    home_club_goals,
    away_club_goals,

    home_club_position,
    away_club_position,

    trim(home_club_manager_name) as home_club_manager_name,
    trim(away_club_manager_name) as away_club_manager_name,

    trim(stadium) as stadium,

    attendance,

    trim(referee) as referee,

    trim(home_club_formation) as home_club_formation,
    trim(away_club_formation) as away_club_formation,

    trim(home_club_name) as home_club_name,
    trim(away_club_name) as away_club_name,
    aggregate,
    trim(competition_type) as competition_type

  

from {{ source('football_raw', 'games') }}

where game_id is not null