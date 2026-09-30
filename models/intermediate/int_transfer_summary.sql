with ranked_transfers as (

    select
        player_id,
        transfer_date,
        transfer_season,
        from_club_id,
        to_club_id,
        from_club_name,
        to_club_name,
        transfer_fee,
        market_value_in_eur,

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
)

select
    player_id,

    count(*) as transfer_count,

    sum(transfer_fee) as total_transfer_fee,
    avg(transfer_fee) as avg_transfer_fee,
    max(transfer_fee) as max_transfer_fee,

    max(case when latest_transfer_rank = 1 then transfer_date end) as latest_transfer_date,
    max(case when latest_transfer_rank = 1 then transfer_season end) as latest_transfer_season,
    max(case when latest_transfer_rank = 1 then from_club_id end) as latest_from_club_id,
    max(case when latest_transfer_rank = 1 then to_club_id end) as latest_to_club_id,
    max(case when latest_transfer_rank = 1 then from_club_name end) as latest_from_club_name,
    max(case when latest_transfer_rank = 1 then to_club_name end) as latest_to_club_name,
    max(case when latest_transfer_rank = 1 then transfer_fee end) as latest_transfer_fee,
    max(case when latest_transfer_rank = 1 then market_value_in_eur end) as latest_transfer_market_value

from ranked_transfers

group by player_id
