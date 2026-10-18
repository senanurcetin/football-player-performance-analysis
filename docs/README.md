# NEXUS Football Intelligence — documentation

**Documentation snapshot: 17 October 2026.** Begin with the [repository README](../README.md), [current project status](PROJECT_STATUS.md) and [real Power BI screenshot gallery](assets/screenshots/README.md).

## Canonical active documents

| Area | Reference | Purpose |
|---|---|---|
| Verification and release | [Current project status](PROJECT_STATUS.md) | Verified evidence and remaining production blockers |
| Architecture | [Architecture and model catalog](ARCHITECTURE.md) | BigQuery/dbt lineage, model grains |
| Data validation | [Data quality](DATA_QUALITY.md) | Rules and dated historical test counts |
| ML | [Player market-value methodology](PLAYER_MARKET_VALUE_ML.md) | Temporal validation and persistence benchmark |
| ML integrity | [Numeric-contract hardening](ML_VALIDATION_HARDENING_20261018.md) | Credential-free input, interval and calibration guards; follow-up science roadmap |
| BI source | [Power BI modeling](POWER_BI_MODELING.md) | PBIP/PBIR structure and DAX |
| Visual identity | [NEXUS design system](BI_DESIGN_SYSTEM.md) | Theme palette and 13-page canvas contract |
| Visual acceptance | [Power BI visual QA](POWER_BI_VISUAL_QA.md) | Current page and interaction acceptance matrix |
| Deployment handoff | [Desktop open and refresh](POWER_BI_DESKTOP_HANDOFF.md) | Production versus synthetic edition; data reconciliation |
| Product | [Football Intelligence product](FOOTBALL_INTELLIGENCE_PRODUCT.md) | Product questions and known boundaries |
| Presentation contract | [Production portfolio contract](POWER_BI_PORTFOLIO_PRODUCTION_CONTRACT.md) | No fabricated metrics, authorized real data |
| Operations | [Runbook](RUNBOOK.md) | Installation and reproducible execution |
| Hosted CI | [CI-last policy](CI_RELEASE_GATE_POLICY.md) | Opt-in final release gate |
| CI troubleshooting | [CI recovery](ci-recovery.md) | Prior CI failures and workarounds |
| Hiring | [Reviewer brief](hiring-summary.md) | Attribution and verifiable portfolio evidence |
| ML reliability | [Temporal and statistical diagnostics](ML_RELIABILITY_EVALUATION_20261018.md) | Player-grouped bootstrap, offline holdout auditor, chronological folds and observed coverage |
| ML execution | [Research-only engineering plan](ANALYTICS_ENGINEERING_EXECUTION_PLAN_20261018.md) | Ordered tasks, acceptance tests and external access blockers |

## Screenshot evidence

The [curated gallery](assets/screenshots/README.md) includes nine professional screenshots from the actual production-connected Power BI Desktop. The [capture manifest](assets/screenshots/capture_manifest.json) records 13 original PNGs and their SHA-256 checksums. Two unselected player-detail screenshots and two tooltips remain in the technical archive, not the approved promotional image set. The separate offline demo is **synthetic**.

## Historical records

[Browse the historical Power BI archive](archive/README.md). It contains the original dated engineering plans, design revisions, warehouse audits, incident triage and repair records. Prior phrases such as “screenshots pending” reflect the original document date—not the current capture state.

## Documentation maintenance standards

1. Use [project status](PROJECT_STATUS.md) as the single source of truth for release evidence, and link to it rather than copying changing PASS/HOLD assertions.
2. Label every model metric with its validation window, source data, baseline and test scope. Do not call historical imported data live.
3. Do not remove registered resources from Power BI sources simply because a logo/PNG is old; these may be referenced by the report.
4. Separate historical plans from current operating procedures; preserve historical records with date and repository provenance.
5. Before merging, run `python scripts/check_docs_integrity.py`, `python scripts/verify_dashboard_screenshots.py` and the project unit tests.
6. Never commit service-account files, access tokens, private system paths or credentials.
