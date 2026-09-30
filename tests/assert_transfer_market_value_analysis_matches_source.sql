with expected as (

    select
        to_hex(
            md5(
                to_json_string(
                    struct(
                        player_id,
                        transfer_date,
                        transfer_season,
                        from_club_id,
                        to_club_id,
                        from_club_name,
                        to_club_name,
                        transfer_fee,
                        market_value_in_eur,
                        player_name
                    )
                )
            )
        ) as transfer_key,
        player_id,
        transfer_date,
        transfer_fee,
        market_value_in_eur as transfer_record_market_value

    from {{ ref('stg_transfers') }}
),

actual as (

    select
        transfer_key,
        player_id,
        transfer_date,
        transfer_fee,
        transfer_record_market_value

    from {{ ref('fct_transfer_market_value_analysis') }}
),

differences as (

    (select * from expected except distinct select * from actual)

    union all

    (select * from actual except distinct select * from expected)
)

select *
from differences
