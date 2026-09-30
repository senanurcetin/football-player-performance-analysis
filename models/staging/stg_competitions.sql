select

    trim(competition_id) as competition_id,

    trim(competition_code) as competition_code,

    trim(name) as competition_name,

    trim(sub_type) as competition_sub_type,

    trim(type) as competition_type,

    country_id,

    trim(country_name) as country_name,

    trim(domestic_league_code) as domestic_league_code,

    trim(confederation) as confederation,

    total_clubs

from {{ source('football_raw', 'competitions') }}

where competition_id is not null