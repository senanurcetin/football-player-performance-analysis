-- Observational comparison, not a randomized A/B test or causal estimate.
with matched_strata as (

    select
        transfer_year,
        position,
        age_band_at_transfer,
        fee_premium_band,
        valuation_context_change as treatment_group,
        countif(has_365d_outcome) as observed_transfers,
        avg(if(has_365d_outcome, market_value_change_365d_pct, null))
            as avg_market_value_change_365d_pct

    from {{ ref('fct_transfer_fixed_horizon_outcomes') }}

    where valuation_context_change in ('same_competition', 'country_change')

    group by
        transfer_year,
        position,
        age_band_at_transfer,
        fee_premium_band,
        valuation_context_change
),

eligible_strata as (

    select
        transfer_year,
        position,
        age_band_at_transfer,
        fee_premium_band

    from matched_strata

    group by transfer_year, position, age_band_at_transfer, fee_premium_band

    having countif(treatment_group = 'same_competition' and observed_transfers >= 30) = 1
        and countif(treatment_group = 'country_change' and observed_transfers >= 30) = 1
)

select
    transfer_year,
    position,
    age_band_at_transfer,
    fee_premium_band,
    max(if(treatment_group = 'same_competition', observed_transfers, null))
        as same_competition_observed_transfers,
    max(if(treatment_group = 'country_change', observed_transfers, null))
        as country_change_observed_transfers,
    round(max(if(treatment_group = 'same_competition', avg_market_value_change_365d_pct, null)), 2)
        as same_competition_avg_change_365d_pct,
    round(max(if(treatment_group = 'country_change', avg_market_value_change_365d_pct, null)), 2)
        as country_change_avg_change_365d_pct,
    round(
        max(if(treatment_group = 'country_change', avg_market_value_change_365d_pct, null))
        - max(if(treatment_group = 'same_competition', avg_market_value_change_365d_pct, null)),
        2
    ) as observational_difference_pct

from matched_strata

inner join eligible_strata using (
    transfer_year,
    position,
    age_band_at_transfer,
    fee_premium_band
)

group by transfer_year, position, age_band_at_transfer, fee_premium_band

order by transfer_year, position, age_band_at_transfer, fee_premium_band
