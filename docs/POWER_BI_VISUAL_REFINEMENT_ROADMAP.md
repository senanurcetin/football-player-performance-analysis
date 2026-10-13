# NEXUS Football — Power BI visual refinement roadmap

**Date:** 13 October 2026  
**Canonical edition:** `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` (live BigQuery)  
**Comparison edition:** `powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` (synthetic fixtures)  
**Product release:** **HOLD** until actual Desktop rendering and production refresh reconciliation.

**CI execution policy:** Complete source development, offline checks and real Desktop/BigQuery acceptance **before** triggering hosted CI. CircleCI workflows are opt-in through `run_final_ci=true`; see [CI-last release policy](CI_RELEASE_GATE_POLICY.md).

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

A separate source-level data contract mismatch was identified: production `models/intermediate/int_club_performance_summary.sql` emits the club win rate on a **0–100** scale, while the offline demo `fct_club_performance.tmdl` holds **0–1** fractions. Both semantic-model columns use `formatString: 0.0%`, which multiplies its underlying numeric value by 100 for display. In the subsequent **dedicated P0 fix**, the production TMDL Power Query now adds a null-preserving **Win Rate Fraction** step, dividing **only** `win_rate` by 100 before import. The warehouse/dbt mart and demo fixture remain unmodified, and all existing chart bindings still target `win_rate`. The read-only model test `tests/test_powerbi_win_rate_scale_contract.py` protects this distinction. **Still required:** actual Power BI Desktop refresh and a comparison of the displayed club rate with `wins / matches` from live BigQuery; do not mark the product accepted from static M source alone. This is separate from the unresolved production `fct_club_risk_profile` refresh errors.

## Stage 4 source implementation — Transfer Market / Player Valuation

Both editable PBIR editions received a typography and contrast improvement across eight bound visuals: four financial comparison charts, two category-distribution donuts and two multi-column evidence tables. The common dark page canvas `#091E33` and white/light native visual panels are unchanged.

- **Two evidence tables:** `Transfer transaction details` (615px / 7 fields) and `Player valuation estimates` (≈512px / 8 fields). Title 8→13pt, column-header/body 8→10pt, row padding 3→4pt and header background `#487FD8`→`#173451` under white text. Existing unit-aware headers, data projections, sorting and panel widths are unchanged. Review horizontal scrolling with actual data.
- **Four financial bar/column charts:** Title 8→13pt, data labels 8→10pt and both axis title fonts 10→11pt; values, measures, categories, sorting, colors and geometry are unchanged.
- **Two donut charts:** Title 8→13pt; legend/label text 8→9pt, and label colors `#487FD8`→dark `#122942` on light panels for improved small-text contrast. The 235px market donut remains compact and may require Desktop inspection for truncated category names.

The existing `tests/test_powerbi_transfer_value_editorial.py` now expects 11pt finance/valuation axes but retains its 10pt 365-day transfer-outcome contract, so this pass does not alter the distinct observational outcomes page. The new `tests/test_powerbi_financial_visual_typography.py` guards both editions, table surfaces, native title/label sizes and the footer boundary (y=679, at least 8px clearance). No fake performance metrics, transfer outcomes or model predictions were introduced.

**Acceptance still blocked:** source parity alone cannot establish accurate actual values, table scroll quality, interactions, or dark/light contrast in Power BI Desktop. Keep **HOLD** until authentic real-data 100%-zoom captures and warehouse reconciliation are reviewed.

## Stage 5 source implementation — Home / Closing navigation

The original NEXUS logo and established hero copy on the dark `#071829` canvas are preserved. This narrow native Power BI interaction pass improves **all seven Home module links** and the Closing-to-Home CTA in both `workspace` and `offline-demo`.

- The Home module links now use uniform **13pt** button text (previously 12pt), with each default, hover and selected state carrying an explicit identical label. Previously the Player Performance hover/selected states and Clubs & Leagues hover state had no own text literal and relied on inherited formatting.
- Keep the original seven PageNavigation destinations, 392×34 button geometry, 37px vertical rhythm, and NEXUS surfaces: default `#173451`, hover `#245078`, selected `#285E9D`. Keep the short, numbered module names and accessible alternative text.
- The Closing action now reads **← BACK TO HOME** in all states (was **← EXPLORE THE REPORT**, despite always navigating to Home), grows from 13pt to 14pt, and has a distinct NEXUS selected fill `#285E9D`. Its native Home route, alt text, size, position and brand/logo geometry stay intact.
- New `tests/test_powerbi_home_closing_states.py` checks both report editions, full native PageNavigation destinations, per-state labels/font sizes, control colors, and Closing CTA semantics.

This is a PBIR source-state contract; Power BI Desktop must still establish actual hover, focus, keyboard navigation and label wrapping behavior. There is no claim of a rendered screenshot, passing BigQuery refresh or finished release. **HOLD** remains until engine-level acceptance.

