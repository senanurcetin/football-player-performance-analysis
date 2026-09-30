with source_totals as (

    select
        sum(if(to_club_id is not null and not is_future_transfer, transfer_fee, null))
            as inbound_spend,
        sum(if(from_club_id is not null and not is_future_transfer, transfer_fee, null))
            as outbound_income,
        countif(to_club_id is not null and not is_future_transfer) as inbound_transfers,
        countif(from_club_id is not null and not is_future_transfer) as outbound_transfers

    from {{ ref('fct_transfer_market_value_analysis') }}
),

portfolio_totals as (

    select
        sum(inbound_transfer_spend) as inbound_spend,
        sum(outbound_transfer_income) as outbound_income,
        sum(inbound_transfers) as inbound_transfers,
        sum(outbound_transfers) as outbound_transfers

    from {{ ref('fct_club_transfer_portfolio') }}
)

select *

from source_totals
cross join portfolio_totals

where source_totals.inbound_spend is distinct from portfolio_totals.inbound_spend
    or source_totals.outbound_income is distinct from portfolio_totals.outbound_income
    or source_totals.inbound_transfers != portfolio_totals.inbound_transfers
    or source_totals.outbound_transfers != portfolio_totals.outbound_transfers
