with source_dates as (

    select game_date as date_day
    from {{ ref('stg_games') }}

    union all

    select appearance_date
    from {{ ref('stg_appearances') }}

    union all

    select transfer_date
    from {{ ref('stg_transfers') }}

    union all

    select valuation_date
    from {{ ref('stg_player_valuations') }}
),

expected as (

    select
        min(date_day) as min_date,
        greatest(max(date_day), current_date()) as max_date,
        date_diff(
            greatest(max(date_day), current_date()),
            min(date_day),
            day
        ) + 1 as expected_rows

    from source_dates

    where date_day is not null
),

actual as (

    select
        min(date_day) as min_date,
        max(date_day) as max_date,
        count(*) as actual_rows

    from {{ ref('dim_date') }}
)

select *

from expected

cross join actual

where expected.min_date != actual.min_date
    or expected.max_date != actual.max_date
    or expected.expected_rows != actual.actual_rows
