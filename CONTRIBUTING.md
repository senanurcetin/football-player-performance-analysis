# Contributing

Thank you for considering a contribution to this project. This document covers the conventions and workflow used to keep the codebase consistent and the CI green.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Branch Conventions](#branch-conventions)
- [Commit Messages](#commit-messages)
- [dbt Model Standards](#dbt-model-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Requirements](#documentation-requirements)
- [Pull Request Process](#pull-request-process)

---

## Getting Started

```bash
git clone <repo-url>
cd football-analyze
pip install -r requirements.txt
cp profiles.yml.example ~/.dbt/profiles.yml   # fill in your credentials
dbt debug
dbt build --select path:models/staging
```

All commands are documented in [docs/RUNBOOK.md](docs/RUNBOOK.md).

---

## Branch Conventions

| Prefix | Use case |
|---|---|
| `feat/` | New model, new dashboard page, new ML feature |
| `fix/` | Bug fix in existing logic |
| `refactor/` | Non-breaking restructure with no behavior change |
| `docs/` | Documentation-only changes |
| `ci/` | Workflow or automation changes |
| `chore/` | Dependency bumps, tooling, seed updates |

Example: `feat/fct-player-rolling-form-v2`

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) spec:

```
<type>(<scope>): <short imperative description>
```

| Type | When to use |
|---|---|
| `feat` | New model, metric, or page |
| `fix` | Correcting incorrect logic or test |
| `docs` | README, ARCHITECTURE, or docstring update |
| `refactor` | Code restructure without behavior change |
| `test` | Adding or modifying data tests |
| `ci` | GitHub Actions workflow changes |
| `chore` | Tooling, dependency, or config change |

Examples:
```
feat(marts): add fct_player_rolling_form model
fix(ml): correct leakage in prior_valuation join window
docs(runbook): add BigQuery Storage API troubleshooting section
```

---

## dbt Model Standards

### Naming

- Staging: `stg_<source_entity>` — one source table, one staging model
- Intermediate: `int_<entity>_<action>` — reusable aggregation or join
- Mart: `fct_<entity>_<subject>` or `dim_<entity>` — analytics-ready grain
- ML: `ml_<entity>_<purpose>` — training or scoring features

### Configuration

All mart models must declare:

```yaml
config:
  partition_by:
    field: <date_field>
    data_type: date
    granularity: year
  cluster_by: [<high-cardinality-join-keys>]
```

### Style

- One CTE per logical step; name CTEs after what they produce, not what they do
- Use `safe_divide()` for all division — never raw `/`
- Use `coalesce(..., nullif(..., 0))` pattern for display fallbacks
- All monetary fields use BigQuery `NUMERIC`
- Boolean columns follow `is_*` or `has_*` naming convention

---

## Testing Requirements

Every new model must include:

- `not_null` and `unique` on the primary key
- At least one grain assertion (`assert_<model>_grain.sql`) for fact tables
- A row-count reconciliation against its source when one exists

ML models additionally require:

- `assert_ml_features_precede_target` — no future data in features
- `assert_ml_scoring_readiness` — all required fields present

Run the full test suite before opening a PR:

```bash
dbt test
```

---

## Documentation Requirements

CI enforces 100% documentation coverage. Every new model and every new column must have a description in `schema.yml`.

Format:

```yaml
models:
  - name: fct_example
    description: "One-sentence grain statement. One-sentence purpose."
    columns:
      - name: example_id
        description: "Surrogate key — MD5 hash of (player_id, date)."
        tests:
          - not_null
          - unique
```

---

## Pull Request Process

1. Open a PR against `main`
2. Fill in the PR template completely
3. Ensure all CI checks pass (dbt build, tests, documentation coverage)
4. At least one reviewer approval is required before merging
5. Squash-merge with a conventional commit title

Do not merge if:
- Any test is failing
- Any model or column lacks documentation
- The `dbt source freshness` check is erroring
