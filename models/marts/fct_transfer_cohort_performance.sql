{{ config(cluster_by=["horizon_days", "cohort_type", "cohort_value"]) }}

with outcomes as (

    select
        transfer_key,
        position,
        age_band_at_transfer,
        cast(transfer_year as string) as transfer_year,
        fee_premium_band,
        valuation_context_change,
        fee_market_value_difference_pct,
        horizon_days,
        has_outcome,
        outcome_status,
        market_value_change_pct

    from {{ ref('fct_transfer_fixed_horizon_outcomes') }}

    unpivot (
        (has_outcome, outcome_status, market_value_change_pct)
        for horizon_days in (
            (has_90d_outcome, outcome_90d_status, market_value_change_90d_pct) as 90,
            (has_180d_outcome, outcome_180d_status, market_value_change_180d_pct) as 180,
            (has_365d_outcome, outcome_365d_status, market_value_change_365d_pct) as 365
        )
    )
),

cohorts as (

    select *, 'overall' as cohort_type, 'all' as cohort_value from outcomes
    union all
    select *, 'transfer_year', transfer_year from outcomes
    union all
    select *, 'position', coalesce(position, 'unknown') from outcomes
    union all
    select *, 'age_band_at_transfer', age_band_at_transfer from outcomes
    union all
    select *, 'fee_premium_band', fee_premium_band from outcomes
    union all
    select *, 'valuation_context_change', valuation_context_change from outcomes
),

aggregated as (

    select
        horizon_days,
        cohort_type,
        cohort_value,
        count(*) as transfer_count,
        countif(has_outcome) as observed_outcome_count,
        countif(outcome_status = 'missing_baseline') as missing_baseline_count,
        countif(outcome_status = 'not_yet_observable') as not_yet_observable_count,
        countif(outcome_status = 'missing_followup') as missing_followup_count,
        round(100 * safe_divide(countif(has_outcome), count(*)), 2)
            as outcome_coverage_pct,
        round(avg(if(has_outcome, market_value_change_pct, null)), 2)
            as avg_market_value_change_pct,
        round(approx_quantiles(if(has_outcome, market_value_change_pct, null), 100 ignore nulls)[safe_offset(50)], 2)
            as median_market_value_change_pct,
        round(approx_quantiles(if(has_outcome, market_value_change_pct, null), 100 ignore nulls)[safe_offset(25)], 2)
            as p25_market_value_change_pct,
        round(approx_quantiles(if(has_outcome, market_value_change_pct, null), 100 ignore nulls)[safe_offset(75)], 2)
            as p75_market_value_change_pct,
        round(stddev_samp(if(has_outcome, market_value_change_pct, null)), 2)
            as stddev_market_value_change_pct,
        round(
            100 * safe_divide(
                countif(has_outcome and market_value_change_pct > 0),
                countif(has_outcome)
            ),
            2
        ) as positive_outcome_rate_pct,
        round(avg(fee_market_value_difference_pct), 2) as avg_fee_premium_pct

    from cohorts

    group by horizon_days, cohort_type, cohort_value
)

select
    *,
    round(
        avg_market_value_change_pct
        - 1.96 * safe_divide(stddev_market_value_change_pct, sqrt(observed_outcome_count)),
        2
    ) as avg_change_ci95_lower_pct,
    round(
        avg_market_value_change_pct
        + 1.96 * safe_divide(stddev_market_value_change_pct, sqrt(observed_outcome_count)),
        2
    ) as avg_change_ci95_upper_pct,
    observed_outcome_count >= 30 as meets_minimum_sample_size,
    case
        when observed_outcome_count >= 100 then 'strong'
        when observed_outcome_count >= 30 then 'directional'
        else 'insufficient'
    end as analytical_reliability

from aggregated
