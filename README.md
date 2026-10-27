# NEXUS Football Intelligence

**Football Player Performance Analysis | BigQuery · dbt · Python/ML · Power BI**

[![BigQuery](https://img.shields.io/badge/Warehouse-BigQuery-4285F4)](docs/ARCHITECTURE.md)
[![dbt](https://img.shields.io/badge/Transform-dbt-FF694B)](dbt_project.yml)
[![Power BI](https://img.shields.io/badge/Dashboard-Editable%20PBIP-F2C811)](powerbi/workintech-20261028/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

An end-to-end **historical football analytics** project connecting BigQuery/dbt data engineering, player and transfer analytics, time-aware market-value modeling and a 13-page editable Power BI report. The foundation is a **collaborative Workintech Data Pro team project**; subsequent work and authorship are traceable in Git history.

**Project objective — advanced noncommercial data analytics:** This repository is a professional technical/research and portfolio project, **not** a commercial software product. Success is measured by the quality of its datasets, reproducible pipelines, SQL/dbt modeling, statistically sound ML evaluation, interactive BI and clear technical explanation. Power BI Service publication, paid hosting, continuous live match feeds, commercial release approvals and service-level operations are **out of scope**, not outstanding completion requirements.

**Current Desktop edition — 28 October 2026:** Owner-reported successful testing of the **34-source, 87-relationship** Power BI model; it was reversibly promoted to the same local PBIP path with a complete backup. All **13 pages and 308 visuals** are preserved. Static and local regression checks passed, but a post-cutover Desktop run was not independently captured.

**Workintech warehouse evidence:** 46/46 dbt models, 243/243 successful dbt tests, seven ML outputs and 31/31 governed physical Power BI source contracts in the owner-authorized recovery. Three additional unique sources lie outside the 31-table contract. The archive's latest match is **6 July 2026**; there is no claim of live October fixtures.

**[Current verified status](docs/PROJECT_STATUS.md)** · **[34-source PBIP](powerbi/workintech-20261028/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip)** · **[Docs](docs/README.md)** · **[27 October genuine screenshots](docs/assets/screenshots/README.md)** · **[Local cutover and rollback](docs/WORKINTECH_PRODUCTION_PROMOTION_20261028.md)**

![Nine genuine Power BI report pages captured 27 October 2026](docs/assets/screenshots/NEXUS_Football_Page_Gallery.png)

## Project origin — Workintech team project

**This is a collaborative training project developed with a team during the Workintech Data Pro program, not a solo-authored portfolio project.** The repo's foundation also incorporates earlier collaborative/upstream dbt work. The current fork documents subsequent extensions in its analytics models, semantic layer, Power BI reporting, validation, and player-market-value research. Treat those as **repository-level outputs**, not an assertion that one person created every component.

Attribution and historical model provenance are established by the repository's upstream Git history, contributor commits and the collaborative-project statement above. The 27 October Power BI screenshots are historical captures; the owner subsequently accepted the existing visual workstream, but an authenticated post-refresh metric audit remains outstanding.

## What the project delivers

| Component | Scope |
|---|---|
| Data engineering | Transfermarkt raw data on BigQuery, dbt staging and intermediate models, analytics marts, snapshots, data quality |
| Football analytics | Player performance, positional cohorts, club/league comparisons, transfer-value and 365-day observed outcomes |
| Machine learning | Player market-value estimation with time-aware features and a previous-value persistence benchmark |
| Interactive BI | 9 presentation pages, 2 hidden drillthrough detail pages, 2 tooltip pages in editable PBIP/PBIR format |
| Presentation | NEXUS midnight/navy design, cyan and lavender accents; verifiable real Desktop PNGs |

The repository extends earlier collaborative work; project contributions and historical authorship must be read from upstream and current Git commit history. The football dataset remains subject to the [source data license and terms](https://www.kaggle.com/datasets/davidcariboo/player-scores).

## Power BI dashboard screenshots

The visuals below are cropped **actual Windows Power BI Desktop captures**; they are not regenerated charts or synthetic offline-demo images.

| Player performance | Player segmentation |
|---|---|
| [![Performance](docs/assets/screenshots/production/02_player_performance.png)](docs/assets/screenshots/production/02_player_performance.png) | [![Segmentation](docs/assets/screenshots/production/03_player_segmentation.png)](docs/assets/screenshots/production/03_player_segmentation.png) |
| **Per-90 ranking, goals/assists and player comparison** | **Position, age and market-value cohorts** |

| Observed transfer outcomes (365 days) | Transfer and market value |
|---|---|
| [![Transfer outcomes](docs/assets/screenshots/production/05_transfer_success.png)](docs/assets/screenshots/production/05_transfer_success.png) | [![Transfer analysis](docs/assets/screenshots/production/06_transfer_market.png)](docs/assets/screenshots/production/06_transfer_market.png) |
| **Eligible outcomes, follow-up coverage and observed rates** | **Fees, premiums, transfers and valuation distributions** |

| Player market-value prediction | ML model reliability |
|---|---|
| [![Prediction](docs/assets/screenshots/production/07_market_value_prediction.png)](docs/assets/screenshots/production/07_market_value_prediction.png) | [![Reliability](docs/assets/screenshots/production/08_ml_reliability.png)](docs/assets/screenshots/production/08_ml_reliability.png) |
| **Published valuation estimates and quality segmentation** | **Feature diagnostics, segment metrics and model-quality gates** |

Browse [the current gallery and all 13 hash-verified original screenshots](docs/assets/screenshots/README.md), including Home, Club & League, Closing, two unselected-player detail states and two technical tooltips. The visible fee premium M% error, tooltip currency scaling, and residual legend/table truncation remain documented defects.

### Source editions

| Edition | Editable report | Usage |
|---|---|---|
| **28 October — owner-accepted Desktop source** | [34-source Workintech PBIP](powerbi/workintech-20261028/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip) | 87 relationships, 13 pages, 308 visuals, full rollback available |
| 27 October — pre-dedup historical source | [65-source PBIP](powerbi/workintech-20261027/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip) | Previous model edition preserved |
| Earlier production-connected | [Prior PBIP](powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip) | Historical data-analiz-490513 edition, preserved |
| Offline regression demo | [`powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`](powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip) | Explicitly **synthetic data**, never evidence of actual player outcomes |

The repository publishes PBIP/PBIR source, **not** a publicly hosted live Power BI Service report. Observed 365-day transfer success is **not** an ML prediction; coverage, cohort definitions and horizon are material to interpretation.

## Architecture

```mermaid
flowchart LR
    A[Transfermarkt source] --> B[BigQuery raw]
    B --> C[dbt staging]
    C --> D[dbt intermediate]
    D --> E[dbt marts]
    E --> F[Power BI PBIP]
    E --> G[ML feature marts]
    G --> H[Python train and validate]
    H --> I[Prediction marts]
    I --> F
    C --> J[Historical snapshots]
```

The 27 October owner-executed Workintech build completed 12 staging, 7 intermediate, 25 marts and 2 ML preparation models (46 in total), with 243 passing dbt tests. That does not make archived match events current. See the [model catalog, lineage and source contracts](docs/ARCHITECTURE.md).

## Market-value modeling and limitations

A previous-value persistence baseline is essential: predicting the next valuation **level** can achieve a high R² even when the change is difficult to predict. The project evaluates chronology-aware features and quality cohorts rather than claiming that fit on levels proves market forecasting ability.

| Historical v5 evaluation | Ensemble | Previous-value baseline |
|---|---:|---:|
| MAE (EUR) | 781,409 | 867,156 |
| RMSE (EUR) | 2,039,156 | 2,248,309 |
| R² (value level) | 0.9756 | 0.9704 |
| WAPE | 12.51% | 13.88% |

*Historical evaluation reproduced from the project's documentation, not a fresh test performed during the October 2026 screenshot capture.* See [methodology and temporal leakage controls](docs/PLAYER_MARKET_VALUE_ML.md).

Related research: [Kaggle market-value baseline notebook](https://www.kaggle.com/code/senanuretin/your-market-value-r2-is-mostly-last-year-s-price) and [Hugging Face model card](https://huggingface.co/senanurcetin/transfermarkt-value-change-lgbm).

## Reproduction

Requires Python 3.10+, an authorized Google Cloud BigQuery environment, the source datasets, and compatible Power BI Desktop for PBIP editing.

```bash
python -m pip install -r requirements.txt
# Configure profiles.yml.example under ~/.dbt/profiles.yml (do not commit secrets)
dbt debug
dbt source freshness --selector raw_sources
dbt build
dbt test
```

To validate the market-value pipeline, with data credentials and training dependencies set up:

```bash
python -m pip install -r requirements-ml.txt
# Run with an authorized Google Cloud project and suitable ADC credentials.
# The following may create local artifacts and query billed BigQuery data.
python scripts/train_player_market_value.py --project-id YOUR_GCP_PROJECT
python scripts/verify_ml_artifact.py
# Run only after governed ML tables have been explicitly published.
python scripts/verify_published_ml_outputs.py --project-id YOUR_GCP_PROJECT
```

Offline source checks and screenshot artifact integrity:

```bash
python scripts/check_powerbi_project.py
python scripts/check_declared_documentation.py  # YAML declarations only, not physical BigQuery columns
python scripts/check_powerbi_offline_demo.py
python scripts/audit_powerbi_visuals.py
python scripts/audit_powerbi_layout.py
python scripts/verify_dashboard_screenshots.py
python -m unittest discover -s tests
```

**Verification boundary:** Static tests validate source and stored screenshots; they do not certify current BigQuery data or Power BI interactions. The **18–19 October 2026 documentation audit** removed obsolete product/portfolio/CI-recovery handoffs, created [KPI contracts](docs/KPI_DICTIONARY.md), and reconciled actual CI workflow triggers in the [runbook](docs/RUNBOOK.md). Historical screenshot values were checked but the three-row 365d discrepancy and full runtime acceptance remain open. No productization or public deployment is planned. See the [runbook](docs/RUNBOOK.md) and [visual QA requirements](docs/POWER_BI_VISUAL_QA.md).

## Repository structure

```text
.
├── .circleci/                # CI configuration
├── .github/                  # Repository workflows and collaboration
├── analyses/                 # Analytical SQL
├── docs/
│   ├── assets/screenshots/   # Genuine Desktop captures, curated gallery and SHA-256 evidence
│   ├── ARCHITECTURE.md
│   ├── BI_DESIGN_SYSTEM.md
│   ├── PLAYER_MARKET_VALUE_ML.md
│   └── RUNBOOK.md
├── macros/                   # dbt macros
├── models/                   # Staging, intermediate, mart and ML models
├── powerbi/
│   ├── workintech-20261028/  # Accepted 34-source Desktop PBIP
│   ├── workintech-20261027/  # Historical 65-source source PBIP
│   ├── workspace/            # Older BigQuery-backed PBIP
│   └── offline-demo/         # Synthetic regression fixture
├── scripts/                  # ML training, preflight, asset verification
├── seeds/                    # Reference seeds
├── snapshots/                # Historical dimension snapshots
├── tests/                    # dbt and Python quality tests
├── dbt_project.yml
└── profiles.yml.example
```

Diagnostic Power BI caches and temporary local scripts are excluded from source control. Registered report images under `powerbi/**/StaticResources/` remain because deleting them can break the native PBIR report.

## Advanced analytics project status

- [x] Editable NEXUS production PBIP and separate synthetic test edition retained.
- [x] 13 genuine report-area PNG captures, including nine fully rendered presentation views.
- [x] Nine NEXUS-framed portfolio images and a consolidated gallery.
- [x] Real-capture provenance, hashes and automated screenshot integrity checks.
- [x] Owner confirmed the tested 34-source Desktop report worked; its source was reversibly promoted and checked.
- [x] Advanced data-engineering, historical analytics, model-development and Power BI reporting components implemented and documented.
- [ ] Recommended analytical validation: independently reconcile priority Power BI KPI measures with BigQuery and test selected-player filter/drillthrough behavior.
- [ ] Recommended ML research hardening: reproduce model quality on a fresh authorized chronological holdout with baseline and subgroup comparisons.

**Not project requirements:** commercial certification, Power BI Service scheduled refresh, live match ingestion or hosted CI. These would belong to a separate deployment project, not to the present noncommercial analytics goal.

**Quality rule:** Do not turn successful source tests or historical screenshots into unsupported claims of a current live deployment.

## Documentation and contribution

[Documentation index](docs/README.md) · [Screenshot evidence](docs/assets/screenshots/README.md) · [Architecture](docs/ARCHITECTURE.md) · [Data quality](docs/DATA_QUALITY.md) · [ML model](docs/PLAYER_MARKET_VALUE_ML.md) · [Power BI modeling](docs/POWER_BI_MODELING.md) · [BI design](docs/BI_DESIGN_SYSTEM.md) · [Operations](docs/RUNBOOK.md) · [Contributing](CONTRIBUTING.md) · [MIT license](LICENSE)

### GitHub-hosted BigQuery access preflight

Repository workflows already reference Google Cloud project `data-analiz-490513` and the `GCP_SERVICE_ACCOUNT_JSON` GitHub secret. A new [manual metadata-only GitHub Actions preflight](.github/workflows/bigquery-readonly-preflight.yml) can check whether that identity can read the `football_mart` transfer-table metadata **without any SQL queries or model publication**. Merely having the workflow or a secret reference is not successful authentication; BigQuery reconciliation, historical ML retesting, Desktop refresh and final CircleCI remain separately gated.
