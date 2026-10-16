# Power BI runtime repair — native quality status and visual legibility

Date: 17 October 2026. Production source: `powerbi/workspace/FootballPlayerAnalysis`.

## Root cause and evidence

Actual owner-provided Power BI Desktop screenshots showed three field-error visuals on **Player Market Value Prediction**: **Prediction Quality** slicer, **Quality Distribution** donut and **Player Valuation Estimates** table. The corresponding drillthrough detail visuals also used a calculated TMDL field `Quality Label EN`. Source-level mapping had left an avoidable runtime dependency on this computed column.

A read-only, authenticated BigQuery query against `data-analiz-490513.football_ml.ml_player_market_value_current_predictions` confirmed the already available real English source column `prediction_quality_status` and its complete observed value mapping:

| Warehouse status | Turkish historical label | Actual rows |
|---|---|---:|
| high | Yüksek | 4,393 |
| limited | Sınırlı | 2,124 |
| medium | Orta | 1,324 |
| **Total** | | **7,841** |

The report's slicer, donut, prediction records and detail visuals now bind directly to `prediction_quality_status` rather than the calculated translation field. The unnecessary calculated column was removed from both PBIR editions. **No BigQuery rows, models, forecast values or scoring outputs were changed.**

## Visual adjustments

- Removed all `#6FA56D` and `#C8F5C0` residual green colors from the report visuals, replacing them with NEXUS blue and a neutral cool secondary tone. This includes ML Model Reliability cards, slicers and subtitle.
- Enlarged high-level section-title and footer text containers, retracted section baselines from adjacent visual surfaces, and improved the Player Performance left-panel heading bounds.
- Expanded header title containers where safe inside their existing header bands. Reduced text size in the cramped Interpretation Protocol panel.
- Updated numeric format of `Scored Player Count` and related player-count measures to plain `#,0`; the narrow KPI no longer appends the long word `players` after its value.
- Preserved the 13-page report structure, native visual types, original registered NEXUS branding and actual data/model partitions; internal offline QA remains synthetic and never a source for portfolio screenshots.

## Limitations and final gates

Changes are implemented and validated **at source level** through Python tests and existing release checks. Source corrections target the specific screenshot failures but do not establish that Power BI Desktop has hot-reloaded and rendered the corrected edition; it generally needs to reopen the latest PBIP source and refresh the real model.

Small vertical white marks at text-container ends are consistent with the screenshot's apparent overflowing text containers, but their exact rendering origin has not been independently established. Text bounds were improved; **do not claim the bars are gone without fresh Desktop screenshot proof**. Similarly, the reopened report must verify that the three formerly failing prediction visuals and both drillthrough pages render real data.

**Portfolio release = HOLD** until the updated production PBIP is reopened, refreshed, and all 13 pages (9 full-size pages, two drillthroughs and two tooltip pages) are visually validated, including slicers, labels, hover detail, original official logo and runtime field error absence.
