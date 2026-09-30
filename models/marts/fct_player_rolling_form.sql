{{ config(
    partition_by={"field": "appearance_date", "data_type": "date", "granularity": "year"},
    cluster_by=["player_id", "competition_id", "player_club_id"]
) }}

select
    appearance_id,
    game_id,
    player_id,
    player_name,
    position,
    sub_position,
    player_club_id,
    player_club_name,
    competition_id,
    season,
    appearance_date,
    hosting,
    opponent_club_id,
    opponent_club_name,
    club_result,
    club_points,
    minutes_played,
    goals,
    assists,
    is_starter,
    is_captain,
    count(*) over player_last_5 as rolling_5_appearances,
    sum(minutes_played) over player_last_5 as rolling_5_minutes,
    sum(goals) over player_last_5 as rolling_5_goals,
    sum(assists) over player_last_5 as rolling_5_assists,
    sum(yellow_cards) over player_last_5 as rolling_5_yellow_cards,
    sum(red_cards) over player_last_5 as rolling_5_red_cards,
    sum(club_points) over player_last_5 as rolling_5_club_points,
    round(
        safe_divide(sum(goals) over player_last_5, nullif(sum(minutes_played) over player_last_5, 0)) * 90,
        4
    ) as rolling_5_goals_per_90,
    round(
        safe_divide(sum(assists) over player_last_5, nullif(sum(minutes_played) over player_last_5, 0)) * 90,
        4
    ) as rolling_5_assists_per_90,
    round(avg(minutes_played) over player_last_5, 2) as rolling_5_avg_minutes,
    countif(is_starter) over player_last_5 as rolling_5_starts,
    countif(is_captain) over player_last_5 as rolling_5_captain_appearances

from {{ ref('fct_player_match_performance') }}

window player_last_5 as (
    partition by player_id
    order by appearance_date, game_id, appearance_id
    rows between 4 preceding and current row
)
