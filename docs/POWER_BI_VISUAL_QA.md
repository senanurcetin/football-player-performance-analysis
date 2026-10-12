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

The obsolete six-image **green-era dashboard gallery and its README were deleted from the active repository**. The superseded editorial-cover SVG was removed too. No historical slide deck is shipped as the active product. The authoritative deliverable is the native, editable PBIR in `powerbi/workspace` and `powerbi/offline-demo`. The two report definitions have a NEXUS palette, but **have not been rendered in Desktop** to verify contrast, data, refresh or charts. Never substitute an invented dashboard screenshot.

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

An offline source parity test is provided at [`tests/test_powerbi_chart_design.py`](../tests/test_powerbi_chart_design.py). **No new Power BI report screenshot has been produced or approved**: actual Desktop open/refresh, chart interactions, DAX evaluation, cross-filters and final display quality still require testing on the authorized Windows machine. The old green-era captures were removed rather than retained in the active repository.

## Additional native report design — 13 October 2026 (CI-free source review)

Two more **editable PBIR pages** now match the 365-day report's card and typography system in **both** `workspace` and `offline-demo`:

| Page | Actual bound chart panels | Source directory |
| --- | --- | --- |
| Player Segmentation | Players by Position; Age Group Distribution; Goals by Club; Market Value by Position | `Report/definition/pages/24c53960ddc19662d824/visuals/a7e1*/visual.json` |
| Club & League Analysis | Club Win Rate; Goal Difference by Club; Competition Matches; Goals by Competition | `Report/definition/pages/25f58efd2bb140e62be9/visuals/a7e2*/visual.json` |

All **eight real charts** retain their original category/value query bindings and chart types. Each receives 13 pt navy titles, 11 pt high-contrast data labels and consistent 12 pt panel corners. The existing blue/lavender series scheme remains intact. There are **16 native visual-source edits**: 8 charts × 2 report editions. Textbox decorations, page backgrounds and underlying measurements are untouched.

The expanded [source regression](../tests/test_powerbi_chart_design.py) checks JSON parity, chart types, visual titles, display settings and nonempty data query state. This is a **static source review without CI** — not evidence that Power BI Desktop refreshes, cross-filtering or dashboard page renders pass. Historic PNGs remain historic until the actual PBIR project is opened and visually captured.

## Editorial NEXUS page compositions — 13 October 2026

The presentation is a single native PBIR report with **distinct, coordinated page identities**: dark navy Home, deep-blue performance control room, soft lavender player segmentation, ice-blue club/league, slate-blue transfer market, cool-blue market-value prediction and technical blue ML reliability. Both drillthrough detail pages and both tooltips have subdued corresponding backgrounds. All 13 pages keep their Power BI-native objects; there are no exported slide duplicates.

The visible report storyline now places **ML Model Reliability before Closing**, keeps the Home entry first, and uses clean page/tab labels without decorative emojis. The 365-day Transfer Success page has its own asymmetric evidence-chart composition.

**In addition, 16 primary query-bound chart/table/card objects per report edition were recolored** at the object level, not just via the global theme. These cover Player Performance, Transfer & Market Value, Market Value Prediction and ML Model Reliability. Obsolete green or unbranded gray accents were replaced with NEXUS blue, lavender, navy and neutral shades. All existing DAX, query state and chart types are preserved. Smaller secondary objects still require visual inspection.

The four principal native charts on **Player Segmentation** and **Club & League Analysis** were given page-specific asymmetric layouts while respecting 1280×720 bounds, existing navigation bands and original data-binding roles. Source tests now assert paired workspace/offline positions, page background palette and no overlap among those four per-page chart objects. This is *source geometry only*; visible visual collision with other legacy objects still requires Desktop review.

The six obsolete green-era PNG files, their gallery index and the superseded editorial cover were deleted; no current screenshot was fabricated or substituted. RegisteredResources embedded in the PBIR are **not deleted without confirming that report object bindings no longer reference them**.

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
