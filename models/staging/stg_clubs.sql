select

    club_id,

    trim(club_code) as club_code,
    trim(name) as club_name,

    domestic_competition_id,

    total_market_value,

    squad_size,
    average_age,

    foreigners_number,
    foreigners_percentage,

    national_team_players,

    trim(stadium_name) as stadium_name,
    stadium_seats,

    trim(net_transfer_record) as net_transfer_record,

    trim(coach_name) as coach_name,

    last_season

from {{ source('football_raw', 'clubs') }}

where club_id is not null