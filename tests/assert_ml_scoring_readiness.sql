with readiness as (

    select
        count(*) as row_count,
        safe_divide(
            countif(previous_market_value_eur is null),
            count(*)
        ) as previous_market_value_missing_rate,
        safe_divide(
            countif(competition_id is null),
            count(*)
        ) as competition_context_missing_rate,
        safe_divide(
            countif(age_at_target_date is null),
            count(*)
        ) as age_missing_rate

    from {{ ref('ml_player_market_value_scoring') }}

)

select
    'previous_market_value_missing_rate' as failed_metric,
    previous_market_value_missing_rate as observed_rate,
    0.35 as maximum_rate

from readiness

where row_count = 0
    or previous_market_value_missing_rate > 0.35

union all

select
    'competition_context_missing_rate',
    competition_context_missing_rate,
    0.35

from readiness

where competition_context_missing_rate > 0.35

union all

select
    'age_missing_rate',
    age_missing_rate,
    0.05

from readiness

where age_missing_rate > 0.05
