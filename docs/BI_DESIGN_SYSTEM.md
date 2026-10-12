# NEXUS Power BI design system

The visual target is the NEXUS portfolio artwork in `nexus-web-v2/public/project-previews/football-player-performance-analysis-artwork.svg`. This is a **design reference, not a report screenshot**.

| Role | Color |
|---|---|
| Shell / deep navy | `#071829` |
| Hero / panel navy | `#091E33` |
| Slate typography | `#122942` |
| Canvas / visual surface | `#EAF1FA` / `#FFFFFF` |
| Primary data blue | `#4EA8FF` |
| Secondary lavender | `#8F9BFF` |
| Positive emphasis (blue, not green) | `#487FD8` |
| Warning / risk | `#F6B95F` / `#F27E90` |

No fluorescent green or green/teal should be used in the palette. Keep the semantic meaning of data and preserve existing KPI and DAX logic. The report still connects to Google BigQuery; recoloring does not supply data. Publish no screenshots until a real local rendered report is inspected.

The Power BI report includes native graphics that may have their own explicit fill/font formatting; change those per-visual settings separately and check dark/light contrast in Power BI Desktop.

## Versioned, report-wide implementation

The current source theme is `Report/StaticResources/RegisteredResources/NEXUSMidnight-20261012-v2.json`, registered in `Report/definition/report.json` in **both** the workspace and offline-demo reports. It defines standard visual-title typography, white content panels and subtle blue borders for 13 native visual types. It is a fallback: explicit `visual.json` formatting can take precedence, so further hardcoded color sweeps and Desktop contrast checks remain required.

The 11 full-size pages use 1280 × 720 layouts. The two report-page tooltips are registered as hidden 560 × 320 `ActualSize` pages because their existing charts are laid out across that width. Tooltip pages are not normal report navigation destinations. All meaningful demo screenshots must include an explicit synthetic-data indicator.

At least 36 primary chart/KPI objects per report edition now have descriptive `visual.visualContainerObjects.general[].properties.altText`, including both tooltips. Static alt text describes metrics and filters rather than invented current statistics; it cannot substitute for a rendered screen-reader/keyboard test.

For page-level delivery progress, check [the all-dashboard development plan](POWER_BI_ALL_DASHBOARDS_PLAN.md), then [the render/refresh acceptance gate](POWER_BI_VISUAL_QA.md). A source-level theme commit is **not** evidence of a visually passed Power BI Desktop report.
