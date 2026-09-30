select

    perf.player_id,
    p.player_name,
    p.position,
    p.sub_position,
    p.current_club_id,
    p.current_club_name,
    p.market_value_in_eur,
    p.market_value_in_eur is not null as has_current_market_value,

    perf.matches_played,
    perf.total_goals,
    perf.total_assists,
    perf.total_minutes_played,
    perf.total_yellow_cards,
    perf.total_red_cards,
    perf.avg_minutes_per_match,
    perf.goals_per_match,
    perf.assists_per_match,
    perf.goals_per_90,
    perf.assists_per_90

from {{ ref('int_player_performance_summary') }} perf

left join {{ ref('int_player_profile') }} p
    on perf.player_id = p.player_id
