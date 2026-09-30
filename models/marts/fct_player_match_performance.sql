{{ config(
    partition_by={"field": "appearance_date", "data_type": "date", "granularity": "year"},
    cluster_by=["player_id", "player_club_id", "competition_id"]
) }}

with lineup_context as (

    select
        game_id,
        player_id,
        club_id,
        logical_or(lineup_type = 'starting_lineup') as is_starter,
        logical_or(team_captain = 1) as is_captain,
        array_agg(position ignore nulls order by game_lineups_id limit 1)[safe_offset(0)]
            as lineup_position

    from {{ ref('stg_game_lineups') }}

    group by game_id, player_id, club_id
)

select
    appearances.appearance_id,
    appearances.game_id,
    appearances.player_id,
    players.player_name,
    players.position,
    players.sub_position,
    appearances.player_club_id,
    clubs.club_name as player_club_name,
    appearances.competition_id,
    games.season,
    appearances.appearance_date,
    case
        when appearances.player_club_id = games.home_club_id then 'home'
        when appearances.player_club_id = games.away_club_id then 'away'
        else 'unknown'
    end as hosting,
    case
        when appearances.player_club_id = games.home_club_id
            then games.away_club_id
        when appearances.player_club_id = games.away_club_id
            then games.home_club_id
    end as opponent_club_id,
    case
        when appearances.player_club_id = games.home_club_id
            then games.away_club_name
        when appearances.player_club_id = games.away_club_id
            then games.home_club_name
    end as opponent_club_name,
    case
        when appearances.player_club_id = games.home_club_id
            then games.home_club_goals
        when appearances.player_club_id = games.away_club_id
            then games.away_club_goals
    end as club_goals,
    case
        when appearances.player_club_id = games.home_club_id
            then games.away_club_goals
        when appearances.player_club_id = games.away_club_id
            then games.home_club_goals
    end as opponent_goals,
    case
        when appearances.player_club_id = games.home_club_id
            and games.home_club_goals > games.away_club_goals then 'win'
        when appearances.player_club_id = games.away_club_id
            and games.away_club_goals > games.home_club_goals then 'win'
        when games.home_club_goals = games.away_club_goals then 'draw'
        when appearances.player_club_id in (games.home_club_id, games.away_club_id)
            then 'loss'
        else 'unknown'
    end as club_result,
    case
        when appearances.player_club_id = games.home_club_id
            and games.home_club_goals > games.away_club_goals then 3
        when appearances.player_club_id = games.away_club_id
            and games.away_club_goals > games.home_club_goals then 3
        when games.home_club_goals = games.away_club_goals then 1
        when appearances.player_club_id in (games.home_club_id, games.away_club_id)
            then 0
    end as club_points,
    appearances.minutes_played,
    appearances.goals,
    appearances.assists,
    appearances.yellow_cards,
    appearances.red_cards,
    round(safe_divide(appearances.goals, nullif(appearances.minutes_played, 0)) * 90, 4)
        as goals_per_90,
    round(safe_divide(appearances.assists, nullif(appearances.minutes_played, 0)) * 90, 4)
        as assists_per_90,
    coalesce(lineups.is_starter, false) as is_starter,
    coalesce(lineups.is_captain, false) as is_captain,
    lineups.lineup_position,
    lineups.player_id is not null as has_lineup_context,
    appearances.appearance_date > current_date() as is_future_appearance

from {{ ref('stg_appearances') }} appearances

inner join {{ ref('stg_games') }} games
    on appearances.game_id = games.game_id

left join lineup_context lineups
    on appearances.game_id = lineups.game_id
    and appearances.player_id = lineups.player_id
    and appearances.player_club_id = lineups.club_id

left join {{ ref('dim_players') }} players
    on appearances.player_id = players.player_id

left join {{ ref('dim_clubs') }} clubs
    on appearances.player_club_id = clubs.club_id
