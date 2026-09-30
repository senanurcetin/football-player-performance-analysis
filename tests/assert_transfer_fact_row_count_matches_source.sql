with row_counts as (

    select
        (select count(*) from {{ ref('stg_transfers') }}) as staging_rows,
        (select count(*) from {{ ref('fct_transfers') }}) as fact_rows
)

select *

from row_counts

where staging_rows != fact_rows
