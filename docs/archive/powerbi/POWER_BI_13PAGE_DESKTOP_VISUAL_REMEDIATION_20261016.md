# NEXUS Football Intelligence — 13-page Desktop design remediation

> **Archived historical record — 17 October 2026.** This document preserves prior engineering decisions and evidence; it is not the current delivery status. For current verified vs. pending checks, see [Project status](../../PROJECT_STATUS.md) and the [documentation index](../../README.md).


**Evidence:** Eleven genuine user-supplied Power BI Desktop page screenshots from 16 October 2026, plus PBIR definitions for two hidden tooltips. **Release:** HOLD until fresh, actual Windows Power BI Desktop rendering of this commit.

## Verified defects in the supplied screenshots

The historical BigQuery Import now loads through ADBC v2 (previous PR #75); screenshots show genuine bound data. Outstanding visual defects were presentation and filter-scope issues, not simulated data.

| Page | Screenshot review | Applied PBIR improvement |
| --- | --- | --- |
| Home | Main editorial text and logo are readable; small decorative/renderer marks appear | Preserve genuine logo, copy and page geometry; section text parity checked |
| Player Performance Analysis | Ranking title low contrast; position tiles nearly white; player count abbreviated as `B` | Native chart title contrast, dark selector fill, explicit unit settings for count cards, clean body styling |
| Player Segmentation | Native chart axis/card count abbreviation `B` (Turkish bin) misleading in English report | Explicit no-auto-unit overrides for count labels and count axes; chart title ink normalized |
| Club & League Analysis | Count/goal chart abbreviations `B`; some labels crowd x-axis | Explicit no-auto-unit overrides on count-volume charts; preserve original dimensions and scrolling |
| Observed Transfer Outcomes / 365 Days | Caution KPI wraps/truncates; transfer status count abbreviation `B` | Compact caution KPI font and normalized count display units |
| Transfer & Market Value Analysis | Table pale rows/light font; donut labels truncate | Midnight data-table banding, stronger legend font, dark native KPI/filters retained |
| Player Market Value Prediction | Pale KPI/filter rail; pale player table with low-contrast text; Turkish quality categories | Dark rail/cards/filters, high-contrast table, calculated English quality labels, compact player count |
| ML Model Reliability | Pale panels; source tables illegible; one slicer label is Turkish | Dark KPIs/slicers/rail, dark-blue table row banding and white type, `Model Version` label |
| Closing | Intro and navigation largely intact; source text sometimes tightly bounded | Preserve hero and brand; check shared small-label typography |
| Player Transfer Detail | Logo invisible inside frame; table pale/illegible; unfiltered KPI falsely displays whole-market totals | Raise official image above opaque shape, dark table, **detail-only player-filtered measures** that return BLANK with no player selected |
| Player Prediction Detail | Same logo and table problems; value/interval KPI aggregates despite no selected player; Turkish legend | Correct official logo z-order, dark table, detail-only guarded measures and English legend |
| Transfer tooltip (hidden) | Not pictured | Source and bound native tooltip palette consistency validated |
| Prediction tooltip (hidden) | Not pictured | Source and bound native tooltip palette consistency validated |

### Accessible palette

Native table rows `#10283F` and `#193650` with light ink `#EFF7FF`; white `#FFFFFF` table column headers on `#122942`/`#173451` or `#10283F`. This fixes the actual white-on-pale washed-out screenshots while retaining the NEXUS navy/cyan identity. Fixed standard title and legend contrast, rail fill, native cards and slicers across both PBIR editions; preserved the authorized original transparent NEXUS logo unchanged.

### Genuine source values and derived labels

- `kalite_etiketi_tr` is preserved as the original BigQuery physical column; **Quality Label EN** is a *derived semantic-model label*, translating only known `Yüksek → High`, `Sınırlı → Limited`, `Orta → Medium` and retaining all unrecognized original labels as fallback. No warehouse rows or labels are fabricated.
- Dashboard counting charts explicitly request number **display units 1 (none)** instead of Power BI's locale-abbreviated thousands `B`. This is a presentation override, not a change to source totals.
- Six detail-only DAX measures guard on `HASONEVALUE([player_id])` and return `BLANK()` without exactly one filtered player. The previous general-market measures remain available in the wider report, with unchanged aggregation.
- The native transfer rail retains the existing warehouse-supported `market_value_direction_after_transfer` English categories.

### Automated checks

Run `python -m unittest discover -s tests -p 'test_powerbi_*.py' -q` and `python scripts/check_powerbi_release_handoff.py`. The new `test_powerbi_13page_visual_accessibility.py` validates all 13 pages in both PBIR editions, high-contrast native table rows, original logo z-order, selection-safe detail measures, and English quality labels. Offline demo is internal-only and never published as authentic real-player figures.

### Remaining manual Desktop acceptance gate

The supplied screenshots are from the **previous report build**, not evidence of how the newly modified PBIR files render. The authoring/source checks are not proof of a 13-page successful pixel-level render. Reopen the genuine **production** PBIP from the merged commit, refresh 31 BigQuery partitions through ADBC, inspect 9 visible + 2 drillthrough + 2 tooltip pages at Fit to Page, exercise slicers, verify labels/units/contrast/clear player context, confirm no `Missing_References` or editor-only white glyphs, and capture fresh genuine page screenshots. Keep `portfolio_release=HOLD` until then. If any unsupported native visual property was ignored, correct it using the actual Desktop result rather than claiming source tests proved the appearance.