## Stage 6 source implementation — native contextual tooltip polish

An audit of the **two hidden 560×320 tooltip pages** found lingering legacy green visuals, despite already-correct pale NEXUS page canvases. The visual-level background of the transfer and prediction header was `#2E6B45`, chart/card panels used `#F6FBF5`, and axis labels were green-gray `#536A60`. Each tooltip still presented mixed-language labels, a 9pt title, and 8pt chart labels.

This source pass revises three existing native visuals per tooltip, in **both** production and synthetic PBIR editions:

- Header strips use NEXUS navy `#173451`, concise English module labels and 11pt white text; original positions (x=10, y=8, 540×28) remain unchanged.
- Existing scatter and multi-row metric cards retain bound queryState, tooltip filter context and 560×320 geometry. Their light surfaces are white, 11pt title text is `#122942`, scatter axis/legend and card headings are 9pt, with slate axis labels `#526981`.
- Scatter headings now distinguish **average fee versus premium/discount (%)** and **predicted value versus upside (%)**, rather than mixing unrelated or ambiguous translated terms.
- The 1280×720 hidden **Prediction Detail** report had an obviously corrupt bilingual string (`li taşır.`) and an ungrounded suggestion that a narrow interval proves high model confidence. Its five 9pt explanatory bullets now distinguish forecast upside from realized outcomes, clarify that model intervals are not guarantees, and keep the scouting judgment appropriately qualified.

The new `tests/test_powerbi_tooltip_and_prediction_context.py` checks the two native tooltip canvases, geometry, per-visual NEXUS styles and edition parity, plus the Prediction Detail explanation. **No** DAX, schema, BigQuery source, visuals’ underlying projections, model uncertainty computation or original logo resource has changed.

**Desktop acceptance required:** render tooltips from actual parent report visuals and verify the compact legends/headers are not clipped. Confirm Prediction Detail text fits at 100% zoom and actual player-context drillthrough filters work. Source-only tests do not prove hover/keyboard behavior. Hosted CI remains explicitly gated by the separate CI-last policy; release is **HOLD**.

## Stage 7 local-source preflight repair — CI remains gated

With the authorized Windows device reachable, the current source repository was cloned into a **temporary local audit checkout**, without any hosted CI run. Real local execution initially reported **2 failures among 79** Power BI source unittests: a stale Transfer Success lower-row expectation (260px instead of native 239px), and an authentic ML Reliability Home-button overlap with the registered logo. This work corrects both source defects and strengthens their regression coverage.

The comprehensive handoff additionally exposed **two layout warnings** (one per PBIP edition): the legacy **Transfer Hacmi** column chart at x=353, y=470 overlapped the 615px transaction evidence table by approximately 87% and extended below the footer. It has been preserved, relabeled **Transfers by Position**, given NEXUS styling, and moved to the unoccupied lower-right panel at **x=985, y=470, 248×201**. The 615×201 table remains in place, and the source measures and queryState are unmodified. An explicit test now asserts right-side placement, native Transfer Count aggregation and footer clearance in both report editions.

**Executed Windows local evidence on the repaired branch:**
- **80/80** `test_powerbi_*.py` tests PASS, including the added table/chart collision guard and enhanced Reliability masthead guard.
- `python -m compileall -q scripts` PASS; `python scripts/check_offline_ci.py` PASS (**11 YAML / 51 SQL-Jinja** files).
- Production PBIP structural, synthetic demo fixture and query binding checks PASS; **33 fixture tables**, 13 pages, model provenance maintained.
- `python scripts/audit_powerbi_layout.py` PASS with **0 layout warnings** across workspace/demo.
- `python scripts/check_powerbi_release_handoff.py` PASS with `source_checks=PASS` and **6/6 preflight components passing**.

**Still not release acceptance:** no authenticated BigQuery refresh or screenshot-based Desktop rendering was performed. Power BI Desktop was detected as installed on the device, but this does not prove the report opened, refreshed or rendered. The `fct_club_risk_profile` production issue, win-rate reconciliation, hover/drillthrough tests and 13-page real-data screenshots remain gated. The prior CircleCI failure was locally reproduced and repaired, not re-run in hosted CircleCI. **Portfolio release remains HOLD.**

## Required local checks (no GitHub Actions quota)

```powershell
python scripts/check_powerbi_release_handoff.py --output powerbi-handoff.json
python -m unittest discover -s tests -p 'test_powerbi_ml_table_typography.py' -v
python scripts/audit_powerbi_layout.py
```

Do not mark the project ready for portfolio screenshots before verifying **real workspace** credentials, error-free refresh and table/tooltip rendering. Synthetic `dim_clubs` 6-row source corrections and the unrelated production `fct_club_risk_profile` refresh triage remain separate acceptance cases.
