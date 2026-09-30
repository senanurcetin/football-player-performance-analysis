{{ config(cluster_by=["segment_type", "segment_value"]) }}

with base as (

    select
        *,
        case
            when market_value_baseline is null then 'unavailable'
            when market_value_baseline < 1000000 then 'under_1m'
            when market_value_baseline < 5000000 then '1m_to_5m'
            when market_value_baseline < 20000000 then '5m_to_20m'
            else '20m_plus'
        end as market_value_band

    from {{ ref('fct_transfer_fixed_horizon_outcomes') }}
),

segments as (

    select *, 'overall' as segment_type, 'all' as segment_value from base
    union all
    select *, 'transfer_year', cast(transfer_year as string) from base
    union all
    select *, 'position', coalesce(position, 'unknown') from base
    union all
    select *, 'age_band_at_transfer', age_band_at_transfer from base
    union all
    select *, 'market_value_band', market_value_band from base
    union all
    select *, 'valuation_context_change', valuation_context_change from base
)

select
    segment_type,
    segment_value,
    count(*) as transfer_count,
    countif(has_known_transfer_fee) as known_fee_count,
    round(100 * safe_divide(countif(has_known_transfer_fee), count(*)), 2)
        as known_fee_coverage_pct,
    countif(market_value_baseline is not null) as market_value_baseline_count,
    round(100 * safe_divide(countif(market_value_baseline is not null), count(*)), 2)
        as market_value_baseline_coverage_pct,
    countif(has_fee_market_value_comparison) as fee_value_comparison_count,
    round(100 * safe_divide(countif(has_fee_market_value_comparison), count(*)), 2)
        as fee_value_comparison_coverage_pct,
    countif(has_90d_outcome) as outcome_90d_count,
    round(100 * safe_divide(countif(has_90d_outcome), count(*)), 2)
        as outcome_90d_coverage_pct,
    countif(has_180d_outcome) as outcome_180d_count,
    round(100 * safe_divide(countif(has_180d_outcome), count(*)), 2)
        as outcome_180d_coverage_pct,
    countif(has_365d_outcome) as outcome_365d_count,
    round(100 * safe_divide(countif(has_365d_outcome), count(*)), 2)
        as outcome_365d_coverage_pct,
    countif(has_pre_180d_performance) as pre_180d_performance_count,
    round(100 * safe_divide(countif(has_pre_180d_performance), count(*)), 2)
        as pre_180d_performance_coverage_pct,
    countif(has_post_180d_performance) as post_180d_performance_count,
    round(100 * safe_divide(countif(has_post_180d_performance), count(*)), 2)
        as post_180d_performance_coverage_pct,
    greatest(
        100 - round(100 * safe_divide(countif(has_known_transfer_fee), count(*)), 2),
        100 - round(100 * safe_divide(countif(has_fee_market_value_comparison), count(*)), 2),
        100 - round(100 * safe_divide(countif(has_365d_outcome), count(*)), 2)
    ) as maximum_material_missingness_pct,
    case
        when count(*) < 30 then 'insufficient_sample'
        when greatest(
            100 - 100 * safe_divide(countif(has_known_transfer_fee), count(*)),
            100 - 100 * safe_divide(countif(has_fee_market_value_comparison), count(*)),
            100 - 100 * safe_divide(countif(has_365d_outcome), count(*))
        ) > 50 then 'high_bias_risk'
        when greatest(
            100 - 100 * safe_divide(countif(has_known_transfer_fee), count(*)),
            100 - 100 * safe_divide(countif(has_fee_market_value_comparison), count(*)),
            100 - 100 * safe_divide(countif(has_365d_outcome), count(*))
        ) > 25 then 'monitor'
        else 'acceptable'
    end as coverage_bias_risk

from segments

group by segment_type, segment_value
