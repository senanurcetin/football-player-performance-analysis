-- Transfer-level 365-day DAX vs. dbt label reconciliation (read-only).
-- Compile via dbt, then execute in an AUTHORIZED BigQuery session.
-- As-of date MUST match the screenshot/refresh date and visual filter context.
-- No source history is reconstructed by passing a historical date alone.
-- Usage: dbt compile --select audit_transfer_365d_row_level_20261020
--   --vars '{"pbi_capture_as_of_date":"2026-10-17"}'
--
-- Output is ONLY discordant or duplicate transfer keys; a zero-row result
-- is NOT standalone proof of a historic 8,581 vs 8,584 comparison unless
-- the complete source populations, timestamps and filters are reconciled.

WITH capture_parameters AS (
    SELECT DATE('{{ var("pbi_capture_as_of_date", "2026-10-17") }}') AS capture_date
),
source_cutoff AS (
    SELECT
        p.capture_date,
        MAX(h.source_latest_valuation_date) AS source_latest_valuation_date,
        LEAST(p.capture_date, MAX(h.source_latest_valuation_date))
            AS effective_cutoff_date
    FROM {{ ref('fct_transfer_fixed_horizon_outcomes') }} AS h
    CROSS JOIN capture_parameters AS p
    GROUP BY p.capture_date
),
horizon_per_key AS (
    SELECT
        h.transfer_key,
        COUNT(*) AS horizon_rows,
        COUNTIF(COALESCE(h.has_365d_outcome, FALSE))
            AS observed_horizon_rows,
        COUNTIF(
            h.target_365d_date IS NOT NULL
            AND DATE_ADD(h.target_365d_date, INTERVAL 30 DAY)
                <= cutoff.effective_cutoff_date
        ) AS matured_horizon_rows,
        COUNTIF(
            COALESCE(h.has_365d_outcome, FALSE)
            AND h.target_365d_date IS NOT NULL
            AND DATE_ADD(h.target_365d_date, INTERVAL 30 DAY)
                <= cutoff.effective_cutoff_date
        ) AS dax_observed_horizon_rows,
        MIN(h.transfer_date) AS first_transfer_date,
        MAX(h.transfer_date) AS last_transfer_date,
        MIN(h.target_365d_date) AS first_target_365d_date,
        MAX(h.target_365d_date) AS last_target_365d_date
    FROM {{ ref('fct_transfer_fixed_horizon_outcomes') }} AS h
    CROSS JOIN source_cutoff AS cutoff
    GROUP BY h.transfer_key
),
labels_per_key AS (
    SELECT
        transfer_key,
        COUNT(*) AS label_rows
    FROM {{ ref('fct_transfer_success_labels') }}
    GROUP BY transfer_key
),
comparison AS (
    SELECT
        COALESCE(h.transfer_key, l.transfer_key) AS transfer_key,
        cutoff.capture_date,
        cutoff.source_latest_valuation_date,
        cutoff.effective_cutoff_date,
        COALESCE(h.horizon_rows, 0) AS horizon_rows,
        COALESCE(h.observed_horizon_rows, 0) AS observed_horizon_rows,
        COALESCE(h.matured_horizon_rows, 0) AS matured_horizon_rows,
        COALESCE(h.dax_observed_horizon_rows, 0) > 0 AS dax_observed,
        COALESCE(l.label_rows, 0) > 0 AS in_success_labels,
        COALESCE(l.label_rows, 0) AS label_rows,
        h.first_transfer_date,
        h.last_transfer_date,
        h.first_target_365d_date,
        h.last_target_365d_date
    FROM horizon_per_key AS h
    FULL OUTER JOIN labels_per_key AS l
        ON h.transfer_key = l.transfer_key
    CROSS JOIN source_cutoff AS cutoff
)
SELECT
    *,
    CASE
        WHEN transfer_key IS NULL THEN 'null_transfer_key'
        WHEN horizon_rows > 1 THEN 'duplicate_horizon_key'
        WHEN label_rows > 1 THEN 'duplicate_label_key'
        WHEN horizon_rows = 0 THEN 'label_without_horizon_key'
        WHEN in_success_labels AND NOT dax_observed
            AND observed_horizon_rows > 0 AND matured_horizon_rows = 0
            THEN 'label_before_maturity_cutoff'
        WHEN in_success_labels AND NOT dax_observed
            THEN 'label_without_matured_observation'
        WHEN dax_observed AND NOT in_success_labels
            THEN 'matured_observation_without_label'
        ELSE 'unexpected_inconsistency'
    END AS discrepancy_reason
FROM comparison
WHERE dax_observed != in_success_labels
    OR horizon_rows != 1
    OR label_rows > 1
    OR transfer_key IS NULL
ORDER BY discrepancy_reason, transfer_key
