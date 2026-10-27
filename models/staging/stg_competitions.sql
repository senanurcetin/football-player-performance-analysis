-- Publisher's competitions table omits five competition IDs used by games
-- (POCP, CGB, COL1, KLUB, UKRS in the 2026-10-27 Kaggle archive).
-- Retain original metadata verbatim and derive ONLY the missing identifiers
-- from actual game records. Fallback names explicitly say "Unmapped", never
-- invent country, confederation, subtype, or league classification.
-- Preserve the original ten-column Power BI dimension contract.
with publisher_competitions as (
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
),

unmapped_competitions as (
    select distinct
        games.competition_id
    from {{ ref('stg_games') }} as games
    left join publisher_competitions as publisher
        on games.competition_id = publisher.competition_id
    where games.competition_id is not null
        and publisher.competition_id is null
)

select * from publisher_competitions

union all

select
    competition_id,
    competition_id as competition_code,
    concat('Unmapped competition (', competition_id, ')') as competition_name,
    cast(null as string) as competition_sub_type,
    cast(null as string) as competition_type,
    cast(null as int64) as country_id,
    cast(null as string) as country_name,
    cast(null as string) as domestic_league_code,
    cast(null as string) as confederation,
    cast(null as int64) as total_clubs
from unmapped_competitions
