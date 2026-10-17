# Football Power BI visual quality and release gate

> **Historical record archived 17 October 2026.** Contains dated design/refresh decisions; not a current claim. See [current project status](../../PROJECT_STATUS.md) and [visual QA](../../POWER_BI_VISUAL_QA.md).

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

An offline source parity test is provided at [`tests/test_powerbi_chart_design.py`](../../../tests/test_powerbi_chart_design.py). **No new Power BI report screenshot has been produced or approved**: actual Desktop open/refresh, chart interactions, DAX evaluation, cross-filters and final display quality still require testing on the authorized Windows machine. The old green-era captures were removed rather than retained in the active repository.

## Additional native report design — 13 October 2026 (CI-free source review)

Two more **editable PBIR pages** now match the 365-day report's card and typography system in **both** `workspace` and `offline-demo`:

| Page | Actual bound chart panels | Source directory |
| --- | --- | --- |
| Player Segmentation | Players by Position; Age Group Distribution; Goals by Club; Market Value by Position | `Report/definition/pages/24c53960ddc19662d824/visuals/a7e1*/visual.json` |
| Club & League Analysis | Club Win Rate; Goal Difference by Club; Competition Matches; Goals by Competition | `Report/definition/pages/25f58efd2bb140e62be9/visuals/a7e2*/visual.json` |

All **eight real charts** retain their original category/value query bindings and chart types. Each receives 13 pt navy titles, 11 pt high-contrast data labels and consistent 12 pt panel corners. The existing blue/lavender series scheme remains intact. There are **16 native visual-source edits**: 8 charts × 2 report editions. At that particular chart-edit stage, textbox decorations, page backgrounds and underlying measurements were untouched; a later source change unified the nine analytics/drillthrough page backgrounds.

The expanded [source regression](../../../tests/test_powerbi_chart_design.py) checks JSON parity, chart types, visual titles, display settings and nonempty data query state. This is a **static source review without CI** — not evidence that Power BI Desktop refreshes, cross-filtering or dashboard page renders pass. Historic PNGs remain historic until the actual PBIR project is opened and visually captured.

## Editorial NEXUS page compositions — 13 October 2026

The presentation is one editable native PBIR report with **distinct, coordinated page compositions**, not different full-page pastel backgrounds. The current nine analytics/drillthrough pages share the NEXUS `#091E33` canvas; Home and Closing use `#071829`; only the two 560×320 contextual tooltip pages use pale `#E7F0FC` and `#E8ECFA` backgrounds. The earlier lavender/ice-blue page surfaces were superseded by the dark-unification changes in PR #44. See [the canonical 13-page canvas contract](../../BI_DESIGN_SYSTEM.md#current-pbir-canvas-contract-13-october-2026). All pages retain editable Power BI-native objects; there are no exported slide duplicates. Desktop visual acceptance remains HOLD.

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

## Actual Desktop screenshots and feedback — 13 October 2026

The user provided **real Power BI Desktop screenshots** of the synthetic Home and
Player Segmentation pages. They showed non-shippable design defects: legacy burgundy
theme-color shapes in page headers and navigation, emoji sidebar controls, white
textbox containers obscuring pale hero typography, technical axis labels and an
undifferentiated lavender value donut. This is **negative visual evidence** and
supersedes prior source-only claims of completed dashboard modernization.

A subsequent PBIR source change explicitly sets NEXUS navy header/side-panel
fills on the six main analytical pages; changes the seven navigation shortcuts on
those pages from emoji to aligned H/P/S/C/T/V/M monograms while **retaining page
navigation targets**; disables Home/Closing textbox backgrounds; and replaces
Segmentation's market-value donut with a horizontal bar comparison. Production
and offline-demo definitions are both updated. The prediction-page hardcoded
R²/WAPE claim is removed from the editorial subtitle; model-quality metrics
must be checked from actual evaluated measures.

The **six-row synthetic `fct_club_risk_profile` fixture** had quoted numeric
literals in typed M columns, fractional values where governed SQL expects
percentage points, and minimum-cohort flags inconsistent with the 30-observation
threshold. These have been repaired and a fixture-level check added. If the
**production BigQuery** table still reports six row errors, use Power BI's
**View errors / Details** pane and supply the exact column and message; the
synthetic correction alone does not prove a production-refresh fix.

Source checks without hosted CI:

```bash
python scripts/check_powerbi_offline_demo.py
python scripts/check_powerbi_visual_feedback.py
python scripts/audit_powerbi_layout.py
```

**Release remains HOLD:** no updated Power BI Desktop reload, DAX/Power Query
execution, full-page contrast inspection or current screenshot recapture was
observed. The next release must use new authentic Desktop screenshots.

## Original NEXUS brand image — 13 October 2026

The official NEXUS logo has been registered as a binary PBIR resource in the
BigQuery workspace and synthetic offline edition. Nine visible pages and two
hidden drillthrough pages reference the same canonical image per edition.
Original source identity is guarded by its Git blob SHA. A source-level
`test_powerbi_nexus_logo.py` checks every image reference and its placement.

**Not yet verified in Desktop:** whether the `visualType=image` rendering,
resource-loading behavior, default scaling and hero contrast are acceptable.
Capture screenshots only after loading the updated PBIP in Power BI Desktop;
keep the mandatory synthetic watermark in demo screenshots and no fabricated
real-world model claims. Portfolio release remains **HOLD** until reviewed.

