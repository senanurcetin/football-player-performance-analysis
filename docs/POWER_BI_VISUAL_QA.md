# Football Power BI visual quality and release gate

## Verified source contract — October 2026

The authoritative production mart at `models/marts/fct_transfer_success_labels.sql` emits **only observed 365-day outcomes**, using **20 percentage points of market-value growth** as the binary success threshold. This is an *observational transfer outcome*, **not** an ML transfer-success prediction. The staging mart `fct_transfer_fixed_horizon_outcomes.sql` separately holds 90-, 180- and 365-day outcome records and their completeness statuses.

Both `powerbi/workspace/FootballPlayerAnalysis` and `powerbi/offline-demo/FootballPlayerAnalysis` now use matching 365-day measures for the Transfer Success Analysis page. Using a filter of `label_horizon_days = 90` on the production labels table would return no rows.

The offline demonstration uses 24 fictional transfer rows, with coherent fixture keys, fee-to-value percentage **points** (not fractions), 365-day valuation dates, observed result statuses, and 20% success flags. The demo currently contains 11 positive and 13 negative examples. It is not representative of source distributions or real players.

## Transfer Success Analysis page — required evidence

The page includes four breakdowns (transfers by position, average fee, success rate, and follow-up status), plus these four indicators:

| Metric | Definition |
|---|---|
| Eligible transfers (365d) | Distinct transfer keys whose 365-day target plus 30-day observation window is before the latest valuation cutoff |
| Observed outcomes (365d) | Eligible transfer keys with a non-missing observed 365-day outcome |
| Follow-up coverage (365d) | Observed / eligible, in percent |
| Reliability notice | Small observed sample (<30), low follow-up coverage (<80%), or observational-only reminder; none implies causal validity |

The reporting cutoff is `MIN(TODAY(), MAX(source_latest_valuation_date))`. This avoids presenting recent, not-yet-observable transfers as failed follow-ups. Rates and outcomes must be reconciled to the live warehouse before production publication.

## Historical images vs. present PBIR

The six files in `docs/assets/screenshots/` belong to an older **green** presentation. They are retained as historical files and have been removed from the current README dashboard preview. They must not be used as current NEXUS screenshots. The two PBIR definitions have a NEXUS navy/blue theme, but have **not** been rendered in Desktop to verify actual contrast, content or labels.

## Repeatable source-level checks (without CI quota)

From repository root with Python 3.10+:

```powershell
python scripts/check_powerbi_project.py
python scripts/check_powerbi_offline_demo.py
python scripts/audit_powerbi_visuals.py
```

The demo preflight includes a 365-day SQL-contract guard and fixtures reconciliation. The visual audit checks page count/order, visual binding fields, watermark presence on normal demo pages, basic bounds and obviously incorrect CountNonNull summarization. These scripts **do not** execute Power BI DAX, Microsoft custom visuals, Power Query or BigQuery queries; source validation is not Desktop acceptance.

## Required Power BI Desktop acceptance

1. Open **offline demo** `powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`. Refresh all 33 inline fixture tables; no BigQuery credentials should be requested.
2. Confirm Home opens initially. Test left-nav and Home links, plus hidden detail drillthroughs and both tooltips.
3. Inspect every visible page, especially the three rebuilt pages. Verify chart types, populated data, units, titles, native and custom visuals, tooltips, axes and cross-filter behavior.
4. Verify Transfer Success Analysis has four chart panels **and** four cohort/reliability cards. The success threshold is 20% over 365 days, not 90-day, and observed/eligible counts must reconcile. The demo reliability warning must not suggest the sample is decision-ready.
5. Inspect Player Performance rates and Top N charts to ensure counts are not used in place of per-90 values. Check panel contrast against NEXUS dark/light surfaces and ensure no teal/green fragments remain.
6. Verify the `SYNTHETIC DEMO / NOT REAL DATA` watermark is readable on **all 11 full-size pages**, including when images are cropped.
7. Capture authentic current Desktop-rendered screenshots only after passes 1–6. Do not edit old images to simulate success.
8. On the production PBIP, authenticate BigQuery separately; reconcile source counts, transfer cohorts, labels and costs to governed SQL; check that DAX uses the populated 365-day label mart.

## Known blockers and release decision

The authorized Desktop Commander device was **offline at the latest check**. No open/refresh/render tests or real BigQuery reconciliation have been completed. Source-level structural tests can run without CI quotas; **passing them is insufficient for visual signoff**. The remaining synthetic marts are illustrative and may contain other implausible relationships or time-series values.

**Decision: HOLD portfolio release until a local Desktop evidence pass is recorded.**
