# Football ML reliability — statistical audit (18 October 2026)

**Scope:** new reproducible, local statistical evidence in the established NEXUS player-valuation pipeline. This implementation does **not** retrieve Kaggle data, refresh BigQuery marts, retrain the production model during source review, alter the production Power BI report, or establish updated model performance claims.

## Components

1. `rolling_origin_season_splits(frame)`: defines expanding-training chronological candidate folds, never using the test season or a future season as training observations. **It does not refit, tune or score a model.** Any downstream walk-forward runner must place its model fitting, blend tuning and interval calibration strictly before each test season.
2. `grouped_mae_skill_bootstrap(frame)`: estimates the relative MAE improvement over the previous-market-value persistence baseline using **player ID as the resampling unit**. It reports a point estimate, 95% percentile bootstrap interval, player groups, row count, replicate count and seed-reproducible results. Repeated player-seasons are kept together, not independently resampled.
3. `interval_coverage_by_group(frame)`: measures observed prediction interval coverage and median width by season, position and prediction-quality status. Groups with fewer than **30 observations** have their coverage and width suppressed rather than presented as reliable sample statistics.
4. `scripts/train_player_market_value.py` records the grouped-bootstrap MAE-skill statistics in `metrics.json` and writes `interval_coverage_cohorts.csv` alongside the existing predictions and evaluation artifacts. These are **descriptive evaluation artifacts** and do **not** modify release thresholds, published prediction schema, output data source or model weights.
5. `scripts/evaluate_ml_artifacts.py` provides a credential-free read-only inspection of an already-generated `test_predictions.csv` **paired with the matching `metrics.json`**. It rejects inconsistent declared model versions, train/tune/calibration/test chronology and row counts; this verifies the two artifacts agree, **not** that warehouse provenance is independently authenticated. It checks that model version and row keys are coherent, that numeric inputs are finite, and that prediction interval bounds contain the estimate. The script produces `reliability_summary.json` (observed baseline comparisons, player-grouped bootstrap and SHA-256 source hash) plus `segment_metrics.csv` (season, position, quality status and market-value tier). Cohorts below 30 observations keep row and unique-player counts but suppress unreliable point metrics.

## Reproduce offline tests

Install pinned `requirements-ml.txt` and run:

```bash
python -m unittest discover -s tests -p 'test_ml_reliability.py' -v
python -m unittest discover -s tests -p 'test_evaluate_ml_artifacts.py' -v
# The following require the complete current repository checkout:
python scripts/check_ml_pipeline.py
python -m unittest discover -s tests
# The following requires genuine already-held-out training evaluation predictions:
python scripts/evaluate_ml_artifacts.py --input artifacts/player_market_value/test_predictions.csv --metrics artifacts/player_market_value/metrics.json --output-dir artifacts/player_market_value/offline_reliability
```

The initial synthetic-only suites contain **21 declared regression tests**: nine for the temporal/bootstrap helpers and twelve for the standalone evaluation artifact auditor, including metadata coherence checks. Earlier isolated checks were reported for the helpers; a reconstructed offline subset of the three new ML research suites passed **33/33 tests**, with **93% combined statement coverage**; the actual combined GitHub checkout, original #78 numeric-contract suite and full historical repository suite still require verification. Separately, the walk-forward research suite has **12 locally executed PASS tests** using NumPy, pandas and scikit-learn; this is **not** evidence that the whole GitHub repository suite or production integration passed. The full project suite, production model training, dbt builds and BigQuery-backed reconciliation were **not** executed during this change. Existing local prediction artifacts are necessary to produce actual model-specific audit results; no synthetic metrics should be published as real football findings.

## Refitted walk-forward research (offline)

`scripts/walk_forward_research.py` is an **additional, separate research workflow**. It reads a caller-exported historical ML training feature CSV and the generated `feature_contract.json`. For each eligible year, it fits independent models on earlier seasons, tunes an ML/persistence blend on a later-but-still-past season, reserves the next season for interval calibration, and evaluates only on a further held-out season. The **same pre-calibration fitted model** is used for calibration and test inference, so calibration rows cannot enter its fit. A past-only positional median is a second benchmark.

The workflow emits per-year sample size, MAE, WAPE, persistence skill, position-median MAE, a conservative finite-sample split-conformal residual radius, and **empirical** held-out interval coverage. No trained models, forecast marts or Power BI fields are published. It is an independent historical research estimator, **not the governed v5 production ensemble**. Its sklearn configuration differs from v5 and results must not be compared as a v5 champion release gate.

With an already-authorized export of the governed `ml_player_market_value_training` feature table:

