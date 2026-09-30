select

    t.player_id,

    p.player_name,
    p.position,
    p.current_club_name,

    t.season,
    t.competition_id,

    t.matches_played,
    t.total_goals,
    t.total_assists,
    t.total_minutes_played,

    t.total_yellow_cards,
    t.total_red_cards,

    t.goals_per_match,
    t.assists_per_match,

    t.goals_per_90,
    t.assists_per_90,

    t.season_market_value,
    t.season_market_value_date,
    t.season_market_value is not null as has_season_market_value

from {{ ref('int_player_season_performance') }} t

left join {{ ref('dim_players') }} p
    on t.player_id = p.player_id
