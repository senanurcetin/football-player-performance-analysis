# NEXUS Football Intelligence — Midnight V3 Design Baseline

**Date:** 16 October 2026  
**Scope:** Native Power BI PBIP source, both the real BigQuery workspace and its separate internal QA fixture.  
**Status:** Source proposal / Power BI Desktop visual and BigQuery refresh acceptance **HOLD**.

## What changed

The report's previous registered theme still defaulted to **white** visualization surfaces and dark ink despite the 14 October 2026 dark analytical canvas redesign. That could make a newly created or unformatted native Power BI chart look like a pasted white rectangle. V3 instead makes the default surfaces navy and keeps accessible text hierarchy, without changing the individually authored native visual layouts.

- Registered theme: `NEXUSMidnight-20261016-v3.json` in both `Report/StaticResources/RegisteredResources/` folders.
- Report manifest: `Report/definition/report.json` now selects V3. The old V2 resource is kept for traceability.
- Canvas fallback: `#091E33`; chart fallback: `#10283F`; muted border: `#294761`.
- Primary labels: `#ECF4FF`; secondary labels: `#B9D1E8`.
- Approved NEXUS 2.0 series accents in order: `#4EA8FF`, `#8F9BFF`, `#00E0FF`, `#6E55C6`; remaining palette slots are unchanged.
- All 13 currently registered native theme visual categories use the same dark default chrome. Existing per-visual settings can override the theme and remain unchanged.
- Existing **NEXUS official transparent logo PNG** remains registered and referenced across the report; it is not replaced by a redesigned or generated wordmark.

## Real-data preservation

The production PBIP remains bound to `GoogleBigQuery.Database([UseStorageApi=false])`, project `data-analiz-490513`, marts `football_mart` and model evidence in `football_ml`. This change does **not** modify semantic TMDL, Power Query M, DAX, filters, slicers, drillthrough, chart queryState, visual geometry or actual metric values. A BigQuery *import model* refreshes when the Desktop report is refreshed; registration of BigQuery source is not itself evidence of a completed refresh.

The `offline-demo` directory remains a separate engineering fixture whose mandatory synthetic provenance must never be suppressed, used as a real-data presentation, or published in the portfolio. Production pages have no demo/sample labels.

## Test and final desktop review

Source check: `python -m unittest discover -s tests -p 'test_powerbi_*.py' -q`. New regression: `tests/test_powerbi_dark_theme_v3.py` checks production-fixture parity, manifest registration, approved palette and WCAG-like fallback ink-on-surface contrast. This is a **static** readability check, not a certificate for every chart's actual rendered state.

**Desktop acceptance is still required:** open only the production `.pbip` on the owner's PC after source work ends, authenticate to BigQuery, refresh every table, verify zero conversion errors (including club marts), inspect all 13 pages with both native charts and their text labels, and check pale tooltip pages for theme fallback contrast. Confirm source-data coverage dates independently of the warehouse modification timestamp; the BigQuery audit on 13 October found some marts last modified in June 2026.

Do not run final CircleCI acceptance or publish screenshots until the local Power BI Desktop inspection is explicitly complete. Do not claim that this source edit alone makes the report publication-ready.
