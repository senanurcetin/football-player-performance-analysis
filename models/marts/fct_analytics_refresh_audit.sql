{{ config(
    materialized='incremental',
    unique_key='audit_key',
    on_schema_change='append_new_columns'
) }}

with audit_row as (
    select
        '{{ invocation_id }}' as audit_key,
        timestamp('{{ run_started_at }}') as audit_generated_at_utc,
        '{{ target.name }}' as dbt_target_name,
        (select count(*) from {{ ref('stg_games') }}) as source_game_rows,
        (select count(*) from {{ ref('stg_appearances') }}) as source_appearance_rows,
        (select count(*) from {{ ref('stg_transfers') }}) as source_transfer_rows,
        (select count(*) from {{ ref('stg_player_valuations') }}) as source_valuation_rows,
        (select count(*) from {{ ref('fct_match') }}) as match_rows,
        (select count(*) from {{ ref('fct_player_match_performance') }}) as player_match_rows,
        (select count(*) from {{ ref('fct_transfer_fixed_horizon_outcomes') }}) as historical_transfer_rows,
        (
            select known_fee_coverage_pct
            from {{ ref('fct_data_coverage_bias') }}
            where segment_type = 'overall' and segment_value = 'all'
        ) as overall_known_fee_coverage_pct,
        (
            select fee_value_comparison_coverage_pct
            from {{ ref('fct_data_coverage_bias') }}
            where segment_type = 'overall' and segment_value = 'all'
        ) as overall_fee_value_comparison_coverage_pct,
        (
            select outcome_365d_coverage_pct
            from {{ ref('fct_data_coverage_bias') }}
            where segment_type = 'overall' and segment_value = 'all'
        ) as overall_365d_outcome_coverage_pct,
        (
            select countif(coverage_bias_risk = 'high_bias_risk')
            from {{ ref('fct_data_coverage_bias') }}
        ) as high_bias_risk_segment_count,
        (
            select countif(not meets_minimum_sample_size)
            from {{ ref('fct_transfer_cohort_performance') }}
        ) as insufficient_sample_cohort_count
)

select *
from audit_row

{% if is_incremental() %}
where '{{ invocation_id }}' not in (select audit_key from {{ this }})
{% endif %}
