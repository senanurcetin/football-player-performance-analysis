# Football Intelligence — research execution plan and closure matrix

**Original plan:** 18 October 2026. **Reconciled:** 19 October 2026 against independently executed Windows source tests. No productization, publication, or synthetic figures presented as real football metrics.

**Use [PROJECT_STATUS.md](PROJECT_STATUS.md) for the release decision.** This is a work breakdown and its dated evidence, not a second approval record.

## Research and analytics engineering workstream

| Work package | Deliverable | Current state / acceptance evidence |
| --- | --- | --- |
| P0 — Numeric ML safety | Reject invalid targets, duplicate/blank keys, corrupt intervals, negative prior valuation and invalid years | **SOURCE DONE; offline tests PASS** on actual `main` checkout |
| P0 — Training/data as-of controls | Strict prior observations, chronology and canonical player/date/source EUR; coverage parity | **SOURCE DONE; offline SQL/SQLite tests PASS**; authenticated dbt table tests still unrun |
| P1 — ML uncertainty diagnostics | Deterministic rolling-origin fold logic, player-group bootstrap and interval coverage by cohort | **SOURCE DONE; offline Python PASS**; real data assessment pending |
| P0 — Corrected historical estimator identity | Calibrate and test the **same fitted estimator**; record fit/calibration provenance | **SOURCE DONE; offline Python PASS**; actual held-out metrics require new evaluation |
| P1 — Offline held-out artifact report | Strict CSV/metadata pairing, hashes, provenance and report output collisions | **SOURCE DONE; offline tests PASS** |
| P0 — Full repository verification | Source syntax, YAML/Jinja, all Python tests, docs, dbt model parse | **PASS 19 Oct:** **243/243 full Python**, **47/47 ML**; dbt parse **46 models and 243 declared tests**, zero warehouse queries |
| P0 — Warehouse provenance and actual data tests | Authenticated freshness, event dates, source-to-model key/label grain and valuation exclusion audit | **BLOCKED:** no approved BigQuery session; read-only SQL exists but **has not been executed** |
| P1 — Real historical rolling-origin/backtest | Real source feature export, refitted temporal folds, comparison against persistence, MAE/WAPE, interval coverage, drift | **NOT RUN** on revised code; historical v5 metrics are not new acceptance |
| P1 — Transfer 365-day follow-up | Compare DAX maturity-filtered visual population vs. unfiltered label table; quantify three observed-key difference | **SOURCE DEFINITIONS IDENTIFIED; live 3-key reconciliation still open** |
| P0 — Existing Power BI | 13 screenshot hash checks, PBIR static checks and owner review | **STATIC PASS; owner previously accepted**; refresh/parity with current BigQuery open |
| P0 — Final hosted CI | Run the nine opt-in CircleCI jobs on the approved commit | **NOT RUN; defer until warehouse, model and owner acceptance gates met** |

## Verified reproducibility

On 19 October an independent full Git checkout was tested on Windows via SentinelX. The [executed evidence report](SENTINELX_OFFLINE_VERIFICATION_20261019.md) records exact `e84632af9aee1a3552a6d1904aa645ec1adc7a65` and a subsequent source/doc update `4bd7d53d17df6497bb8759052781387c3dcd44a2` verified with the nine-phase portable runner. Python full unit discovery **243/243 PASS**, ML subset **47/47 PASS**, YAML/Jinja source preflight and dbt parse PASS. This verifies source contracts, **not** actual valuation cohort counts or revised model quality.

Original research source was integrated through GitHub PRs #78–#87, including numeric contracts, fixed-estimator calibration, date/event-grain and coverage parity, double opt-in model publication, and Kaggle/SentinelX offline verification. For specifics, consult [numeric hardening](ML_VALIDATION_HARDENING_20261018.md), [ML reliability](ML_RELIABILITY_EVALUATION_20261018.md), [event-grain analysis](ML_VALUATION_EVENT_GRAIN_AUDIT_20261019.md) and [Power BI history](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md), rather than repeating per-commit notes here.

## Completion prerequisites before final CI

**Authorized warehouse first.** Verify upstream freshness/source modifications separately from business event dates. Run read-only `analyses/audit_ml_valuation_event_grain_20261019.sql`, `analyses/audit_ml_feature_lineage_20261019.sql`, `analyses/audit_transfer_365d_capture_20261018.sql` and the dbt singular as-of/coverage tests using a separately approved BigQuery project. Capture processed cost, source as-of, SQL/manifest version and source count deltas. Source parser success does **not** prove these queries succeed.

**Corrected model evaluation second.** Using governed real data, rerun chronological training/tuning/calibration/test and rolling-origin comparisons, keeping model-fit data separate from calibration labels. Require persistence baseline, segment sample sizes and uncertainty/coverage checks; never copy earlier v5 model scores as if this retrain was performed.

**Power BI reconciliation third.** Owner's existing acceptance stands. Refresh and reconcile real KPI denominators against the authorized warehouse when available. Keep synthetic fixtures distinct and preserve original screenshots.

**Single CI last.** Run CircleCI only with explicit final opt-in `run_final_ci=true` and all nine jobs only after prior evidence is reviewed. GitHub model publication has separate double authorization and can incur BigQuery cost. No scheduled model publication is active.

**Current result: REVIEW PENDING**, despite completed source engineering and genuine offline test passes.
