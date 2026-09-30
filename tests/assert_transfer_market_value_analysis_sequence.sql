with expected as (

    select
        *,

        row_number() over (
            partition by player_id
            order by
                transfer_date,
                transfer_key
        ) as expected_sequence_number,

        count(*) over (
            partition by player_id
        ) as expected_transfer_count,

        count(transfer_fee) over (
            partition by player_id
        ) as expected_known_fee_count,

        sum(transfer_fee) over (
            partition by player_id
        ) as expected_total_transfer_fee,

        sum(transfer_fee) over (
            partition by player_id
            order by
                transfer_date,
                transfer_key
            rows between unbounded preceding and current row
        ) as expected_cumulative_transfer_fee

    from {{ ref('fct_transfer_market_value_analysis') }}
)

select
    transfer_key

from expected

where transfer_sequence_number != expected_sequence_number
    or player_transfer_count != expected_transfer_count
    or known_fee_transfer_count != expected_known_fee_count
    or total_transfer_fee is distinct from expected_total_transfer_fee
    or cumulative_known_transfer_fee is distinct from expected_cumulative_transfer_fee
    or is_latest_transfer
        is distinct from (expected_sequence_number = expected_transfer_count)
