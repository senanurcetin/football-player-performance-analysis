select

    national_team_id,

    trim(name) as national_team_name,

    trim(team_code) as team_code,

    country_id,

    trim(country_name) as country_name,

    trim(country_code) as country_code,

    trim(confederation) as confederation,

    squad_size,

    average_age,

    foreigners_number,

    foreigners_percentage,

    total_market_value,

    trim(coach_name) as coach_name,

    fifa_ranking,

    last_season

from {{ source('football_raw', 'national_teams') }}

where national_team_id is not null