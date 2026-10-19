# NEXUS Football Intelligence — independently executed offline verification

**Execution date:** 19 October 2026. **Source revision:** `e84632af9aee1a3552a6d1904aa645ec1adc7a65` (`main` at verification time). **Operator context:** SentinelX-connected Windows host, separate GitHub checkout under an agent-controlled workspace. The user's earlier checkout was not edited. **No productization.**

## Verified results

| Gate | Execution | Result |
| --- | --- | --- |
| Git checkout and provenance | Fresh, shallow `main` clone from public GitHub; git worktree clean; exact 40-character SHA independently read | **PASS** |
| Python runtime | Dedicated virtual environment, Python 3.13.14; pinned `requirements.txt` and `requirements-ml.txt` installed | **PASS** |
| Python source syntax | `python -m compileall -q scripts tests` | **PASS** |
| Offline YAML/Jinja source check | `scripts/check_offline_ci.py`: 11 YAML and 54 SQL/Jinja source files | **PASS** |
| Documentation integrity | `scripts/check_docs_integrity.py` — zero missing Markdown targets, broken anchors, missing headings or invalid Unicode | **PASS** |
| ML regression suite | `python -m unittest discover -s tests -p 'test_ml_*.py' -v` | **47/47 PASS** |
| Full Python unit suite | `python -m unittest discover -s tests -p 'test_*.py' -v` | **243/243 PASS** |
| ML synthetic pipeline smoke | `scripts/check_ml_pipeline.py` | **PASS** |
| Formal portable offline runner | `scripts/run_offline_verification.py --phases source ml full --expected-commit <SHA>` | **PASS**, all nine checks; exact commit match |
| dbt project parse | `dbt parse --no-partial-parse` with temporary **non-credentialed placeholder BigQuery profile** | **PASS**, dbt core 1.12.6, BigQuery adapter 1.11.1 |
| dbt registration inventory | Generated local `target/manifest.json` inspected | **46 models, 2 snapshots, 8 analyses, 243 registered dbt tests** |
| Critical dbt source tests registered | `assert_ml_training_asof_integrity`, `assert_ml_scoring_asof_integrity`, `assert_ml_training_row_coverage` | **3/3 present**, **NOT executed as BigQuery tests** |
| Saved screenshot files | `scripts/verify_dashboard_screenshots.py` | **PASS**, 13 recorded PNG captures (9 main, 2 detail, 2 tooltip) |
| Power BI structural preflight | `scripts/check_powerbi_project.py` | **PASS**, **not** a live Desktop acceptance |

The user previously accepted Power BI; no Desktop interaction or live warehouse report refresh was attempted in this source-first validation. The Python test suite contains offline/synthetic and contract fixtures. Passing them does **not** measure current football market-value model accuracy or prove latest warehouse freshness.

## Reproduction and evidence boundaries

On the Windows SentinelX host, the source code was checked out to an isolated workspace directory (not the original owned Git checkout). A separate Python virtual environment was installed using project-pinned requirements; generated local `target/` manifests, test logs, and the portable JSON report remain **local verification evidence**. These outputs were not copied into the public repository because they contain machine-specific execution paths and are not necessary for source reproduction.

The formal report includes `commit_sha=e84632af9aee1a3552a6d1904aa645ec1adc7a65`, `overall_status=PASS` and nine individually successful source/ML/full checks. The full unit test result was independently checked and reports `Ran 243 tests ... OK`.

The dbt parse used a **dummy, nonauthenticated profile**, so it validated source/model compilation structure **without** BigQuery connection, remote table reads, permissions or usage costs. The SentinelX agent account has **zero active `gcloud` authenticated accounts** and no configured default project. The user account's data credentials were not read, copied, or impersonated.

## Acceptance work deliberately deferred

1. **Warehouse read-only verification — BLOCKED/NOT RUN.** Authorized BigQuery project/account required to inspect fresh source dates, actual model-table grains, 365-day row coverage and the amended canonical-valuation exclusion counts, then run dbt singular tests against real data. No query or table mutation was attempted.
2. **Empirical historical model verification — NOT RUN.** After verified warehouse export, rerun the corrected time-based train/tune/calibrate/holdout logic and persistence baselines, stratified error/interval coverage, player-group bootstrap, and rolling-origin research. Previous historical model scores cannot be promoted as results from changed source code.
3. **Power BI — USER ACCEPTANCE ALREADY GIVEN.** The recorded screenshot and PBIP source structural checks passed. Actual post-refresh source KPI reconciliation is deferred until the warehouse is verified; no new Desktop runtime acceptance is claimed.
4. **Final hosted CI — NOT RUN.** User requested single final opt-in only after source, warehouse, model and BI gates. The independent ML production workflow remains manual and double-opt-in to avoid billable scheduled jobs.

**Project release decision: REVIEW PENDING.** The previously blocked **offline Python/source/dbt parse gate is now verified for the exact tested commit**. This alone does not authorize model publication or production release.
