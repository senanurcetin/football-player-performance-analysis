# Genuine Power BI Desktop screenshot gallery

**Captured 17 October 2026 from the production-connected Power BI PBIP at source commit `db0819b`.** The contents are actual Desktop renders, not fabricated screenshots or synthetic-demo results. A new live BigQuery refresh and final user acceptance have not been independently certified.

![Nine-page NEXUS gallery](NEXUS_Football_Page_Gallery.png)

## Curated presentation pages

| # | Page | Portfolio framing | Clean report image |
|---|---|---|---|
| 01 | Home | [PNG](portfolio/01_home.png) | [PNG](production/01_home.png) |
| 02 | Player Performance Analysis | [PNG](portfolio/02_player_performance.png) | [PNG](production/02_player_performance.png) |
| 03 | Player Segmentation | [PNG](portfolio/03_player_segmentation.png) | [PNG](production/03_player_segmentation.png) |
| 04 | Club & League Analysis | [PNG](portfolio/04_club_league.png) | [PNG](production/04_club_league.png) |
| 05 | Transfer Success Analysis (365d) | [PNG](portfolio/05_transfer_success.png) | [PNG](production/05_transfer_success.png) |
| 06 | Transfer & Market Value Analysis | [PNG](portfolio/06_transfer_market.png) | [PNG](production/06_transfer_market.png) |
| 07 | Player Market Value Prediction | [PNG](portfolio/07_market_value_prediction.png) | [PNG](production/07_market_value_prediction.png) |
| 08 | ML Model Reliability | [PNG](portfolio/08_ml_reliability.png) | [PNG](production/08_ml_reliability.png) |
| 09 | Closing | [PNG](portfolio/09_closing.png) | [PNG](production/09_closing.png) |

## Technical evidence (not approved for portfolio display)

- [Player Transfer Detail](production/10_transfer_detail.png) — unselected player; unresolved visual placeholder/error states.
- [Player Prediction Detail](production/11_prediction_detail.png) — unselected player; unresolved visual placeholder/error states.
- [Transfer tooltip](internal/12_tooltip_transfer.png) and [Prediction tooltip](internal/13_tooltip_prediction.png) — hidden report-page tooltips.

## Provenance and quality

- 13 full-resolution report-only PNGs at **2177 × 1229 px**. Power BI UI chrome was cropped, chart values were not altered.
- Nine separately framed versions use NEXUS editorial styling, preserving the original charts.
- [Capture manifest](capture_manifest.json) records original page names, source commit and per-image SHA-256 fingerprints.
- The PNGs inside `powerbi/**/StaticResources/` are not obsolete screenshots: many are still registered report dependencies and are deliberately retained.
- Run `python scripts/verify_dashboard_screenshots.py` to check captured image dimensions, SHA-256 hashes, and README references.

**Release boundary:** Capturing real imported model values is not evidence of current-day warehouse freshness, interactive testing of all hidden pages, or an approved Power BI Service publication.
