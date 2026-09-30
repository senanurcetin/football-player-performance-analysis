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

date_bounds as (

    select
        min(date_day) as start_date,
        greatest(max(date_day), current_date()) as end_date

    from source_dates

    where date_day is not null
),

dates as (

    select date_day

    from date_bounds,
        unnest(generate_date_array(start_date, end_date)) as date_day
)

select
    date_day,
    cast(format_date('%Y%m%d', date_day) as int64) as date_key,

    extract(year from date_day) as calendar_year,
    extract(quarter from date_day) as calendar_quarter_number,
    concat('Q', cast(extract(quarter from date_day) as string))
        as calendar_quarter_name,

    extract(month from date_day) as calendar_month_number,
    format_date('%B', date_day) as calendar_month_name,
    format_date('%b', date_day) as calendar_month_short_name,
    format_date('%Y-%m', date_day) as calendar_year_month,
    cast(format_date('%Y%m', date_day) as int64) as calendar_year_month_sort,

    extract(isoyear from date_day) as iso_year,
    extract(isoweek from date_day) as iso_week_number,
    mod(extract(dayofweek from date_day) + 5, 7) + 1 as iso_day_of_week_number,

    extract(day from date_day) as calendar_day_of_month,
    format_date('%A', date_day) as calendar_day_name,

    extract(dayofweek from date_day) in (1, 7) as is_weekend,
    date_day = current_date() as is_today,
    date_day > current_date() as is_future_date

from dates
