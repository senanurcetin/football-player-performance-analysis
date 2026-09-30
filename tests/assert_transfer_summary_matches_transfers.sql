with ranked as (

    select
        *,
        row_number() over (
            partition by player_id
            order by
                transfer_date desc,
                transfer_season desc,
                to_club_id desc,
                from_club_id desc,
                transfer_fee desc,
                market_value_in_eur desc,
                to_club_name desc,
                from_club_name desc
        ) as latest_transfer_rank

    from {{ ref('stg_transfers') }}
),

expected as (

    select
        player_id,
        count(*) as transfer_count,
        sum(transfer_fee) as total_transfer_fee,
        avg(transfer_fee) as avg_transfer_fee,
        max(transfer_fee) as max_transfer_fee,
        max(if(latest_transfer_rank = 1, transfer_date, null)) as latest_transfer_date,
        max(if(latest_transfer_rank = 1, transfer_fee, null)) as latest_transfer_fee,
        max(if(latest_transfer_rank = 1, market_value_in_eur, null))
            as latest_transfer_market_value

    from ranked

    group by player_id
)

select
    coalesce(expected.player_id, actual.player_id) as player_id

from expected

full outer join {{ ref('int_transfer_summary') }} actual
    on expected.player_id = actual.player_id

where expected.player_id is null
    or actual.player_id is null
    or expected.transfer_count != actual.transfer_count
    or expected.total_transfer_fee is distinct from actual.total_transfer_fee
    or expected.avg_transfer_fee is distinct from actual.avg_transfer_fee
    or expected.max_transfer_fee is distinct from actual.max_transfer_fee
    or expected.latest_transfer_date != actual.latest_transfer_date
    or expected.latest_transfer_fee is distinct from actual.latest_transfer_fee
    or expected.latest_transfer_market_value is distinct from actual.latest_transfer_market_value
