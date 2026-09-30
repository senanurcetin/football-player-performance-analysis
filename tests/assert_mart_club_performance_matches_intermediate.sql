with expected as (

    select
        performance.club_id,
        clubs.club_name,
        clubs.domestic_competition_id,
        performance.matches_played,
        performance.wins,
        performance.draws,
        performance.losses,
        performance.goals_scored,
        performance.goals_conceded,
        performance.goal_difference,
        performance.win_rate,
        performance.avg_goals_scored,
        performance.avg_goals_conceded

    from {{ ref('int_club_performance_summary') }} performance

    left join {{ ref('dim_clubs') }} clubs
        on performance.club_id = clubs.club_id
),

differences as (

    (
        select * replace (
            cast(round(win_rate, 2) as numeric) as win_rate,
            cast(round(avg_goals_scored, 2) as numeric) as avg_goals_scored,
            cast(round(avg_goals_conceded, 2) as numeric) as avg_goals_conceded
        )
        from expected

        except distinct

        select * replace (
            cast(round(win_rate, 2) as numeric) as win_rate,
            cast(round(avg_goals_scored, 2) as numeric) as avg_goals_scored,
            cast(round(avg_goals_conceded, 2) as numeric) as avg_goals_conceded
        )
        from {{ ref('fct_club_performance') }}
    )

    union all

    (
        select * replace (
            cast(round(win_rate, 2) as numeric) as win_rate,
            cast(round(avg_goals_scored, 2) as numeric) as avg_goals_scored,
            cast(round(avg_goals_conceded, 2) as numeric) as avg_goals_conceded
        )
        from {{ ref('fct_club_performance') }}

        except distinct

        select * replace (
            cast(round(win_rate, 2) as numeric) as win_rate,
            cast(round(avg_goals_scored, 2) as numeric) as avg_goals_scored,
            cast(round(avg_goals_conceded, 2) as numeric) as avg_goals_conceded
        )
        from expected
    )
)

select *
from differences
