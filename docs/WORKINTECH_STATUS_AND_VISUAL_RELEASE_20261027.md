# NEXUS Football Intelligence — Workintech recovery and visual evidence (27 October 2026)

**Evidence date:** 27 October 2026. **Target:** Google BigQuery EU, workintech-working, and the owner's Windows Power BI Desktop. This is the current execution record; earlier October 17–20 status notes remain historical evidence rather than current acceptance.

## Reconstructed warehouse and actual verification

| Layer | Verified result | Interpretation |
| --- | --- | --- |
| Input archive | Kaggle davidcariboo/player-scores, 12 tables and 7,497,433 source rows | Historical archive; latest game date 6 July 2026. Not live football data. |
| BigQuery raw | workintech-working.nexus_football_raw | Typed load, original 12 tables and source row-count checks. |
| dbt | 46/46 models: 12 staging, 7 intermediate, 25 marts, 2 ML preparation models | Two snapshots under nexus_football_snapshots. |
| Quality | 243/243 dbt tests passed in owner's successful Verify run | Does not guarantee future data freshness. |
| Governed ML | Seven ML outputs published and quality-checked | Predictions are estimates, not realized profit or transfer prices. |
| Power BI physical contract | ONLINE_CONTRACT_PASS, 31/31 tables: 22 marts and 9 ML | Verifies table/column compatibility, not every interactive report behavior. |

Local provenance: the recovery folder at C:\ProgramData\SentinelX\workspace\football-recovery-20261027 contains workintech_warehouse_build_status.json, powerbi_bigquery_all_contract_result.json, and the raw-source typed manifest. No private keys are committed.

**Different environment:** The older data-analiz-490513 / football_mart workflow is a separate historical project target. Do not equate its output and source freshness with workintech-working.

## Power BI editions

- **User's actual rendered PBIP:** C:\Users\MONSTER\Documents\NEXUS-Football-PBI\FootballPlayerAnalysis\FootballPlayerAnalysis.pbip
- **Dated repository source:** [Workintech PBIP](../powerbi/workintech-20261027/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip). This is a separate, editable copy without the machine's local cache or credentials.
- **Earlier report:** [Legacy production-connected PBIP](../powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip), preserved.
- **Synthetic regression edition:** [Offline demo](../powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip), not actual player values.

A new inventory finding in the user-edited PBIP identifies **65 BigQuery-connected TMDL table definitions**: 31 governed Workintech tables with the corrected BillingProject setting and 34 additional imported or duplicate Workintech tables. Some extra definitions are referenced in model relationships. The 31/31 physical contract concerns the 31 governed tables only. Do not automatically delete the extra tables or claim the entire 65-table semantic model has been reconciled.

The report retains 13 pages and 308 visuals, including 30 analytic charts. October 27 PBIR/TMDL changes affected 32 files: blank-category filters, shorter competition names and follow-up status labels, horizontal bar orientations, number-display settings and clearer explanation. Existing DAX measure logic and established pages were preserved by the visual pass.

## Real Power BI Desktop screenshots

![Nine-page current Power BI gallery](assets/screenshots/NEXUS_Football_Page_Gallery.png)

[Full-resolution screenshots, technical captures and SHA-256 manifest](assets/screenshots/README.md)

The user supplied 13 original PNG captures from Downloads\futbol on 27 October: nine presentation pages, two player-detail drillthrough pages, and two tooltip pages. Their original bytes and hashes were preserved when adding them to this repository. Images show an imported report, not a row-level reconciliation to the warehouse or a live 27 October football feed.

## Open visual and semantic issues shown in the new screenshots

1. **Fee premium chart:** The Transfer & Market Value page still displays near-zero percentage axes with nonsensical M% units while the headline KPI indicates about -69.4%. This chart requires a specific percentage/scale repair. Do not label it correct simply because the data loads.
2. **Tooltip money scaling:** Two tooltip screenshots show inflated displayed numbers (for example €739836,0M and €5250045,3M). These are likely formatting defects; they are not evidence of genuine transfer fees or player values at that magnitude.
3. **Truncated text and scrollbars:** ML quality legend, long club names and table columns still truncate or require horizontal scrolling. Inspect at 100% Desktop zoom before an external presentation.
4. **Unselected player detail:** The two drillthrough captures show No player selected and blank selected-player cards. The state does not itself mean the DAX is broken; selected-player navigation remains to be demonstrated.
5. **ML interpretation:** Small samples, feature drift, model reliability, and prediction intervals must be considered before treating model metrics as deployment-ready.
6. **Historical freshness:** The recovered source is historical (latest game 6 July 2026). Screenshots should not be marketed as live current games.

## Reproducibility and release

Run repository-local integrity checks with an approved local Python environment:

    python scripts/verify_dashboard_screenshots.py
    python scripts/check_docs_integrity.py
    python -m unittest discover -s tests -p "test_*.py"

On Windows, the contact sheet can be rebuilt using the repository script:

    powershell -NoProfile -File scripts/build_dashboard_gallery.ps1

**Still open:** Fix the actual percentage/tooltip display defects; investigate the 34 additional TMDL imports and their dependencies; test drillthrough with a real selected player; compare important imported KPIs with their BigQuery sources; configure separate Power BI Service publication, cloud credentials, and scheduled refresh; obtain owner acceptance. Do not trigger repeated cloud retraining or hosted CI merely for documentation edits.
