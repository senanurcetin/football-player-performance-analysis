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

## Page-specific editorial art direction (2026-10-13)

**One report; no duplicate slide presentations.** All native Power BI page, DAX, query and navigation bindings remain editable in the two intentional editions (BigQuery production workspace and deterministic offline-demo).

| Page | Canvas | Art direction |
| --- | --- | --- |
| Home / Closing | `#071829` | Dark editorial opening and closing |
| Player Performance | `#091E33` | Deep-blue tactical operations dashboard |
| Player Segmentation | `#EDEBFA` | Lavender audience/cohort analysis; 60/40 then 40/60 chart balance |
| Club & League | `#E7F2FD` | Ice-blue club benchmarking; 45/55 then 60/40 chart balance |
| Transfer Success 365d | `#E9F1FA` | Neutral blue-white evidence pages |
| Transfer & Market Value | `#E8ECF8` | Cool slate-blue financial analysis |
| Player Market Value Prediction | `#E7EFFB` | Light blue forecast/valuation surface |
| ML Model Reliability | `#E6EDF9` | Pale technical blue and high data contrast |
| Transfer Detail / Prediction Detail | `#EBEFF9` / `#E8EBF6` | Muted contextual drillthroughs |
| Transfer Tooltip / Prediction Tooltip | `#E7F0FC` / `#E8ECFA` | Legible 560×320 hover explanations |

These colors belong to the NEXUS navy, blue and lavender family. Chart components remain white with dark navy labels and blue/lavender data marks. Page changes are performed in **real PBIR JSON**, not images or rendered marketing slides. Final contrast/overflow must still be checked in Power BI Desktop.

## One current presentation, no redundant asset mirrors (13 October 2026)

- The current presentation is the **single editable PBIR report**, with two intentional source variants: `workspace` (BigQuery) and `offline-demo` (deterministic synthetic fixtures). Neither variant is a legacy slide deck.
- Home and Closing use a consistent navy editorial treatment, with distinct headlines (`THE GAME, IN DATA.` / `EVIDENCE DRIVES DECISIONS.`). Home navigation is typographic rather than decorative emoji buttons; all Power BI page-navigation references remain intact.
- The intervening 11 primary/detail/tooltip pages use **different NEXUS-coordinated canvases and asymmetric chart layouts** documented above; the report is not a sequence of identically laid-out graphics.
- Seven duplicate PNG resources in each variant's *project-root* `StaticResources/RegisteredResources` folder were byte-identical to their correctly registered copies under `Report/StaticResources/RegisteredResources`. The **14 redundant mirrors (18,263,794 bytes in tracked file sizes)** have been deleted; the seven assets still referenced in the registered PBIR resource package are retained in both variants.
- Historical green Power BI galleries and superseded editorial cover illustrations remain excluded from this repository. **Do not add separate PDF/PPTX exports or replacement mockup PNGs** solely to represent this source report.

These statements are based on Git trees, SHA equivalence and PBIR JSON inspection. **Engine-level validation remains required** before claiming the report can be opened and refreshed in Power BI Desktop, before deleting further registered assets, or before publishing current screenshots.

## Versioned, report-wide implementation

The current source theme is `Report/StaticResources/RegisteredResources/NEXUSMidnight-20261012-v2.json`, registered in `Report/definition/report.json` in **both** the workspace and offline-demo reports. It defines standard visual-title typography, white content panels and subtle blue borders for 13 native visual types. It is a fallback: explicit `visual.json` formatting can take precedence, so further hardcoded color sweeps and Desktop contrast checks remain required.

The 11 full-size pages use 1280 × 720 layouts. The two report-page tooltips are registered as hidden 560 × 320 `ActualSize` pages because their existing charts are laid out across that width. Tooltip pages are not normal report navigation destinations. All meaningful demo screenshots must include an explicit synthetic-data indicator.

At least 36 primary chart/KPI objects per report edition now have descriptive `visual.visualContainerObjects.general[].properties.altText`, including both tooltips. Static alt text describes metrics and filters rather than invented current statistics; it cannot substitute for a rendered screen-reader/keyboard test.

For page-level delivery progress, check [the all-dashboard development plan](POWER_BI_ALL_DASHBOARDS_PLAN.md), then [the render/refresh acceptance gate](POWER_BI_VISUAL_QA.md). A source-level theme commit is **not** evidence of a visually passed Power BI Desktop report.
