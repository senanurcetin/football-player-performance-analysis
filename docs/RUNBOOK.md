# Operations Runbook

## Purpose

This runbook describes how to configure, validate, build, and publish the dbt project safely.

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

Snapshots are written to `<base>_snapshots`. CI builds staging prerequisites before PR snapshots, runs snapshot validity tests during the full build, and deletes temporary staging, intermediate, mart, ML, and snapshot datasets after every PR validation.

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

The pipeline validates all blocking release gates before publishing any prediction table. Run the GitHub Actions `ML Production` workflow for the governed production path; it runs weekly on Monday at 05:00 UTC and can also be started manually.

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
After generation, `python scripts/check_documentation_coverage.py` verifies that every model and physical model column has a description.

## Deployment Procedure

Deployment has two explicit parts:

1. Build the dbt models in BigQuery.
2. Publish the validated code to GitHub.

Recommended sequence:

```bash
dbt source freshness --selector raw_sources
dbt snapshot
dbt build
dbt docs generate
git diff --check
git status
git add --all
git commit -m "describe the change"
git push origin main
```

Do not push a model change when `dbt build` or required tests fail.

## GitHub Actions

The `dbt CI` workflow runs:

- Daily metadata freshness checks
- Daily and production Type-2 snapshot capture
- Full production build and docs generation after a push to `main`
- Full pull-request validation in isolated temporary BigQuery datasets
- Automatic pull-request dataset cleanup

Configure the repository Actions secret `GCP_SERVICE_ACCOUNT_JSON` with the complete service account JSON document. The workflow never prints the secret.

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
