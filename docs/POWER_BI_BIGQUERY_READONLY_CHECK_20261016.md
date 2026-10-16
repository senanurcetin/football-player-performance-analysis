# NEXUS Football — read-only warehouse evidence and Home quality-audit label

**Inspection date:** 16 October 2026  
**Production project:** `data-analiz-490513` · **Dataset:** `football_mart` · **Location:** `EU`.  
**Publication state:** **HOLD** pending authenticated Power BI Desktop refresh, render and KPI reconciliation.

## What was verified against the real warehouse

The authorized Windows Google Cloud CLI was used without altering, recreating or appending to any tables. The following metadata were returned by `bq show`, using each table's recorded `lastModifiedTime` (UTC). These are **warehouse table modification timestamps**, *not* the football source event-date range or a Power BI cache-refresh timestamp.

| Real BigQuery table | Rows | Last modified (UTC) |
| --- | ---: | --- |
| `football_mart.fct_club_risk_profile` | 5,714 | 2026-06-21 10:52:55 |
| `football_mart.fct_club_performance` | 3,270 | 2026-06-21 10:51:29 |
| `football_mart.fct_player_performance` | 28,736 | 2026-06-21 10:51:43 |
| `football_mart.fct_analytics_refresh_audit` | 17 | 2026-06-21 10:52:57 |

A **read-only** bounded aggregate query was executed with `--maximum_bytes_billed=10485760` (10 MiB), yielding:

| Measure | Verified value |
| --- | --- |
| Audit rows | 17 |
| Latest `audit_generated_at_utc` | **2026-06-21 10:50:30.267 UTC** |

The Google CLI printed an **Application Default Credentials cache write permission** warning under the user's existing profile, but the bounded BigQuery query itself completed with exit code 0. This warning does not prove refresh health for Power BI Desktop.

## New BigQuery-derived Home indicator

The editable report's top-right Home metadata text (formerly a fixed count of seven views) is now a native Power BI **card**, not a static overlay or an invented figure.

- Measure `fct_analytics_refresh_audit[Last Warehouse Audit Label]` takes the maximum of the **existing BigQuery mart's** `audit_generated_at_utc` column.
- It formats the actual imported UTC audit date as `QUALITY AUDIT / DD MMM YYYY` in English, or `AUDIT / NOT AVAILABLE` when the evidence is missing.
- Its report visual is `Report/definition/pages/5cb4db7e746975558322/visuals/fa9241e97af65797688c/visual.json`, in the original 250×35 top-right slot. The card's value is **DAX evaluated from the imported model**, not a literal or project-generated date.
- Production source remains `GoogleBigQuery.Database([UseStorageApi=false])`. The separate `offline-demo` fixture is unchanged in provenance, and the same semantic measure evaluates only its labeled synthetic QA partition in that internal edition.
- A **Power BI Desktop refresh is still required** before the new KPI can be said to show this observed date on-screen. Source-only regression asserts the binding and prevents introducing a hard-coded audit date.

**Interpretation:** An audit timestamp is neither an event-data coverage date nor proof of a continuously updated/live feed. The public report should be described as historical, evidence-led football intelligence until an independently verified new data ingestion run and period-coverage checks establish current season freshness.

## Reproducible CLI metadata preflight (read-only)

```powershell
bq.cmd --location=EU show --format=prettyjson data-analiz-490513:football_mart.fct_club_risk_profile
bq.cmd --location=EU show --format=prettyjson data-analiz-490513:football_mart.fct_club_performance
bq.cmd --location=EU show --format=prettyjson data-analiz-490513:football_mart.fct_player_performance
bq.cmd --location=EU show --format=prettyjson data-analiz-490513:football_mart.fct_analytics_refresh_audit
```

The verified aggregate was equivalent to:

```sql
SELECT
  COUNT(*) AS audit_rows,
  CAST(MAX(audit_generated_at_utc) AS STRING) AS latest_audit_utc
FROM `data-analiz-490513.football_mart.fct_analytics_refresh_audit`
```

with `bq query --use_legacy_sql=false --location=EU --maximum_bytes_billed=10485760`. The initial experiment at a 10,000,000-byte cap failed because BigQuery required a minimum 10,485,760-byte billing limit; this failure was **not** considered evidence of missing warehouse rows. No new pipeline loads or credentials were created.

## Acceptance boundary

Do not claim a Power BI Desktop refresh, preview image, production data-reconciliation pass, model retraining, automatic schedule or current-season stream. The newly bound card, all 13 pages, interactive filters, model DAX/Power Query execution, credentials and license-dependent sharing remain subject to final owner-controlled Desktop inspection. CI is intentionally gated.
