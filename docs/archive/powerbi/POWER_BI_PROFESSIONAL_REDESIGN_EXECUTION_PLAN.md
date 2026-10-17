# NEXUS Football Intelligence — Professional Design Execution Plan

> **Archived historical record — 17 October 2026.** This document preserves prior engineering decisions and evidence; it is not the current delivery status. For current verified vs. pending checks, see [Project status](../../PROJECT_STATUS.md) and the [documentation index](../../README.md).


**Prepared:** 13 October 2026  
**Repository baseline:** `main` after PR #60 (`a1d48fb` at plan creation)  
**Canonical deliverable:** editable Power BI PBIR/PBIP; no substitute screenshots, static mockups or fabricated metrics  
**Editions:** live-BigQuery `powerbi/workspace/FootballPlayerAnalysis/` and clearly labeled synthetic `powerbi/offline-demo/FootballPlayerAnalysis/`  
**Release:** **HOLD**. The nine CircleCI jobs remain gated until all source, Desktop, visual, warehouse and interaction acceptance is finished.

## 1. Problem and outcome

Source-level work has established the navy NEXUS palette, branding, 13-page report structure, typography improvements and most basic geometric guards. At the time of planning, the current main branch passed **87/87 Power BI source tests**, **6/6 source handoff checks**, and the static layout audit reported **zero warnings**. This does **not** establish that the report looks professional when actually rendered in Power BI Desktop. User feedback explicitly identifies generic legacy-dashboard composition and a logo that looks pasted onto the page.

**Design outcome:** a cohesive *Football Intelligence product* where each page conveys a clear analytical question and decision, not a familiar grid of indistinguishable KPI cards, tables and charts. Improve **visual structure, chart selection, analytical narrative, affordances and interaction**, not another cosmetic color/font pass. Keep native editable Power BI assets and truthful data/provenance.

### Nonnegotiable constraints

1. Preserve original NEXUS wordmark artwork; use measured whitespace, alignment, scale and nonintrusive signature treatment. Never redraw the logo. The existing SVG-in-PBIR rendering capability must be visually verified.
2. Production numbers come only from validated BigQuery/model measures. Do not invent insights or baseline percentages to fill the design; a "no evidence" state is better than a fake card.
3. Never conflate observed 365-day transfer outcomes, retrospective valuations and ML predictions. Show prediction uncertainty, sample coverage, limitations and freshness explicitly wherever relevant.
4. Production and synthetic PBIR editions must share the same presentation/layout/queries as appropriate, while keeping separate source partitions and accurate, low-noise synthetic-data disclosures.
5. Refactor visual hierarchies without breaking slicers, drillthrough, interactions, accessibility, formatting, filter context or query binding. Chart-type swaps need a source contract and a Desktop proof.
6. No CircleCI invocation until the final accepted source commit: the opt-in `run_final_ci=true` gate stays **off** throughout the redesign.

## 2. Design system / visual target

| Layer | Target design | Acceptance |
| --- | --- | --- |
| Editorial hierarchy | One primary question/insight per page, optional context paragraph, focused KPI strip, one dominant explanatory graphic plus supporting comparisons | A reviewer can state the page's main question in **5 seconds** without reading a dense table |
| 1280×720 canvas | Consistent left-navigation lane, branded masthead, bounded content grid, fixed footer, 16–24px spacing rhythm | No collision, clipping or off-canvas element in **actual Desktop screenshots**, not just JSON |
| Typography | Distinct hero / section / data / provenance levels; conventional UI type, meaningful whitespace, not tiny all-caps everywhere | Normal chart labels ≳10–11pt where feasible; primary labels ≳12pt; actual 100% view legible |
| Chart surfaces | Dark shell `#091E33` / restrained white/near-white analytics panels; purposeful use of NEXUS blue/lavender, not excessive glow or gradient decoration | Color conveys metric role; axis/legend/category labels pass contrast and overlap checks |
| Scales/formatting | Units on every financial/percentage/valuation measure; consistent currency (EUR), per-90 and percentage-point semantics, negative/positive conventions | A percent cannot be confused with a fraction; axis tick labels and table headers fit |
| Evidence / confidence | Sample-size, missing-fee coverage, observation horizon, model prediction interval, snapshot provenance | No interpretation of a thin sample as a robust ranking; uncertainty remains visible |
| Logo | Compact signature lockup integrated with title/section rules; no large square brand artwork or disconnected floating overlay | Cropped wordmark loads in Desktop; no blurring/clipping; appropriate negative space |
| Interaction | Predictable Home/back, slicer/reset, active state, cross-filter, drillthrough and compact tooltip | Every native button and relevant filter has a functioning Desktop interaction |
| Synthetic edition | Clear but quiet "SYNTHETIC DATA / NOT REAL" notice on full-size demo pages | No confusion with production and no intrusive banner over charts |

