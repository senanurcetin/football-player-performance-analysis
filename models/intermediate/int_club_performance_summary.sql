select
    club_id,

    count(distinct game_id) as matches_played,

    sum(case when is_win = 1 then 1 else 0 end) as wins,
    sum(case when is_win = 0 and own_goals = opponent_goals then 1 else 0 end) as draws,
    sum(case when is_win = 0 and own_goals <> opponent_goals then 1 else 0 end) as losses,

    sum(own_goals) as goals_scored,
    sum(opponent_goals) as goals_conceded,

    sum(own_goals) - sum(opponent_goals) as goal_difference,

    round(
        safe_divide(sum(case when is_win = 1 then 1 else 0 end), count(distinct game_id)) * 100,
        2
    ) as win_rate,

    round(avg(own_goals), 2) as avg_goals_scored,
    round(avg(opponent_goals), 2) as avg_goals_conceded

from {{ ref('stg_club_games') }}

group by club_id