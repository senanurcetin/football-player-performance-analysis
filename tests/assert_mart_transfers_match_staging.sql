with expected as (

    select
        transfers.player_id,
        players.position,
        players.sub_position,
        transfers.player_name,
        transfers.transfer_date,
        transfers.transfer_season,
        transfers.from_club_id,
        transfers.to_club_id,
        transfers.from_club_name,
        transfers.to_club_name,
        transfers.transfer_fee,
        transfers.market_value_in_eur,
        transfers.transfer_fee - transfers.market_value_in_eur
            as fee_market_value_difference,
        round(
            safe_divide(
                transfers.transfer_fee - transfers.market_value_in_eur,
                nullif(transfers.market_value_in_eur, 0)
            ) * 100,
            2
        ) as fee_market_value_difference_pct

    from {{ ref('stg_transfers') }} transfers

    left join {{ ref('dim_players') }} players
        on transfers.player_id = players.player_id
),

differences as (

    (select * from expected except distinct select * from {{ ref('fct_transfers') }})

    union all

    (select * from {{ ref('fct_transfers') }} except distinct select * from expected)
)

select *
from differences
