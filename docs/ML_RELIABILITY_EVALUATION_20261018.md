# Football ML reliability — statistical audit (18 October 2026)

**Scope:** new reproducible, local statistical evidence in the established NEXUS player-valuation pipeline. This implementation does **not** retrieve Kaggle data, refresh BigQuery marts, retrain the production model during source review, alter the production Power BI report, or establish updated model performance claims.

## Components

1. `rolling_origin_season_splits(frame)`: defines expanding-training chronological candidate folds, never using the test season or a future season as training observations. **It does not refit, tune or score a model.** Any downstream walk-forward runner must place its model fitting, blend tuning and interval calibration strictly before each test season.
2. `grouped_mae_skill_bootstrap(frame)`: estimates the relative MAE improvement over the previous-market-value persistence baseline using **player ID as the resampling unit**. It reports a point estimate, 95% percentile bootstrap interval, player groups, row count, replicate count and seed-reproducible results. Repeated player-seasons are kept together, not independently resampled.
3. `interval_coverage_by_group(frame)`: measures observed prediction interval coverage and median width by season, position and prediction-quality status. Groups with fewer than **30 observations** have their coverage and width suppressed rather than presented as reliable sample statistics.
4. `scripts/train_player_market_value.py` records the grouped-bootstrap MAE-skill statistics in `metrics.json` and writes `interval_coverage_cohorts.csv` alongside the existing predictions and evaluation artifacts. These are **descriptive evaluation artifacts** and do **not** modify release thresholds, published prediction schema, output data source or model weights.
5. `scripts/evaluate_ml_artifacts.py` provides an independent, credential-free read-only inspection of a versioned, already-generated `test_predictions.csv`. It checks that model version and row keys are coherent, that numeric inputs are finite, and that prediction interval bounds contain the estimate. The script produces `reliability_summary.json` (observed baseline comparisons, player-grouped bootstrap and SHA-256 source hash) plus `segment_metrics.csv` (season, position, quality status and market-value tier). Cohorts below 30 observations keep row and unique-player counts but suppress unreliable point metrics.

## Reproduce offline tests

Install pinned `requirements-ml.txt` and run:

```bash
python -m unittest discover -s tests -p 'test_ml_reliability.py' -v
python -m unittest discover -s tests -p 'test_evaluate_ml_artifacts.py' -v
# The following require the complete current repository checkout:
python scripts/check_ml_pipeline.py
python -m unittest discover -s tests
# The following requires genuine already-held-out training evaluation predictions:
python scripts/evaluate_ml_artifacts.py --input artifacts/player_market_value/test_predictions.csv --output-dir artifacts/player_market_value/offline_reliability
```

The new synthetic-only offline suites contain **19 regression tests**: nine for the temporal/bootstrap helper functions and ten for the standalone artifact auditor. All **19 passed** in the isolated Python environment using NumPy and pandas; this is **not** evidence that the whole GitHub repository suite or production integration passed. The full project suite, model training, dbt builds and BigQuery-backed reconciliation were **not** executed during this change. Existing local prediction artifacts are necessary to produce actual model-specific audit results; no synthetic metrics should be published as real football findings.

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
