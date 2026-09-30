{{ config(cluster_by=["season", "competition_id", "club_id"]) }}

select
    club_games.club_id,
    clubs.club_name,
    games.season,
    date(games.season, 7, 1) as season_start_date,
    games.competition_id,
    competitions.competition_name,
    count(distinct club_games.game_id) as matches_played,
    countif(club_games.is_win = 1) as wins,
    countif(club_games.is_win = 0 and club_games.own_goals = club_games.opponent_goals)
        as draws,
    countif(club_games.is_win = 0 and club_games.own_goals != club_games.opponent_goals)
        as losses,
    sum(club_games.own_goals) as goals_scored,
    sum(club_games.opponent_goals) as goals_conceded,
    sum(club_games.own_goals) - sum(club_games.opponent_goals) as goal_difference,
    sum(
        case
            when club_games.is_win = 1 then 3
            when club_games.own_goals = club_games.opponent_goals then 1
            else 0
        end
    ) as points,
    round(100 * safe_divide(countif(club_games.is_win = 1), count(*)), 2)
        as win_rate_pct,
    round(avg(club_games.own_goals), 2) as avg_goals_scored,
    round(avg(club_games.opponent_goals), 2) as avg_goals_conceded,
    round(avg(games.attendance), 2) as avg_attendance,
    countif(club_games.hosting = 'home') as home_matches,
    countif(club_games.hosting = 'away') as away_matches,
    count(distinct club_games.own_manager_name) as managers_used,
    count(distinct if(club_games.hosting = 'home', games.home_club_formation, games.away_club_formation))
        as formations_used,
    max(club_games.own_position) as highest_recorded_position,
    min(club_games.own_position) as lowest_recorded_position

from {{ ref('stg_club_games') }} club_games

inner join {{ ref('stg_games') }} games
    on club_games.game_id = games.game_id

left join {{ ref('dim_clubs') }} clubs
    on club_games.club_id = clubs.club_id

left join {{ ref('dim_competitions') }} competitions
    on games.competition_id = competitions.competition_id

where games.game_date <= current_date()

group by
    club_games.club_id,
    clubs.club_name,
    games.season,
    games.competition_id,
    competitions.competition_name
