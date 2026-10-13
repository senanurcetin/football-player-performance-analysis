# NEXUS Football — live BigQuery read-only audit (13 October 2026)

**Project:** `data-analiz-490513` · **dataset:** `football_mart` · **BigQuery location:** `EU`.

This document records **actually executed**, read-only BigQuery metadata and aggregate queries from the authorized Windows Google Cloud CLI session. It does not document a successful Power BI Desktop refresh. All queries were restricted to at most 100 MB billed bytes per query.

## Verified production facts

| Actual BigQuery mart | Rows | Unique club IDs | Live SQL observations |
| --- | ---: | ---: | --- |
| `fct_club_risk_profile` | 5,714 | 5,714 | 0 missing keys/names, 0 invalid transfer counts, 0 coverage/success rates outside 0–100, 0 missing risk categories, 0 unsafe `NUMERIC→FLOAT64` casts |
| `fct_club_performance` | 3,270 | 3,270 | 0 impossible matches/wins, 0 rates outside 0–100, 0 mismatches between recorded win rate and `100 * wins / matches` (tolerance 0.11 percentage points) |

The risk mart's `avg_overpay_pct` is **BigQuery NUMERIC** (range in scanned rows: **−100 to 600**); the Power BI semantic model declares `double`. All non-null current BigQuery values were `SAFE_CAST` convertible to `FLOAT64`. The proposed **production-only** Power Query `Table.TransformColumns` step explicitly converts that field with `Number.From` and leaves nulls unchanged. This normalizes the import contract; **it is not proof the historical six-row Desktop refresh problem is fixed**. The six-row error count may refer to an entirely different local fixture or refresh and must be re-observed in Desktop.

The `fct_club_performance.win_rate` warehouse values are on a **0–100** scale; their observed range is 0–100 and all 3,270 rows reconcile. The **existing** Power Query `Win Rate Fraction` step divides this field by 100 for correct Power BI `0.0%` formatting. No dbt mart value was changed.

## Warehouse freshness gate

`bq show` last-modified timestamps correspond to **21 June 2026 10:52:55 UTC** for `fct_club_risk_profile` and **21 June 2026 10:51:29 UTC** for `fct_club_performance`. Those are the **mart table modification timestamps**, not proven event-data coverage. As of the **13 October 2026** audit, they are substantially older than the inspection date. Do not describe the portfolio metrics as a live/current-season feed without verifying the source data's event-date range and pipeline freshness. A historical football research snapshot can still be valid if the date and scope are honestly labeled.

## Reproducibility and data protection

- CLI: `gcloud 589.0.0`, `bq 2.1.40`, authenticated project read access; queries ran successfully in `EU`.
- Schema inspection: `bq show --schema --format=prettyjson data-analiz-490513:football_mart.fct_club_risk_profile` and `fct_club_performance`.
- Aggregate queries use `COUNT(*)`, `COUNT(DISTINCT club_id)`, `COUNTIF(...)`, `SAFE_CAST(avg_overpay_pct AS FLOAT64)`, and `ABS(win_rate - 100 * SAFE_DIVIDE(wins,matches_played)) > 0.11`. No player-level or account information was extracted to this document.
- No `UPDATE`, `CREATE`, `DELETE`, `MERGE`, `dbt run` or dataset-changing action was executed; CLI credentials were not copied into the repository.

## Desktop acceptance — still OPEN

1. Open the current **production** PBIP, not the offline synthetic or an older temporary copy, using Power BI Desktop.
2. Refresh `fct_club_risk_profile`; record actual row count, error count, the failing Applied Step and the full error text if an error appears.
3. Confirm `avg_overpay_pct` is a valid numeric column in the loaded model and check a small number of displayed values against BigQuery.
4. Refresh `fct_club_performance` and verify the formatted win rate against actual `wins / matches` for a known club.
5. Check genuine data coverage dates and preserve a clear historical-snapshot disclosure where appropriate; complete screenshots and all 13-page visual acceptance.
6. Run hosted CircleCI **only after** these Desktop/warehouse gates and the remaining development work are complete.

**Acceptance:** `source_checks=PASS` can coexist with `powerbi_desktop_refresh=NOT_VERIFIED`, `bigquery_production_reconciliation=NOT_VERIFIED`, and **portfolio_release=HOLD**.
