# Power BI Modeling Guide

## Report File Format

The report is a PBIP project stored at `powerbi/workspace/FootballPlayerAnalysis/`. It uses the PBIR v4 format: all page and visual definitions live under `Report/definition/` as plain JSON files. This makes every visual property version-controllable and diff-readable.

**Requirements:** Power BI Desktop June 2026 (v2.155+) with the **Enhanced Report Format** preview feature enabled.

**Format rules:**
- Never add or restore `Report/report.json` — its presence alongside `Report/definition/` causes a load error (`You cannot have both PBIR and PBIR-Legacy formats in the same PBIP`).
- The legacy `Report/sections/` directory is retained for historical reference only.
- Visual definitions follow the schema at `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json`.

**Opening the report:** Open `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` directly in PBI Desktop. Data requires a BigQuery connection; refresh credentials from `football.json` service account if prompted.

## Recommended Dataset

Connect Power BI to the BigQuery `football_mart` dataset. The mart layer is materialized as tables and is the supported BI interface. Do not build report relationships directly against staging or intermediate views.

Use `powerbi/MODEL_SPEC.md` and `powerbi/MEASURES.dax` as the version-controlled report contract. Use `docs/KPI_DICTIONARY.md` for metric definitions and population rules.

## Recommended Star Schema

| Dimension | Recommended fact relationships |
| --- | --- |
| `dim_players` | Player facts on `player_id` |
| `dim_clubs` | Club facts and transfer club roles on `club_id` |
| `dim_competitions` | Competition facts on `competition_id` |
| `dim_date` | Fact business dates on `date_day` |

Use single-direction, one-to-many relationships from dimensions to facts. For transfer analysis, `transfer_date` should normally be the active date relationship. Prior valuation, next valuation, and other date roles should be inactive relationships used with `USERELATIONSHIP`, or separate role-playing date dimensions.

## NULL Semantics

Canonical nullable fields preserve source truth:

- `NULL` monetary values mean unavailable or unknown, not zero.
- `0` transfer fee is a recorded zero value and remains distinguishable through `fee_status = 'zero_fee'`.
- Historical dimension rows can contain limited attributes because only their identifiers were available from historical facts.
- Calculated comparison values remain `NULL` when their required inputs are unavailable.

Do not use Power Query or DAX to replace unknown transfer fees, market values, or value changes with zero. Doing so changes totals, averages, and comparison populations.

## Fields for Visuals

Use these non-null fields for visual categories and slicers:

| Canonical field | Visual field |
| --- | --- |
| `dim_players.player_name` | `dim_players.player_name_display` |
| `dim_players.position` | `dim_players.position_display` |
| `dim_players.current_club_name` | `dim_players.current_club_name_display` |
| `dim_clubs.club_name` | `dim_clubs.club_name_display` |

Use canonical fields when analyzing missing-data rates. Use `player_record_type`, `club_record_type`, and profile-completeness fields to separate current source profiles from limited historical references.

For current club profile reports, filter `club_record_type = "current_profile"`. The current dimension contains 796 current profiles and 8,236 historical-reference rows retained for referential integrity.

## Availability Flags

Use fact-table availability flags before calculating KPIs from optional values:

| Analysis | Required filter |
| --- | --- |
| Transfer fee averages | `has_known_transfer_fee = TRUE` |
| Fee-to-market-value comparison | `has_fee_market_value_comparison = TRUE` |
| Transfer market-value baseline | `has_market_value_baseline = TRUE` |
| Post-transfer value movement | `has_post_transfer_value_change = TRUE` |
| Current player market value | `has_current_market_value = TRUE` |
| Seasonal market value | `has_season_market_value = TRUE` |
| Valuation club or competition breakdown | `has_club_context = TRUE` or `has_competition_context = TRUE` |

Example DAX:

```dax
Average Fee Premium % =
CALCULATE(
    AVERAGE(fct_transfer_market_value_analysis[fee_market_value_difference_pct]),
    fct_transfer_market_value_analysis[has_fee_market_value_comparison] = TRUE(),
    fct_transfer_market_value_analysis[is_future_transfer] = FALSE()
)
```

## Date Modeling

Mark `dim_date[date_day]` as the Power BI date table. Sort:

- `calendar_month_name` by `calendar_month_number`
- `calendar_month_short_name` by `calendar_month_number`
- `calendar_year_month` by `calendar_year_month_sort`

The dimension is continuous from July 1, 1993 through June 30, 2030 in the current source snapshot. It contains 13,514 rows and is protected by uniqueness, not-null, and continuity tests.

## Report View Recommendations

- Hide technical keys from report consumers after relationships are created.
- Hide `dim_clubs.total_market_value`; it is entirely null in the current raw source snapshot.
- Keep `has_*`, `record_type`, completeness, status, and future-date fields visible for filters and quality checks.
- Default historical transfer reports to `is_future_transfer = FALSE`.
- Keep NULL values in imported data and handle visual labels with the provided display fields.

## Refresh Gate

Refresh Power BI only after these commands pass:

```bash
dbt source freshness --selector raw_sources
dbt snapshot
dbt build
python scripts/check_documentation_coverage.py
```

Review `fct_analytics_refresh_audit` for volume changes and `fct_data_coverage_bias` for coverage risk. Every transfer-outcome page must show transfer population, observed outcomes, outcome coverage, and reliability or bias status.

## ML Evaluation Report

For a player market value model evaluation page, connect to `football_ml.ml_player_market_value_evaluation_predictions`. This table contains only the 2024-2025 temporal backtest seasons and can relate to:

- `dim_players` on `player_id`
- `dim_competitions` on `competition_id`
- `dim_date` on `target_market_value_date`

Recommended visuals include actual versus predicted value, absolute error by position, WAPE by season, and the largest over- and under-predictions. Do not present this evaluation table as a live future forecast.

For a current player value estimation page, connect to `football_ml.ml_player_market_value_current_predictions`. This table contains one current estimate for each player active in the latest observed season. Use `prediction_as_of_date` visibly in the report so consumers understand the estimate date.

For decision-facing visuals, filter `prediction_quality_status` to `high` or `medium`. Display `prediction_interval_band`, `prediction_lower_eur`, and `prediction_upper_eur` with the point estimate. Limited-quality rows intentionally use the governed previous-value baseline fallback; keep them on a separate data-quality page rather than mixing them into model-led rankings.

Use `football_ml.ml_player_market_value_evaluation_metrics` for season, position, sub-position, age-band, competition, country, value-band, prior-value availability, and quality-segment performance. Filter decision-facing segment results to `meets_minimum_sample_size = TRUE`. Use `football_ml.ml_player_market_value_feature_drift` as a refresh gate and review every `significant` PSI status. Use `football_ml.ml_player_market_value_model_registry` to identify the model version behind each refresh.

Use `football_ml.ml_player_market_value_quality_gates` on the model-monitoring page. Decision-facing reports should only refresh when all `blocking` rows pass. Use `football_ml.ml_player_market_value_feature_importance` for predictive-driver visuals, and label them as model dependence rather than causal explanation.

The latest validation passed all 241 project tests, all 43 ML-feature tests, and documentation for all 878 model columns.
