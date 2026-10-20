# Operations Runbook

> **Updated 19 October 2026:** SentinelX independently executed full Python **243/243 baseline, 246/246 post-cleanup, and 249/249 after the declared-doc gate PASS**, the nine-phase offline runner and nonauthenticated dbt parse. These are **real source test results**, not proof of authenticated BigQuery freshness or historical model accuracy. See [executed evidence](SENTINELX_OFFLINE_VERIFICATION_20261019.md) and [current project status](PROJECT_STATUS.md).

## Purpose

This runbook describes safe, reproducible **analytics-engineering development, validation and documentation** of the dbt/ML project. It does not authorize productization, public publishing, or paid cloud processing.

**Operating state (18 October 2026):** GitHub `dbt CI` is `workflow_dispatch`-only and additionally requires `ENABLE_GITHUB_ACTIONS_CI=true`; its cloud validation requires `ENABLE_BIGQUERY_CI=true` and BigQuery credentials. CircleCI jobs are gated by `run_final_ci=true` and are final-stage opt-in. **Updated 19 October 2026:** GitHub `ML Production` no longer has a weekly schedule. It is manual dispatch only and additionally requires both `ENABLE_ML_PRODUCTION=true` as a repository variable and `confirm_final_release=true` on the actual dispatch. On 19 October at 10:26 UTC an earlier **scheduled** workflow attempted to run but failed at the `GCP_SERVICE_ACCOUNT_JSON` nonempty check, before dbt, model fitting or publishing. This was independently verified in GitHub job steps. The failed workflow is not a release or a data-quality PASS.

## Prerequisites

- Python 3.10+
- `dbt-bigquery` 1.11.1
- Google Cloud service account with BigQuery job and dataset permissions
- Raw tables loaded into `football_raw`
- BigQuery processing location matching the source datasets

## Security Rules

- Never commit a service account JSON file.
- Keep `profiles.yml` outside the repository or in an ignored local directory.
- Do not place credentials in SQL, YAML model files, README files, logs, or GitHub issues.
- Use separate development and production targets when multiple environments are available.

Install the pinned adapter:

```bash
pip install -r requirements.txt
```

## Profile Example

```yaml
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: "{{ env_var('DBT_PROJECT_ID') }}"
      dataset: "{{ env_var('DBT_DATASET', 'football') }}"
      keyfile: "{{ env_var('DBT_KEYFILE') }}"
      threads: 4
      location: EU
```

Copy `profiles.yml.example` outside the repository and set `DBT_PROJECT_ID`, `DBT_KEYFILE`, and optionally `DBT_DATASET` and `DBT_SOURCE_DATABASE`.

## First-Time Validation

```bash
dbt --version
dbt debug
dbt parse
dbt source freshness --selector raw_sources
```

Expected outcome:

- BigQuery connection succeeds.
- The project parses without errors.
- All sources and models are discovered.

## Build Commands

### Full Build

Build all models and run their tests:

```bash
dbt build
```

### Type-2 Snapshots

Capture changing player and club profile attributes:

```bash
dbt snapshot
```

Snapshots are written to `<base>_snapshots`. The **manually gated** `dbt CI` YAML includes steps for snapshot prerequisites only if the event type is a pull request; the workflow currently registers only `workflow_dispatch`, so these PR-specific steps are **not automatically exercised**. Do not describe the source configuration as proof that isolated PR datasets or cleanup actually ran. Capture successful BigQuery execution logs separately.

### Source Freshness

```bash
dbt source freshness --selector raw_sources
```

Freshness is based on BigQuery table last-modified metadata. It warns after 7 days and errors after 14 days.

### Player Market Value ML

Build and validate the leakage-safe ML feature table:

```bash
dbt build --select tag:ml
```

Install the local zero-cost training dependencies and run the time-based evaluation:

```bash
pip install -r requirements-ml.txt
python scripts/train_player_market_value.py \
  --project-id YOUR_GCP_PROJECT_ID \
  --credentials /absolute/path/to/service-account.json \
  --publish-predictions-table ml_player_market_value_evaluation_predictions \
  --publish-current-predictions-table ml_player_market_value_current_predictions \
  --publish-evaluation-metrics-table ml_player_market_value_evaluation_metrics \
  --publish-drift-table ml_player_market_value_feature_drift \
  --publish-model-registry-table ml_player_market_value_model_registry \
  --publish-feature-importance-table ml_player_market_value_feature_importance \
  --publish-quality-gates-table ml_player_market_value_quality_gates
```

Local model artifacts and prediction CSV files are written under `artifacts/player_market_value/` and are intentionally excluded from Git. The published BigQuery tables support evaluation, current estimates, segment metrics, drift monitoring, and model-version audit history.

Before a Power BI refresh, confirm that `assert_ml_scoring_readiness` passes, review `ml_player_market_value_feature_drift`, and filter decision-facing predictions to `prediction_quality_status in ('high', 'medium')`. Limited-quality rows intentionally publish the governed baseline fallback and belong on the data-quality page.

