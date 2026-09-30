select
    horizon_days,
    cohort_type,
    cohort_value,
    transfer_count,
    observed_outcome_count,
    outcome_coverage_pct,
    median_market_value_change_pct,
    avg_market_value_change_pct,
    avg_change_ci95_lower_pct,
    avg_change_ci95_upper_pct,
    positive_outcome_rate_pct,
    analytical_reliability

from {{ ref('fct_transfer_cohort_performance') }}

where meets_minimum_sample_size
    and cohort_type != 'overall'

order by horizon_days, cohort_type, median_market_value_change_pct desc
