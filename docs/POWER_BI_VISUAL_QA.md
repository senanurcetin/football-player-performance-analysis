# Power BI Desktop visual QA — current acceptance checklist

**As of 17 October 2026.** The [historical visual QA log](archive/powerbi/POWER_BI_VISUAL_QA_HISTORY_20261017.md) preserves the chronological implementation details. For release state, see [Project status](PROJECT_STATUS.md).

## 18 October 2026 static screenshot and KPI acceptance

**KONTROL EDİLDİ — recorded images and comparable historical measures only.** Independently read the 17 October Power BI production screenshot artifacts and recomputed SHA-256 on all 13 committed images: **13/13 exact manifest matches**, all **2177 × 1229**. Matched player count 47,702, transfers 40,208, fee coverage 64.2%, scoring records 7,841 and decision-ready percentage 72.9% to independently documented historical figures. Full method and unmatched dimensions: [18 October screenshot/value audit](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md).

**DOĞRULANMADI:** Observed transfer label card **8,581** does not equal the old `fct_transfer_success_labels` documented row count **8,584** (3-row difference). These may be different filters/grains; do not assert a real data change or resolve the difference by inventing rows. The drillthrough captures visibly contain three error/placeholder tiles per page and no selected-player context. Nothing in the screenshot audit certifies fresh BigQuery data or current live Power BI interaction.

## What is verified

- Actual Windows Power BI Desktop opened the [production-connected PBIP](../powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip) and displayed imported KPI/chart data on nine presentation pages.
- All 13 report screens were captured on 17 October, including 2 hidden drillthrough pages and 2 tooltips; their **13/13 SHA-256 hashes were independently checked on 18 October**. See [real screenshot gallery](assets/screenshots/README.md), [hash manifest](assets/screenshots/capture_manifest.json) and [value comparison](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md).
- Static PBIR binding/geometry audits and 158 Python tests passed during the documentation audit. Source tests are **not** live warehouse tests.
- **Not verified:** new BigQuery production refresh and KPI reconciliation; owner signoff; selected-player drillthrough tests. Some unselected-player detail visuals contain placeholders/errors.

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
