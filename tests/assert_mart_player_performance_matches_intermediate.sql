with expected as (

    select
        performance.player_id,
        profile.player_name,
        profile.position,
        profile.sub_position,
        profile.current_club_id,
        profile.current_club_name,
        profile.market_value_in_eur,
        performance.matches_played,
        performance.total_goals,
        performance.total_assists,
        performance.total_minutes_played,
        performance.total_yellow_cards,
        performance.total_red_cards,
        performance.avg_minutes_per_match,
        performance.goals_per_match,
        performance.assists_per_match,
        performance.goals_per_90,
        performance.assists_per_90

    from {{ ref('int_player_performance_summary') }} performance

    left join {{ ref('int_player_profile') }} profile
        on performance.player_id = profile.player_id
),

actual as (

    select
        player_id,
        player_name,
        position,
        sub_position,
        current_club_id,
        current_club_name,
        market_value_in_eur,
        matches_played,
        total_goals,
        total_assists,
        total_minutes_played,
        total_yellow_cards,
        total_red_cards,
        avg_minutes_per_match,
        goals_per_match,
        assists_per_match,
        goals_per_90,
        assists_per_90

    from {{ ref('fct_player_performance') }}
),

differences as (

    (
        select * replace (
            cast(round(avg_minutes_per_match, 2) as numeric) as avg_minutes_per_match,
            cast(round(goals_per_match, 2) as numeric) as goals_per_match,
            cast(round(assists_per_match, 2) as numeric) as assists_per_match,
            cast(round(goals_per_90, 2) as numeric) as goals_per_90,
            cast(round(assists_per_90, 2) as numeric) as assists_per_90
        )
        from expected

        except distinct

        select * replace (
            cast(round(avg_minutes_per_match, 2) as numeric) as avg_minutes_per_match,
            cast(round(goals_per_match, 2) as numeric) as goals_per_match,
            cast(round(assists_per_match, 2) as numeric) as assists_per_match,
            cast(round(goals_per_90, 2) as numeric) as goals_per_90,
            cast(round(assists_per_90, 2) as numeric) as assists_per_90
        )
        from actual
    )

    union all

    (
        select * replace (
            cast(round(avg_minutes_per_match, 2) as numeric) as avg_minutes_per_match,
            cast(round(goals_per_match, 2) as numeric) as goals_per_match,
            cast(round(assists_per_match, 2) as numeric) as assists_per_match,
            cast(round(goals_per_90, 2) as numeric) as goals_per_90,
            cast(round(assists_per_90, 2) as numeric) as assists_per_90
        )
        from actual

        except distinct

        select * replace (
            cast(round(avg_minutes_per_match, 2) as numeric) as avg_minutes_per_match,
            cast(round(goals_per_match, 2) as numeric) as goals_per_match,
            cast(round(assists_per_match, 2) as numeric) as assists_per_match,
            cast(round(goals_per_90, 2) as numeric) as goals_per_90,
            cast(round(assists_per_90, 2) as numeric) as assists_per_90
        )
        from expected
    )
)

select *
from differences
