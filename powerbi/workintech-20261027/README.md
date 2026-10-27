# Workintech Power BI — 27 October 2026 source edition

**POST-SCREENSHOT SOURCE FIX:** Four visual.json definitions corrected (percentage axis and labels, two tooltip currencies and crowded donut category labels). The active report has byte-identical patched files; no new screenshots were requested. Run the source dry-run repair script scripts/fix_powerbi_visual_formats_20261027.py and its five regression tests test_powerbi_fixed_formats_20261027.py. The on-screen appearance remains to be independently observed when convenient.


This directory is the **versioned, editable PBIP/PBIR/TMDL snapshot** of the report the Windows owner actually opened and screenshotted on 27 October 2026.

**Main file:** [FootballPlayerAnalysis.pbip](FootballPlayerAnalysis/FootballPlayerAnalysis.pbip)

## Provenance

- Captured from the owner's imported Desktop project in Documents/NEXUS-Football-PBI.
- 13 report pages, 308 visuals, 30 analytic chart visuals.
- 31 governed Workintech BigQuery connector partitions contain BillingProject=workintech-working and reference 22 nexus_football_mart + 9 nexus_football_ml tables. Their physical table-column contract passed independently.
- The actual user-edited project **also includes 34 other imported/duplicate BigQuery connector table definitions**. Several are used by relationships, so no clean-up was performed. This source edition preserves the original relationship graph pending an explicit reconciliation.
- Local binary cache files (Model/.pbi), access tokens, and private service-account JSON credentials are **not** published.
- The screenshot gallery is stored in [documentation assets](../../docs/assets/screenshots/README.md) rather than in report StaticResources, which contain their own runtime-dependent design assets.

## Correctness boundary

This is the most recent collected **user-edited source snapshot**, not a certified clean 31-table release. Model duplicates, visual tooltips, M% chart formatting and selected-player navigation still require Desktop review. Do not claim that 31/31 governed BigQuery source checks also certified 34 additional sources.

The prior main repository edition is preserved at [powerbi/workspace](../workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip); the offline demo remains synthetic. The runtime evidence and open issue list are in the [27 October execution record](../../docs/WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md).

**To open:** Keep all Model and Report directories together. Use Power BI Desktop and your own authorized Google BigQuery sign-in; credentials and private key contents are never to be committed.
