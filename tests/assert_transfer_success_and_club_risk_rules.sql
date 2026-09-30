select transfer_key as invalid_key, 'transfer_success_label' as model_name
from {{ ref('fct_transfer_success_labels') }}
where label_horizon_days != 365
    or label_status != 'observed'
    or success_threshold_pct != 20
    or is_successful_transfer != if(market_value_change_at_horizon_pct >= 20, 1, 0)

union all

select cast(club_id as string), 'club_risk_profile'
from {{ ref('fct_club_risk_profile') }}
where observed_365d_transfers != successful_transfers + unsuccessful_transfers
    or outcome_365d_coverage_pct not between 0 and 100
    or known_fee_coverage_pct not between 0 and 100
    or transfer_success_rate_pct not between 0 and 100
    or meets_minimum_sample_size != (observed_365d_transfers >= 30)
    or (not meets_minimum_sample_size and transfer_risk_category != 'insufficient_data')
