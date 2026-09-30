with expected as (

    select
        valuations.player_id,
        players.player_name,
        players.position,
        players.sub_position,
        valuations.valuation_date,
        valuations.market_value_in_eur,
        valuations.current_club_id,
        valuations.current_club_name,
        valuations.player_club_domestic_competition_id as competition_id

    from {{ ref('stg_player_valuations') }} valuations

    left join {{ ref('dim_players') }} players
        on valuations.player_id = players.player_id
),

actual as (

    select
        player_id,
        player_name,
        position,
        sub_position,
        valuation_date,
        market_value_in_eur,
        current_club_id,
        current_club_name,
        competition_id

    from {{ ref('fct_market_value_history') }}
),

differences as (

    (select * from expected except distinct select * from actual)

    union all

    (select * from actual except distinct select * from expected)
)

select *
from differences
