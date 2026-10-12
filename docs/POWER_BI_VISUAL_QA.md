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

## Implemented Power BI PBIR source design — 12 October 2026

**Actual editable report change:** the 365-day Transfer Success Analysis page has four **native data charts** edited in both `powerbi/workspace/FootballPlayerAnalysis` and `powerbi/offline-demo/FootballPlayerAnalysis`. The source changes are in each chart's `Report/definition/pages/4c63ad904b1db6e0d156/visuals/*/visual.json`, **not** generated cover art.

| Panel | Visual type | Display title | NEXUS series color |
| --- | --- | --- | --- |
| Transfer count by position | Clustered bar | Observed transfers by position · 365d | `#4EA8FF` |
| Mean transfer fee | Clustered column | Average transfer fee by position · 365d | `#8F9BFF` |
| Observed success rate | Clustered bar | Observed success rate by position · 365d | `#487FD8` |
| Outcome follow-up | Donut chart | 365d outcome follow-up status | `#8F9BFF` |

These concrete PBIR edits standardize 13 pt chart titles, 11 pt data labels, dark-blue label contrast and 12 pt corner radius. Existing queryState bindings and underlying models are untouched. The native report still uses BigQuery in workspace and deterministic synthetic inputs in offline-demo; the four chart JSON payloads match across both modes.

An offline source parity test is provided at [`tests/test_powerbi_chart_design.py`](../tests/test_powerbi_chart_design.py). **No new Power BI report screenshot has been produced or approved**: actual Desktop open/refresh, chart interactions, DAX evaluation, cross-filters and final display quality still require testing on the authorized Windows machine. The historical green-themed screenshots stay historical.

## Additional native report design — 13 October 2026 (CI-free source review)

Two more **editable PBIR pages** now match the 365-day report's card and typography system in **both** `workspace` and `offline-demo`:

| Page | Actual bound chart panels | Source directory |
| --- | --- | --- |
| Player Segmentation | Players by Position; Age Group Distribution; Goals by Club; Market Value by Position | `Report/definition/pages/24c53960ddc19662d824/visuals/a7e1*/visual.json` |
| Club & League Analysis | Club Win Rate; Goal Difference by Club; Competition Matches; Goals by Competition | `Report/definition/pages/25f58efd2bb140e62be9/visuals/a7e2*/visual.json` |

All **eight real charts** retain their original category/value query bindings and chart types. Each receives 13 pt navy titles, 11 pt high-contrast data labels and consistent 12 pt panel corners. The existing blue/lavender series scheme remains intact. There are **16 native visual-source edits**: 8 charts × 2 report editions. Textbox decorations, page backgrounds and underlying measurements are untouched.

The expanded [source regression](../tests/test_powerbi_chart_design.py) checks JSON parity, chart types, visual titles, display settings and nonempty data query state. This is a **static source review without CI** — not evidence that Power BI Desktop refreshes, cross-filtering or dashboard page renders pass. Historic PNGs remain historic until the actual PBIR project is opened and visually captured.

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
