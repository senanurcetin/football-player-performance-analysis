select
    season,
    competition_id,
    home_club_manager_name as manager_name,
    home_club_formation as formation,
    count(*) as home_matches,
    round(100 * avg(if(match_result = 'home_win', 1, 0)), 2) as home_win_rate_pct,
    round(avg(home_club_goals), 2) as avg_home_goals,
    round(avg(away_club_goals), 2) as avg_goals_conceded,
    round(avg(attendance), 2) as avg_attendance

from {{ ref('fct_match') }}

where not is_future_game
    and home_club_manager_name is not null
    and home_club_formation is not null

group by season, competition_id, home_club_manager_name, home_club_formation

having count(*) >= 10

order by season desc, home_win_rate_pct desc
