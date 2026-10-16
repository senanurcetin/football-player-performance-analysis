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
- It formats the actual imported UTC audit date in English. If the quality audit is **more than 90 days old** as measured by DAX `UTCNOW()`, the visual shows `HISTORICAL / DD MMM YYYY`; otherwise it shows `QUALITY AUDIT / DD MMM YYYY`. Missing evidence displays `AUDIT / NOT AVAILABLE`.
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

The repeatable `--execute` CLI gate was subsequently run successfully against all three actual warehouse tables. It reported **WARN (0 blocking findings)**, exactly because the latest audit was **117.22 days old** on 16 October 2026. This explicitly confirms the live CLI contract while keeping Desktop refresh `NOT_VERIFIED` and publication `HOLD`.

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

## Independent statistical domain checks — 16 October 2026

Additional **real** BigQuery SELECT aggregates were executed with the same EU billing cap, independent of the native Power BI importer.

| Asserted domain | Verified result |
| --- | ---: |
| Club performance records / distinct clubs | 3,270 / 3,270 |
| Performance rows with no or nonpositive match count | 0 |
| Club performance win rates disagreeing with 100 × wins / matches (tolerance 0.11 percentage points) | 0 |
| BigQuery min/max `win_rate` in **percentage points** | 0.0 / 100.0 |
| Club risk records / distinct clubs | 5,714 / 5,714 |
| Club risk negative incoming transfer count | 0 |
| Known-fee, 365-day-outcome and success percentages outside [0, 100] | 0 each |
| Observed 365-day transfers exceeding total incoming transfers | 0 |

These checks establish selected warehouse-domain consistency, **not** that Power BI Desktop refreshed its Import partitions or that every transfer outcome passed independent reconciliation. They do not imply current-season event coverage.

A repeatable source-only companion command is available in `scripts/check_powerbi_warehouse_quality.py`. It intentionally requires `--execute`, executes three immutable read-only SELECTs, rejects results with duplicate club keys or impossible counts, and warns about historical audit age. Each query carries `--maximum_bytes_billed=10485760`; without explicit execution, no warehouse request occurs.

```powershell
python scripts/check_powerbi_warehouse_quality.py --execute --output warehouse-quality.json
```

Its return classifications are **PASS** (domain checks and audit age within configured bounds), **WARN** (no domain anomaly, but stale/missing audit evidence), **FAIL** (actual domain problems), or **BLOCKED** (cannot safely complete query). A WARN is expected from the confirmed June 2026 audit when executed in October 2026. Never substitute simulated data or overwrite the timestamp to make it pass. In every state, actual Desktop visual and refresh acceptance remains HOLD.
