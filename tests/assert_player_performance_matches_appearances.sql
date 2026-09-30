with expected as (

    select
        player_id,
        count(distinct game_id) as matches_played,
        sum(goals) as total_goals,
        sum(assists) as total_assists,
        sum(minutes_played) as total_minutes_played,
        sum(yellow_cards) as total_yellow_cards,
        sum(red_cards) as total_red_cards

    from {{ ref('stg_appearances') }}

    group by player_id
)

select
    coalesce(expected.player_id, actual.player_id) as player_id

from expected

full outer join {{ ref('int_player_performance_summary') }} actual
    on expected.player_id = actual.player_id

where expected.player_id is null
    or actual.player_id is null
    or expected.matches_played != actual.matches_played
    or expected.total_goals != actual.total_goals
    or expected.total_assists != actual.total_assists
    or expected.total_minutes_played != actual.total_minutes_played
    or expected.total_yellow_cards != actual.total_yellow_cards
    or expected.total_red_cards != actual.total_red_cards
