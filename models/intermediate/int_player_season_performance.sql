with performance as (

    select
        appearances.player_id,
        games.season,
        appearances.competition_id,

        count(distinct appearances.game_id) as matches_played,

        sum(appearances.goals) as total_goals,
        sum(appearances.assists) as total_assists,
        sum(appearances.minutes_played) as total_minutes_played,

        sum(appearances.yellow_cards) as total_yellow_cards,
        sum(appearances.red_cards) as total_red_cards,

        round(safe_divide(sum(appearances.goals), count(distinct appearances.game_id)), 2)
            as goals_per_match,
        round(safe_divide(sum(appearances.assists), count(distinct appearances.game_id)), 2)
            as assists_per_match,

        round(
            safe_divide(sum(appearances.goals), nullif(sum(appearances.minutes_played), 0)) * 90,
            2
        ) as goals_per_90,
        round(
            safe_divide(sum(appearances.assists), nullif(sum(appearances.minutes_played), 0)) * 90,
            2
        ) as assists_per_90,

        max(games.game_date) as player_last_game_date

    from {{ ref('stg_appearances') }} appearances

    inner join {{ ref('stg_games') }} games
        on appearances.game_id = games.game_id

    group by
        appearances.player_id,
        games.season,
        appearances.competition_id
),

season_market_value as (

    select
        performance.player_id,
        performance.season,
        performance.competition_id,

        array_agg(
            valuations.market_value_in_eur ignore nulls
            order by valuations.valuation_date desc
            limit 1
        )[safe_offset(0)] as season_market_value,

        array_agg(
            valuations.valuation_date ignore nulls
            order by valuations.valuation_date desc
            limit 1
        )[safe_offset(0)] as season_market_value_date

    from performance

    left join {{ ref('stg_player_valuations') }} valuations
        on performance.player_id = valuations.player_id
        and valuations.valuation_date <= performance.player_last_game_date

    group by
        performance.player_id,
        performance.season,
        performance.competition_id
)

select
    performance.player_id,
    performance.season,
    performance.competition_id,
    performance.matches_played,
    performance.total_goals,
    performance.total_assists,
    performance.total_minutes_played,
    performance.total_yellow_cards,
    performance.total_red_cards,
    performance.goals_per_match,
    performance.assists_per_match,
    performance.goals_per_90,
    performance.assists_per_90,
    season_market_value.season_market_value,
    season_market_value.season_market_value_date

from performance

left join season_market_value
    on performance.player_id = season_market_value.player_id
    and performance.season = season_market_value.season
    and performance.competition_id = season_market_value.competition_id
