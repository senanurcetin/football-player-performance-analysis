# NEXUS Football — Power BI visual refinement roadmap

**Date:** 13 October 2026  
**Canonical edition:** `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` (live BigQuery)  
**Comparison edition:** `powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` (synthetic fixtures)  
**Product release:** **HOLD** until actual Desktop rendering and production refresh reconciliation.

## Product direction

One editable 13-page PBIR report with a restrained dark NEXUS identity; not a duplicate deck, generated dashboard image, or redesign that destroys analytic bindings. Apply typography and spacing improvements **inside native visuals**, protect honest metric semantics and accessibility, and keep production/demo PBIR styles in parity.

| Element | Source token / standard |
| --- | --- |
| Hero Home/Closing | `#071829` |
| Nine analytics and drillthrough page canvases | `#091E33` |
| Supporting dark KPI surface | `#102B47` |
| Primary data / comparison series | `#4EA8FF` / `#8F9BFF` |
| Light chart surface / labels | `#FFFFFF` / `#122942` |
| Warning emphasis | `#F6B95F` or `#F27E90` only when the data calls for it |
| Two genuine tooltip canvases | `#E7F0FC` / `#E8ECFA` |

## Stages, acceptance and current evidence

| Stage | Scope | Source deliverable | Native Desktop acceptance |
| --- | --- | --- | --- |
| 1 — ML Reliability typography | Feature Importance, Quality Gates, Segment Performance tables | 13pt titles, 10pt headers/values, 4pt row padding; preserve all visual geometry/queryState; source parity regression | Full text readable without overlap/undesired clipped headings at 100% zoom; scroll behavior acceptable |
| 2 — Performance hierarchy | Five KPI cards, per-90 and Top-N visuals, filters | Consistent hierarchy, high-contrast labels and sensible spacing; no DAX edits | Actual ranked values, titles, filter interaction and small-data cases |
| 3 — Segmentation and clubs | Player Segmentation and Club & League four-panel analytics | Meaningful axis labels; visual density, category sorting and differentiated asymmetric panels | Real data labels and values do not collide; negative differentials and percent formats are correct |
| 4 — Transfers and valuation | Transfer Success 365d, Transfer & Market Value, Player Market Value Prediction | Better unit-aware tables, evidence hierarchy, uncertainty visual distinction | Observed 365-day outcomes are not mislabeled as ML; real fee/percent tables readable and correct |
| 5 — Navigation / editorial | Home, Closing, sidebar, footer | Seven identifiable Home links, predictable active/hover/focus, official logo, readable concise link labels | Click, keyboard focus and footer reachability; no logo SVG issues |
| 6 — Details / hover | Two hidden drillthrough pages and two 560x320 tooltips | Contextual backgrounds, aligned typography, clipped-content guards and source link-contract tests | Drillthrough filter context and tooltip hover display actual relevant rows |
| 7 — Release evidence | All 9 visible + 2 drillthrough + 2 tooltip pages | Local structural checks and explicit evidence checklist; no expensive hosted CI | 13-page real Desktop screenshot matrix, successful production BigQuery refresh, DAX/SQL reconciliation, zero release blockers |

### Stage 1 source implementation

The editable **ML Model Reliability** page uses three data-bound `tableEx` visuals:

- `6a52894b1eadaab185b4` — Feature Importance (425×230)
- `9cac2684a07ca1c85ca6` — Quality Gates (425×230)
- `44ef7cfce32d97d2bb52` — Segment Performance (870×225)

Previously all had 8pt title/header/value and row padding 3pt. The first typography pass increases the title to **13pt**, column headers and values to **10pt**, and row padding to **4pt** in both source editions. Table positions, data projections, sorting, numeric formats, page links and DAX remain unchanged. The Segment Performance header background is additionally darkened from `#487FD8` to `#173451`, improving white 10pt header contrast from approximately 3.96:1 to 12.75:1; the first two headers retain `#122942`. Wrapped headers are retained. The new source regression checks edition equality, unchanged bounds/projection counts and the new typography. The increase may cause horizontal scrolling or narrower visible data: verify in Desktop and adjust only with screenshot evidence.

