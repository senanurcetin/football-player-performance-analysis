# Data Quality and Validation

## Validation Status

The project was fully validated against BigQuery on June 15, 2026.

| Validation | Result |
| --- | ---: |
| Full CI validation resources | 292 |
| Full project tests | 241 passed |
| Source freshness | 12 of 12 sources passed |
| Model descriptions | 46 of 46 models documented |
| Column descriptions | 878 of 878 model columns documented |
| Mart models | 25 |
| Type-2 snapshots | 2 |
| Semantic models / metrics / exposures | 2 / 7 / 3 |
| ML feature build | 45 passed |
| ML training feature rows | 90,704 |
| ML current scoring feature rows | 7,841 |
| ML-specific tests | 43 passed |
| Warnings | 0 |
| Errors | 0 |
| Non-null fact-to-dimension orphan keys | 0 |

The full project contains 46 models, 2 snapshots, 5 analyses, 3 exposures, 7 metrics, 2 semantic models, and 241 tests. The ML-only feature build contains two table models and 43 tests.

Documentation coverage is complete across the transformation layers: 153 staging columns, 103 intermediate columns, 557 mart columns, and 65 ML columns. dbt persists these descriptions to the generated catalog and BigQuery metadata.

## Source Freshness

All 12 raw sources use BigQuery table last-modified metadata. This is intentionally different from using historical business dates such as game or transfer dates.

| Threshold | SLA |
| --- | ---: |
| Warning | More than 7 days since the raw table was modified |
| Error | More than 14 days since the raw table was modified |

At the June 15, 2026 validation, all raw sources passed freshness and were approximately five days old.

## Current Mart Row Counts

| Model | Rows |
| --- | ---: |
| `dim_players` | 47,702 |
| `dim_clubs` | 9,032 |
| `dim_competitions` | 67 |
| `dim_date` | 13,514 |
| `fct_player_performance` | 28,736 |
| `fct_player_career_timeline` | 189,789 |
| `fct_club_performance` | 3,270 |
| `fct_competition_performance` | 67 |
| `fct_market_value_history` | 507,815 |
| `fct_transfers` | 40,208 |
| `fct_transfer_market_value_analysis` | 40,208 |
| `dim_national_teams` | 118 |
| `time_spine_daily` | 13,149 |
| `fct_match` | 88,807 |
| `fct_player_match_performance` | 1,885,688 |
| `fct_player_rolling_form` | 1,885,688 |
| `fct_club_season_performance` | 21,583 |
| `fct_club_transfer_portfolio` | 30,311 |
| `fct_transfer_fixed_horizon_outcomes` | 39,780 |
| `fct_transfer_cohort_performance` | 156 |
| `fct_data_coverage_bias` | 53 |
| `fct_agent_portfolio` | 3,849 |
| `fct_transfer_success_labels` | 8,584 |
| `fct_club_risk_profile` | 5,714 |

Row counts represent the BigQuery state at validation time and can change when raw data is refreshed.

## Transfer and Market Value Analysis Coverage

The detailed transfer mart preserves every staged transfer and exposes the data availability needed to interpret each calculation.

| Coverage metric | Rows |
| --- | ---: |
| Unique transfer records | 40,208 |
| Transfers with a known fee | 25,821 |
| Transfers with a selected market value baseline | 24,913 |
| Transfers with both a known fee and market value baseline | 20,001 |
| Transfers with a prior valuation | 24,886 |
| Transfers with a subsequent valuation | 35,077 |
| Transfers with a calculated post-transfer value change | 21,820 |
| Future-dated transfer records explicitly flagged | 428 |

Comparable fixed-horizon analysis is deliberately more restrictive. Across 39,780 historical transfers, 90-day outcome coverage is 15.86%, 180-day coverage is 24.39%, and 365-day coverage is 21.58%. The overall segment is classified `high_bias_risk`; outcome findings must be shown with coverage and cannot be generalized to missing-follow-up transfers.

## ML Validation

The player market value model is evaluated with a time-based holdout:

| Split | Rows |
| --- | ---: |
| Evaluation training seasons 2012-2023 | 78,324 |
| Ensemble tuning season | 2022 |
| Interval calibration season | 2023 |
| Temporal backtest seasons 2024-2025 | 12,380 |
| Production training rows through 2025 | 90,704 |

| Metric | Ensemble model | Previous-value baseline |
| --- | ---: | ---: |
| MAE | EUR 781,409 | EUR 867,156 |
| RMSE | EUR 2,039,156 | EUR 2,248,309 |
| R2 | 0.9756 | 0.9704 |
| WAPE | 12.51% | 13.88% |
| Median absolute percentage error | 13.23% | 14.29% |

High- and medium-quality ensemble weights are selected only on 2022. Limited-quality rows use a governed baseline fallback because sparse-context ML estimates are not reliable enough for model-led publishing. Predicted-value-band conformal intervals are calibrated only on 2023. The code uses the 2024-2025 backtest rows only for evaluation and release gating, not fitting, automated weight selection, or interval calibration. Backtest interval coverage is 89.63% overall and 83.66% for actual EUR 20M+ players.

The current scoring readiness check passes with 27.09% missing previous values, 28.59% missing competition context, and 0% missing age. Missing optional inputs are preserved and imputed; predictions are labeled `high`, `medium`, or `limited` so downstream reports can filter by readiness.

GitHub CI also runs `scripts/check_ml_pipeline.py` with synthetic missing and categorical values to detect preprocessing, model-fitting, ensemble, prediction-validation, segment-metric, and drift regressions without retraining against production data.