These are **design targets**, not claims of current screenshot compliance. Avoid arbitrary additions of shapes where content structure can be improved.

## 3. Sequenced work packages

### P0 — Obtain truthful visual baseline before another mass redesign (0.5–1.5 engineer-days)

- Open the **current main** production PBIP from the correct path in Power BI Desktop, not an older temporary copy.
- Capture genuine 100% zoom Desktop screenshots of the **nine visible pages**, both hidden drillthrough pages (reached with real filter context), and both tooltip hover states. Capture the offline-demo home and one analytical page separately to check provenance.
- Classify each screenshot on a 0–3 scale for five dimensions: **hierarchy, graph quality, typography, spacing/brand integration and analytical clarity**. Produce a prioritized annotated defect register with affected page/visual ID and source path.
- Record the exact build, Git SHA, page IDs, data source (BigQuery vs synthetic), data-refresh status and known limitations. Mask personal identifiers/connection details.
- Confirm the original NEXUS wordmark actually renders; a valid PBIR JSON resource reference alone is insufficient.

**Gate:** a reproducible baseline screenshot matrix plus page-specific evidence. If actual screenshots cannot be obtained, do not declare visual completion and do not add ornamental changes blindly.

### P1 — Rebuild reusable reporting shell (1–2 engineer-days)

- Define a single practical masthead, logo signature, active left navigation, title/subtitle, content-grid/footers and spacing tokens for all nine full-size analytic/detail pages.
- Revisit the recently added 76 decorative brand source elements: keep only elements that improve hierarchy, remove needless bars/plates if they produce visual clutter or focus collisions.
- Establish chart surface types: **hero chart**, **secondary chart**, **evidence table**, **contextual KPI**, **notice/quality gate**. They must be visually distinguishable, not repeated cards of equal weight.
- Align light/dark contrast, consistent corner treatment, legends, tick formats and data labels. Protect a minimum 8px gap to the footer already at y=679.
- Build screenshot-driven native PBIR tests for grid boundaries, chart/label styles, original logo references and production/demo source parity.

**Gate:** the same editorial product shell on every applicable page; zero actual overlap/clipping; real Desktop review of logo and navigation.

### P2 — Transform visible analytics by decision workflow (4–7 engineer-days)

| Sequence | Page | Primary story / composition (not just a recolor) | Required interaction / semantics |
| --- | --- | --- | --- |
| 1 | **Player Performance Analysis** | Replace five equal-weight KPIs with a hierarchy that prioritizes a player/per-90 comparison; use one dominant performance/ranking visual, supporting distribution, then a compact evidence table | Club/position filters; minimum-minutes qualifier; per-90 units, data labels and Top-N sorting |
| 2 | **Player Segmentation** | Move from a symmetric four-chart dashboard to a **cohort/role comparison**: primary segment differences, secondary distribution and measurable context. Do not overinterpret an unsupervised segment | Player/position context, coherent cluster color mapping, meaningful category sorting, null/no-data states |
| 3 | **Club & League Analysis** | Turn four equal-size graphics into a **league comparison**: a dominant ranked league/club performance graphic, supporting win-rate vs sample-size context and goal differential evidence | Win rate displayed as 0–100% correctly (warehouse raw 0–100 is normalized to 0–1 in PBI); competition filter; sample count |
| 4 | **Transfer Success Analysis (365d)** | Lead with the **observed 365-day outcome and coverage** rather than attractive but potentially misleading categorical charts; follow with success/failure distribution and club/position evidence | An observed result is **not** an ML prediction; distinguish known outcome, missing outcome and minimum sample |
| 5 | **Transfer & Market Value Analysis** | Create a deliberate primary fee-vs-reference-value comparison, premium/discount explanation, then right-sized transfer-volume view and accessible transaction table | Currency labels, market-value baseline dates, unknown-fee handling; preserve repaired transfer-count/chart/table separation |
| 6 | **Player Market Value Prediction** | Give predicted vs previous value a visual hierarchy and show **interval/uncertainty** prominently; reorganize lower tables/cards to support a valuation decision rather than a flat spreadsheet page | No guarantee/profit language; quality and coverage qualifiers, prior/current comparison and clear missing-estimate states |
| 7 | **ML Model Reliability** | Build a **model governance board**: key quality gates/metrics at top, held-out baseline comparison as primary evidence, feature attribution and segment performance as drillable supporting sections | WAPE/baseline interpretation, quality gate status, sample count, drift/freshness, feature importance not mislabeled causal |
| 8 | **Home** | Evaluate the new seven-module two-column research atlas in real Desktop; refine editorial whitespace, hierarchy and wordmark lockup without restoring a giant image | All seven native page links, focus states and synthetic provenance parity |
| 9 | **Closing** | Treat as an editorial conclusion/navigation surface: concise evidence→decision flow and a restrained visual signature, not another fake KPI/dashboard | Native Home return action, readable text wrapping and clear ending |