**Verification boundary:** Live PBIR JSON/source comparisons can prove exactly which fields changed, but cannot prove Power BI actually renders 10pt table text as intended. This stage remains **SOURCE UPDATED / DESKTOP QA HOLD** until the user tests in Microsoft Power BI Desktop.

## Stage 2 source implementation — Player Performance

The five bound KPI cards on page `d2bc1e6a078c5c5b125c` now share a 64px height, y=118 baseline, 200px widths, and exact 12px gaps (x=157,369,581,793,1005). The minutes card title is shortened to **Avg Minutes / Match** without changing its average/minutes measure.

A concrete footer collision was found in the source geometry: the Goals vs Assists scatter originally ended at y=699.26 and the pivot performance table ended at y=702.53, **below the footer starting at y=679**. They now end at approximately y=670.22 and y=670.04, preserving an approximately 9px clearance before the footer. The combo chart already ended at y≈671 and remains unchanged. Two PBIP editions share the identical layout and underlying query bindings.

New `tests/test_powerbi_player_performance_layout.py` checks KPI rhythm, all bound Player Performance visuals against the footer, and workspace/demo query parity. Source-file position checks do not prove the chart's scroll/render behavior: inspect scatter axes, pivot table rows and footer reachability at 100% zoom in **real Power BI Desktop** before acceptance.

## Stage 3 source implementation — Segmentation / Club & League

Both editions now present the 8 native, data-bound two-page charts with **11pt category/value-axis titles** (previously 10pt). The 13pt chart headings, 11pt data labels, white panels, NEXUS blue/lavender data accents, filtering, original category/value projections, and the asymmetric 1280×720 compositions remain intact.

Business titles now reveal what is aggregated:
- Segmentation: **Player Goals by Club** for `Sum(fct_player_performance.total_goals)`, and **Total Market Value by Position** for `Sum(fct_player_performance.market_value_in_eur)`.
- Club & League: **Matches by Competition** for `Sum(fct_competition_performance.matches_played)`.
- Club Win Rate, Goal Difference by Club, and remaining charts retain their established titles. Source regression guards now pin the relevant aggregation queryRefs.

The earlier layout regression had accidentally retained obsolete **280px** lower-row heights, but the current PBIR lower panels are already **268px**: starting at y=403, they end at **y=671**, preserving 8px before the footer at y=679. This turn fixes the stale `test_powerbi_chart_design.py` expectation and tightens its footer gate; `test_powerbi_ux_polish.py` likewise now checks the current y=679 footer and 11pt axes. No further relocation of those well-positioned panels was warranted.

### P0 observation — verify win-rate scale before publishing

A separate source-level data contract mismatch remains: production `models/intermediate/int_club_performance_summary.sql` multiplies the club win rate by **100**, whereas the offline demo `fct_club_performance.tmdl` contains fractions (e.g. 0.40000). **Both** semantic-model columns currently declare `formatString: 0.0%`, whose percent scaling may display production ratios incorrectly (40.0 raw → 4,000% displayed), even if the underlying warehouse metric is correct. This is **not** an axis-font defect and must not be concealed with a new label or confused with the unrelated `fct_club_risk_profile` refresh errors. Reconcile the live BigQuery club rate to `wins / matches` in Power BI Desktop and choose one proven scale before promoting the report. No production mart, query, or model type was modified in this visual-only batch.

## Required local checks (no GitHub Actions quota)

```powershell
python scripts/check_powerbi_release_handoff.py --output powerbi-handoff.json
python -m unittest discover -s tests -p 'test_powerbi_ml_table_typography.py' -v
python scripts/audit_powerbi_layout.py
```

Do not mark the project ready for portfolio screenshots before verifying **real workspace** credentials, error-free refresh and table/tooltip rendering. Synthetic `dim_clubs` 6-row source corrections and the unrelated production `fct_club_risk_profile` refresh triage remain separate acceptance cases.
