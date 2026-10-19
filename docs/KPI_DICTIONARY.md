# Football Intelligence — governed KPI dictionary

**Reviewed 18 October 2026.** Definitions are grounded in the checked-in [DAX measures](../powerbi/MEASURES.dax), [dbt semantic metrics](../models/semantic.yml), and [marts](../models/marts/). They are **metric contracts**, not newly measured warehouse results. For observed historical figures use [Data quality](DATA_QUALITY.md); for their current verification status use [Project status](PROJECT_STATUS.md).

## Measure contract

| KPI | Source / grain | Definition / denominator | Display rule and exclusions |
| --- | --- | --- | --- |
| Players | `dim_players`; one player ID | Count distinct `player_id` within the selected dimension and visual filters | Show population/time context; **not** interchangeable with active performance player counts |
| Performance G+A / 90 | Appearance/performance facts; eligible player-minute population | 90 × (goals + assists) / played minutes; guard zero/missing minutes | Rate, not total goals; disclose any minimum-minutes cut and season/club filters |
| Club win rate | `fct_club_performance`; club results | Wins / played matches at the governed performance grain | Format a fraction 0–1 as percentage **once**; verify scale before multiplying an already-percent column |
| Historical transfers | `fct_transfer_fixed_horizon_outcomes`; transfer key | `DISTINCTCOUNT(transfer_key)`; DAX `[Historical Transfers]` | Excludes source-flagged future transfers in fixed-horizon mart; never compare unfiltered counts to other transfer marts |
| Observed 365d transfers | Fixed-horizon Power BI DAX grain | Distinct transfer keys with `has_365d_outcome = TRUE` **and** `target_365d_date + 30 days <= MIN(TODAY(), MAX(source_latest_valuation_date))` | Maturity-filtered visual counter, **not** equivalent to all `fct_transfer_success_labels` rows |
| 365d observed coverage | Same fixed-horizon grain | Maturity-filtered observed 365d distinct keys / maturity-filtered eligible 365d distinct keys | Both numerator and denominator use **the same** as-of-source maturity cutoff; report n and percent |
| 365d successful transfers | `fct_transfer_success_labels`; **only observed** keys | `is_successful_transfer = 1` when `market_value_change_365d_pct >= 20` | Threshold is **+20 percentage points of market-value change**. Observational label, **not** a predicted probability, profit or causal effect |
| Observed 365d success rate | `fct_transfer_success_labels` / group | Positive observed labels / observed labels with a comparable baseline | Rate must disclose group n; not valid to classify missing follow-up as failure. Use n≥30 for governed club-risk rankings |
| Known fee coverage | `fct_data_coverage_bias` | `SUM(known_fee_count) / SUM(transfer_count)` when the bias mart grain is aggregatable for the selected filters | Zero and unknown fees are distinct; DAX returns fractional share formatted as percent |
| Fee premium / discount | `fct_transfer_market_value_analysis` | Percent difference between known fee and selected valid value baseline, only where `has_fee_market_value_comparison = TRUE` | Unknown `NULL` amount must **not** be replaced with zero; show valid comparison n |
| Net transfer spend | `fct_club_transfer_portfolio` | `SUM(net_transfer_spend)` at selected club/season grain | Currency EUR, with the model's inbound/outbound transfer convention |
| Model held-out MAE | `football_ml` evaluation prediction rows | Mean absolute EUR difference: `mean(abs(actual - estimate))` | Historical 2024–2025 backtest, **not** current live prediction accuracy; compare with previous-value persistence MAE |
| Model held-out WAPE | Same held-out rows | 100 × sum(abs(actual − estimate)) / sum(actual) for positive market value | Percentage points; check finite values and population, not model release state |
| Model skill over persistence | Same held-out rows | 100 × (1 − model MAE / previous-value MAE) | Undefined if baseline MAE is zero; temporal/cluster uncertainty requires separate checks |
| Current scored players | `football_ml.ml_player_market_value_current_predictions`; one scored active player | Count distinct scored player keys at model/prediction-as-of version | This differs from `dim_players` player universe; show model version and estimation-as-of date |
| Decision-ready share | Same current predictions | Count(`prediction_quality_status` in `high, medium`) / count(all scored current rows) | Limited rows are baseline fallback, not reliable model-led recommendations. Show n and % |
| Interval coverage | Held-out evaluation predictions | Fraction of held-out actual values between inclusive model lower/upper bounds | Empirical retrospective coverage, **not** a guaranteed 90% band for every cohort |
| Eligible group reliability | `fct_club_risk_profile`, segment ML metrics | Group meets `meets_minimum_sample_size = TRUE` (typically n≥30) | Preserve suppressed rates as blank/missing rather than zero |

## Time, filters and denominator requirements

- Keep **transfer date**, **market-value observation date**, **source table modified time**, **screenshot capture time**, and **ML prediction-as-of time** separate. Historical screenshot values from 17 October are not new source timestamps.
- For **365-day** comparisons, the fixed-horizon mart selects an observed valuation **within ±30 days of the exact 365-day target** and requires an eligible positive baseline. Do not compare to an arbitrary next valuation.
- The native DAX **observed/eligible 365d counters both apply the 30-day post-target maturity cutoff against the earlier of TODAY and the last valuation-source date**. The `fct_transfer_success_labels` dbt mart does **not** apply that cutoff. **Screenshot 8,581 observed / 36,571 eligible**, versus dated mart documentation **8,584 success-label rows / 39,780 historical fixed-horizon rows**, describe structurally different populations. The source-level difference is verified; the precise three missing row keys remain unverified without authorized BigQuery readback. See the [Power BI source audit](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md).
- DAX fractional rates such as `[365d Outcome Coverage %]` and `[Known Fee Coverage %]` use `DIVIDE` (0–1) and need percent formatting; mart fields already named `*_pct` often represent 0–100. **Inspect the stored model definition** before multiplying by 100.
- Group aggregations must be weighted by underlying numerator/denominator or underlying facts, **not blindly averaged over differently sized cohorts**, unless the result is explicitly labeled an unweighted average of group rates.
- Player profiles and past performances must not be used as post-transfer causal controls without appropriate identification design. Historical valuation sources are estimates, not transaction prices.

## Source precedence and audit commands

1. Native semantic logic: [`powerbi/MEASURES.dax`](../powerbi/MEASURES.dax) and the actual production PBIR's field bindings, [`models/semantic.yml`](../models/semantic.yml), dbt model SQL and dbt schema tests.
2. Observed, date-qualified benchmarks: [`docs/DATA_QUALITY.md`](DATA_QUALITY.md) and [`docs/PLAYER_MARKET_VALUE_ML.md`](PLAYER_MARKET_VALUE_ML.md).
3. Screenshot-to-warehouse reconciliation: [`docs/POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md`](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md) and the [read-only follow-up query](../analyses/audit_transfer_365d_capture_20261018.sql).
4. Current release evidence: [`docs/PROJECT_STATUS.md`](PROJECT_STATUS.md). Do not override this with earlier draft/archived claims.

Recheck links and code semantics from the full repository checkout with `python scripts/check_docs_integrity.py`; any BigQuery source reconciliation remains a separate **authorized and billable** read-only operation.
