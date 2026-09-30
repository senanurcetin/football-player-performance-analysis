select
    player_id,

    count(distinct game_id) as matches_played,

    sum(goals) as total_goals,
    sum(assists) as total_assists,
    sum(minutes_played) as total_minutes_played,

    sum(yellow_cards) as total_yellow_cards,
    sum(red_cards) as total_red_cards,

    round(avg(minutes_played), 2) as avg_minutes_per_match,

    round(safe_divide(sum(goals), count(distinct game_id)), 2) as goals_per_match,
    round(safe_divide(sum(assists), count(distinct game_id)), 2) as assists_per_match,

    round(safe_divide(sum(goals), nullif(sum(minutes_played), 0)) * 90, 2) as goals_per_90,
    round(safe_divide(sum(assists), nullif(sum(minutes_played), 0)) * 90, 2) as assists_per_90

from {{ ref('stg_appearances') }}

group by player_id