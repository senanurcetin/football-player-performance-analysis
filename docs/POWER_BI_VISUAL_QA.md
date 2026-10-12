# Power BI visual QA and release gate (12 October 2026)

## Scope and authoritative source

Both `powerbi/offline-demo/FootballPlayerAnalysis/` and `powerbi/workspace/FootballPlayerAnalysis/` are PBIP/PBIR sources. The **production** report queries BigQuery. The **offline demo** uses deterministic synthetic import fixtures. Do not confuse synthetic data with real football metrics.

The old `Report/sections/` directory is legacy metadata; the editable PBIR source for this review is `Report/definition/pages/*/visuals/*/visual.json`. Microsoft PBIR uses one `page.json` per page and one `visual.json` per visual. The old screenshot gallery is not proof of a successful current Desktop render.

## Source changes in this branch

| Page / control | Source issue | Applied change |
|---|---|---|
| Player Segmentation | 11 objects, no data visuals | Players by position; age-group distribution; goals by club; market value by position; page title |
| Club & League Analysis | 11 objects, no data visuals | Club win rate; goal difference; competition matches; goals by competition; page title |
| Transfer Success Prediction | no data visuals | Transfers by position; average fee; 0/1 success-rate chart; outcome status; page title |
| Startup navigation | Transfer & Market Value selected by default | Home as active page |
| Player Performance treemap | CountNonNull on assists/90 while labeling a rate | Average of assists/90 for treemap sizing |
| Player Performance accent | teal present on selected visuals | Replaced known teal with NEXUS blue |
| Synthetic transfer fixtures | same from/to club, impossible 1-24 success flags, same-day outcome | Rotated club destinations, recalculated synthetic fee/baseline ratios, ages and 90-day outcomes, binary success flags |

Changes to fixtures are *illustrative*, not validated football research. The new visible report charts have PBIR queryState bindings to existing tables/columns and stay inside 1280×720 page boundaries. The production BigQuery model partitions were not changed.

## Repeatable source-level check (no CI quota)

From repository root, with Python 3.10+:

```powershell
python scripts/audit_powerbi_visuals.py
```

This inspects page ordering, page/visual names, missing data visuals, model field references, invalid root-level `visualContainerObjects`, layout overflow, visible demo watermarks, and a list of legacy teal colors. Exit code 1 means at least one structural error. A clean static check **does not** prove Power BI Desktop can render, refresh, or evaluate DAX successfully. Treat warnings as review items.

## Power BI Desktop acceptance checklist (not yet executed)

Use the **offline-demo** PBIP first, not the production PBIP.

1. Open `powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`; preserve *exact* error details if a parsing/model problem occurs.
2. Refresh the semantic model locally. Verify all 33 import tables and no unexpected BigQuery authentication requests.
3. Open each of the 11 full-size pages; review every KPI, chart, segment, axis scale, title and data label. The two tooltip pages must behave as tooltips, not standard tabs.
4. Verify new pages: four rendered data charts each (Segmentation, Club/League, Transfer Success); confirm positive/negative signs, rates bounded by 0–1 where applicable, and filters propagate through relationships as expected.
5. Check that the Home page opens first, page-navigation action buttons work, and the hidden drillthrough detail pages are reachable only by intended interactions.
6. Check the **SYNTHETIC DEMO / NOT REAL DATA** watermark remains visible on every full-size screenshot and the NEXUS navy/blue contrast is legible; exclude green/teal remnants.
7. Validate report-page tooltips, bookmarks, slicers and any custom visuals. A JSON query binding does not guarantee that a third-party custom visual package is installed.
8. Collect actual Desktop-rendered screenshots at 100% scale. Replace placeholder/gallery images only after the visual pass.

For **production**, separately authenticate BigQuery and reconcile at least the core `Total Goals`, `Total Assists`, `Total Minutes`, transfer counts, market value and model-quality measures to governed SQL/warehouse outputs. Do not extrapolate observed demo fixtures to production claims.

## Remaining release blockers

- A Power BI Desktop open/refresh pass is required. As of this review the authorized Desktop Commander machine is offline.
- The completeness, metric plausibility and time-series coherence of all 33 **synthetic** tables are not fully verified; this branch corrects the identified transfer counterexamples but is **not** a general data-quality certification.
- Actual screenshots and accessibility/contrast inspection require rendered visuals.
- Confirm custom visual compatibility and model/visual performance locally; no CI workflows were changed.

**Release decision: HOLD for Desktop verification.** Source changes can be reviewed or merged without representing the report as rendered or production-validated.
