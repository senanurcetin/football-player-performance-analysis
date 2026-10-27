# NEXUS Football Intelligence — current verification status

**POST-RECONSTRUCTION RELEASE AUDIT (27 October):** [Autonomous Workintech quality gate](WORKINTECH_AUTONOMOUS_QUALITY_GATE_20261027.md) identified 31 duplicate imports, 3 additional data-source tables, two orphan appearance-player references and planned/future transfers requiring explicit semantics. Release remains on hold pending semantic reconciliation and end-to-end validation; no new screenshots required or requested.


**CURRENT EXECUTION ADDENDUM — 27 October 2026:** [27 October verified Workintech release record](WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md). Workintech BigQuery layers **46/46**, dbt quality **243/243**, seven governed ML outputs and 31/31 physical Power BI source contracts passed in the owner-executed recovery. The new 13 Desktop images render real imported data. **Pending:** fee-premium M%/tooltip format defects, selected-player drillthrough, 34 additional imported table dependencies, BigQuery-to-screen KPI comparison, owner acceptance and hosted CI. **The historical 20 October REVIEW PENDING decision below does not describe the completed 27 October warehouse run.**


**HISTORICAL STATUS — 20 October 2026 (superseded by the 27 October addendum above).** Scope was research-grade football analytics, dbt, historical market-value modeling and Power BI. This original decision is preserved for traceability, not a new 27 October release verdict.

**Final documentation/layout candidate (19 October 2026):** After consolidating the active documentation index, status, CI and ML-methodology language, three new repository-hygiene tests were added. The isolated Windows checkout at `fcb66f72e27dfdd2178e41a31b67749e6f26005b` passed **246/246 Python tests** (including all three new structure checks), and its exact-SHA **nine-stage offline runner reported PASS**. The structure audit found **no tracked temporary artifacts, generated caches, or exact duplicate active Markdown documents**. Original historical Power BI audit records were retained. These are source/structure checks, not authenticated BigQuery table execution.

**19 October repeat check:** an independent Windows checkout of `7dab032b0e88de33f6dedd01fb16cad3b163768c` again passed the SHA-bound **nine-stage offline runner**. The dbt manifest exposes **46 documented models and 878 described declared columns**. The strict physical-column coverage check needs `catalog.json` from a permitted warehouse docs generation; it is NOT RUN. Following that review, the extended offline dbt/YAML documentation guard and **three new regression cases** passed; the full local Python suite passed **249/249**. This does not validate BigQuery column reality, and every subsequent source revision still requires its own verification.

**Decision: REVIEW PENDING.** Source integration, full Python tests, dbt compilation/parse and documentation checks **PASS**; authenticated BigQuery checks and revised **real-data** historical ML evaluation **have not run**. The owner has accepted the existing Power BI workstream, but the current warehouse reconciliation has not been verified. Final hosted CI has **not** been triggered.

## Verification record — executed, not inferred

| Verification | Result / evidence |
| --- | --- |
| Tested source | Public `main` at `e84632af9aee1a3552a6d1904aa645ec1adc7a65`, clean independent checkout on Windows via SentinelX |
| Python unit tests | **243/243 PASS** — full `python -m unittest discover -s tests -p 'test_*.py' -v` |
| ML-focused tests | **47/47 PASS** — `test_ml_*.py` |
| Formal offline source/ML/full runner | **9/9 checks PASS**, with exact Git commit match; detailed record in [executed evidence](SENTINELX_OFFLINE_VERIFICATION_20261019.md) |
| Python syntax and dbt YAML/Jinja preflight | **PASS** — 11 YAML files, 54 SQL/Jinja files |
| Documentation links and headings | **PASS** — no broken local Markdown links or anchors in the tested commit |
| Real-world BigQuery access | **NOT RUN** — SentinelX agent account has no active Google Cloud login/project; no credential was requested or used |
| Offline dbt parse | **PASS** with credential-free temporary profile: dbt 1.12.6 / BigQuery adapter 1.11.1; **46 models, 2 snapshots, 8 analyses and 243 declared dbt tests** |
| dbt tests against live tables | **NOT RUN** — manifest discovery is not warehouse execution |
| Actual revised market-value backtest | **NOT RUN** — no authorized verified historical feature export |
| Historical Power BI screenshots/PBIP source | **PASS** — 13 screenshots and static PBIR source checks; these are not evidence of a fresh Desktop refresh |
| Owner's Power BI acceptance | **ACKNOWLEDGED** — user directed focus to ML/data; selected-player interactions and post-refresh BI/warehouse parity were not rerun |
| Final CircleCI | **NOT RUN** — final-stage-only opt-in; no per-merge hosted CI |

