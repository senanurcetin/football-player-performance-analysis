with expected_and_actual as (

    select
        'int_club_performance_summary' as model_name,
        (select count(distinct club_id) from {{ ref('stg_club_games') }}) as expected_rows,
        (select count(*) from {{ ref('int_club_performance_summary') }}) as actual_rows

    union all

    select
        'int_competition_summary',
        (select count(distinct competition_id) from {{ ref('stg_games') }}),
        (select count(*) from {{ ref('int_competition_summary') }})

    union all

    select
        'int_player_market_value_summary',
        (
            select count(distinct player_id)
            from {{ ref('stg_player_valuations') }}
            where market_value_in_eur is not null
        ),
        (select count(*) from {{ ref('int_player_market_value_summary') }})

    union all

    select
        'int_player_performance_summary',
        (select count(distinct player_id) from {{ ref('stg_appearances') }}),
        (select count(*) from {{ ref('int_player_performance_summary') }})

    union all

    select
        'int_player_profile',
        (select count(*) from {{ ref('stg_players') }}),
        (select count(*) from {{ ref('int_player_profile') }})

    union all

    select
        'int_player_season_performance',
        (
            select count(*)
            from (
                select distinct
                    appearances.player_id,
                    games.season,
                    appearances.competition_id
                from {{ ref('stg_appearances') }} appearances
                inner join {{ ref('stg_games') }} games
                    on appearances.game_id = games.game_id
            )
        ),
        (select count(*) from {{ ref('int_player_season_performance') }})

    union all

    select
        'int_transfer_summary',
        (select count(distinct player_id) from {{ ref('stg_transfers') }}),
        (select count(*) from {{ ref('int_transfer_summary') }})
)

select *

from expected_and_actual

where expected_rows != actual_rows
