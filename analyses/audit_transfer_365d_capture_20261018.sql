-- Read-only reconciliation of Power BI 365-day KPI logic vs. dbt label mart.
-- No tables are built, updated, dropped, or backfilled by this analysis.
--
-- Power BI native TMDL sources:
-- powerbi/workspace/FootballPlayerAnalysis/Model/definition/tables/
--   fct_transfer_fixed_horizon_outcomes.tmdl
-- DAX "Observed Transfers (365d)" counts DISTINCT transfer_key with
--   target_365d_date + 30 days <= MIN(TODAY(), MAX(source_latest_valuation_date))
--   AND has_365d_outcome = TRUE.
-- The success-label mart includes ALL has_365d_outcome rows, without the
-- above as-of-date maturity condition. Their row counts are not equivalent.
--
-- Compile with dbt and run on an authorized BigQuery profile, optionally
-- setting --vars '{"pbi_capture_as_of_date":"2026-10-17"}'.
-- A date alone cannot time-travel an overwritten table: source snapshots,
-- visual filters and model refresh time must also be reproduced.
--
-- The default captures the actual 17 Oct 2026 screenshot local date.
WITH source_cutoff AS (
    SELECT LEAST(
        DATE('{{ var("pbi_capture_as_of_date", "2026-10-17") }}'),
        MAX(source_latest_valuation_date)
    ) AS effective_cutoff_date
    FROM {{ ref('fct_transfer_fixed_horizon_outcomes') }}
),
label_keys AS (
    SELECT transfer_key
    FROM {{ ref('fct_transfer_success_labels') }}
    GROUP BY transfer_key
),
per_transfer AS (
    SELECT
        h.transfer_key,
        COALESCE(CAST(h.position AS STRING), '<NULL_POSITION>') AS position_group,
        h.outcome_365d_status,
        h.has_365d_outcome,
        h.target_365d_date,
        c.effective_cutoff_date,
        l.transfer_key IS NOT NULL AS is_in_success_label_mart,
        (
            h.target_365d_date IS NOT NULL
            AND DATE_ADD(h.target_365d_date, INTERVAL 30 DAY)
                <= c.effective_cutoff_date
        ) AS is_matured_for_capture
    FROM {{ ref('fct_transfer_fixed_horizon_outcomes') }} AS h
    CROSS JOIN source_cutoff AS c
    LEFT JOIN label_keys AS l USING (transfer_key)
),
groups AS (
    SELECT 'all' AS cohort, 'overall' AS segment, *
    FROM per_transfer
    UNION ALL
    SELECT 'position' AS cohort, position_group AS segment, *
    FROM per_transfer
),
summary AS (
    SELECT
        cohort,
        segment,
        MAX(effective_cutoff_date) AS effective_cutoff_date,
        COUNT(*) AS fixed_horizon_rows,
        COUNT(DISTINCT transfer_key) AS fixed_horizon_keys,
        COUNTIF(has_365d_outcome) AS observed_anytime,
        COUNTIF(is_in_success_label_mart) AS success_label_rows,
        COUNTIF(is_matured_for_capture) AS dax_eligible_transfer_rows,
        COUNTIF(
            is_matured_for_capture AND has_365d_outcome
        ) AS dax_observed_transfer_rows,
        COUNTIF(
            is_in_success_label_mart AND
            (NOT is_matured_for_capture OR is_matured_for_capture IS NULL)
        ) AS label_rows_excluded_by_dax_maturity,
        COUNTIF(
            is_matured_for_capture AND has_365d_outcome
            AND NOT is_in_success_label_mart
        ) AS matured_observed_missing_success_label,
        COUNTIF(
            is_in_success_label_mart AND NOT has_365d_outcome
        ) AS unexpected_label_without_outcome
    FROM groups
    GROUP BY cohort, segment
)
SELECT
    *,
    ROUND(
        100 * SAFE_DIVIDE(dax_observed_transfer_rows, dax_eligible_transfer_rows),
        2
    ) AS dax_observed_coverage_pct,
    success_label_rows - dax_observed_transfer_rows
        AS observed_vs_label_row_difference
FROM summary
ORDER BY cohort, segment
