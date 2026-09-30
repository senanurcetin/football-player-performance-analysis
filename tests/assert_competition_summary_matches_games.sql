with participating_clubs as (

    select
        competition_id,
        home_club_id as club_id

    from {{ ref('stg_games') }}

    union all

    select
        competition_id,
        away_club_id as club_id

    from {{ ref('stg_games') }}
),

expected_metrics as (

    select
        competition_id,
        count(distinct game_id) as matches_played,
        sum(home_club_goals + away_club_goals) as total_goals

    from {{ ref('stg_games') }}

    group by competition_id
),

expected_participation as (

    select
        competition_id,
        count(distinct club_id) as club_participation_count

    from participating_clubs

    group by competition_id
)

select
    coalesce(
        summary.competition_id,
        expected_metrics.competition_id,
        expected_participation.competition_id
    ) as competition_id

from {{ ref('int_competition_summary') }} summary

full outer join expected_metrics
    on summary.competition_id = expected_metrics.competition_id

full outer join expected_participation
    on coalesce(summary.competition_id, expected_metrics.competition_id)
        = expected_participation.competition_id

where summary.competition_id is null
    or expected_metrics.competition_id is null
    or expected_participation.competition_id is null
    or summary.matches_played != expected_metrics.matches_played
    or summary.total_goals != expected_metrics.total_goals
    or summary.club_participation_count != expected_participation.club_participation_count
