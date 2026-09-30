select concat(cast(horizon_days as string), '-', cohort_type, '-', cohort_value) as row_key,
    'cohort' as model_name

from {{ ref('fct_transfer_cohort_performance') }}

where observed_outcome_count + missing_baseline_count + not_yet_observable_count + missing_followup_count
        != transfer_count
    or outcome_coverage_pct not between 0 and 100
    or positive_outcome_rate_pct not between 0 and 100
    or meets_minimum_sample_size != (observed_outcome_count >= 30)
    or avg_change_ci95_lower_pct > avg_change_ci95_upper_pct

union all

select concat(segment_type, '-', segment_value), 'coverage'

from {{ ref('fct_data_coverage_bias') }}

where known_fee_coverage_pct not between 0 and 100
    or market_value_baseline_coverage_pct not between 0 and 100
    or fee_value_comparison_coverage_pct not between 0 and 100
    or outcome_90d_coverage_pct not between 0 and 100
    or outcome_180d_coverage_pct not between 0 and 100
    or outcome_365d_coverage_pct not between 0 and 100
    or pre_180d_performance_coverage_pct not between 0 and 100
    or post_180d_performance_coverage_pct not between 0 and 100
    or maximum_material_missingness_pct not between 0 and 100
