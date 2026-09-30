with duplicate_counts as (

    select 'fct_match' as model_name, count(*) - count(distinct game_id) as duplicate_rows
    from {{ ref('fct_match') }}

    union all

    select 'fct_player_match_performance', count(*) - count(distinct appearance_id)
    from {{ ref('fct_player_match_performance') }}

    union all

    select 'fct_player_rolling_form', count(*) - count(distinct appearance_id)
    from {{ ref('fct_player_rolling_form') }}

    union all

    select
        'fct_club_season_performance',
        count(*) - count(distinct to_json_string(struct(club_id, season, competition_id)))
    from {{ ref('fct_club_season_performance') }}

    union all

    select
        'fct_club_transfer_portfolio',
        count(*) - count(distinct to_json_string(struct(club_id, transfer_season)))
    from {{ ref('fct_club_transfer_portfolio') }}

    union all

    select 'fct_transfer_fixed_horizon_outcomes', count(*) - count(distinct transfer_key)
    from {{ ref('fct_transfer_fixed_horizon_outcomes') }}

    union all

    select
        'fct_transfer_cohort_performance',
        count(*) - count(distinct to_json_string(struct(horizon_days, cohort_type, cohort_value)))
    from {{ ref('fct_transfer_cohort_performance') }}

    union all

    select
        'fct_data_coverage_bias',
        count(*) - count(distinct to_json_string(struct(segment_type, segment_value)))
    from {{ ref('fct_data_coverage_bias') }}

    union all

    select 'fct_transfer_success_labels', count(*) - count(distinct transfer_key)
    from {{ ref('fct_transfer_success_labels') }}

    union all

    select 'fct_club_risk_profile', count(*) - count(distinct club_id)
    from {{ ref('fct_club_risk_profile') }}
)

select *
from duplicate_counts
where duplicate_rows != 0