After adding the executed-evidence documentation, commit `4bd7d53d17df6497bb8759052781387c3dcd44a2` was fetched into the Windows verification workspace and the same **nine-stage offline runner passed again** for that exact SHA. Documentation edits after this record require their own source and test recheck; they do not retroactively certify BigQuery.

## Remaining acceptance gates, in order

1. **Authorized read-only warehouse evidence (BLOCKED).** Establish an approved, separate BigQuery session. Verify raw source modification time separately from event dates; run `assert_ml_training_asof_integrity`, `assert_ml_scoring_asof_integrity`, `assert_ml_training_row_coverage`, the canonical player/date valuation exclusion audit ([SQL](../analyses/audit_ml_valuation_event_grain_20261019.sql)) and other dbt checks. Record project, as-of/source timestamp, source-row and unique-key counts and query cost authorization. No anonymous/fixture substitute.
2. **Empirical ML evidence (NOT RUN).** On verified real feature rows, rerun corrected training/tuning/calibration/holdout and rolling-origin comparisons against previous-value persistence. Report MAE, WAPE, interval coverage/width, n per segment, cluster-bootstrap status and drift. **Earlier historical v5 figures are not validated for the revised code.**
3. **Power BI source reconciliation (OWNER-ACCEPTED, freshness OPEN).** Maintain the user's prior design approval and the original production PBIP. Once BigQuery is verified, reconcile comparable KPI populations. The **8,581** screenshot 365-day observed count uses a DAX maturity cutoff while the **8,584** historical dbt success-label count does not; the three actual row keys remain unidentified. Do not invent a match. The two player-detail screens were originally captured without a selected player, so past screenshots alone do not prove drillthrough interactions.
4. **Final hosted CI (NOT RUN).** Only after the above gates and owner approval, run the nine-job CircleCI workflow once with `run_final_ci=true`. A push or PR with no checks is not PASS. Do not trigger a cost-bearing cloud/model publication to compensate for missing source evidence.

### Credential and CI policy

