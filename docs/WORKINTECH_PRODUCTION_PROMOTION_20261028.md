# NEXUS Football Intelligence — accepted Workintech PBIP production promotion

**Date:** 28 October 2026. **Scope:** Windows desktop Power BI project source, not a Power BI Service/cloud deployment.

**Owner acceptance:** The owner reported that the tested Power BI report worked correctly. Based on that acceptance, the assistant completed a **reversible on-disk promotion** of the already prepared and static-validated 34-source PBIP to the user's existing Desktop report path. It did not ask for further screenshots.

## Promoted source

- **Active report:** `C:\Users\MONSTER\Documents\NEXUS-Football-PBI\FootballPlayerAnalysis\FootballPlayerAnalysis.pbip`
- **Versioned 28 October Git source:** [34-source Workintech PBIP](../powerbi/workintech-20261028/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip)
- **Earlier dated 27 October source, preserved:** [65-source Workintech PBIP](../powerbi/workintech-20261027/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip)
- **Acceptance QA source:** `C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-full-dedup-qa-20261028\FootballPlayerAnalysis`
- **Complete, unmodified previous active model with local data cache:** `C:\Users\MONSTER\Documents\NEXUS-Football-PBI\Backups\FootballPlayerAnalysis-pre-dedup-acceptance-20261028-010708-743756`
- **Machine-readable cutover audit:** `C:\ProgramData\SentinelX\workspace\football-recovery-20261027\workintech_pbip_production_promotion_20261028.json`

### Cutover guardrails and checks

1. Confirmed **Power BI Desktop was not running** at cutover.
2. Independently compared all common files in the active and QA PBIPs. The **only three changed common files** were `Model/definition/model.tmdl`, `Model/definition/relationships.tmdl`, and `Model/diagramLayout.json`; all other common file bytes were identical.
3. Prepared a byte-verified temporary staging copy of all **991 QA files**.
4. Atomically renamed the original active Desktop report directory into the complete rollback directory on the same drive.
5. Swapped the validated QA copy into the same active report path; existing Windows shortcuts therefore continue pointing at that path.
6. Rechecked **every promoted file hash** against the QA candidate. Rechecked the old backup model counts and total file sizes.
7. The prior local Desktop `.pbi` cache was **preserved in the rollback**, not carried into the new semantic model to avoid stale 65-source import/cache behavior. This means Desktop may rebuild model data on its next open/refresh.

| Model statistic | Before | Promoted / accepted |
| --- | ---: | ---: |
| Model TMDL files | 148 | 77 |
| BigQuery-connected source tables | 65 | **34** |
| Relationship definitions | 158 | **87** |
| Report pages | 13 | 13 |
| Report visuals | 308 | 308 |
| Byte-level match with accepted QA model | N/A | **PASS** |

**Git edition:** the 34 remaining BigQuery sources include 31 contract-verified governed Workintech tables plus three additional unique tables; those three are not automatically certified by the earlier 31/31 physical contract. The model is suitable for the owner's accepted Desktop use, but production Service operations, scheduled refresh, KPI parity against live BigQuery, and wider commercial release controls remain separate.

## Runtime evidence boundary

The owner explicitly stated testing succeeded, which is recorded as **owner acceptance** of the tested model. The assistant did **not** independently open Power BI Desktop after cutover or run DAX/TOM queries against the promoted instance. Do not label the byte-level cutover check as a fresh on-screen or runtime test.

**No new screenshots were required or requested.** The existing 13 original October 27 images remain historical visual evidence; those images are not recaptured or altered.

## Rollback and ongoing maintenance

The original complete PBIP (including approximately 267 MB of existing Desktop model cache and settings) remains in the above rollback directory. If regression is later reported, first close Desktop, then restore that directory to the original active path using the transactional rollback procedure. **Do not delete this backup as part of routine cache cleanup.**

The dated source directories allow the old and new versions to be examined without replacing the owner's active report. The Workintech offline release gate may still identify archive quality risks and three additional BI sources outside the original 31-table contract; it is a separate data-product risk control, not a claim that the owner's tested PBIP source cannot be promoted.

**Status:** `OWNER_ACCEPTED_PBIP_SOURCE_PROMOTED; POST_CUTOVER_DESKTOP_RUNTIME_NOT_INDEPENDENTLY_OBSERVED`.
