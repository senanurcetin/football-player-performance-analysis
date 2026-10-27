# Power BI Desktop visual QA — current acceptance checklist

**LATEST VISUAL REVIEW (27 OCTOBER):** The [new 13 genuine Desktop screenshots](assets/screenshots/README.md) and [execution/defect register](WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md) supersede the 17–18 October static-image status below. 13 pages, 308 visuals, 30 charts were inventoried; 32 PBIR/TMDL files were changed and source-backup/hash verification passed. **Visible P0/P1 issues remain:** Transfer Fee Premium M% axis, distorted €m tooltip labels, legend/table truncation and untested selected-player drillthrough. Do not present prior visual-QA closure as signoff for the refreshed Workintech report.


**Historical capture: 17 October 2026; reviewed 19 October.** The owner subsequently accepted Power BI as an existing workstream, and the full offline source suite plus PBIP static checks passed. That acceptance is **not** a new live BigQuery refresh, source parity or selected-player interaction test. The [historical visual QA log](archive/powerbi/POWER_BI_VISUAL_QA_HISTORY_20261017.md) preserves implementation details; see the [project status](PROJECT_STATUS.md).

## 18 October 2026 static screenshot and KPI acceptance

**KONTROL EDİLDİ — recorded images and comparable historical measures only.** Independently read the 17 October Power BI production screenshot artifacts and recomputed SHA-256 on all 13 committed images: **13/13 exact manifest matches**, all **2177 × 1229**. Matched player count 47,702, transfers 40,208, fee coverage 64.2%, scoring records 7,841 and decision-ready percentage 72.9% to independently documented historical figures. Full method and unmatched dimensions: [18 October screenshot/value audit](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md).

**SOURCE-LEVEL DEFINITION CHECKED, ROW-LEVEL OPEN:** The native DAX card showing **8,581** filters `fct_transfer_fixed_horizon_outcomes` using a **30-day-after-target maturity gate and as-of-source cutoff**. The separate dbt `fct_transfer_success_labels` table reported **8,584** historical records but has **no corresponding cutoff**; these are *not* identical measures. Exact three-row isolation remains unexecuted without authenticated BigQuery data. Do not assert a real data change or invent records. The drillthrough captures visibly contain three error/placeholder tiles per page and no selected-player context. Nothing in the screenshot audit certifies fresh BigQuery data or current live Power BI interaction.

## What is verified

- Actual Windows Power BI Desktop opened the [production-connected PBIP](../powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip) and displayed imported KPI/chart data on nine presentation pages.
- All 13 report screens were captured on 17 October, including 2 hidden drillthrough pages and 2 tooltips; their **13/13 SHA-256 hashes were independently checked on 18 October**. See [real screenshot gallery](assets/screenshots/README.md), [hash manifest](assets/screenshots/capture_manifest.json) and [value comparison](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md).
- Static PBIR binding/geometry audits and 158 Python tests passed during the documentation audit. Source tests are **not** live warehouse tests.
- **Owner accepted existing Power BI workstream. Still not technically verified:** a **new BigQuery refresh/KPI reconciliation** or selected-player drillthrough interactions. Some historical unselected-player screenshots show placeholders/errors; do not describe those captures as repaired.

## Page acceptance matrix

| Type | Coverage | Required result |
|---|---|---|
| Presentation (9) | Home; Player Performance; Player Segmentation; Club & League; Transfer Success (365d); Transfer & Market Value; Player Market Value Prediction; ML Model Reliability; Closing | Genuine images available; test slicers, labels, contrast, navigation, values and accessibility |
| Drillthrough (2) | Player Transfer Detail; Player Prediction Detail | Test selected-player and cleared contexts; repair error/placeholder visuals; recapture only after verification |
| Tooltip (2) | Transfer tooltip; Prediction tooltip | Confirm invocation context, filters, scale, no clipping or unsupported visual |

## Mandatory Desktop + warehouse checks

1. Open the **production** PBIP, record report Git SHA, Desktop build and data source. Do not substitute the synthetic `offline-demo` edition.
2. Refresh with authorized BigQuery credentials. Record table row counts, errors, actual last football event and audit timestamps. A screenshot capture date is not a data freshness date.
3. Reconcile player totals and rate measures; confirm club win-rate fraction is multiplied by 100 **once**.
4. Reconcile eligible/observed denominators and follow-up coverage for **365-day observed transfer success**. The positive label is **20 percentage points of market-value growth** and is **not** an ML probability.
5. Confirm the published ML valuations are real model records and explain quality-cohort routing and persistence-baseline comparison.
6. Inspect nine pages at Fit to Page and 100% zoom: native slicers, blank behavior, scrollbars, visual labels, text, chart contrast, keyboard access and navigation.
7. Select an actual player and validate both detail pages. Clear filters and confirm no broken-field visual errors; invoke both tooltip pages.
8. Preserve genuine captures and SHA-256 fingerprints; never publish synthetic sample values as if they were real player outcomes.
9. Obtain user signoff and complete any final authorized CI before changing the [release status](PROJECT_STATUS.md) from pending.

## Repeatable source checks

```bash
python scripts/check_powerbi_project.py
python scripts/check_powerbi_offline_demo.py
python scripts/audit_powerbi_visuals.py
python scripts/audit_powerbi_layout.py
python scripts/verify_dashboard_screenshots.py
python scripts/check_docs_integrity.py
python -m unittest discover -s tests
```

These are static checks of repository contents, **not** proof of successful Power BI Desktop interaction, BigQuery refresh or current model performance. See [Desktop handoff](POWER_BI_DESKTOP_HANDOFF.md), [CI-last policy](CI_RELEASE_GATE_POLICY.md), and [historical defects](archive/README.md).

**Release blockers:** unresolved player-detail visuals/selection flow, unverified fresh production data/KPI reconciliation, and absent final owner signoff.