The pipeline validates all blocking release gates before publishing any prediction table. The GitHub Actions `ML Production` workflow was changed on 19 October 2026 to **manual dispatch only with double confirmation**, not a weekly schedule. **Do not trigger it for documentation or pre-release test review**: it builds warehouse models and may publish tables. Running it requires explicit data permissions, budget approval, and separate release-gate acceptance. Documentation and offline source tests should run first.

Verify a local or downloaded governed artifact with:

```bash
python scripts/verify_ml_artifact.py
```

Verify published BigQuery outputs and cross-table model-version consistency with:

```bash
python scripts/verify_published_ml_outputs.py \
  --project-id YOUR_GCP_PROJECT_ID \
  --dataset football_ml \
  --credentials /absolute/path/to/service-account.json
```

### Layer Builds

```bash
dbt build --select path:models/staging
dbt build --select path:models/intermediate
dbt build --select path:models/marts
dbt build --selector marts_with_upstream
```

### Tests Only

```bash
dbt test
dbt test --select path:models/marts
```

### Generate dbt Documentation

```bash
dbt docs generate
dbt docs serve
```

Generated files under `target/` are local artifacts and should not be committed.
After generation, `python scripts/check_documentation_coverage.py` verifies that every model and physical model column has a description. Without BigQuery or a generated `target/catalog.json`, run `python scripts/check_declared_documentation.py` to check source SQL/YAML descriptions (46 models and 878 declared columns at the 19 October audit). **Offline declared coverage is not physical warehouse coverage**, so the catalog-based gate remains open.

**Kaggle update, 19 October 2026:** Use `notebooks/nexus_football_offline_verification.ipynb` with CPU and Internet enabled; the report runner now rejects missing or mismatched full commit SHAs. A valid test report must include `source_commit_verification.status=passed` in addition to `overall_status=PASS`. See [Kaggle instructions](REPRODUCIBLE_OFFLINE_VERIFICATION_20261019.md).

## Executed Windows offline verification — 19 October 2026

A connected SentinelX Windows agent successfully cloned the latest `main` into an isolated directory, installed the pinned dependencies in a dedicated Python 3.13.14 virtual environment, and ran the **entire Python suite (243/243 PASS)**, ML tests (47/47 PASS), documentation and YAML/Jinja validators, ML synthetic smoke and a **credential-free dbt parse**. The [dated evidence report](SENTINELX_OFFLINE_VERIFICATION_20261019.md) records source SHA, counts and remaining authentication gaps. These local tests **do not** validate source warehouse freshness or current model metrics; leave Power BI and hosted CI gated until those checks are resolved.

## Quota-free independent CPU verification

When Desktop Commander is unavailable, use the [Colab/Kaggle verification notebook](../notebooks/nexus_football_offline_verification.ipynb) and [offline runbook](REPRODUCIBLE_OFFLINE_VERIFICATION_20261019.md). In an independent CPU checkout, execute `python scripts/run_offline_verification.py --phases source ml` and, only if green, `--phases full`. Keep the generated SHA-tagged JSON reports. The workflow does not execute BigQuery, hosted CI or model publication, and cloud-source verification still requires an authorized separate run.

## Research validation and controlled integration

Local source checks should not cause a paid BigQuery build. From a complete checkout and a suitable Python environment:

```bash
python -m compileall -q scripts
python scripts/check_docs_integrity.py
python scripts/check_declared_documentation.py
python scripts/check_offline_ci.py
python -m unittest discover -s tests
python scripts/check_powerbi_project.py
python scripts/verify_dashboard_screenshots.py
git diff --check
```

For the new ML research work, use the additional **synthetic offline** checks:

```bash
python -m unittest discover -s tests -p 'test_ml_numeric_contract.py' -v
python -m unittest discover -s tests -p 'test_ml_reliability.py' -v
python -m unittest discover -s tests -p 'test_evaluate_ml_artifacts.py' -v
python -m unittest discover -s tests -p 'test_walk_forward_research.py' -v
python scripts/check_ml_pipeline.py
```

Model artifact evaluation on **real historical exported data** is a distinct task: consult [ML reliability methodology](ML_RELIABILITY_EVALUATION_20261018.md) and keep outputs under ignored `artifacts/`. Never report synthetic-fixture test output as football forecasting skill.

Review/commit changes to a **feature branch** and use a reviewed pull request, rather than directly pushing `main`. The historical numeric-validation PR #78 and research/BI-audit PR #79 were merged in that order on **19 October 2026**. Both merge commits used `[skip ci]` without intentionally launching hosted CI. Future changes should still use reviewed feature branches; preserve the final CI opt-in policy. Source integration does **not** mean that authenticated warehouse/Power BI acceptance passed.

Authenticated dbt commands (`dbt source freshness`, `dbt snapshot`, `dbt build`, `dbt docs generate`) are **separate, permissioned, potentially billable** warehouse operations, not prerequisite calls to run uncredentialed Markdown checks. Run them only against the intended environment once access, budget and source provenance are established.

