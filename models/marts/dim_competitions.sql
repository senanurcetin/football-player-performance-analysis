select
    competition_id,
    competition_code,
    competition_name,
    competition_sub_type,
    competition_type,
    country_id,
    country_name,
    domestic_league_code,
    confederation,
    total_clubs

from {{ ref('stg_competitions') }}