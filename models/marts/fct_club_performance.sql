select

    perf.club_id,

    c.club_name,
    c.domestic_competition_id,

    perf.matches_played,

    perf.wins,
    perf.draws,
    perf.losses,

    perf.goals_scored,
    perf.goals_conceded,

    perf.goal_difference,

    perf.win_rate,

    perf.avg_goals_scored,
    perf.avg_goals_conceded

from {{ ref('int_club_performance_summary') }} perf

left join {{ ref('dim_clubs') }} c
    on perf.club_id = c.club_id
