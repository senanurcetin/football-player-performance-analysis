select
    national_team_id,
    national_team_name,
    team_code,
    country_id,
    country_name,
    country_code,
    confederation,
    squad_size,
    average_age,
    foreigners_number,
    foreigners_percentage,
    total_market_value,
    coach_name,
    fifa_ranking,
    last_season,
    coalesce(nullif(national_team_name, ''), concat('Unknown National Team #', cast(national_team_id as string)))
        as national_team_name_display,
    national_team_name is not null as has_team_name,
    total_market_value is not null as has_total_market_value,
    fifa_ranking is not null as has_fifa_ranking

from {{ ref('stg_national_teams') }}
