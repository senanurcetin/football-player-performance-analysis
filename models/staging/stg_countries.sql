select

    country_id,

    trim(country_name) as country_name,

    trim(country_code) as country_code,

    trim(confederation) as confederation,

    total_clubs,

    total_players,

    average_age

from {{ source('football_raw', 'countries') }}

where country_id is not null