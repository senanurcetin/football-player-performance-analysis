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
