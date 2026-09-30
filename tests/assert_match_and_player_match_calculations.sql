select cast(game_id as string) as row_key, 'match' as model_name

from {{ ref('fct_match') }}

where total_goals is distinct from home_club_goals + away_club_goals
    or home_goal_difference is distinct from home_club_goals - away_club_goals
    or match_result is distinct from case
        when home_club_goals > away_club_goals then 'home_win'
        when home_club_goals < away_club_goals then 'away_win'
        else 'draw'
    end

union all

select appearance_id, 'player_match'

from {{ ref('fct_player_match_performance') }}

where goals_per_90 is distinct from round(safe_divide(goals, nullif(minutes_played, 0)) * 90, 4)
    or assists_per_90 is distinct from round(safe_divide(assists, nullif(minutes_played, 0)) * 90, 4)
    or club_points not in (0, 1, 3)
    or (club_result = 'win' and club_points != 3)
    or (club_result = 'draw' and club_points != 1)
    or (club_result = 'loss' and club_points != 0)
