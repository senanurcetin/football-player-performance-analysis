# Club risk profile — Power BI refresh triage

**Purpose:** Diagnose the reported six-row import/refresh error in the
**production BigQuery** `fct_club_risk_profile` table without silently
changing production values. This procedure is read-only and optional until
the Power BI Desktop error details are available.

## Known, source-verified facts

- Production Power BI imports
  `data-analiz-490513.football_mart.fct_club_risk_profile` using
  `GoogleBigQuery.Database([UseStorageApi=false])`.
- The report semantic model declares **13 columns**, including integer club
  and transfer counts, four DOUBLE numeric metrics, a Boolean minimum-sample
  indicator, and text fields. The dbt mart computes percentages in **0–100
  percentage points**, *not 0–1 fractions*.
- The synthetic `offline-demo` uses a separate six-row local Power Query
  `#table`, already corrected in an earlier PR; its fix does **not**
  demonstrate that the six production error rows are resolved.
- Data-source failure, schema mismatch and Power Query conversion errors
  require distinct remedies. **The six-row count alone does not establish
  a cause.**

## Step 1 — capture the actual Desktop error

In **Transform data / Power Query Editor**, select
`fct_club_risk_profile` in the production edition. Locate the failing step
and use **Keep Errors / View Errors** on the affected column. Record the
exact column, native error text, step name and row identifier (`club_id`
where available). Do not share credentials or connection tokens.

A missing permission, missing table, schema change and failed type
conversion should not be addressed with the same modification.

## Step 2 — read-only BigQuery schema inspection

Run in the appropriate authorized billing/project context:

```sql
SELECT
  ordinal_position,
  column_name,
  data_type,
  is_nullable
FROM `data-analiz-490513.football_mart.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'fct_club_risk_profile'
ORDER BY ordinal_position;
```

Compare with the Power BI table at
`powerbi/workspace/FootballPlayerAnalysis/Model/definition/tables/fct_club_risk_profile.tmdl`.
Expected logical shape (not a claim of actual live schema):

| Model type | Columns |
| --- | --- |
| INT64 | club_id, total_incoming_transfers, transfers_with_known_fee, observed_365d_transfers, successful_transfers, unsuccessful_transfers |
| STRING | club_name, transfer_risk_category |
| Numeric / floating | known_fee_coverage_pct, outcome_365d_coverage_pct, avg_overpay_pct, transfer_success_rate_pct |
| BOOL | meets_minimum_sample_size |

BigQuery `NUMERIC` and `FLOAT64` can have distinct connector mappings:
record the actual data type before deciding on a conversion.

## Step 3 — inspect anomalies, without changing the mart

```sql
SELECT
  club_id,
  club_name,
  total_incoming_transfers,
  transfers_with_known_fee,
  observed_365d_transfers,
  successful_transfers,
  unsuccessful_transfers,
  known_fee_coverage_pct,
  outcome_365d_coverage_pct,
  avg_overpay_pct,
  transfer_success_rate_pct,
  meets_minimum_sample_size,
  transfer_risk_category,
  ARRAY_CONCAT(
    IF(transfers_with_known_fee > total_incoming_transfers,
       ['known fees exceed transfers'], []),
    IF(observed_365d_transfers > total_incoming_transfers,
       ['365d observations exceed transfers'], []),
    IF(known_fee_coverage_pct NOT BETWEEN 0 AND 100,
       ['known-fee coverage outside 0-100'], []),
    IF(outcome_365d_coverage_pct NOT BETWEEN 0 AND 100,
       ['365d coverage outside 0-100'], []),
    IF(transfer_success_rate_pct NOT BETWEEN 0 AND 100,
       ['success rate outside 0-100'], [])
  ) AS possible_data_anomalies
FROM `data-analiz-490513.football_mart.fct_club_risk_profile`
ORDER BY club_id
LIMIT 200;
```

The anomaly flags are *triage aids*, not a substitute for a Power Query
error message. For example, `NULL` success-rate values may reflect missing
label coverage, while `avg_overpay_pct` may validly exceed 100 and is not
clipped by this query. The mart classification must not be rewritten based
on a superficial error count.

## Step 4 — decide on a fix only with evidence

If the live warehouse schema conflicts with the declared Power BI type,
update the exact model column or explicitly typed Power Query step after
confirming that the conversion is lossless. If the warehouse mart values or
nullability are wrong, fix and test the authoritative dbt model instead.
If the root cause is a data-access or refresh-credential error, resolve
authorization rather than mutating numerical data.

Then refresh the **production** PBIP and reconcile record counts and risk
classification. Verify that the **synthetic** report remains independent.
No fix is accepted until both the error-detail evidence and real refresh
result are documented. The portfolio publication gate remains **HOLD**.

## Offline source guard (no CI)

```bash
python -m unittest discover -s tests -p 'test_powerbi_club_risk_source_contract.py'
python scripts/check_powerbi_offline_demo.py
```

These checks validate file contracts only; they do not query BigQuery.
