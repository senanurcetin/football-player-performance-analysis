# Football Power BI screenshot gallery — evidence status

Six historical report captures are tracked in this directory. They are **not** a complete capture of the current 11-page PBIR source (9 standard pages and 2 drill-through pages), nor proof that the latest Power BI Desktop report opens, refreshes, renders, or evaluates DAX correctly. The offline-demo PBIP contains **synthetic** data; do not present screenshots of it as production football metrics.

| Existing file | Historical report page |
| --- | --- |
| [01_player_performance.png](01_player_performance.png) | Player Performance Analysis |
| [02_player_segmentation.png](02_player_segmentation.png) | Player Segmentation |
| [03_club_league_analysis.png](03_club_league_analysis.png) | Club & League Analysis |
| [04_transfer_success_prediction.png](04_transfer_success_prediction.png) | Transfer Success Prediction |
| [05_transfer_market_value.png](05_transfer_market_value.png) | Transfer & Market Value Analysis |
| [06_market_value_prediction.png](06_market_value_prediction.png) | Player Market Value Prediction (ML) |

These files are linked from the [root README gallery](../../../README.md#dashboard-preview). Values and descriptions there refer to historical snapshots, not freshly reconciled warehouse results.

## Requirements before replacing any image

1. Follow [the visual QA and release gate](../../POWER_BI_VISUAL_QA.md) for the editable PBIR paths and local audit command.
2. Open and refresh the **offline-demo** PBIP in Power BI Desktop. Check each of the 11 pages, navigation, drill-through behavior, DAX, field references, labels, contrast, and the visible `SYNTHETIC DEMO / NOT REAL DATA` marking.
3. Capture **real Desktop-rendered** images at a documented report commit and theme revision. Record whether the source was the offline synthetic demo or the separately authenticated BigQuery production report.
4. Validate any production numerical claims against governed warehouse SQL before treating them as current. Synthetic fixtures are never a substitute for that reconciliation.
5. Keep the prior capture as a historical artifact until a verified replacement is reviewed; do not fabricate a screen or label conceptual artwork as a report capture.

**Release status as of 12 October 2026:** HOLD — Desktop open/refresh and current visual review have not been confirmed. This gallery inventory does not itself perform those checks.
