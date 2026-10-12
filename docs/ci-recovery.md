# CI and cloud validation

GitHub is the canonical repository. CircleCI runs the credential-free
checks in `.circleci/config.yml`. The same lightweight dbt source checks
are available in the GitHub `dbt CI / offline-preflight` job.

## Automatic and credential-free checks

The preflight validates YAML and Jinja syntax of dbt source files and
compiles Python scripts. The separate CircleCI ML job executes the
synthetic-data model/quality-gate smoke test
(`python scripts/check_ml_pipeline.py`).

These tests need no GCP project access, cannot modify cloud data, and
do not claim to have run dbt models or confirmed BigQuery freshness.

For local reproduction:

```bash
python -m pip install PyYAML==6.0.3 Jinja2==3.1.6
python -m compileall -q scripts
python scripts/check_offline_ci.py
python -m pip install -r requirements-ml.txt
python scripts/check_ml_pipeline.py
```

## Opt-in authenticated dbt / documentation

Previously both workflows failed at the first credential setup step,
because `GCP_SERVICE_ACCOUNT_JSON` was empty. This is a repository
configuration failure, not a dbt model validation failure.

To enable cloud checks, set a GitHub Actions repository secret named
`GCP_SERVICE_ACCOUNT_JSON` containing the intended, minimally scoped
BigQuery service-account JSON. Then set the Actions repository variable
`ENABLE_BIGQUERY_CI=true`. Only after both are configured will the
existing authenticated dbt validation and Pages build execute on their
configured triggers.

For security, do not commit or paste the service-account JSON into the
repository, a CircleCI YAML file, issues or logs. Rotate credentials if
previously disclosed.

Cloud workflows retain the existing data-access, snapshot and
documentation checks. They are *skipped*, not passed, until explicitly
enabled. Periodic source freshness also requires cloud credentials.

The CircleCI jobs only read checked-out source and install public Python
dependencies. If CircleCI GitHub OAuth is authorized but a repository
does not show pipelines, verify that the individual repository was
selected under CircleCI projects and that the active organization/VCS
integration allows pipeline triggers. GitHub commit checks are not proof
of CircleCI execution when no CircleCI check run has been reported.

## Cost and validation policy

Keep fast static checks mandatory; never replace cloud validation with
a fake credential or silently green failed dbt runs. Expensive
BigQuery-backed builds and docs publishes are opt-in, and their absence
must remain visible in release decisions.