Implementation rule: preserve underlying query roles and data semantics; when a different native visual type is more effective, prove the replacement with a separate PBIR field-binding test and actual Desktop rendering before removing the original.

### P3 — Context, details and meaningful interaction (1–2 engineer-days)

- **Transfer Detail (hidden):** a credible player/transfer profile: fee, reference baseline, observed follow-up and time horizon separated spatially. Test **actual player drillthrough** rather than a manually opened empty page.
- **Prediction Detail (hidden):** prior vs predicted, uncertainty interval, model provenance, and cautious interpretation, with supporting evidence not buried in uniform micro-tables.
- **Transfer + Prediction Tooltips (560×320):** high-density but readable; one explicit headline, one small explanatory visual and a concise metrics area. Validate hover clipping and limited-space legends.
- Audit selected/unselected/hover/focus states of the seven Home links, left rail, reset filters, slicers, keyboard tab order and drillthrough back path.
- Verify empty data, one-point data, long club names, null transfer fees, negative valuations/goal differences and narrow/outlier axes on production data. Do not use arbitrary fake figures to conceal these cases.

**Gate:** reproducible, passing Desktop interaction matrix (including relevant cross-filter context), not just source code checks.

### P4 — Finish with actual rendering, data accuracy and release (1–3 engineer-days plus external dependencies)

1. **Source quality:** updated tests pass, original BigQuery/demo partitions unmodified except separately authorized data fixes; all edited PBIR files parse; both editions preserve chart semantics and navigation.
2. **Visual evidence:** 13/13 distinct surfaces have genuine, dated Desktop captures at the current commit; zero visible clipped labels, logo/image failures, footer collisions or unexplained blank panels. Review at 100% and ordinary display scaling.
3. **Data acceptance:** actual production Desktop refresh completes with zero errors; `fct_club_risk_profile` row count and fields reconcile to validated BigQuery; `fct_club_performance.win_rate` correct; model/transfer metrics match authoritative sources. The mart modification timestamps were last observed in June 2026: disclose snapshot age and investigate source-date coverage.
4. **Demo integrity:** all 33 fixture tables load with zero errors and zero unplanned BigQuery prompts; synthetic provenance is visible without covering evidence.
5. **Reviewer sign-off:** screenshot before/after matrix, issue register, visual scorecard, verified test output and remaining limitations committed to a new design acceptance report.
6. **Only after all preceding gates:** explicitly run final CircleCI with `run_final_ci=true` on the signed-off `main` commit; require all nine jobs to succeed. Correct failures before removing product **HOLD**.

## 4. PR/review discipline and cadence

- **PR 1 — Desktop baseline & design tokens:** evidence/scorecard and reusable shell; no speculative visual mass-edit.
- **PR 2 — Performance + Segmentation + Clubs:** purpose-built page hierarchy.
- **PR 3 — Observed Transfers + Market + Prediction:** evidence-first transfer and valuation stories.
- **PR 4 — ML Reliability + details + 560×320 tooltips:** readable model quality, genuine contextual interactions.
- **PR 5 — Home/Closing/branding final pass:** based on actual screenshots and first four PRs rather than appearance guesses.
- **PR 6 — Acceptance fixes:** only defects found during Desktop render/refresh, plus attached real screenshot evidence and final provenance.
- **Final CI gate:** not a PR development step; opt-in only after product acceptance.