## Closing hero collision and route completion — 13 October 2026

A source-geometry review found the previous Closing editorial text boxes ran
behind the 300x300 registered NEXUS logo. The Closing text area now ends at
x=863 while the logo starts at x=890, and the copy is tightened to
**EVIDENCE. INSIGHT. ACTION.** The original brand image remains unchanged.

The ML Model Reliability header and Closing page now include real native Power
BI **PageNavigation** buttons returning to Home. All six seven-letter side
rails include accessible destination names (42 buttons per edition, or 84
described controls total), without altering their native target IDs or visual
geometry. These changes improve source-level clarity and keyboard navigation
semantics, but screen-reader and on-screen interaction behavior still require
Desktop testing.

Source gate: `python -m unittest discover -s tests -p 'test_powerbi_navigation_completion.py'`
plus `python scripts/audit_powerbi_layout.py`. No hosted CI was invoked;
real Power BI Desktop open/refresh/render acceptance is still **HOLD**.

## Transfer and modeled-value visual terminology — 13 October 2026

The four **365-day Transfer Outcomes** breakdowns now show native chart axis
titles with business labels instead of internal fields (for example,
`position`). The 365-day follow-up *status* breakdown uses horizontal bars
rather than a monochrome donut; its accessibility description explicitly says
missing follow-up is **not** a failed player transfer. The page header reads
**Observed Transfer Outcomes / 365 Days** to distinguish observed evidence
from predictions. Existing queries, row context, target horizon and KPI
definitions are untouched.

The Transfer Market and Player Valuation report pages now explicitly name
positions, seasons, fee premium/discount (%), modeled upside (%), and
predicted value. Known fee and predicted value axes use `€m` **only where
the existing PBIR `labelDisplayUnits` is set to 1,000,000**; source model
values are euros and are not rescaled or rewritten. Percentage measures
remain model-formatted as `0.0%`. Category labels in the two remaining
composition donuts are now readable English instead of internal Turkish
field identifiers; these charts retain their original grouping queries.

Source guard: `python -m unittest discover -s tests -p 'test_powerbi_transfer_value_editorial.py'`.
Real chart rendering, responsive text clipping, DAX outputs and production
BigQuery refresh are **not** verified here. The portfolio release gate remains
**HOLD** pending the owner's Power BI Desktop screenshot review.

## ML Reliability readable evidence panel — 13 October 2026

The native ML Reliability page had a source-level contrast defect: the
model-reading guide rendered pale/white text over a very pale side panel.
The side panel now uses `#102B47` NEXUS navy with legible `#E7F2FD`
content, and the content box ends within its colored surface. The filter
caption is corrected to the same contrast-safe treatment.

The old guide included **unsubstantiated universal WAPE/R² cutoffs** and
mixed-language labels. It now explains model evaluation using a held-out
baseline, predictive (not causal) feature importance, blocking quality gates,
freshness/drift, and segment sample sizes. The feature-importance column
formerly labeled `Tür` is presented as **Feature Type** without changing
the underlying queryRef or English report data.

Source gate: `python -m unittest discover -s tests -p 'test_powerbi_ml_reliability_panel.py'`.
The test checks source content, Power BI JSON parity, side-panel geometry
and WCAG-inspired text/background contrast calculations. It **does not**
replace real Power BI Desktop rendering, model evaluation or screen-reader
testing. Release remains **HOLD** until visually accepted.

## Read-only production club-risk refresh diagnosis

For the reported **six-row production** `fct_club_risk_profile` import error,
use [the schema and row triage procedure](POWER_BI_CLUB_RISK_REFRESH_TRIAGE.md).
This separates the BigQuery connector/warehouse issue from the already
corrected **synthetic six-row fixture**. It includes a live schema query and
checks for null/range/count anomalies; no production model or data is
silently altered and the root cause remains **unverified** until Desktop
provides the exact error column and message.

## Desktop screenshot remediation — 13 October 2026

The user-reported six errors on **offline-demo `dim_clubs`** can be traced in
source to 12 quoted floating-point literals (`average_age` and
`foreigners_percentage`) in six typed Power Query `#table` rows. These were
changed to numeric literals with the original values preserved. This
is a **source fix**; a fresh Desktop refresh is required to verify the six
errors disappear. It does not establish anything about production BigQuery.

The active report's source changes in both editions now cover:
- A tightly cropped official NEXUS masthead wordmark (original brand bytes
  retained) at larger size; Home/Closing keep the original brand image.
- Nine standard `#091E33` analytic/drillthrough canvases, unified blue
  chart palette and dark, high-contrast Performance KPI cards.
- Performance filter title contrast, treemap text accents, scatter-series
  accent and pivot-table striping, without changing any data queries.
- Six highly visible and readable bottom navigation legends, with lower
  visuals ending at or above y=671, legends beginning y=679, and no overlap.
- Both 1280×720 legacy pastel full-page shapes in Transfer Detail and
  Prediction Detail changed to NEXUS navy; green table stripe colors removed.
- Original demo provenance remains **only in the synthetic edition**.
  The production workspace edition never displays the synthetic watermark.

Release remains **HOLD**: manually inspect Power BI Desktop for SVG image
support, data refresh (especially `dim_clubs`), readable charts/filters,
footer fit, and transfer/prediction detail chart contrast. No fabricated
screen captures or unverified success claims.

Static guard:
`python -m unittest discover -s tests -p 'test_powerbi_desktop_feedback_fixes.py'`.
