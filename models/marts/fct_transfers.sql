select

    t.player_id,

    p.position,
    p.sub_position,

    t.player_name,

    t.transfer_date,
    t.transfer_season,

    t.from_club_id,
    t.to_club_id,

    t.from_club_name,
    t.to_club_name,

    t.transfer_fee,
    t.market_value_in_eur,

    t.transfer_fee - t.market_value_in_eur as fee_market_value_difference,

    round(
        safe_divide(
            t.transfer_fee - t.market_value_in_eur,
            nullif(t.market_value_in_eur, 0)
        ) * 100,
        2
    ) as fee_market_value_difference_pct

from {{ ref('stg_transfers') }} t

left join {{ ref('dim_players') }} p
    on t.player_id = p.player_id