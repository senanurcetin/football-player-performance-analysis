{{ config(materialized='table') }}

select date_day
from unnest(generate_date_array(date('2000-01-01'), date('2035-12-31'))) as date_day
