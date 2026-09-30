with current_clubs as (

    select
        club_id,
        club_code,
        club_name,
        domestic_competition_id,
        total_market_value,
        squad_size,
        average_age,
        foreigners_number,
        foreigners_percentage,
        national_team_players,
        stadium_name,
        stadium_seats,
        net_transfer_record,
        coach_name,
        last_season

    from {{ ref('stg_clubs') }}
),

club_history_events as (

    select
        home_club_id as club_id,
        nullif(home_club_name, '') as club_name,
        nullif(home_club_manager_name, '') as coach_name,
        season,
        game_date as event_date,
        3 as source_priority

    from {{ ref('stg_games') }}

    union all

    select
        away_club_id as club_id,
        nullif(away_club_name, '') as club_name,
        nullif(away_club_manager_name, '') as coach_name,
        season,
        game_date as event_date,
        3 as source_priority

    from {{ ref('stg_games') }}

    union all

    select
        from_club_id as club_id,
        nullif(from_club_name, '') as club_name,
        cast(null as string) as coach_name,
        extract(year from transfer_date) as season,
        transfer_date as event_date,
        2 as source_priority

    from {{ ref('stg_transfers') }}

    where from_club_id is not null

    union all

    select
        to_club_id as club_id,
        nullif(to_club_name, '') as club_name,
        cast(null as string) as coach_name,
        extract(year from transfer_date) as season,
        transfer_date as event_date,
        2 as source_priority

    from {{ ref('stg_transfers') }}

    where to_club_id is not null

    union all

    select
        current_club_id as club_id,
        nullif(current_club_name, '') as club_name,
        cast(null as string) as coach_name,
        extract(year from valuation_date) as season,
        valuation_date as event_date,
        1 as source_priority

    from {{ ref('stg_player_valuations') }}

    where current_club_id is not null

    union all

    select
        current_club_id as club_id,
        nullif(current_club_name, '') as club_name,
        cast(null as string) as coach_name,
        last_season as season,
        date '9999-12-31' as event_date,
        4 as source_priority

    from {{ ref('stg_players') }}

    where current_club_id is not null
),

historical_clubs as (

    select
        club_id,

        array_agg(
            club_name ignore nulls
            order by event_date desc, source_priority desc, club_name desc
            limit 1
        )[safe_offset(0)] as club_name,

        array_agg(
            coach_name ignore nulls
            order by event_date desc, source_priority desc, coach_name desc
            limit 1
        )[safe_offset(0)] as coach_name,

        max(season) as last_season

    from club_history_events

    group by club_id
),

combined_clubs as (

    select
        current_clubs.*,
        'current_profile' as club_record_type

    from current_clubs

    union all

    select
        historical_clubs.club_id,
        cast(null as string) as club_code,
        historical_clubs.club_name,
        cast(null as string) as domestic_competition_id,
        cast(null as string) as total_market_value,
        cast(null as int64) as squad_size,
        cast(null as float64) as average_age,
        cast(null as int64) as foreigners_number,
        cast(null as float64) as foreigners_percentage,
        cast(null as int64) as national_team_players,
        cast(null as string) as stadium_name,
        cast(null as int64) as stadium_seats,
        cast(null as string) as net_transfer_record,
        historical_clubs.coach_name,
        historical_clubs.last_season,
        'historical_reference' as club_record_type

    from historical_clubs

    left join current_clubs
        on historical_clubs.club_id = current_clubs.club_id

    where current_clubs.club_id is null
),

scored_clubs as (

    select
        *,

        round(
            (
                cast(club_name is not null as int64)
                + cast(domestic_competition_id is not null as int64)
                + cast(squad_size is not null as int64)
                + cast(average_age is not null as int64)
                + cast(foreigners_number is not null as int64)
                + cast(national_team_players is not null as int64)
                + cast(stadium_name is not null as int64)
                + cast(stadium_seats is not null as int64)
                + cast(coach_name is not null as int64)
                + cast(last_season is not null as int64)
            ) / 10 * 100,
            2
        ) as club_profile_completeness_pct

    from combined_clubs
)

select
    *,

    coalesce(
        nullif(club_name, ''),
        concat('Unknown Club #', cast(club_id as string))
    ) as club_name_display,

    club_name is not null as has_club_name,
    club_record_type = 'current_profile' as has_current_profile,

    case
        when club_profile_completeness_pct >= 90 then 'complete'
        when club_profile_completeness_pct >= 60 then 'partial'
        else 'limited'
    end as club_profile_completeness_status

from scored_clubs
