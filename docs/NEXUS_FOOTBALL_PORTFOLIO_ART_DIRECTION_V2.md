# NEXUS Football Intelligence — Portfolio Art Direction v2.0

**Status:** Native PBIR design implementation in progress; release HOLD.  
**Audience:** Recruiters, data science hiring managers, analysts and portfolio reviewers.  
**Language:** English throughout the published report.  
**Production data:** Google BigQuery, not screenshots, CSV stand-ins or manufactured dashboard metrics.  
**Application:** Power BI Desktop (free) and portable editable PBIP/PBIR source files.

## Brand source of truth

Approved NEXUS 2.0 identity was located in the user's connected Google Drive:

- [NEXUS Identity 2.0 source folder](https://drive.google.com/drive/folders/1rU3QCrdwCdHB0tYVLIq0W6aPqpj3iOsY).
- **Primary mark:** `NEXUS_Official_Transparent_Logo` (1200×360, transparent) for dark navigation/headers.
- **Compact mark:** `NEXUS_Official_X_Transparent` (512×512) for small isolated marks only when a wordmark cannot fit.
- **Alternative:** `NEXUS_Official_Midnight_Logo` for editorial cover use when a solid midnight field is intentional.
- **Do not use:** LinkedIn/YouTube/Patreon/Dev.to banners as dashboard chrome; their ratios and safe areas are intended for those sites, not Power BI.
- Read the original `README.md`: approved third Figma variant with cyan–blue–lavender–violet X. Do not redraw logo letterforms. The repository already registers `NEXUS_Official_Transparent_Logo.png` in both editable report resource packages; confirm identity/bytes before any asset replacement.

Approved color tokens:

| Purpose | Token | Usage |
| --- | --- | --- |
| Outer page | `#061524` / `#0B0F19` | Dark framing and editorial cover |
| Main action/selection | `#4EA8FF` | Selected state, primary analytic emphasis |
| Cyan highlight | `#00E0FF` | One high-importance line, key conversion, signature X |
| Secondary series | `#8F9BFF` | Alternative cohort/benchmark |
| Tertiary series | `#6E55C6` | Third category or interval context |
| Panel background | `#FFFFFF` | High-legibility native analytical chart surfaces |
| Panel border | `#DCE8F5` | Quiet technical framing, not decorative card outlines |
| Body text, on light | `#122942` | Strong editorial contrast |
| Secondary labels | `#526C83` | Explanatory labels with adequate contrast |

**Implementation:** report-native JSON theme (workspace + offline fixture edition) uses the same eight analytical series hues, slightly softer border, 10px radius and 12pt primary chart titles where supported. All original chart query states and model bindings remain untouched. Theme success must still be checked in Microsoft Power BI Desktop.

## Premium does not mean pretending to have a paid Power BI license

Build with regular native PBIR components: bar charts, scatter plots, small multiples where supported, KPI cards, analytical tables, drillthroughs, bookmarks/navigation and tooltips. Avoid a dependency on Pro-only deployment, paid AppSource custom visuals, unsupported fonts or publish-to-web services. The final product should **look** like a credible commercial data analysis interface while remaining reproducible without purchasing a license.

## Analytical storytelling: each page gets a different reading rhythm

| User question | Page | Hero chart / evidence | Interpretation rule |
| --- | --- | --- | --- |
| Where is on-pitch productivity concentrated? | Player Performance | Per-90 leaderboard and minutes context | Rate comparisons require playing-time context |
| How does the player population differ? | Segmentation | Position and age cohort distribution | Cohorts are not ML clusters |
| Which teams perform better? | Club & League | Win-rate comparison plus match counts | Warehouse 0–100 win rates normalized only once |
| How much transfer success is observed? | Transfer Success (365d) | Outcomes and 365-day observation coverage | Never treat retrospective labels as predicted wins |
| Which deals look mispriced? | Transfers & Market Value | Fee vs benchmark and premium/discount | Separate missing fee and unknown valuations |
| What does the valuation model estimate? | Player Valuation | Previous value vs prediction and interval | Prediction ≠ future realized profit |
| When can we trust the model? | Model Reliability | Holdout, baseline, segment error and drift | Explain sample size, uncertainty and out-of-time validation |
| Where should the reviewer navigate? | Home | Purpose-built research module navigation | No fake featured metrics |
| What is the takeaway? | Closing | Methodology, evidence and decision links | No unsupported performance claims |

Each main page receives: one question, an editorial 2-level heading, an **evidence-first hero visualization**, 1–2 real context comparisons, a usable analytical table or explanatory note and consistent filter controls. Avoid five identically weighted cards, tiny illegible labels, ornamental gradients and grids with no prioritization.

## Content and provenance rules

- **Production report:** English titles and narrative, no presentation labels announcing test/demo/synthetic/fake data. Publish only if actual BigQuery model loads and metrics reconcile. It must remain a real-data report, not just the removal of a label.
- **Internal offline fixtures:** retain truthful provenance, clearly separated from the production PBIP. Do not rename fictional values into real data or present offline fixture screenshots in the public portfolio.
- Keep `powerbi/workspace` BigQuery tables/partitions connected; never replace them with a local CSV to make the dashboard appear populated.
- Avoid claims of real-time football information until snapshot and model freshness are checked. Verified BigQuery mart modifications were historically in June 2026; report data coverage must be disclosed accurately when accepted.
- No secret keys, Google auth tokens, user identifiers or provider credentials in Git.

## Acceptance and portfolio photography

1. A clean clone of the public PBIP validates schemas, query references, native visual types, signed source provenance and registered image assets.
2. All nine visible pages, two drillthrough contexts and two tooltips open correctly in actual Desktop at 100% zoom. Desktop remains closed until the user's explicit final check.
3. Every requested measure and chart is driven by actual BigQuery-based Power Query imports, not manually typed results. Actual refresh succeeds with zero unexpected errors and representative KPI source reconciliation.
4. Screenshot review covers cut-off chart labels, pivot scrolling, typography, navigation, filter state, logo interpolation, color contrast and full image bounds. Export PNGs only from the actual production page; no synthetic screenshot substitutes.
5. Explain the analysis in portfolio README: problem, source, data processing, questions, ML caveats, Power BI interface and deployment limitations; link only verified screenshots.
6. CircleCI remains disabled via `run_final_ci=false` until local source/Desktop/warehouse acceptance is complete. No claim of CI success from static JSON checks.

## Immediate implementation phases

**Phase A — identity and theme:** use existing registered official transparent logo; ensure full-bleed dark shell, calm white analytics surfaces, consistent chart hierarchy, coherent focus and border tokens.  
**Phase B — analytical structure:** rebuild transfer/valuation/reliability pages with decision-first narrative; audit nine visible views to remove dated generic chart grids.  
**Phase C — production integrity:** source data freshness contract, English audit, no internal demo markers in production, BigQuery-specific connector guards, explicit source and computed-measure correctness.  
**Phase D — final Desktop acceptance:** only at the user's final checkpoint, capture legitimate images, fix visual defects, then explicitly trigger final hosted CircleCI.

This art direction is **not** a rendered Power BI screenshot or proof of model refresh. Publication status remains **HOLD** until real acceptance.
