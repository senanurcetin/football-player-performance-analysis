# NEXUS Football Intelligence — Portfolio Production Release Profile

> **Archived historical record — 17 October 2026.** This document preserves prior engineering decisions and evidence; it is not the current delivery status. For current verified vs. pending checks, see [Project status](../../PROJECT_STATUS.md) and the [documentation index](../../README.md).


## The actual portfolio artifact

**Open only:** `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`

**Output:** a professional, **English-language**, fully editable Power BI Desktop report connected to **real** BigQuery tables. No premium Power BI subscription is needed to build and inspect this local PBIP; online sharing and refresh features depend on the chosen license and service.

**Source of facts:** the existing production import partitions use `GoogleBigQuery.Database([UseStorageApi=false])` against project `data-analiz-490513`, dataset `football_mart`. They remain unchanged by this identity update. Source binding is not proof of a successful data refresh; during final, user-approved Desktop inspection confirm refreshed values and errors explicitly.

**Do not publish the internal development fixture:** `powerbi/offline-demo` contains clearly identified synthetic rows for engineering QA. It is not a source of portfolio screenshots or reported performance. Its disclosures are kept truthful and are separate from the production page surfaces.

## Official identity (new Drive assets)

Approved brand: **NEXUS 2.0**, Google Drive `Logo/NEXUS_Identity_2_0`. Primary wordmark: `NEXUS_Official_Transparent_Logo.png`, transparent RGBA **1200 × 360**, **25,171 bytes**, Git blob `6faaa1ec7fd4a849c3cffe3fa424f3aba9fe9ab6`. The asset is registered in the PBIR resource manifest, not linked to a temporary Drive URL. Existing original resources are preserved for traceability.

Palette: ink `#0B0F19`, navy `#061524`, cyan `#00E0FF`, electric blue `#4EA8FF`, lavender `#8F9BFF`, violet `#6E55C6`, neutral silver `#B9C5CE`. Accent usage is selective: blue for primary data, lavender for comparisons, violet for modeled estimates, muted neutral for context, and warning hues only for material problems.

Brand placements are aligned with the existing report masthead/identity plate: Home and Closing **194×58**, seven analytical pages **156×47**, and two detail pages **138×41**. They use the original ~3.33:1 wordmark ratio rather than the old square image frame. Text remains readable and separated from native Back/navigation buttons. The registered resource and positions are identical in both PBIR editions.

## Analytical design rules

1. Each page must answer a distinct decision question. A ranked hero visual should carry the main metric; supporting visualizations explain distributions, coverage, or uncertainty. Avoid equally weighted default cards.
2. Transfer success is an **observed 365-day outcome**, not a prediction. Fee/valuation comparisons must show known-fee coverage and credible EUR units.
3. Model valuations must show previous versus predicted estimates and evidence of uncertainty, not claims of guaranteed profit. Model reliability should lead with test-set/baseline evidence rather than decorative KPIs.
4. Use **native** Power BI visuals and realistic Desktop layouts; never require premium-only features to make the report legible. Custom visualization dependencies must be checked before final publishing.
5. Every visible title, explanatory annotation, axis unit and navigation label in production should be in English. Existing Turkish *internal table/column names* do not necessarily appear as visual copy and must not be blindly renamed if doing so would break DAX.
6. No fabricated values, stock data substituting for missing BigQuery rows, synthetic screenshots, or hidden source limitations.

## Preflight and last-mile acceptance

Run the static tests and existing PBIR source/layout audits in the source repository. The new `tests/test_powerbi_portfolio_production_contract.py` confirms approved asset bytes/registry/theme, absent development banners on production text surfaces, and native production BigQuery import contract.

**Only during the final user-approved PC session**, open the current production PBIP, authenticate BigQuery and refresh. Check table error counts, 13-page real rendering (nine visible, two drillthrough, two tooltips), actual slicer navigation, visual and logo clipping, screenshot contrast, sample-size limits, data recency and KPI reconciliation. Then update the portfolio README with genuine report screenshots.

The latest previously recorded warehouse table modification dates were in June 2026: verify **event-data coverage and refresh recency** before describing any metrics as current-season/live. A clearly dated historical analysis remains useful for a professional portfolio.

**CircleCI is a final release gate** only. The opt-in parameter `run_final_ci` stays false while visual/warehouse/desktop work is unresolved. Release status: **HOLD** until real desktop acceptance.
