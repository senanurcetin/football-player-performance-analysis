select
    player_id,
    transfer_date,
    from_club_id,
    to_club_id

from {{ ref('fct_transfers') }}

where fee_market_value_difference
        is distinct from transfer_fee - market_value_in_eur
    or fee_market_value_difference_pct
        is distinct from round(
            safe_divide(
                transfer_fee - market_value_in_eur,
                nullif(market_value_in_eur, 0)
            ) * 100,
            2
        )