Each implementation PR needs: before/after **real** Desktop evidence (when Desktop access allows it); affected visual IDs; changed data/projection list (ideally none); production/offline source parity; test output; potential clipping/interaction risks; and honest AI-assisted disclosure. No assertions that Desktop visuals are proven from static geometry tests. Do not claim "finished" after fonts, palette or logo pass alone.

## 5. Completion criteria and prioritization

**Design completion:** genuine screenshots and a reviewed visual scorecard for 13/13 surfaces; no **P0/P1** issues; no 0/3 ratings in hierarchy, typography, chart quality, brand integration, analytical clarity; all required interactions verified and no false data/source claims. Aim for average **≥2.5/3** with qualitative sign-off from the user; this numerical target is a review heuristic, not a mathematically objective aesthetic measure.

**Engineering completion:** all relevant local tests green, updated regressions for each transformed native chart, zero source overlaps, Power BI refresh 0 unexpected errors, representative KPI cross-checks pass, and (last) all nine CircleCI jobs green.

**Current known blockers:** no accepted 13-page actual Desktop screenshot set; live Desktop refresh outcome unverified; older BigQuery marts require freshness/context evaluation. These are independent of the latest logo redesign PR #60 and must not be mislabeled completed.

**First next action:** capture and score the *current* 13 Desktop views, select one page (Player Performance or ML Reliability) as a high-impact **pilot**, and approve its actual rendered direction **before** applying that component hierarchy across the other report pages. This is how to stop repeatedly polishing the old layout.

## First pilot implementation — Player Performance (13 October 2026)

The first native source-level pilot has begun on **Player Performance Analysis** (page d2bc1e6a078c5c5b125c). See [the visual-specific pilot design and Desktop review checklist](POWER_BI_PLAYER_PERFORMANCE_PILOT.md).

Instead of five equal cards and three near-equal charts, the page has a **larger first-read G+A / 90 KPI** (278x74), a 510px-wide primary player-efficiency bar ranking, two supporting rate distributions and a separate bottom evidence row. The left-side position and club filters stay operational at their original coordinates. Two restrained numbered text dividers signal the analysis sequence without introducing fake values.

Implementation is mirrored between production and honest offline-demo sources. A local Git diff replay verified that the **24 original touched PBIR source visuals (12 per edition)** retained their original native visual types, query objects and PageNavigation, with **16 added pure shape/text nodes** and no changes to the data model or registered branding resources. The rewritten source regression covers all 11 original data-bound controls per edition, queryRefs, non-overlap, source parity, footer clearance and section hierarchy.

**Current evidence:** 89/89 Power BI unit tests PASS, dbt offline source preflight PASS, all six Power BI source handoff checks PASS, zero native layout warnings. **Still not approved:** genuine 100% zoom Desktop screenshot, narrow treemap labels, 496px pivot horizontal scrolling, actual click/hover/selection and production refresh. This is a committed *pilot*, not completion of the remaining report pages or a fully accepted visual redesign. CI remains final-stage opt-in.

## Implementation update — Segmentation and Club/League native editorial redesign (13 October 2026)

After the Player Performance pilot, the next two full-size analytical pages have source-level evidence hierarchies:

- **Player Segmentation**: deliberate observed roster-cohort composition (position-count hero, age distribution, then club goals and aggregate EUR market value by position), never mislabeled as an unsupervised ML segment model.
- **Club & League Analysis**: club win-rate ranking as the dominant outcome, goal difference as supporting evidence, then competition match and goal volumes at an explicitly distinct observational grain.

The two pages no longer share the old geometric four-panel template. There are 16 changed data-bound native charts (8 original visual IDs in each of the two source editions) and 24 new non-query editorial labels/rules (12 per edition). Native chart type, complete queryState/query content, navigation, registered logos and production vs offline data partitions are preserved. See [exact geometry, tests and Desktop acceptance checklist](POWER_BI_COHORT_LEAGUE_EDITORIAL_REDESIGN.md).

**Executed local checks:** 93/93 Power BI source unit tests PASS, offline YAML/Jinja preflight PASS, 6/6 source handoff gates PASS and zero source layout warnings. This is not a claimed real Desktop screenshot or final design approval. The next stage is visually verifying this composition in Power BI Desktop before revising its smaller labels or proceeding to the three transfer/valuation pages. CircleCI remains off by default and release remains HOLD.
