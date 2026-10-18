# NEXUS Football Intelligence — data-science execution plan

**Date:** 18 October 2026
**Scope:** analytics engineering, data quality, statistical methodology, scientific validation and existing native Power BI correctness. **No productization, public hosting, new sales workflows, mock dashboards or synthetic-as-real metrics.**

## Delivery principles

1. **Truth first.** A code commit, offline unit test, model fit or Power BI screenshot cannot substitute for an authenticated data-freshness and warehouse reconciliation.
2. **Preserve production behavior unless independently validated.** Existing v5 feature definitions, model weights, output schemas, Power BI pages and approved brand assets remain unchanged by the current ML reliability work.
3. **No unintended paid execution.** CircleCI is a final opt-in gate. Kaggle, BigQuery and Desktop Commander were not available to this session; no retraining, external pipeline jobs, warehouse mutations or Power BI refresh were initiated.
4. **Reproducibility.** Every future verified metric needs code commit, model version, dataset-as-of timestamp, evaluation season window, population/denominator, estimator and baseline.
5. **Attribution.** Preserve the Workintech team's original collaboration history and the upstream authorship record.

## Ordered work packages

| Stage | Priority | Action | Concrete acceptance criterion | Dependency / status |
| --- | --- | --- | --- | --- |
| 1 | P0 | ML numeric-contract integrity | NaN/Inf, duplicate/missing keys and incomplete intervals fail closed; synthetic regression coverage | Draft PR #78 created; full repository suite not yet run |
| 2 | P1 | Temporal and uncertainty foundations | Chronological candidate folds, player-cluster bootstrap CI, empirical interval coverage/width, group n | Draft PR #79; nine local helper tests passed |
| 3 | P1 | Reproducible holdout evaluation package | Credential-free CLI pairs held-out `test_predictions.csv` with `metrics.json`, rejects inconsistent seasons/version/row counts, and emits SHA-256-backed JSON plus sample-governed CSV | Implemented on PR #79; latest artifact-provenance tests still require a full checkout run |
| 4 | P0 | Integration tests and change reconciliation | Full Python unit suite and ML pipeline smoke test pass on a current checkout; stacked #79 reviewed only after #78; no modifications outside planned files | **PARTIAL LOCAL PASS:** reconstructed research-only subset 33/33 tests PASS and 93% aggregate statement coverage. Full checkout, complete historical 158+ tests, #78 suite, GitHub checks and release gates still unverified |
| 5 | P0 | Warehouse provenance and source freshness | Read-only authenticated BigQuery validation of source modification times, business event dates, model row grains, missingness and dashboard metrics; compare to documented historical June snapshot | **BLOCKED:** BigQuery plugin is DISABLED_BY_ADMIN in the current ChatGPT session; no authenticated SQL execution. Historical June 2026 counts remain unrefreshed |
| 6 | P1 | Rolling-origin empirical backtest | An independent experimental refitting runner with strict train/tune/calibrate/test chronology, persistence and past-only position baselines is implemented and has 12 passing synthetic tests. **Actual empirical backtest remains blocked** | **SOURCE IMPLEMENTED; DATA RUN BLOCKED:** no authorized historical ML feature export |
| 7 | P1 | Transfer outcome and coverage study | Quantify selection/coverage bias and 365-day observed outcome denominators; separate association from causal attribution | **READ-ONLY SQL WRITTEN:** `analyses/audit_transfer_365d_capture_20261018.sql` inventories source cohorts; cannot execute because BigQuery is disabled. Three-row visual-vs-mart discrepancy remains |
| 8 | P0 | Native Power BI visual acceptance | Production-connected 13-page Desktop verification including selected player drillthrough, tooltips, source KPIs and refresh errors; record actual screenshots and owner signoff | **STATIC CHECKED / RUNTIME BLOCKED:** 13/13 capture SHA-256s verified and comparable historical KPI figures reconciled in `docs/POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md`. Player-selected drillthrough/tooltip runtime acceptance and 365d 3-row discrepancy still open |
| 9 | P0 | Final quality gate | Execute existing opt-in CI on the accepted commit, attach evidence and only then update release status from HOLD | **NOT TRIGGERED**: prerequisites unmet |

## Implemented code deliverables

**PR #78 — Numeric validation:** `scripts/train_player_market_value.py`, `tests/test_ml_numeric_contract.py`, and the methodology note. Does not claim new training results.

**PR #79 — Model reliability:** `scripts/ml_reliability.py`, `scripts/evaluate_ml_artifacts.py`, `scripts/walk_forward_research.py`, their three regression modules, held-out evaluation artifact wiring and methodology notes. The governed v5 production model is unchanged. The new research-only walk-forward runner fits independent historical estimator instances but does not publish or promote them.

### Offline report execution

With the pinned ML dependencies installed and an **existing, governed held-out prediction CSV**:

```bash
python -m unittest discover -s tests -p 'test_ml_reliability.py' -v
python -m unittest discover -s tests -p 'test_evaluate_ml_artifacts.py' -v
python scripts/evaluate_ml_artifacts.py \
  --input artifacts/player_market_value/test_predictions.csv \
  --metrics artifacts/player_market_value/metrics.json \
  --output-dir artifacts/player_market_value/offline_reliability \
  --min-rows 30 --replicates 500 --seed 42
```

Output artifacts are `reliability_summary.json` (model/version/season window, observed error and coverage, player-grouped bootstrap and input SHA-256) and `segment_metrics.csv` (season, position, quality cohort and target value tier; n, unique players and metrics). No personal or player-level predictions are copied into these aggregate reports.

**The source CSV is required.** Do not manufacture evaluation metrics by substituting a synthetic fixture. Tests use synthetic data strictly as regression checks.

## Scientific and operational constraints

- Label all historical evaluation results **historical**, never live. Last independently documented warehouse evidence is June 2026.
- Persistence MAE is the mandatory reference, while R² of price levels alone can overstate usable forecasting skill.
- A bootstrap CI is not a causal conclusion or a guarantee under season-to-season distribution shift.
- An expanding-window **split generator alone is not a completed rolling-origin backtest**.
- Report sample size and observed 365-day follow-up coverage on all transfer-cohort comparisons.
- A 90% nominal interval should not be presented as calibrated for each position, league or price band without adequate held-out evidence.
- The production Power BI source and synthetic test edition must never be conflated.
- No external publication or model promotion without the actual verified release gates.

## Merge dependency

PR #79 was explicitly stacked on PR #78, integrating numeric safeguards and reliability diagnostics in the same training script and retaining both documentation sets. The GitHub comparison of #79 against #78 includes the documented reliability code, research runner, tests and status files, while #78 remains targeted to main. Review and validate #78 first; once accepted, retarget #79 to main and rerun the full regression suite. Both remain drafts until acceptance, with no release claims.
