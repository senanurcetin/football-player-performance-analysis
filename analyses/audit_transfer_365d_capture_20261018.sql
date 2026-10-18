-- Research-only, read-only BigQuery/dbt diagnostic for the historical
-- 365-day screenshot difference: 8,581 displayed vs 8,584 mart rows.
--
-- Run after dbt compile with an authorized warehouse profile.
-- This SQL deliberately does NOT assume that the screenshot is unfiltered.
-- It exposes the source populations and position/status breakdown so the
-- actual Power BI DAX / visual filters can be reconciled separately.
--
-- DO NOT run `dbt run` or modify a source table to make numbers match.
WITH horizon AS (
    SELECT
        transfer_key,
        position,
        outcome_365d_status,
        has_365d_outcome,
        market_value_baseline
    FROM {{ ref('fct_transfer_fixed_horizon_outcomes') }}
), labels AS (
    SELECT
        transfer_key,
        position,
        label_status,
        is_successful_transfer
    FROM {{ ref('fct_transfer_success_labels') }}
), audit AS (
    SELECT
        'fixed_horizon_population' AS source_population,
        COALESCE(CAST(position AS STRING), '<NULL_POSITION>') AS position_group,
        COALESCE(CAST(outcome_365d_status AS STRING), '<NULL_STATUS>') AS status_group,
        COUNT(*) AS row_count,
        COUNT(DISTINCT transfer_key) AS unique_transfer_keys,
        COUNTIF(has_365d_outcome) AS observed_outcomes,
        COUNTIF(market_value_baseline IS NOT NULL) AS known_baseline_rows,
        CAST(NULL AS INT64) AS positive_success_labels
    FROM horizon
    GROUP BY 1, 2, 3
    UNION ALL
    SELECT
        '365d_success_labels' AS source_population,
        COALESCE(CAST(position AS STRING), '<NULL_POSITION>') AS position_group,
        COALESCE(CAST(label_status AS STRING), '<NULL_STATUS>') AS status_group,
        COUNT(*) AS row_count,
        COUNT(DISTINCT transfer_key) AS unique_transfer_keys,
        COUNT(*) AS observed_outcomes,
        COUNT(*) AS known_baseline_rows,
        COUNTIF(is_successful_transfer = 1) AS positive_success_labels
    FROM labels
    GROUP BY 1, 2, 3
)
SELECT *
FROM audit
ORDER BY source_population, position_group, status_group
