select

    player_id,
    trim(first_name) as first_name,
    trim(last_name) as last_name,
    trim(name) as player_name,
    last_season,
    current_club_id,
    trim(country_of_birth) as country_of_birth,
    trim(city_of_birth) as city_of_birth,
    trim(country_of_citizenship) as country_of_citizenship,
    cast(date_of_birth as date) as birth_date,
    trim(sub_position) as sub_position,
    trim(position) as position,
    trim(foot) as preferred_foot,
    case
        when height_in_cm between 100 and 250 then height_in_cm
    end as height_in_cm,
    cast(contract_expiration_date as date) as contract_expiration_date,
    trim(agent_name) as agent_name,
    international_caps,
    international_goals,
    current_national_team_id,
    current_club_domestic_competition_id,
    trim(current_club_name) as current_club_name,
    market_value_in_eur,
    highest_market_value_in_eur

from {{ source('football_raw', 'players') }}

where player_id is not null
