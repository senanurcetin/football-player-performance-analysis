{{ config(cluster_by=["transfer_risk_category", "club_id"]) }}

with club_population as (

    select
        to_club_id as club_id,
        any_value(to_club_name having max transfer_date) as club_name,
        count(*) as total_incoming_transfers,
        countif(has_known_transfer_fee) as transfers_with_known_fee,
        round(100 * safe_divide(countif(has_known_transfer_fee), count(*)), 2)
            as known_fee_coverage_pct,
        countif(has_365d_outcome) as observed_365d_transfers,
        round(100 * safe_divide(countif(has_365d_outcome), count(*)), 2)
            as outcome_365d_coverage_pct,
        round(avg(fee_market_value_difference_pct), 2) as avg_overpay_pct

    from {{ ref('fct_transfer_fixed_horizon_outcomes') }}

    where to_club_id is not null

    group by to_club_id
),

label_summary as (

    select
        to_club_id as club_id,
        countif(is_successful_transfer = 1) as successful_transfers,
        countif(is_successful_transfer = 0) as unsuccessful_transfers,
        round(100 * avg(is_successful_transfer), 2) as transfer_success_rate_pct

    from {{ ref('fct_transfer_success_labels') }}

    where to_club_id is not null

    group by to_club_id
)

select
    population.club_id,
    population.club_name,
    population.total_incoming_transfers,
    population.transfers_with_known_fee,
    population.known_fee_coverage_pct,
    population.observed_365d_transfers,
    population.outcome_365d_coverage_pct,
    population.avg_overpay_pct,
    coalesce(labels.successful_transfers, 0) as successful_transfers,
    coalesce(labels.unsuccessful_transfers, 0) as unsuccessful_transfers,
    labels.transfer_success_rate_pct,
    population.observed_365d_transfers >= 30 as meets_minimum_sample_size,
    case
        when population.observed_365d_transfers < 30 then 'insufficient_data'
        when population.avg_overpay_pct > 30
            and labels.transfer_success_rate_pct < 40 then 'high_risk'
        when population.avg_overpay_pct > 10
            or labels.transfer_success_rate_pct < 50 then 'medium_risk'
        else 'low_risk'
    end as transfer_risk_category

from club_population population

left join label_summary labels using (club_id)
