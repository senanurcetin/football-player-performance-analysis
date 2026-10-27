# NEXUS Football — genuine Power BI Desktop screenshot gallery

**Capture versus current source:** These 13 original PNGs represent Desktop before the later 27 October visual-format repair. They are not retouched or replaced. The PBIR sources were subsequently corrected for the fee-premium percentage scale, two currency tooltip formats and prediction-quality donut labels. These file changes have passed offline regression; no subsequent Desktop render is claimed. See [current verification](../../WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md).


**Latest capture: 27 October 2026.** The images are genuine user-supplied Power BI Desktop screenshots from the Workintech-connected report, not fabricated diagrams, an offline synthetic demo, or images of a current live football feed.

![27 October 2026 nine-page NEXUS Power BI gallery](NEXUS_Football_Page_Gallery.png)

## Nine presentation pages

| # | Page | Current original Desktop PNG | Presentation copy |
| --- | --- | --- | --- |
| 01 | Home / Football Decoded | [Original](production/01_home.png) | [PNG](portfolio/01_home.png) |
| 02 | Player Performance Analysis | [Original](production/02_player_performance.png) | [PNG](portfolio/02_player_performance.png) |
| 03 | Player Segmentation | [Original](production/03_player_segmentation.png) | [PNG](portfolio/03_player_segmentation.png) |
| 04 | Club & League Analysis | [Original](production/04_club_league.png) | [PNG](portfolio/04_club_league.png) |
| 05 | Observed Transfer Outcomes / 365 Days | [Original](production/05_transfer_success.png) | [PNG](portfolio/05_transfer_success.png) |
| 06 | Transfer & Market Value Analysis | [Original](production/06_transfer_market.png) | [PNG](portfolio/06_transfer_market.png) |
| 07 | Player Market Value Prediction | [Original](production/07_market_value_prediction.png) | [PNG](portfolio/07_market_value_prediction.png) |
| 08 | ML Model Reliability | [Original](production/08_ml_reliability.png) | [PNG](portfolio/08_ml_reliability.png) |
| 09 | Closing / From Evidence to Decisions | [Original](production/09_closing.png) | [PNG](portfolio/09_closing.png) |

The portfolio and production PNGs are byte-identical for the nine main pages; no numbers were repainted or simulated. The contact-sheet gallery scales screenshots for navigation and is not evidence of additional validation.

## Technical and hidden report pages (not approved as release hero images)

- [10 — Player Transfer Detail](production/10_transfer_detail.png). Opened without selecting a player: the empty cards are a legitimate contextual state, not a successful selected-player drillthrough test.
- [11 — Player Market Value Prediction Detail](production/11_prediction_detail.png). Also captured in the unselected-player state.
- [12 — Transfer / fee vs value tooltip](internal/12_tooltip_transfer.png). Small hidden tooltip; currency display-format anomaly remains.
- [13 — Model / player valuation tooltip](internal/13_tooltip_prediction.png). Small hidden tooltip; currency display-format anomaly remains.

## Provenance, checks and limitations

- Original user folder: C:\Users\MONSTER\Downloads\futbol; screenshot timestamps 21:27–21:36 on 27 October 2026.
- Nine main pages are approximately 2,4k × 1,2k pixels. Two hidden tooltip images are about 550 × 315 pixels. Different dimensions are expected.
- The [capture manifest](capture_manifest.json) records **all 13 original file names, exact pixel sizes, SHA-256 hashes, page identities, source edition and known visible defects**.
- Run: python scripts/verify_dashboard_screenshots.py. This checks source hashes, portfolio identity, expected page counts and local README links.
- Regenerate the overview gallery on Windows using scripts/build_dashboard_gallery.ps1; it reads the original PNGs without altering their pixels.
- The earlier 17 October screenshots were backed up outside the source tree in the local recovery folder. Git history also retains previous versions.
- These images show real imported Power BI Desktop data. They do **not** establish up-to-the-minute event freshness, the correctness of every KPI, selected-player navigation, Service scheduled refresh, or final external-publication approval.

**Visible known issues on 27 October:** incorrect M% scale in the fee premium chart on page 06, anomalously scaled currency in both tooltips, truncated quality-donut label and table text, and unselected-player placeholders. See the [current execution and release record](../../WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md).
