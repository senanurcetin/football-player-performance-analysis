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

Previously all had 8pt title/header/value and row padding 3pt. The first typography pass increases the title to **13pt**, column headers and values to **10pt**, and row padding to **4pt** in both source editions. Table positions, data projections, sorting, colors, formats, page links and DAX remain unchanged. Wrapped headers are retained. The new source regression checks edition equality, unchanged bounds/projection counts and the new typography. The increase may cause horizontal scrolling or narrower visible data: verify in Desktop and adjust only with screenshot evidence.

**Verification boundary:** Live PBIR JSON/source comparisons can prove exactly which fields changed, but cannot prove Power BI actually renders 10pt table text as intended. This stage remains **SOURCE UPDATED / DESKTOP QA HOLD** until the user tests in Microsoft Power BI Desktop.

## Required local checks (no GitHub Actions quota)

```powershell
python scripts/check_powerbi_release_handoff.py --output powerbi-handoff.json
python -m unittest discover -s tests -p 'test_powerbi_ml_table_typography.py' -v
python scripts/audit_powerbi_layout.py
```

Do not mark the project ready for portfolio screenshots before verifying **real workspace** credentials, error-free refresh and table/tooltip rendering. Synthetic `dim_clubs` 6-row source corrections and the unrelated production `fct_club_risk_profile` refresh triage remain separate acceptance cases.
