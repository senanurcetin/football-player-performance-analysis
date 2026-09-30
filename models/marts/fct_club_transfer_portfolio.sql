{{ config(cluster_by=["transfer_season", "club_id"]) }}

with transfer_sides as (

    select
        to_club_id as club_id,
        transfer_season,
        'inbound' as transfer_direction,
        transfer_key,
        transfer_fee,
        market_value_baseline,
        fee_market_value_difference,
        fee_market_value_difference_pct,
        market_value_change_after_transfer,
        market_value_change_after_transfer_pct,
        has_known_transfer_fee,
        has_fee_market_value_comparison,
        has_post_transfer_value_change

    from {{ ref('fct_transfer_market_value_analysis') }}

    where to_club_id is not null
        and not is_future_transfer

    union all

    select
        from_club_id,
        transfer_season,
        'outbound',
        transfer_key,
        transfer_fee,
        market_value_baseline,
        fee_market_value_difference,
        fee_market_value_difference_pct,
        market_value_change_after_transfer,
        market_value_change_after_transfer_pct,
        has_known_transfer_fee,
        has_fee_market_value_comparison,
        has_post_transfer_value_change

    from {{ ref('fct_transfer_market_value_analysis') }}

    where from_club_id is not null
        and not is_future_transfer
)

select
    sides.club_id,
    clubs.club_name,
    sides.transfer_season,
    countif(transfer_direction = 'inbound') as inbound_transfers,
    countif(transfer_direction = 'outbound') as outbound_transfers,
    countif(transfer_direction = 'inbound' and has_known_transfer_fee)
        as inbound_known_fee_transfers,
    countif(transfer_direction = 'outbound' and has_known_transfer_fee)
        as outbound_known_fee_transfers,
    sum(if(transfer_direction = 'inbound', transfer_fee, null)) as inbound_transfer_spend,
    sum(if(transfer_direction = 'outbound', transfer_fee, null)) as outbound_transfer_income,
    coalesce(sum(if(transfer_direction = 'inbound', transfer_fee, null)), 0)
        - coalesce(sum(if(transfer_direction = 'outbound', transfer_fee, null)), 0)
        as net_transfer_spend,
    round(avg(if(transfer_direction = 'inbound', transfer_fee, null)), 2)
        as avg_inbound_transfer_fee,
    round(avg(if(transfer_direction = 'outbound', transfer_fee, null)), 2)
        as avg_outbound_transfer_fee,
    round(avg(if(transfer_direction = 'inbound', fee_market_value_difference_pct, null)), 2)
        as avg_inbound_fee_premium_pct,
    round(avg(if(transfer_direction = 'outbound', fee_market_value_difference_pct, null)), 2)
        as avg_outbound_fee_premium_pct,
    round(avg(if(transfer_direction = 'inbound', market_value_change_after_transfer_pct, null)), 2)
        as avg_inbound_post_transfer_value_change_pct,
    countif(transfer_direction = 'inbound' and has_post_transfer_value_change)
        as inbound_transfers_with_value_outcome,
    round(
        100 * safe_divide(
            countif(
                transfer_direction = 'inbound'
                and market_value_change_after_transfer > 0
            ),
            countif(transfer_direction = 'inbound' and has_post_transfer_value_change)
        ),
        2
    ) as inbound_positive_value_outcome_rate_pct,
    round(
        100 * safe_divide(
            countif(transfer_direction = 'inbound' and has_known_transfer_fee),
            countif(transfer_direction = 'inbound')
        ),
        2
    ) as inbound_fee_coverage_pct,
    round(
        100 * safe_divide(
            countif(transfer_direction = 'outbound' and has_known_transfer_fee),
            countif(transfer_direction = 'outbound')
        ),
        2
    ) as outbound_fee_coverage_pct

from transfer_sides sides

left join {{ ref('dim_clubs') }} clubs
    on sides.club_id = clubs.club_id

group by sides.club_id, clubs.club_name, sides.transfer_season
