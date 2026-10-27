# Power BI Model Specification

**LATEST REPORT (27 October):** [Workintech versioned PBIP](workintech-20261027/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip) is an editable Desktop copy with current user-supplied screenshots documented [here](../docs/assets/screenshots/README.md). It retains all original 13 pages. 31 governed source contract tables were verified, but the owner-edited PBIP additionally contains 34 other imported Workintech table definitions that require semantic reconciliation. See [execution status](../docs/WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md).


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
