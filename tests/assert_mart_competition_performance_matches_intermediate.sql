with expected as (

    select
        competition_id,
        competition_name,
        competition_type,
        country_name,
        confederation,
        matches_played,
        total_goals,
        avg_goals_per_match,
        club_participation_count,
        avg_attendance

    from {{ ref('int_competition_summary') }}
),

differences as (

    (
        select * replace (
            cast(round(avg_goals_per_match, 2) as numeric) as avg_goals_per_match,
            cast(round(avg_attendance, 2) as numeric) as avg_attendance
        )
        from expected

        except distinct

        select * replace (
            cast(round(avg_goals_per_match, 2) as numeric) as avg_goals_per_match,
            cast(round(avg_attendance, 2) as numeric) as avg_attendance
        )
        from {{ ref('fct_competition_performance') }}
    )

    union all

    (
        select * replace (
            cast(round(avg_goals_per_match, 2) as numeric) as avg_goals_per_match,
            cast(round(avg_attendance, 2) as numeric) as avg_attendance
        )
        from {{ ref('fct_competition_performance') }}

        except distinct

        select * replace (
            cast(round(avg_goals_per_match, 2) as numeric) as avg_goals_per_match,
            cast(round(avg_attendance, 2) as numeric) as avg_attendance
        )
        from expected
    )
)

select *
from differences
