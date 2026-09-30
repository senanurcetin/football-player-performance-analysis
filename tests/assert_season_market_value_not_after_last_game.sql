with player_last_games as (

    select
        appearances.player_id,
        games.season,
        appearances.competition_id,
        max(games.game_date) as player_last_game_date

    from {{ ref('stg_appearances') }} appearances

    inner join {{ ref('stg_games') }} games
        on appearances.game_id = games.game_id

    group by
        appearances.player_id,
        games.season,
        appearances.competition_id
)

select
    performance.player_id,
    performance.season,
    performance.competition_id

from {{ ref('int_player_season_performance') }} performance

inner join player_last_games
    on performance.player_id = player_last_games.player_id
    and performance.season = player_last_games.season
    and performance.competition_id = player_last_games.competition_id

where performance.season_market_value_date > player_last_games.player_last_game_date
