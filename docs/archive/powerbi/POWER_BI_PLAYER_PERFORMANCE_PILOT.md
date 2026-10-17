# Player Performance — evidence-first visual pilot

> **Archived historical record — 17 October 2026.** This document preserves prior engineering decisions and evidence; it is not the current delivery status. For current verified vs. pending checks, see [Project status](../../PROJECT_STATUS.md) and the [documentation index](../../README.md).


**Prepared:** 13 October 2026
**Page ID:** `d2bc1e6a078c5c5b125c`
**Sources:** `powerbi/workspace/FootballPlayerAnalysis/` (BigQuery) and `powerbi/offline-demo/FootballPlayerAnalysis/` (explicitly synthetic)
**Product status:** **SOURCE UPDATED / DESKTOP DESIGN ACCEPTANCE HOLD**. A real Power BI Desktop capture from the updated PBIP is required; this is not a claimed render or an invented screenshot.

## Design rationale

The previous composition had **five equally sized cards (200×64 each)**, followed by **three near-equal panels** with the most important player-efficiency bar squeezed to **293×239**, then three equal bottom charts. Users could not immediately see the report's primary comparison.

The new visual grammar is a clear analysis sequence:

**SCOUTING LENS** → **G+A PER 90** → **01 / EFFICIENCY RANKING** → **GOALS/90 + ASSISTS/90** → **02 / CROSS-CHECK THE PLAYER EVIDENCE**.

This is a substantive **information hierarchy and geometric composition** change within original Power BI native visuals, not another blanket palette or logo update.

| Native component | Previous bounds (approx x/y/w/h) | Pilot bounds (x/y/w/h) | Purpose |
| --- | --- | --- | --- |
| Primary G+A per 90 KPI | 1005 / 118 / 200 / 64 | **257 / 113 / 278 / 74** | Primary, first-read productivity rate; 26pt value, 13pt heading, blue accented border |
| Total Goals | 369 / 118 / 200 / 64 | 547 / 113 / 160 / 74 | Supporting volume |
| Total Assists | 581 / 118 / 200 / 64 | 719 / 113 / 160 / 74 | Supporting volume |
| Avg Minutes / Match | 793 / 118 / 200 / 64 | 891 / 113 / 174 / 74 | Playing-time context |
| Total Players | 157 / 118 / 200 / 64 | 1077 / 113 / 198 / 74 | Cohort coverage context |
| **Player G+A/90 bar ranking** | 258 / 196 / 293 / 239 | **257 / 220 / 510 / 223** | Main evidence hero, more than twice the width of either 243px treemap |
| Top Players / Goals per 90 | 560 / 196 / 351 / 239 | 780 / 220 / 243 / 223 | Supporting goal-rate view |
| Top Players / Assists per 90 | 919 / 195 / 356 / 239 | 1036 / 220 / 240 / 223 | Supporting assist-rate view |
| Goals vs Assists / by Position | 86 / 451 / 328 / 219 | 86 / 474 / 343 / 197 | Position cross-check |
| Age Group: Rate + Market Value | 420 / 452 / 327 / 219 | 440 / 474 / 327 / 197 | Age-cohort evidence |
| Player pivot evidence table | 755 / 450 / 522 / 220 | 779 / 474 / 496 / 197 | Detailed player metrics and market-value record |

Left-side **position / club slicers** and the seven-button navigation rail remain functional and keep their original bounds, original queryState and selections. Data-chart query references, native chart types, tooltip projections, DAX, model tables, BigQuery source, production/demo provenance, footer location (**y=679**) and registered NEXUS assets have **not** changed.

### Native editorial elements

Six succinct native textboxes clarify the lens, the comparison flow and the need to check playing time; two small shapes add a single visual accent to the primary rate and a thin rule to separate evidence sections. These are **not data-bound**, cannot be mistaken for new measures, and are identical across both PBIR editions.

### Desktop visual acceptance still needed

The 1280×720 source layout ends its analytical charts at **y=671**, leaving the required 8px footer clearance. Static tests establish that the six chart rectangles do not overlap and the two original slicers do not obscure data visuals, but **cannot** establish that the 243px-wide treemaps actually display ten labels legibly. At 100% zoom, inspect:

1. Main G+A/90 bar: player names, units and ranking readability at 510px width.
2. Both 243px treemaps: actual label clipping; if cramped, use a native sorted compact bar view or an appropriate details-on-hover design **after** a screenshot-based review, not a blind chart-type swap.
3. Pivot table: horizontal scroll behavior, market value column and long player names at 496px width.
4. KPI cards: 26pt primary value, narrow support card headings, no overflow on outlier or empty values.
5. Position & club slicers, sidebar Home/navigation, cross-highlighting and tooltip minutes; validate actual filter context.
6. Logo signature and source provenance: original wordmark remains visible; only synthetic edition shows synthetic-data disclosure.

**Completion criteria:** after local source tests and actual Desktop screenshot QA pass, select the pilot as a reusable page-layout standard for Segmentation and Club & League; do **not** copy its specific chart composition verbatim to unrelated pages. Follow [professional redesign execution plan](POWER_BI_PROFESSIONAL_REDESIGN_EXECUTION_PLAN.md).

## Source QA evidence

- `python -m unittest discover -s tests -p 'test_powerbi_*.py' -q`: **89/89 PASS**, including rewritten source contracts for weighted KPI hierarchy, native graph bindings, chart/footer geometry and both-edition parity.
- `python scripts/check_offline_ci.py`: **PASS**, 11 YAML / 51 SQL-Jinja source files; no BigQuery read.
- `python scripts/check_powerbi_release_handoff.py --output ...`: **6/6 source checks PASS**, `visual_layout` zero warnings; `source_checks=PASS`, `portfolio_release=HOLD`.
- Final Git diff audit must confirm original bound `query` and navigation sections are unchanged; no hosted CircleCI was triggered.

*Local PBIR source success is necessary but is not final design acceptance or a production Desktop data-refresh sign-off.*
