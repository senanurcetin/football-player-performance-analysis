# All-dashboard Power BI modernization plan

**Project:** `senanurcetin/football-player-performance-analysis`  
**Report editions:** `powerbi/workspace/FootballPlayerAnalysis/` (BigQuery) and `powerbi/offline-demo/FootballPlayerAnalysis/` (synthetic fixtures)  
**Source of truth:** `Report/definition/` (PBIR), not legacy `Report/sections/` or historical screenshot PNGs.

## Deliverable standard

Every page must be structurally valid, obey NEXUS navy/blue identity, have meaningful chart bindings and readable labels, allow safe navigation, and carry honest data provenance. Never treat static JSON inspection as a Power BI Desktop test. Synthetic outputs must not be presented as real football or model-quality results.

### Page-by-page inventory and remaining acceptance

| PBIR page | Current source work | Power BI Desktop acceptance remaining |
|---|---|---|
| Home | Global NEXUS theme, page order and link-contract checks | Navigation, contrast and keyboard focus |
| Player Performance Analysis | Theme, four primary data visual descriptions, weighted/per-90 legacy corrections | Render, rank direction, drill/filter interactions |
| Player Segmentation | Theme, four query-bound plots and accessibility descriptions | Meaningful nonblank group results; check market-value aggregation |
| Club & League Analysis | Theme, four plot descriptions | Win-rate units, negative goal differences, league filters |
| Transfer Success Analysis (365d) | Theme, four charts plus four cohort/coverage/reliability cards, alt text | Production 365-day outcomes, denominator/coverage and absence of fabricated prediction claims |
| Transfer & Market Value Analysis | Theme and four visual descriptions | Known-fee coverage, percent units, seasonal trends |
| Player Market Value Prediction | Theme and four visual descriptions | Prediction quality, uncertainty bands, non-realized growth caveat |
| ML Model Reliability | Theme and four visual descriptions | Quality-gate logic, missing backtest data and feature importance |
| Closing | Theme, 16:9 canvas registry | Readability and focus ordering |
| Player Transfer Detail (hidden) | Theme and hidden drillthrough registry | Drillthrough entry points, required field context |
| Player Prediction Detail (hidden) | Theme and hidden drillthrough registry | Drillthrough, attribution and quality badges |
| Tooltip Transfer (hidden) | Explicit 560×320 Tooltip page binding, 2 visual descriptions | Hover trigger compatibility and values within small canvas |
| Tooltip Prediction (hidden) | Explicit 560×320 Tooltip page binding, 2 visual descriptions | Hover context and non-interactive tooltip legibility |

All 13 pages receive the registered `NEXUSMidnight-20261012-v2.json` custom report theme. It sets global fallback styling for **13 visual types** without overriding the explicit semantics or individual chart axes. A versioned RegisteredResources reference avoids Desktop caching an old `AccessibleTidal` resource.

## Execution stages

### Stage A — PBIR source work (changes prepared)

- [x] Audit page counts, page order, theme registration, page type and source model distinctions
- [x] Register consistent NEXUS Midnight theme in both report editions
- [x] Repair both tooltip pages per edition: `pageBinding.type=Tooltip`, hidden tab, `ActualSize`, 560×320
- [x] Add metric-specific alternative text for 36 chart/KPI objects in both editions (72 files)
- [x] Add automated whole-report page/theme/tooltip/accessibility regression tests
- [ ] Verify remaining hardcoded theme overrides across **all** pre-existing visual objects (not automatically overruled by theme)
- [x] Remove legacy green surface literals from the four identified ML prediction slicer/KPI/chart visuals in both report editions; add a regression test for these objects
- [x] Replace legacy green/gray hardcoded accents in 16 principal analytics visuals per edition (Player Performance, Transfer & Market Value, Market Value Prediction, ML Model Reliability); preserve their query roles
- [ ] Run all preflight scripts and Python unit tests on a full working copy

### Stage A.2 — Single editorial report and repository diet

- [x] Give each of the 13 editable PBIR pages its own coordinated NEXUS canvas
- [x] Introduce different asymmetric chart compositions on Player Segmentation and Club & League pages; preserve original Category/Y query roles
- [x] Keep Home / Closing dark and maintain demo-versus-production naming distinction
- [x] Remove decorative emoji page-name prefixes; move ML reliability before Closing in visible storytelling order
- [x] Give 365-day Transfer Success its own 63/37 and 67/33 data-chart hierarchy
- [x] Remove the six outdated green Power BI screenshot PNGs, their archive index and the superseded SVG cover
- [x] Keep production workspace and deterministic offline-demo because they serve different data sources, **not** two exported PowerPoint presentations
- [x] Add static regression checks for palette, native chart geometry and workspace/demo role parity
- [ ] Confirm all native visual overlaps and browser/Power BI Desktop rendering; no engine-level validation was run here
- [ ] Audit PBIR RegisteredResources binary image references before considering any further asset removal

### Stage B — Engine-level verification (blocked)

- [ ] Open the offline PBIP in a supported Power BI Desktop
- [ ] Refresh all 33 inline demo model partitions; verify zero unexpected BigQuery prompts
- [ ] Inspect all 11 full-size pages, plus 2 tooltip pages, against their bindings
- [ ] Test Home/sidebar navigation, keyboard tab order, slicers, drillthrough, custom visuals and report-page tooltips
- [ ] Check 365-day outcome counts, value-growth unit conversion and follow-up coverage in Power BI itself
- [ ] Recheck production against authenticated BigQuery marts and SQL governance
- [ ] Run dark/light contrast and overflow checks on screenshots at 100% zoom

### Stage C — Portfolio evidence (blocked until Stage B)

- [ ] Capture **actual** Power BI Desktop screenshots, record report commit and data source
- [ ] Keep visible SYNTHETIC DEMO marking on every demo capture
- [ ] Replace legacy green screenshots **only after** validated real captures exist
- [ ] Reconcile every numeric README/dashboard caption to the matching production or clearly synthetic run
- [ ] Remove 'HOLD' release status only after a documented rendered/warehouse pass

## Offline checks

From repository root in a local checkout (no GitHub Actions minutes needed):

```bash
python scripts/check_powerbi_project.py
python scripts/check_powerbi_offline_demo.py
python scripts/audit_powerbi_visuals.py
python -m unittest discover -s tests -p 'test_powerbi_*.py'
```

The new `tests/test_powerbi_all_dashboard_quality.py` checks **both** model editions for the same 13 pages, start page, canvas and tooltip dimensions, theme registration, required visual styles, six Home navigation links, and accessible alternative text on the 36 specified data visuals. CI config has not been changed as part of this design pass.

**Scope limitation:** The user-authorized Desktop Commander machine was last observed offline. No Power BI Desktop screenshots, DAX execution or BigQuery refresh have been observed during this stage. Design improvements are source-level until verified in Power BI.
