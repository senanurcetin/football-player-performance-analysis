# Football Player Analysis — fully offline demonstration workspace

**SYNTHETIC DEMONSTRATION DATA ONLY.** This is a *separate* copy of the report stored under `powerbi/offline-demo/FootballPlayerAnalysis/`. The original model at `powerbi/workspace/FootballPlayerAnalysis/` still uses **real BigQuery sources** and is not modified to fabricate research outcomes.

## What is included

- All original PBIR report pages, relationships and DAX expressions, plus **12 new query-bound analytic visuals and three page headings** on previously empty Segmentation, Club/League and Transfer Success pages.
- A parallel semantic model in which **33 external BigQuery M partitions** are replaced by small, deterministic inline Power Query `#table` data fixtures.
- All 13 page names include a clear `[DEMO]` label, and Home states that the values are synthetic.
- A blue/navy NEXUS home design. No credentials or Google Cloud account are needed to evaluate inline sample tables.

## Repeatable source checks

From repository root, run `python scripts/check_powerbi_offline_demo.py` for demo fixture reconciliation and the 365-day SQL contract, then `python scripts/audit_powerbi_visuals.py` to inspect PBIR structure and referenced fields in both editions. The release test plan and precise Desktop limitations are in [`docs/POWER_BI_VISUAL_QA.md`](../../docs/POWER_BI_VISUAL_QA.md).

The Transfer Success Analysis uses the governed **365-day / 20%** observed-outcome contract, with four cohort/coverage/reliability cards and four breakdown charts. All 24 demo transfer records and fixed-horizon outcomes have been reconciled to this fictional model; the 33-table demo is still synthetic and not end-to-end statistically validated.

## How to run after source verification

1. Download and unzip the repository. Use Power BI Desktop (PBIR format support enabled as appropriate for the installed version).
2. Open `powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`, **not** the production `powerbi/workspace/...` file.
3. Use **Home → Refresh** to import inline fixtures if the report opens without cached data. No BigQuery login is expected for the demo partitions.
4. If there are schema or DAX errors, preserve the exact **Details** message and fix before making portfolio screenshots.

## Strict limitations

Fixtures are fictional, generated from column names and simple deterministic patterns; they do **not** preserve real entity distributions, temporal consistency, football performance calculations, actual transfer events or ML quality. Existing DAX may yield unusual or blank numbers and some heavily filtered visuals may remain empty. **Opening and refresh have not yet been verified inside Power BI Desktop.** This is a test/demo artifact, not a validated substitute for authenticated production data. All screenshots from it must visibly say **DEMO / SYNTHETIC DATA** and must not be presented as actual football analysis.

For real football visualizations, authenticate and refresh the original BigQuery-backed PBIP instead. Never commit credentials, refresh tokens or account keys.