## Hosted CI: what the repository actually configures

The actual `.github/workflows/dbt-ci.yml` is **manual dispatch only**, not a daily, push-triggered or PR-triggered workflow. The `offline-preflight` job is disabled unless `ENABLE_GITHUB_ACTIONS_CI=true`; its `validate` job additionally requires `ENABLE_BIGQUERY_CI=true` and the authorized `GCP_SERVICE_ACCOUNT_JSON` secret. Because the present event is manual, any SQL branch conditioned on `github.event_name == 'pull_request'` must **not** be described as having run.

The separate `.github/workflows/ml-production.yml` allows **only manual dispatch**, gated by `ENABLE_ML_PRODUCTION=true` and per-run `confirm_final_release=true`. This pipeline may incur BigQuery charges and publish artifacts and must run **only after all model, warehouse, Power BI and final CI reviews are approved**. It is distinct from the `dbt CI` and CircleCI test gates.

`.circleci/config.yml` sets `run_final_ci=false` by default and guards all nine jobs behind an explicit final opt-in. See the [canonical CI policy](CI_RELEASE_GATE_POLICY.md). Credentials must be stored only in authorized GitHub secrets or local ignored files, never checked into Markdown/YAML. Treat untriggered or skipped jobs as **NOT RUN**, not PASS.

## Validation Checklist

- `dbt debug` succeeds.
- `dbt source freshness --selector raw_sources` passes.
- `dbt build` completes with no errors.
- `dbt snapshot` succeeds and `assert_snapshot_history_validity` passes.
- `dbt build --select tag:ml` passes all ML feature and readiness tests.
- The latest model registry row exists and current predictions contain no invalid intervals or negative values.
- Every blocking row in `ml_player_market_value_quality_gates` passes.
- `artifact_manifest.json` contains the model checksum, feature-contract hash, source commit, and runtime versions.
- Significant PSI drift and `limited` predictions are reviewed before BI refresh.
- `fct_data_coverage_bias` and `fct_analytics_refresh_audit` are reviewed before decision-facing BI refresh.
- `dbt test` completes with no warnings or errors.
- Mart row coverage tests pass.
- Fact-to-dimension relationship tests pass.
- Source reconciliation tests pass.
- `git diff --check` reports no formatting errors.
- No credentials or generated `target/` artifacts are staged.
- dbt docs generation succeeds and all staging, intermediate, and mart columns remain documented.
- `python scripts/check_documentation_coverage.py` passes.

## Troubleshooting

### BigQuery Location Error

Ensure the profile `location` matches the raw and target datasets. The validated environment uses `EU`.

### Source Not Found

Check:

- The `DBT_SOURCE_DATABASE` environment variable
- The raw dataset name `football_raw`
- Service account dataset permissions

### Unexpected Relationship Failures

Run the relevant staging and dimension models before the facts:

```bash
dbt build --select path:models/staging
dbt build --select path:models/intermediate
dbt build --select path:models/marts
```

Historical players and clubs should be retained by `dim_players` and `dim_clubs`; a new orphan normally indicates a newly introduced source path that must be included in the appropriate dimension.

### Floating-Point Reconciliation Failure

Business metrics are rounded to two decimal places. Tests normalize these fields to BigQuery `NUMERIC` before exact comparison. New floating metrics should follow the same pattern.

### Raw Data Quality Changes

Consult [Data Quality](DATA_QUALITY.md). Missing raw values are acceptable only when documented and intentionally preserved. A new test failure should not be suppressed without understanding the upstream change.

### Freshness Warning or Error

Confirm whether the raw ingestion job ran and inspect the BigQuery table last-modified timestamps. Do not replace metadata freshness with game, transfer, or valuation business dates.

## Read-only 365d transfer-key audit (prepared 20 October 2026)

After BigQuery credentials and query budget are authorized, compile [the key-level SELECT](../analyses/audit_transfer_365d_row_level_20261020.sql) through dbt with `pbi_capture_as_of_date: "2026-10-17"`. Execute the compiled query in an authenticated read-only session and export the mismatch rows as CSV. Record BigQuery job ID, bytes billed, warehouse modification time, source snapshot, capture date, BI refresh timestamp and all page/slicer filters. No scripts in this step should write any warehouse tables.

Validate the returned CSV offline:

```bash
python scripts/validate_transfer_365d_reconciliation.py   --input /path/to/authorized-transfer-key-export.csv   --capture-date 2026-10-17   --output artifacts/transfer_365d_key_audit.json
```

Compare that result to the [grouped summary query](../analyses/audit_transfer_365d_capture_20261018.sql) under equivalent source/filter conditions. A successful CSV validation is not a source freshness, full-population, or historical screenshot approval. If the original source snapshot is unavailable, record HISTORICAL NOT REPRODUCIBLE. Synthetic offline test: `python -m unittest discover -s tests -p 'test_transfer_365d_key_reconciliation.py' -v`.
