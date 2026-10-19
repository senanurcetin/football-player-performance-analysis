# NEXUS Football Intelligence — technical documentation

**Reviewed: 18 October 2026.** This index covers the existing football analytics, data science, dbt and editable Power BI research project. **No productization or hosting work is in scope.**

**Start here:** [repository README](../README.md) · [verified status and blockers](PROJECT_STATUS.md) · [reproduction runbook](RUNBOOK.md).

## Source-of-truth map

Use one canonical source per topic. Dated research and audit notes supply evidence but **do not override** the project status or prove a newer warehouse run.

| Domain | Canonical document | Scope |
| --- | --- | --- |
| Delivery and verification | [Project status](PROJECT_STATUS.md) | Verified vs. outstanding; historical screenshot and ML evidence; release **REVIEW PENDING** |
| Architecture | [Architecture and model catalog](ARCHITECTURE.md) | BigQuery/dbt lineage, stable grains and marts |
| KPI contracts | [Governed KPI dictionary](KPI_DICTIONARY.md) | Population grains, time windows, rate denominators, NULL and percent conventions |
| Data quality | [Data quality and validation](DATA_QUALITY.md) | Historical June 2026 counts, missingness and statistical limitations |
| ML methodology | [Player market-value methodology](PLAYER_MARKET_VALUE_ML.md) | Production v5 historical baseline, time split, gates and uncertainty |
| Power BI semantics | [Power BI modeling](POWER_BI_MODELING.md) | Production model, metric interpretation, DAX and nullable values |
| Visual specification | [NEXUS design system](BI_DESIGN_SYSTEM.md) | Native editable PBIR, colors, logo, canvas rules and source editions |
| BI verification | [Power BI visual QA](POWER_BI_VISUAL_QA.md) | Nine presentation pages, two drillthroughs, two tooltips; runtime acceptance |
| Desktop procedure | [Power BI Desktop handoff](POWER_BI_DESKTOP_HANDOFF.md) | Actual PBIP opening, offline preflight and authorized refresh |
| Operations | [Runbook](RUNBOOK.md) | Local checks vs. billable BigQuery/dbt; true CI trigger semantics |
| CI governance | [CI-last policy](CI_RELEASE_GATE_POLICY.md) | CircleCI final opt-in and distinct GitHub Actions conditions |
| Research attribution | [Reviewer brief](hiring-summary.md) | Workintech team origins, source and authorship boundaries |

## Focused research and audit evidence

| Evidence | Purpose | Status |
| --- | --- | --- |
| [Numeric ML validation — 18 Oct](ML_VALIDATION_HARDENING_20261018.md) | Required target, key and interval-contract safeguards merged into `main` via PR #78 | Source changes, not an empirical model rerun |
| [ML reliability — 18 Oct](ML_RELIABILITY_EVALUATION_20261018.md) | Offline grouped uncertainty, artifact consistency and refitted walk-forward research | Local synthetic tests only; real feature export still needed |
| [Daily valuation event-grain audit — 19 Oct](ML_VALUATION_EVENT_GRAIN_AUDIT_20261019.md) | Player/date deduplication, conflicting EUR amounts and target row grain | Synthetic SQLite check; warehouse impact NOT VERIFIED |
| [Research-only execution plan — 18 Oct](ANALYTICS_ENGINEERING_EXECUTION_PLAN_20261018.md) | Ordered outstanding work and authorization dependencies | Not a substitute for live test evidence |
| [Power BI historical value audit — 18 Oct](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md) | **13/13** screenshot file hashes and historical KPI reconciliation | **KONTROL EDİLDİ** for matched items; 365-day 3-row mismatch remains |
| [Screenshot gallery and capture manifest](assets/screenshots/README.md) | Source-rendered images, hashes and provenance | 17 Oct images; not current BigQuery freshness |
| [Historical engineering archive](archive/README.md) | Date-stamped earlier designs, incidents and fixes | Read-only background; do not treat as the current acceptance decision |

| [Free CPU offline verification — 19 Oct](REPRODUCIBLE_OFFLINE_VERIFICATION_20261019.md) | [Colab/Kaggle runnable notebook](../notebooks/nexus_football_offline_verification.ipynb), fail-closed JSON runner and evidence limits | Runner has 2 local unit tests PASS; full football checkout still needs execution |

## Maintenance policy

1. Keep the [project status](PROJECT_STATUS.md) as the only current release/acceptance decision. Link to it; don't repeat the same PASS/HOLD assertions in multiple independent files.
2. Preserve **one real-data Power BI PBIP** and a separate visibly **synthetic** offline fixture edition. Never move fixture records into real-data visuals or change the historic imported screenshots to make metrics match.
3. Keep analytics docs research-focused; no sales language, published product promise, hosted demo or new PDF/PPTX packaging. The obsolete active product and portfolio handoff documents were retired in favor of the [design system](BI_DESIGN_SYSTEM.md), [modeling](POWER_BI_MODELING.md), [visual QA](POWER_BI_VISUAL_QA.md) and [Desktop handoff](POWER_BI_DESKTOP_HANDOFF.md).
4. Retain the 19 dated Power BI engineering history documents in [archive](archive/README.md) because they explain earlier defects and decisions. **Do not retroactively rewrite their measurements.**
5. Use dated source/model provenance for every metric, population, cohort, filter and baseline. June warehouse results and 17 October Power BI screenshots are not evidence of an 18 October authenticated BigQuery refresh.
6. After any structural change, run `python scripts/check_docs_integrity.py`, `python scripts/verify_dashboard_screenshots.py`, offline PBIR validators and the full Python test suite **in a genuine complete checkout** before merging. Retain test output and Git commit SHA.
7. Do not commit credentials, access tokens, customer/private paths, generated dbt `target/` or unapproved model artifacts. Hosted CI and BigQuery jobs require explicit permission and budget review.

