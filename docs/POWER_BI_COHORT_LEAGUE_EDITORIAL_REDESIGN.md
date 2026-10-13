# Native editorial redesign — Player Segmentation and Club & League

**Date:** 13 October 2026
**Branch:** `design/segmentation-club-evidence-hierarchy-20261013`
**Sources:** both BigQuery production and clearly synthetic offline-demo PBIR editions.
**Acceptance:** source **PASS**, visual Desktop review **HOLD**, hosted CircleCI **not run**.

## Design distinction

The old two pages had similar four-panel report grids and no real evidence hierarchy. These source changes deliberately construct two different reading paths while preserving the original bound charts, source model and queries:

**Player Segmentation** (page `24c53960ddc19662d824`) is an observed **roster-cohort** analysis, not an ML clustering algorithm. It leads with player **position counts**, checks the **age mix**, then inspects **club goals** and the **EUR total market value by position**. This changes geometry and heading emphasis, not analytical meaning. Counting a position is not proof of unsupervised model assignment.

**Club & League** (page `25f58efd2bb140e62be9`) leads with **club win rate**; **club goal differential** supports the comparison. The second band separates **competition match counts** and **competition goals**, explicitly noting that these competition totals use a different observational grain from the club-rate evidence.

| Page | Native visual | Before (x / y / w / h) | New (x / y / w / h) | Priority |
| --- | --- | --- | --- | --- |
| Segmentation | Players by Position | 105 / 121 / 660 / 256 | **105 / 151 / 754 / 252** | Primary hero; 15pt title, 12pt labels |
| Segmentation | Age Group Distribution | 789 / 121 / 444 / 256 | 882 / 151 / 351 / 252 | Supporting cohort composition |
| Segmentation | Player Goals by Club | 105 / 403 / 458 / 268 | 105 / 452 / 532 / 219 | Supporting club-output comparison |
| Segmentation | Total Market Value by Position | 587 / 403 / 646 / 268 | 660 / 452 / 573 / 219 | Monetary evidence (EUR) |
| Club & League | Club Win Rate | 105 / 121 / 490 / 256 | **105 / 151 / 721 / 252** | Primary ranked outcome, 15pt title |
| Club & League | Goal Difference by Club | 619 / 121 / 614 / 256 | 849 / 151 / 384 / 252 | Supporting goal differential |
| Club & League | Matches by Competition | 105 / 403 / 640 / 268 | 105 / 452 / 542 / 219 | Sample/competition volume, **not** a per-club denominator |
| Club & League | Goals by Competition | 769 / 403 / 464 / 268 | 670 / 452 / 563 / 219 | Competition-output evidence |

The supporting chart titles use **12pt**, with 10pt labels. All original query references, aggregated measures, native visual types, title semantics, data roles, navigation destinations, footer, logo and original data source partitions remain unchanged.

## New native editorial structure

Each page receives **six** additional non-data elements per edition: a quiet descriptive strap (y=82), two numbered section headings (y=117 and 417), a secondary-grain caution label, and two 97px cyan chapter rules (y=145 and 445). All elements are editable native PBIR text/shape objects with no field binding. The primary analysis charts start at y=151; bottom evidence charts end at **y=671**, leaving eight pixels clear of the footer at y=679.

The mandatory offline synthetic-data disclosure remains on the original demo pages and stays separate from the new descriptive strap; the live-BigQuery edition has no synthetic disclosure.

## Genuine execution evidence, not a Desktop render

- **93/93** `test_powerbi_*.py` local Python tests passed, including four new `test_powerbi_cohort_league_editorial.py` tests.
- `python scripts/check_offline_ci.py` **PASS**: 11 YAML + 51 SQL/Jinja offline syntax sources checked without executing warehouse jobs.
- `python scripts/check_powerbi_release_handoff.py` **6/6 source gates PASS**; `visual_layout` **0 warnings**; `portfolio_release=HOLD`.
- `git` replay compared the **16 modified original data charts** with prior `main`: native chart types, complete query objects and navigation links unchanged; **24 new shape/text files** are non-data visuals, identical in the two editions.
- Existing `test_powerbi_chart_design.py` expectations were updated for these deliberate new native chart bounds, 15pt primary titles and subordinate font sizes.

## Desktop visual QA still required

1. At 100% zoom, capture both pages directly from the new PBIP and inspect whether the narrower age/goal-difference panels display all category labels legibly.
2. Compare actual player/club name lengths and axis tick formats; inspect club Win Rate as **0–100%** after the existing production `/100` model import conversion.
3. Validate that the large ranked bar shows useful Top-N without a horizontal scrollbar or ambiguous order. Filter states, blank categories, hover and left-navigation must be exercised in Desktop.
4. Check that competition match counts are **not misrepresented** as the denominator of the displayed club-rate calculation.
5. Verify the registered NEXUS logo renders cleanly, new editorial labels do not collide with the synthetic-source notice, and the content clears the footer.
6. Obtain actual before/after screenshots and user review before accepting the visual language or repeating it on the other report pages.

**Scope limitation:** These two pages now have different source geometry and hierarchies, but this does **not** certify an elite final visual result. Power BI Desktop, BigQuery refresh, production period/source freshness, screenshots and all remaining pages still require separate acceptance. CircleCI remains opt-in and final-stage only.
