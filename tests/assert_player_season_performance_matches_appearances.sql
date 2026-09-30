with expected as (

    select
        appearances.player_id,
        games.season,
        appearances.competition_id,
        count(distinct appearances.game_id) as matches_played,
        sum(appearances.goals) as total_goals,
        sum(appearances.assists) as total_assists,
        sum(appearances.minutes_played) as total_minutes_played,
        sum(appearances.yellow_cards) as total_yellow_cards,
        sum(appearances.red_cards) as total_red_cards

    from {{ ref('stg_appearances') }} appearances

    inner join {{ ref('stg_games') }} games
        on appearances.game_id = games.game_id

    group by
        appearances.player_id,
        games.season,
        appearances.competition_id
)

select
    coalesce(expected.player_id, actual.player_id) as player_id,
    coalesce(expected.season, actual.season) as season,
    coalesce(expected.competition_id, actual.competition_id) as competition_id

from expected

full outer join {{ ref('int_player_season_performance') }} actual
    on expected.player_id = actual.player_id
    and expected.season = actual.season
    and expected.competition_id = actual.competition_id

where expected.player_id is null
    or actual.player_id is null
    or expected.matches_played != actual.matches_played
    or expected.total_goals != actual.total_goals
    or expected.total_assists != actual.total_assists
    or expected.total_minutes_played != actual.total_minutes_played
    or expected.total_yellow_cards != actual.total_yellow_cards
    or expected.total_red_cards != actual.total_red_cards
