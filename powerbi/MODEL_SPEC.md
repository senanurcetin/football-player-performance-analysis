# Power BI Model Specification

Use `football_mart` as the supported BI interface.

## Decision-Facing Pages

- Transfer cohort: `fct_transfer_cohort_performance`
- Transfer fixed-horizon outcomes: `fct_transfer_fixed_horizon_outcomes`
- Transfer coverage and bias: `fct_data_coverage_bias`
- Club transfer portfolio: `fct_club_transfer_portfolio`
- Club transfer risk: `fct_club_risk_profile`
- Player rolling form: `fct_player_rolling_form`
- Club season performance: `fct_club_season_performance`
- Match context: `fct_match`
- Agent portfolio: `fct_agent_portfolio`

Every transfer page must display population count, observed outcome count, coverage percentage, and reliability or bias-risk status.

Do not mix rows below the minimum sample size into decision-facing rankings. Do not present observational comparisons as causal findings.
