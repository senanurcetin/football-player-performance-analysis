{{ config(
    partition_by={"field": "game_date", "data_type": "date", "granularity": "year"},
    cluster_by=["competition_id", "season", "home_club_id", "away_club_id"]
) }}

select
    games.game_id,
    games.game_date,
    games.season,
    games.competition_id,
    competitions.competition_name,
    competitions.competition_type,
    competitions.country_name as competition_country_name,
    games.round,
    games.home_club_id,
    games.home_club_name,
    games.away_club_id,
    games.away_club_name,
    games.home_club_goals,
    games.away_club_goals,
    games.home_club_goals + games.away_club_goals as total_goals,
    games.home_club_goals - games.away_club_goals as home_goal_difference,
    case
        when games.home_club_goals > games.away_club_goals then 'home_win'
        when games.home_club_goals < games.away_club_goals then 'away_win'
        else 'draw'
    end as match_result,
    games.home_club_position,
    games.away_club_position,
    games.home_club_manager_name,
    games.away_club_manager_name,
    games.home_club_formation,
    games.away_club_formation,
    games.stadium,
    games.attendance,
    games.referee,
    games.aggregate,
    games.game_date > current_date() as is_future_game,
    games.attendance is not null as has_attendance,
    games.home_club_formation is not null
        and games.away_club_formation is not null as has_both_formations,
    games.home_club_manager_name is not null
        and games.away_club_manager_name is not null as has_both_managers,
    games.home_club_position is not null
        and games.away_club_position is not null as has_both_table_positions

from {{ ref('stg_games') }} games

left join {{ ref('dim_competitions') }} competitions
    on games.competition_id = competitions.competition_id
