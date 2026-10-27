# NEXUS Football Intelligence — current verification status

**Current date: 28 October 2026.** This is the **single current project-status document**. **Project objective:** an advanced, noncommercial Data Engineering + Data Analytics + Machine Learning + Power BI research/portfolio project. It is **not intended to become a commercial product**. Dated investigations are preserved separately; outdated research limitations are not automatically the present Desktop model status.

## Current edition and acceptance

| Area | Verified evidence | Boundary |
| --- | --- | --- |
| Historical input | 12 Kaggle/Transfermarkt tables; last recorded match **6 July 2026** | Not a live current-season football feed |
| BigQuery and dbt | Owner-authorized **46/46 dbt models** and **243/243 dbt tests** | Future warehouse refresh and monitoring are separate |
| Governed Power BI physical contract | **31/31** checked tables (22 mart + 9 ML) | Three additional unique Power BI imports not covered by this contract |
| Desktop semantic model | Owner reported the tested model worked; **34 BigQuery imports, 87 relationships, 13 pages and 308 visuals**; full rollback retained | Independent post-cutover Desktop/TOM evaluation not run by assistant |
| Structural and visual evidence | 243/243 explicit PBIR field references valid; 13 archived screenshots hash-verified | PNGs taken **27 October**, before subsequent format repairs |
| ML | Historical time-split methodology, baseline/interval and leakage-control framework | Revised real-data temporal holdout has not been independently verified |
| Reproducibility and distribution | Versioned editable PBIP source in Git; existing Desktop path preserved and full rollback available | Hosted Power BI Service and commercial deployment are outside the intended scope |

**Current PBIP:** [Owner-accepted Workintech 28 October edition](../powerbi/workintech-20261028/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip).

## Evidence and provenance

- [Owner-authorized Workintech warehouse and 31-table source-contract verification](WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md).
- [Full import deduplication and 87-relationship static QA](WORKINTECH_FULL_DEDUP_QA_20261028.md) and [local Desktop PBIP cutover with rollback](WORKINTECH_PRODUCTION_PROMOTION_20261028.md).
- [13 genuine 27 October Desktop screenshots and SHA-256 manifest](assets/screenshots/README.md), preserved without retouching or a request for new screenshots.
- [Historical archive quality profiling](WORKINTECH_AUTONOMOUS_QUALITY_GATE_20261027.md): two unmatched player appearance records; 1,214 matches referencing five absent publisher competition codes; one nonpositive valuation; 475 future-dated transfers as of 27 October. Observed 365-day outcomes exclude future transfers.

## Completion assessment and recommended research hardening

**Core project scope: completed.** The historical data pipeline, analytical data model, ML research components, documented 34-source Power BI report and reproducible verification tooling are present; the owner accepted the tested Desktop model. There is no commercial-product, cloud-service or live-football-feed delivery requirement.

**Recommended further analytical validation (not a commercial release gate):**

1. **KPI consistency:** Independently compare important DAX/KPI outputs against BigQuery, including filter context, transfer-outcome denominators and selected-player drillthrough, without requesting new screenshots.
2. **ML scientific reliability:** Re-evaluate revised training/scoring on an authorized chronological holdout, compare against the previous-value baseline and report subgroup support, prediction intervals and leakage sensitivity.
3. **Research reproducibility:** Keep source lineage, analytical assumptions, source licensing and Workintech team attribution explicit; verify the steps from a clean environment when needed.

**Out of scope:** Power BI Service publication, scheduled cloud refresh, commercial licensing/certification, paid hosting, service-level monitoring, continual live-match ingestion and hosted production CI. Such tasks are not conditions for calling this advanced analytics project complete.

## History, ownership and environment

This repository originated as a **collaborative Workintech Data Pro team project** incorporating upstream contributions; Git history is the attribution record. It must not be portrayed as exclusively authored by one contributor.

The historical `data-analiz-490513` warehouse and its `football_mart` tables differ from the recovered `workintech-working` project. Earlier October 17–20 source checks are dated evidence, not claims of the current model state.

See the [documentation index](README.md), [19 October offline verification](SENTINELX_OFFLINE_VERIFICATION_20261019.md), and [earlier recovery plan](WORKINTECH_MIGRATION_20261027.md).

**Decision:** **Advanced noncommercial football analytics project — core implementation complete, owner-accepted local Power BI model.** Historical-data limitations and outstanding independent KPI/ML validation are clearly documented; commercial-service readiness is not the objective.
