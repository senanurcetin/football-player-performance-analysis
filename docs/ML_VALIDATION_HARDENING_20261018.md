# ML validation hardening — 18 October 2026

> **Follow-up 19 October 2026:** The combined Python suite (**243/243 PASS**) and ML-focused suite (**47/47 PASS**) ran in an independent full Windows checkout. This supersedes the original isolated-test-only execution scope recorded below. **No authenticated BigQuery tests or revised real-data training/backtest were run.** See [verification evidence](SENTINELX_OFFLINE_VERIFICATION_20261019.md) and [current status](PROJECT_STATUS.md).

**Scope:** credential-free source integrity. This branch does not retrain the model, query BigQuery, access Kaggle, run Power BI Desktop, publish predictions, or establish new empirical performance metrics.

## Rationale

The established player-market-value training code uses temporal development / tuning / interval-calibration / holdout splits and compares its estimates to the previous-value persistence baseline. This change closes specific numeric-contract gaps **before** model fitting or publication:

| Contract | Previous failure mode | New rule |
| --- | --- | --- |
| Training target | Missing target (NaN) passed the `<= 0` check | Market-value targets must be finite and strictly positive |
| Prediction row key | A single missing key was not detected by `duplicated()` | Reject missing or repeated prediction keys |
| Interval structure | Any omitted interval column silently bypassed interval validation | Reject partial interval structures; optional all-or-none |
| Interval bounds | NaN or infinite lower/upper boundaries escaped inequality checks | Both interval boundaries must be finite |
| Interval calibration inputs | Empty/mismatched arrays, NaN or out-of-range quantile were unchecked | Require aligned, nonempty, finite values and `0 < quantile < 1` |

Existing allowances remain: **missing optional feature values may still be imputed**, and a lower interval may legitimately be truncated at zero. Training/score features with infinity remain invalid.

## As-of and input contracts — 19 October 2026 follow-up

Additional, **fail-closed** source checks are being added after PRs #78–#80:

- Both scoring and training reject **missing, fractional, infinite or nonpositive seasons** before a chronological split; row identifiers must be nonmissing, unique **and nonblank**, and historical previous market value must be **nonnegative** when present. Nullable prior value remains legal for the existing median/baseline fallback.
- Two **read-only singular dbt tests** in `tests/assert_ml_training_asof_integrity.sql` and `tests/assert_ml_scoring_asof_integrity.sql` identify feature-event dates occurring at or after a training target, or strictly after a scoring as-of date, as well as inconsistent previous valuations and impossible counters. They return bad rows; they do **not** mutate warehouse sources.
- `analyses/audit_ml_feature_lineage_20261019.sql` offers a separate, **unexecuted**, read-only profile of row grains, season/date ranges, prior-value missingness and as-of violations. Its query output will only be interpretable with a documented source-refresh/as-of timestamp.
- Three new synthetic `test_ml_numeric_contract.py` test methods cover both frame types. Three additional credential-free `test_ml_asof_sql_contract.py` methods check the SQL contracts (not BigQuery execution). An isolated hand-transcribed reproduction of the input contract passed **4/4 local Python unit tests**, but this is **not** the actual full repository test run or an empirical finding.
- Hosted CI remains explicitly deferred by user instruction. Later BigQuery/dbt checks require authorization and could incur processing costs; do not mislabel committed source checks as completed warehouse validation.

## Offline verification

With Python 3.11 and the dependencies in `requirements-ml.txt` installed, run from the repo root:

```bash
python -m unittest discover -s tests -p 'test_ml_numeric_contract.py' -v
python scripts/check_ml_pipeline.py
python -m unittest discover -s tests
```

The new tests use synthetic-only rows and do not create a BigQuery client. Importing `train_player_market_value.py` requires the pinned Python packages, but neither credentials nor a warehouse connection. **Do not record a PASS until the commands actually execute.**

## Scientific interpretation and remaining work

These are **input/output integrity guards**, not evidence of improved predictive accuracy. Previously reported v5 backtest MAE, R2, WAPE, and interval coverage remain historical, unchanged metrics.

Prioritize the following *separate, evidence-driven* enhancements:

1. **Rolling-origin backtesting (P1):** compare the ensemble, persistence and a simple cohort-median baseline across several forward seasons; report MAE, WAPE, skill over baseline and observed sample sizes by season.
2. **Uncertainty by cohort (P1):** report interval coverage and median interval width for position, source-availability tier and EUR 20M+ players. Assess calibration group size and consider finite-sample conformal quantiles (with explicit small-group fallback). Existing higher-quantile calibration is **not** claimed to supply a formal exchangeability guarantee.
3. **Statistical uncertainty (P1):** estimate improvement confidence intervals using grouped resampling by `player_id`; player-seasons from the same footballer should not be treated as independent observations.
4. **Warehouse audit (P0, access dependent):** when BigQuery authorization is available, verify raw-table modified timestamps separately from match/valuation event dates; rerun dbt freshness and warehouse-to-BI reconciliation. Continue to label the June 2026 warehouse evidence as historical.
5. **Observed transfer outcomes (P1):** report coverage-adjusted descriptive sensitivity and sample denominators; do not describe observed 365-day success as a causal effect or as an ML-predicted event.
6. **Artifact acceptance (P0, access dependent):** rerun current model release gates before publishing any revised estimates. Finish the 13-page Power BI visual interaction audit and obtain explicit owner signoff.

## Release evidence

- Change scope: `scripts/train_player_market_value.py`, `tests/test_ml_numeric_contract.py` and this note.
- Remote BigQuery / Kaggle access: **NOT USED**.
- New training, backtesting and production results: **NOT RUN**.
- Existing Power BI owner acceptance was acknowledged; the **overall project release remains REVIEW PENDING**, following [current status](PROJECT_STATUS.md).
- CI-last policy: `docs/CI_RELEASE_GATE_POLICY.md`; keep hosted CircleCI opt-in.

The original Workintech team project attribution and upstream contributions remain unchanged.
