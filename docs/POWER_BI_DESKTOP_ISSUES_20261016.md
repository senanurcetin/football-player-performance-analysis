# Power BI Desktop issue recovery — 16 October 2026

**Status:** source corrections tested; **actual Desktop rerender pending**. Do not treat a green unit test as visual acceptance.

## Source incident

The owner supplied actual Power BI Desktop captures showing:
- `Missing_References` at 20:16 local time.
- Transfer & Market Value chart/slicer errors and crowded labels.
- The Home wordmark-adjacent **FOOTBALL INTELLIGENCE** heading clipped vertically.
- The transfer count KPI rendered as truncated text (`40.208 tra...` in Turkish-locale Desktop).

The earlier genuine warehouse readback had established historical coverage and Import-mode data (not a live streaming model).

## Root-cause evidence

We used authenticated **read-only** BigQuery `INFORMATION_SCHEMA.COLUMNS` queries in `EU`, across `data-analiz-490513.football_mart` and `football_ml`, capped at 10 MiB billed/query, returning **786 real physical columns**. These were compared against the `sourceColumn:` entries in **33 production TMDL BigQuery Import partitions**.

The first pass found three additional nonexistent physical source columns on `ml_player_market_value_current_predictions`: `position_tr`, `age_group_tr`, `upside_kategori_tr`. Neither `age_group_tr` nor `upside_kategori_tr` was used in report visuals. `position_tr` was used by seven real bound visuals on Prediction, Prediction Detail and Prediction Tooltip. The actual available source field is `position`.

Corrections:
- Removed only the three invalid physical TMDL column declarations (no fabricated replacement fields).
- Updated the DAX dynamic-position title reference to `[position]`.
- Updated seven native visual bindings in each PBIR edition to `position` while retaining their visual types, query measures and canvas coordinates.
- Left all genuine warehouse data, model partitions, identity graphics and prediction values unchanged.
- Production + internal QA source parity maintained; offline fixture **must never be presented as real**.

Second live schema comparison found **0 missing BigQuery physical source fields across the 33 production imports**, after the targeted fix.

Earlier related Transfer & Market Value `fct_transfer_market_value_analysis[position_tr]` source and tooltip references were addressed in PR #71 and #72 and independently crosschecked against the same genuine BigQuery `position` column.

## Visual legibility work (source-only)

To address the screenshots, widened the vertical bounds of the original registered textboxes on Home and Transfer & Market Value, reduced the Home brand headline from 16pt to 14pt to provide baseline clearance, and set `Transfer Count` numeric format to `#,0` instead of appending `transfers` in the value field. Titles remain English and show the metric's purpose.

This is a **layout hypothesis grounded in the affected coordinates**, not proof of pixel-perfect Power BI Desktop rendering. The Desktop viewport shown in the captures also needs to be set to **Fit to page** during review rather than relying on the local enlarged page zoom; semantic correctness and actual visibility must be verified after reopening the updated report.

## Unfinished P0 checks

1. Close the previous already-open Desktop report using owner-approved save/discard choices, then open the **new source commit** `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` (not the offline fixture). A PBIP file update **does not necessarily hot-reload** into an existing Desktop session.
2. Refresh actual BigQuery Import partitions and inspect any error-dialog details. Avoid creating new Google Cloud credentials or modifying BigQuery data.
3. Confirm visually that both transfer plots/slicers and Prediction/Detail/Tooltip visuals contain real values and show **no** `Missing_References` field error.
4. Inspect all **13 pages** at Fit-to-page with 100% visual QA; verify original NEXUS logo, title baseline, filters, KPI values, tooltip interaction, labels, navigation and font glyphs.
5. Confirm the quality audit label remains `HISTORICAL / 21 JUN 2026` unless a new authenticated historical warehouse audit truly exists.
6. Record genuine screenshot evidence and only then promote portfolio publication from `HOLD`.

No claim of completed Desktop visual acceptance, error-free reload or final screenshot signoff is made here.
