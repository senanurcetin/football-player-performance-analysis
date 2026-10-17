# NEXUS Football — professional reporting without a paid Power BI seat

> **Archived historical record — 17 October 2026.** This document preserves prior engineering decisions and evidence; it is not the current delivery status. For current verified vs. pending checks, see [Project status](../../PROJECT_STATUS.md) and the [documentation index](../../README.md).


**Status:** Source-only preflight; final Power BI Desktop refresh and screenshots pending.  
**Public-facing, real-data PBIP:** `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`  
**Internal QA-only fixture:** `powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`

## Licensing and authoring boundary

Power BI Desktop can author and inspect a local editable PBIP without Power BI Pro/PPU. Its professional appearance depends on report design and data modeling rather than purchasing a per-user Power BI license. See [Microsoft's free-user feature guide](https://learn.microsoft.com/en-us/power-bi/fundamentals/end-user-features).

**Do not promise a publicly shared live Power BI Service dashboard or an embeddable public Power BI link on a free-only plan.** Microsoft's free tier does not provide unrestricted collaboration or the ability to create a public "Publish to web" embed code. A portfolio may show *genuine screenshots captured from the authenticated production report* after acceptance and can link to its source repository and documentation. Public interactive hosting would require a separately evaluated authorized deployment and data-access plan.

## Native-first, zero-third-party visual policy

The report's 13 editable PBIR pages currently use built-in Power BI report elements: cards, standard charts, tables, matrix, slicers, first-party button slicer (`advancedSlicerVisual`), text, navigation and original registered NEXUS images. Four legacy custom-visual registrations (lollipop, lollipop-column, radar and risk heatmap) were unused anywhere in either report's actual visual definitions; their stale manifest entries were removed **without changing any bound visual**.

The new `tests/test_powerbi_free_desktop_visuals.py` checks that neither report edition registers unused public custom visuals and that all current `visualType` values are first-party types. This does *not* prove all installed Desktop versions render all first-party types correctly; test the button slicer and other UI interactions in a current Desktop build.

## Complete native data-visual accessibility coverage

A source-level audit across **89 query-bound visuals per edition** (178 visual JSON objects total) found **52 missing accessible descriptions in each PBIR edition**. A deterministic generator now adds source-grounded `altText` to those **104** native report visuals, using existing field projections, titles, and visual types. It preserves all custom editorial descriptions and never modifies native query states, report coordinates, chart types or data partitions. The post-change validator reports **0 remaining missing descriptions** in both editions.

A semantic comparison of the committed diff verified that **all 104 source edits contain only the added accessibility properties**, with no other JSON-semantic changes. Production and fixture descriptions now match for all 89 shared query-bound visuals; one legacy Turkish fixture description was normalized to the existing English production label. New tests guard presence, length, deterministic idempotence, privacy and source parity. Actual assistive-technology behavior and focus order still require Power BI Desktop inspection.

```powershell
python scripts/backfill_powerbi_accessibility.py --compact
python -m unittest discover -s tests -p "test_powerbi_*.py" -q
```

## Final visual acceptance: 13-page review

| Surface | Inspect in Power BI Desktop |
| --- | --- |
| Home | Original transparent NEXUS wordmark; the real BigQuery-derived QUALITY AUDIT label; seven navigation targets |
| Player Performance | Per-90 calculations, filters, sorted players, names and 100% zoom labels |
| Player Segmentation | Position populations, age cohorts and value labels; no false machine-learning segmentation claim |
| Club & League | Win-rate scale, club/competition grain separation and goal differences |
| Transfer Success (365d) | Observed coverage and 20-percentage-point threshold; unknown follow-up is not failure |
| Transfer & Market Value | Known-fee coverage, premium/discount signs, currency EUR and source evidence |
| Player Valuation | ML output, prediction interval and coverage; avoid an investment guarantee |
| ML Reliability | Baseline against holdout, evaluation date, drift/gates and quality sample sizes |
| Closing | Navigation, logo alignment, report limitations and return-home |
| Transfer Detail (hidden) | Drillthrough selection context and accurate amounts |
| Prediction Detail (hidden) | Player context, uncertainty statement and back navigation |
| Transfer Tooltip (hidden) | 560×320 hover region, no clipped navy panel/axis or missing dataset values |
| Prediction Tooltip (hidden) | 560×320 hover region, labeled modeled upside rather than realized return |

Capture *real* Power BI Desktop screenshots at 100% only after a successful authenticated BigQuery import refresh, representative KPI reconciliation, checked font loading and visual overlap review. Store the screenshot evidence with the commit SHA and source event coverage information. Do not publish the synthetic fixture or any illustrative replica as though it were real analytical output.

## Final gate commands (local, no hosted CI)

```powershell
python -m unittest discover -s tests -p "test_powerbi_*.py" -q
python scripts/check_powerbi_release_handoff.py --output powerbi-handoff.json
```

Source PASS is necessary but insufficient. Keep `portfolio_release=HOLD` until Desktop, production warehouse reconciliation and screenshot acceptance are complete.
