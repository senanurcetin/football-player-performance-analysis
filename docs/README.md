# NEXUS Football Intelligence — documentation map

**Reviewed 20 October 2026.** This is an analytics engineering, data science, dbt and existing editable Power BI research project. **No productization or hosted deployment.** The [project status](PROJECT_STATUS.md) is the sole current acceptance authority; the date printed inside a technical research note limits its empirical claims.

## Canonical reference documents

| Topic | Document | Purpose |
| --- | --- | --- |
| Current decision and open gates | [Project status](PROJECT_STATUS.md) | **Offline verification passed; actual BigQuery and corrected historical model evaluation pending** |
| Project entry | [Repository README](../README.md) | Goal, high-level architecture and quick start |
| Technical architecture | [Architecture and model catalog](ARCHITECTURE.md) | Grains, SQL lineage, mart ownership |
| KPI rules | [Governed KPI dictionary](KPI_DICTIONARY.md) | Time and cohort boundaries, denominators, missingness and percentage scales |
| Historical data quality | [Data quality and validation](DATA_QUALITY.md) | **June 2026** warehouse snapshot, not current source freshness |
| ML model and assumptions | [Market-value ML methodology](PLAYER_MARKET_VALUE_ML.md) | Historical v5 results, corrected chronology and release limitations |
| Native Power BI semantics | [Power BI modeling](POWER_BI_MODELING.md) | Measures, filter context and EUR / percentage interpretation |
| NEXUS style and file editions | [BI design system](BI_DESIGN_SYSTEM.md) | Editable real PBIP vs. clearly synthetic offline fixtures |
| BI source and screenshot evidence | [Power BI visual QA](POWER_BI_VISUAL_QA.md) | 13 captured screens and the as-of-date limitation |
| Desktop handling | [Power BI Desktop handoff](POWER_BI_DESKTOP_HANDOFF.md) | Actual Desktop checks and permitted refresh |
| Reproduction and operations | [Runbook](RUNBOOK.md) | Local checks, isolated Windows validation and approved data work |
| Workintech BigQuery recovery | [Isolated recovery and Power BI source plan](WORKINTECH_MIGRATION_20261027.md) | Offline source data, safe target namespaces, open authorization gates |
| Hosted workflow approvals | [Final CI release policy](CI_RELEASE_GATE_POLICY.md) | Nine-job CircleCI opt-in; separately confirmed model publication |
| Attribution | [Project-origin attribution](../README.md) | Original team participation and limitations |

## Date-scoped research and verification evidence

| Evidence | What it establishes | Limitation |
| --- | --- | --- |
| [Executed SentinelX verification — 19 Oct](SENTINELX_OFFLINE_VERIFICATION_20261019.md) | **243/243 baseline and 246/246 after structure audit**, **47/47 ML**, offline dbt parse **PASS** | Does not run dbt tests on BigQuery tables |
| [Portable Colab/Kaggle procedure](REPRODUCIBLE_OFFLINE_VERIFICATION_20261019.md) | Alternative verified-source runner and SHA-bound result JSON | Windows verification was executed; hosted Kaggle was not |
| [Transfer-key reconciliation preparation — 20 Oct](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md) | Read-only anti-join SQL, exported CSV validator, and 9 synthetic regression tests | BigQuery connection disabled; no actual historic three-key match |
| [Numeric validation — 18 Oct](ML_VALIDATION_HARDENING_20261018.md) | Fail-closed keys/targets and as-of training contracts | Model was not refit on new real data |
| [ML reliability — 18–19 Oct](ML_RELIABILITY_EVALUATION_20261018.md) | Bootstrap, finite-sample interval and fitted-predictor identity | Only offline/synthetic evidence for the corrected model |
| [Same-day valuation event grain — 19 Oct](ML_VALUATION_EVENT_GRAIN_AUDIT_20261019.md) | Canonical player-date rule and conflict exclusion policy | Actual excluded source keys/counts unknown |
| [Original research plan — 18 Oct](ANALYTICS_ENGINEERING_EXECUTION_PLAN_20261018.md) | Prioritized requirements with later status addendum | Treat its original phase descriptions as historical |
| [17 Oct Power BI image and KPI audit](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md) | 13 screenshots, static values and 365-day definition discrepancy | No new authenticated source reconciliation |
| [Screenshot captures and manifest](assets/screenshots/README.md) | Reproducible visual snapshots with source provenance | Historical captures only |
| [Archived Power BI design/incident records](archive/README.md) | **19 historical technical records** | Not current acceptance documents |

## Folder structure and maintenance rules

```text
football-player-performance-analysis/
├── models/                 # staging / intermediate / marts / ml (dbt)
├── snapshots/ tests/       # dbt snapshots, singular SQL and Python tests
├── analyses/ macros/ seeds/ # read-only SQL and dbt structural directories
├── scripts/ notebooks/    # local Python tools and optional Colab/Kaggle
├── powerbi/
│   ├── workspace/          # actual editable PBIP production source
│   └── offline-demo/       # explicitly synthetic fixture version
├── docs/
│   ├── assets/screenshots/ # historical screenshots and hashes
│   └── archive/powerbi/    # 19 retained historical audit/design notes
└── .github/ .circleci/     # GitHub manual workflows and final opt-in CI
```

1. Put **current decisions in [PROJECT_STATUS](PROJECT_STATUS.md)**; keep dated research evidence in its original file rather than duplicating old status narratives across active guides.
2. Preserve original screenshot hashes and research attribution. Do not pass a synthetic dashboard or historical June warehouse figure off as current real data.
3. Preserve the separate Power BI real-source and offline-demo editions; never move production data to synthetic fixtures.
4. Do not commit credentials, personal secrets, dbt `target/`, Python virtual environments or local runtime logs. Keep paid cloud work behind explicit approval.
5. After documentation or folder edits: run `python scripts/check_docs_integrity.py`, `python scripts/check_declared_documentation.py`, `python -m unittest discover -s tests -p 'test_*.py'`, `python scripts/check_offline_ci.py`, plus relevant PBIR checks and dbt parse. The declared-doc check covers YAML (46 models / 878 columns audited on 19 October), **not physical warehouse columns**. The physical catalog verification still requires `check_documentation_coverage.py` and a warehouse-generated `target/catalog.json`. Save exact Git SHA and results.
6. **Do not launch final hosted CI** until the authenticated BigQuery source tests and corrected real-data ML evaluation are complete; see [current gates](PROJECT_STATUS.md).