- `.github/workflows/dbt-ci.yml`: manual dispatch and opt-in variables; warehouse validation requires separate authorization.
- `.github/workflows/ml-production.yml`: **manual only**, plus `ENABLE_ML_PRODUCTION=true` and per-run `confirm_final_release=true`. The former weekly schedule was removed after [run #39237422384](https://github.com/senanurcetin/football-player-performance-analysis/actions/runs/39237422384) on 19 October 2026 failed at the empty `GCP_SERVICE_ACCOUNT_JSON` precheck; all subsequent dbt/training/publish steps were **skipped**.
- `.circleci/config.yml`: nine final jobs gated on `run_final_ci=true`, default false. A workflow definition or past check is not a new success. See [CI policy](CI_RELEASE_GATE_POLICY.md).

## Repository and documentation ownership

| Area | Purpose / authoritative entry |
| --- | --- |
| `models/{staging,intermediate,marts,ml}/`, `snapshots/`, `tests/` | Native dbt SQL models, snapshots, singular and schema tests; [architecture](ARCHITECTURE.md) |
| `scripts/`, `requirements*.txt`, `notebooks/` | Python ML evaluation, research tooling and optional portable offline runner; [methodology](PLAYER_MARKET_VALUE_ML.md) |
| `analyses/` | Non-mutating, authorization-gated analytical SQL; [data quality](DATA_QUALITY.md) |
| `powerbi/workspace/` and `powerbi/offline-demo/` | Authentic editable PBIP and separately labelled synthetic fixtures; [design contract](BI_DESIGN_SYSTEM.md) |
| `docs/` | Canonical status, current methodologies, evidence, runbook and index; [documentation map](README.md) |
| `docs/archive/powerbi/` | **19 retained historical investigation/design records**; [archive index](archive/README.md) |
| `.github/`, `.circleci/` | Source checks, manual/cloud and final opted-in CI; [policy](CI_RELEASE_GATE_POLICY.md) |

No tracked `target/`, virtual environment, temporary log or duplicate Markdown document was found in the repository structure audit. The 19 archived records are deliberately historical provenance, **not** active implementation plans; their dated findings are not to be silently rewritten as current. Only `docs/PROJECT_STATUS.md` controls the present release status.

## Evidence and research references

[Executed SentinelX verification](SENTINELX_OFFLINE_VERIFICATION_20261019.md) · [Execution method and alternate Colab/Kaggle notebook](REPRODUCIBLE_OFFLINE_VERIFICATION_20261019.md) · [ML reliability and corrected calibration methodology](ML_RELIABILITY_EVALUATION_20261018.md) · [Source-event valuation audit](ML_VALUATION_EVENT_GRAIN_AUDIT_20261019.md) · [Historic Power BI 365-day comparison](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md) · [Historical June 2026 data-quality snapshot](DATA_QUALITY.md) · [Root project README](../README.md).

## 20 October 2026 — continuation / access boundary

- Before further work, `main` was at `1b9b4648800177c982fbf074a042c5be2a94c9ff`. CircleCI remains explicit opt-in and was not run.
- The provider-native BigQuery connector is disabled by admin; the connected Windows agent reports zero active `gcloud` accounts, an unset default project, and no project credential environment variables. No paid query or publication was attempted.
- A row-level transfer mismatch diagnostic, local CSV validator and **nine synthetic regressions** were prepared under `analyses/`, `scripts/` and `tests/`. The new isolated checkout passed **258/258 full Python unit tests**, production Power BI static source checks, offline demo checks and credential-free dbt parse. **The three historic 365-day difference keys have not been identified.**
- All previously specified real BigQuery/source-freshness tests, historical ML backtest, Power BI post-refresh reconciliation and hosted final CI remain open.

## 20 October — GitHub-hosted BigQuery route identified, not yet verified

GitHub Actions has a configured `data-analiz-490513` project and references the `GCP_SERVICE_ACCOUNT_JSON` repository secret in `dbt-ci.yml` and `ml-production.yml`. This is the **correct alternative connection route** to the unauthenticated SentinelX Windows host. Secret contents are inaccessible from GitHub source and may have changed after the 19 October CI precheck reported an empty secret.

A narrowly scoped [manual metadata-only workflow](../.github/workflows/bigquery-readonly-preflight.yml) and [credential-safe metadata inspector](../scripts/check_bigquery_github_access.py) are prepared. They use the secret **only inside GitHub Actions**, inspect `football_mart` and two historical transfer tables through non-querying BigQuery metadata APIs, and save a redacted status artifact. No BigQuery SQL, billable job, model publication, hosted final CI, or workflow dispatch was executed during preparation. The project's 365-day key-level audit, real-data ML backtest and post-refresh Power BI gates are still open until actual run evidence is obtained.

## 20 October — GitHub preflight run diagnosed (blocked before connection)

GitHub Actions [run 39416694886](https://github.com/senanurcetin/football-player-performance-analysis/actions/runs/39416694886) displayed two attempts. The GitHub API returned job `check-metadata` with `conclusion=skipped`, not a credential failure; its confirmation input had default `false`, and retrying the run retained the original input. The manual metadata-only workflow was revised to **remove the redundant confirmation input and job-level condition**. A fresh `workflow_dispatch` is still required to actually check the secret; use a **new workflow run on current main**, not *Re-run jobs* from run 39416694886. No live BigQuery authentication or data query is established by this YAML change.
