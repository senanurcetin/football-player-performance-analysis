with competition_metrics as (

    select
        competition_id,

        count(distinct game_id) as matches_played,
        sum(home_club_goals + away_club_goals) as total_goals,
        round(avg(home_club_goals + away_club_goals), 2) as avg_goals_per_match,
        round(avg(attendance), 2) as avg_attendance

    from {{ ref('stg_games') }}

    group by competition_id
),

participating_clubs as (

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

club_participation as (

    select
        competition_id,
        count(distinct club_id) as club_participation_count

    from participating_clubs

    group by competition_id
)

select
    metrics.competition_id,

    competitions.competition_name,
    competitions.competition_type,
    competitions.country_name,
    competitions.confederation,

    metrics.matches_played,
    metrics.total_goals,
    metrics.avg_goals_per_match,
    participation.club_participation_count,
    metrics.avg_attendance

from competition_metrics metrics

left join {{ ref('stg_competitions') }} competitions
    on metrics.competition_id = competitions.competition_id

left join club_participation participation
    on metrics.competition_id = participation.competition_id