```bash
python -m unittest discover -s tests -p 'test_walk_forward_research.py' -v
python scripts/walk_forward_research.py \
  --input artifacts/player_market_value/historical_training_export.csv \
  --feature-contract artifacts/player_market_value/feature_contract.json \
  --output artifacts/player_market_value/rolling_origin_research.csv
```

This branch's **12 synthetic-only tests** were executed in an isolated environment with NumPy 2.3.5, pandas 2.2.3 and scikit-learn 1.8.0, all passing; they exercise chronology, no future-target contamination in earlier folds, the distinct calibration stage, actual refitting, input validation, baselines, confidence-interval rank and CLI manifest. This is **not** a genuine rolling-origin performance result, because authorized real feature data was not available. The runner forbids obvious target/identity/future data columns as features; preventing less-obvious leakage depends on the upstream dbt feature-contract and as-of-date audits.

## Diagnostic resilience note — 19 October 2026

The independent player-cluster bootstrap is an **optional descriptive evaluation diagnostic**, not a v5 model promotion gate. Some otherwise valid datasets concentrate all persistence-baseline error in only one player's rows. A player-cluster bootstrap resample may exclude that player, producing a **zero baseline MAE denominator** even though the observed sample has valid relative skill. Previously such a draw raised `ValueError` and could unnecessarily interrupt training.

The corrected diagnostic preserves the observed `mae_skill_vs_persistence_pct`, reports `undefined_bootstrap_resamples`, and returns `bootstrap_ci_status="not_estimable_undefined_resamples"` with JSON `null` CI bounds if **any** resample has an undefined ratio. When every draw is defined, `bootstrap_ci_status="estimated"` and the existing percentile CI is reported. This **does not** replace undefined draws, mislabel conditional estimates as unconditional confidence intervals, or alter governed training weights.

The standalone offline auditor also rejects either source file (`test_predictions.csv` or `metrics.json`) colliding with a generated output path, preventing accidental overwrite. Two isolated numeric scenarios (dense vs. single-error-player baselines) were reproduced locally; additional source regression tests have been added, but the **full GitHub checkout suite remains unrun** for this change. No real-data skill, source freshness or Desktop approval is claimed.

## Valuation-event grain precondition — 19 October 2026

The feature-table source now has a separate [same-day valuation event-grain audit](ML_VALUATION_EVENT_GRAIN_AUDIT_20261019.md): duplicate player-date source records should not multiply supervised targets, conflicting same-day EUR observations are excluded, and previous-value persistence uses only unambiguous past observations. **No conclusion about real player counts or changed MAE is available** until the read-only source collision/exclusion query and actual historical model evaluation are run by an authorized BigQuery user.

## Interpretation and statistical limitations

- **Bootstrap skill** = 100 × (1 − model absolute error total / persistence absolute error total). A value above zero indicates a lower observed MAE than persistence on the supplied cohort. This is not evidence that the predictor beats persistence in each league, season or valuation tier.
- The percentile player-cluster bootstrap accounts for within-player repeated observations but does **not** correct time drift or turn the test sample into a randomized trial. Its 95% confidence interval describes resampling variability for this observed population.
- **Interval coverage** is an empirical retrospective frequency, not a promise of 90% coverage for every season or player group; sparse groups are suppressed.
- The existing prior-valuation persistence baseline is mandatory. High R² on market-value levels alone remains insufficient evidence of forecasting skill.
- **Rolling-origin fold generation is not a completed rolling-origin backtest.** A future model-refit runner needs real governed source rows, temporal feature snapshots, fold-level tuning/calibration and held-out evaluation; it must never reuse future-season information.
- Missing historical transfer follow-up and player-valuation source gaps remain documented in `DATA_QUALITY.md`. Do not replace unknown monetary figures with zero.

## Governance and acceptance

- Genuine production metrics remain those supported by the dated evidence in `PROJECT_STATUS.md` and `PLAYER_MARKET_VALUE_ML.md`.
- Full production evaluation requires an authorized BigQuery environment, recorded source snapshot, model version and timestamp. Kaggle dataset terms and Workintech team attribution remain applicable.
- Hosted CircleCI is final-stage opt-in. This PR uses `[skip ci]` and must not be merged as an empirical release validation.
- Power BI release **remains on hold** until selected-player drillthrough interactions, actual Desktop refresh and warehouse reconciliation are accepted.

## Next steps

Complete fold-specific retraining/evaluation on authorized historical data, evaluate coverage drift by cohort and season, and add finite-sample calibration safeguards only after the current historical model behavior has been benchmarked. A controlled BigQuery freshness and dashboard audit remains the independent P0 prerequisite for publishing a current-season report.
