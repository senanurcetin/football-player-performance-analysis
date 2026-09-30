with row_counts as (

    select
        (select count(*) from {{ ref('stg_player_valuations') }}) as staging_rows,
        (select count(*) from {{ ref('fct_market_value_history') }}) as fact_rows
)

select *

from row_counts

where staging_rows != fact_rows
