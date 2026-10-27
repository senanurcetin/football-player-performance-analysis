# NEXUS Football Intelligence — current verification status

**Current date: 28 October 2026.** This is the **single current project-status document**. Dated investigations are preserved separately; outdated research limitations are not automatically the present Desktop model status.

## Current edition and acceptance

| Area | Verified evidence | Boundary |
| --- | --- | --- |
| Historical input | 12 Kaggle/Transfermarkt tables; last recorded match **6 July 2026** | Not a live current-season football feed |
| BigQuery and dbt | Owner-authorized **46/46 dbt models** and **243/243 dbt tests** | Future warehouse refresh and monitoring are separate |
| Governed Power BI physical contract | **31/31** checked tables (22 mart + 9 ML) | Three additional unique Power BI imports not covered by this contract |
| Desktop semantic model | Owner reported the tested model worked; **34 BigQuery imports, 87 relationships, 13 pages and 308 visuals**; full rollback retained | Independent post-cutover Desktop/TOM evaluation not run by assistant |
| Structural and visual evidence | 243/243 explicit PBIR field references valid; 13 archived screenshots hash-verified | PNGs taken **27 October**, before subsequent format repairs |
| ML | Historical time-split methodology, baseline/interval and leakage-control framework | Revised real-data temporal holdout has not been independently verified |
| Operations | Versioned editable PBIP source in Git; existing local Desktop path preserved | Power BI Service publication, refresh and commercial sign-off not established |

**Current PBIP:** [Owner-accepted Workintech 28 October edition](../powerbi/workintech-20261028/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip).

## Evidence and provenance

- [Owner-authorized Workintech warehouse and 31-table source-contract verification](WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md).
- [Full import deduplication and 87-relationship static QA](WORKINTECH_FULL_DEDUP_QA_20261028.md) and [local Desktop PBIP cutover with rollback](WORKINTECH_PRODUCTION_PROMOTION_20261028.md).
- [13 genuine 27 October Desktop screenshots and SHA-256 manifest](assets/screenshots/README.md), preserved without retouching or a request for new screenshots.
- [Historical archive quality profiling](WORKINTECH_AUTONOMOUS_QUALITY_GATE_20261027.md): two unmatched player appearance records; 1,214 matches referencing five absent publisher competition codes; one nonpositive valuation; 475 future-dated transfers as of 27 October. Observed 365-day outcomes exclude future transfers.

## Remaining acceptance conditions

1. **Analytic semantics:** Compare priority DAX/KPI outputs to governed BigQuery populations, including filters, transfer outcome denominators and selected-player drillthrough. This can proceed without requesting new screenshots.
2. **Model evaluation:** Evaluate revised training and scoring on a fresh authorized chronological holdout (baseline comparisons, segment support, intervals, leakage and drift).
3. **Operations:** Verify access, source-data refresh, Power BI Service deployment/scheduling, monitoring and rollback, if a hosted deployment is required.
4. **Commercial publication:** Reconcile original collaborative attribution, dataset licensing, and approved CI/release governance. No billed cloud action is implied by a documentation merge.

## History, ownership and environment

This repository originated as a **collaborative Workintech Data Pro team project** incorporating upstream contributions; Git history is the attribution record. It must not be portrayed as exclusively authored by one contributor.

The historical `data-analiz-490513` warehouse and its `football_mart` tables differ from the recovered `workintech-working` project. Earlier October 17–20 source checks are dated evidence, not claims of the current model state.

See the [documentation index](README.md), [19 October offline verification](SENTINELX_OFFLINE_VERIFICATION_20261019.md), and [earlier recovery plan](WORKINTECH_MIGRATION_20261027.md).

**Decision:** Advanced professional data engineering, analytics, ML and BI project; **owner-accepted local Power BI source**. Current-data, hosted-service and broader commercial certification remain open.