The v5 production release passes all seven blocking model gates: baseline MAE improvement, latest-approved-champion MAE regression, WAPE, R2, overall interval coverage, EUR 20M+ interval coverage, and no prediction-quality segment performing below its baseline. Its status remains `approved_with_monitoring` because the limited-quality prediction share is 27.09% and ten features show significant PSI drift. These warnings are exposed rather than suppressed.

## Test Coverage

### Source Tests

Source tests validate required identifiers and uniqueness where the source grain guarantees a unique key.

Examples:

- Player, club, game, competition, event, and lineup identifiers are unique and not null.
- Appearance, transfer, and valuation identifiers required for downstream logic are not null.

### Schema Tests

Schema tests validate:

- Unique and not-null model grains
- Relationships between staged models
- Relationships between mart facts and dimensions

### Singular Business-Rule Tests

The `tests/` directory contains 48 custom SQL tests covering:

- Appearance player-game grain
- Two club-perspective rows per game
- Player, club, competition, transfer, and market-value recalculations
- Intermediate and mart row coverage
- Current dimension record preservation
- Market value and transfer fact source reconciliation
- Player season-performance grain
- Market value selection not occurring after the player's last game
- Player age calculation
- Staging sentinel normalization
- Transfer fee calculations
- Detailed transfer source reconciliation, nearest valuation selection, and value-change calculations
- Mart values matching intermediate or staging inputs
- Continuous, gap-free date-dimension coverage
- ML feature dates strictly preceding their target valuation dates
- Complete player-season target coverage in the ML feature table
- Current scoring features not using future appearances or valuations
- ML feature business rules, model coverage, and scoring-readiness missingness thresholds
- Fixed-horizon outcome windows, cohort reliability, and coverage-bias rules
- Match, player-match, rolling-form, club-transfer portfolio, and professional mart grains
- Snapshot validity and exactly one current version per profile key
- Refresh-audit row-volume anomaly detection
- Fixed 365-day transfer-success labels and club-risk sample/coverage governance

## Reconciliation Strategy

Critical facts are validated by recalculating expected values from their upstream models and comparing both directions:

```text
expected EXCEPT DISTINCT actual
actual EXCEPT DISTINCT expected
```

Two-decimal floating metrics are normalized to exact `NUMERIC` values before comparison. This prevents BigQuery floating-point execution differences from creating false failures while retaining exact business-level validation.

## Known Raw Source Limitations

These issues originate in the raw dataset and are not introduced by dbt:

| Limitation | Observed count |
| --- | ---: |
| Historical clubs without a recoverable name | 451 |
| Historical-reference club dimension rows with limited source attributes | 8,236 |
| Historical players without a recoverable name | 1 |
| Appearance records with minutes above a standard 90-minute match | 3 |
| Appearance players missing from the current players source | 2 |
| Lineup rows whose player is missing from the players source | 326,036 |
| Transfers with unknown transfer fee | 14,387 |
| Transfers with unknown market value | 15,849 |
| Future-dated transfer records | 428 |
| Player-season records without a prior eligible valuation | 8,655 |

The raw `clubs.total_market_value` field is also entirely null in the current source snapshot.

### Treatment of Source Limitations

- Missing historical player and club references are retained in dimensions when an identifier exists.
- Missing descriptive fields remain `NULL`; they are not fabricated.
- Missing monetary values remain `NULL` and are excluded naturally from calculations that require them.
- Power BI visuals can use non-null `*_display` fields while canonical source fields remain available for data-quality analysis.
- Dimension `record_type` and profile-completeness fields distinguish current profiles from limited historical references.
- Fact `has_*` fields identify rows that are eligible for optional market-value and transfer-fee calculations.
- Future-dated transfer records are retained and identified by `is_future_transfer`.
- Appearance minutes are preserved because extra time can exceed 90 minutes.
- Seasonal market value remains `NULL` when no valuation exists on or before the relevant last game date.

## Definition of "100% Passing"

For this repository, "100% passing" means:

- Every configured dbt test passes.
- Every configured source freshness check passes.
- All dbt models build successfully.
- Defined transformation and relationship rules are satisfied.
- No warnings or errors are reported.

It does not mean the external raw dataset has no missing values. Raw source limitations are documented separately so downstream consumers can interpret nulls correctly.

## Power BI NULL Readiness

The mart layer is designed so missing values can be modeled without silently changing their meaning:

- Do not replace unknown fees, market values, or calculated changes with zero. A zero is a real business value; `NULL` means unavailable.
- Use display fields such as `player_name_display` and `club_name_display` for chart categories and slicers.
- Filter current-profile reporting with `player_record_type = 'current_profile'` or `club_record_type = 'current_profile'`.
- Use `has_known_transfer_fee`, `has_market_value_baseline`, `has_fee_market_value_comparison`, and related flags before calculating averages or comparison KPIs.
- Use `dim_date` for date filtering and Power BI time-intelligence measures.
- Hide `dim_clubs.total_market_value` from the report view because the current raw source snapshot contains no values for it.

See [Power BI Modeling Guide](POWER_BI_MODELING.md) for the recommended star schema and measure patterns.

## Recommended Refresh Validation

After every raw data refresh:

```bash
dbt build
dbt snapshot
dbt source freshness --selector raw_sources
dbt docs generate
```

Then compare mart row counts and review any changes in known source limitation counts. New failures should be investigated before BI or ML consumers are refreshed.
