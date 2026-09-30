select
    transfer_key

from {{ ref('fct_transfer_market_value_analysis') }}

where market_value_baseline
        is distinct from coalesce(transfer_record_market_value, prior_market_value)
    or market_value_baseline_date
        is distinct from case
            when transfer_record_market_value is not null then transfer_date
            else prior_valuation_date
        end
    or days_since_market_value_baseline
        is distinct from date_diff(transfer_date, market_value_baseline_date, day)
    or fee_market_value_difference
        is distinct from transfer_fee - market_value_baseline
    or fee_market_value_difference_pct
        is distinct from round(
            safe_divide(
                transfer_fee - market_value_baseline,
                nullif(market_value_baseline, 0)
            ) * 100,
            2
        )
    or fee_to_market_value_ratio
        is distinct from round(
            safe_divide(transfer_fee, nullif(market_value_baseline, 0)),
            4
        )
    or market_value_change_after_transfer
        is distinct from next_market_value - market_value_baseline
    or market_value_change_after_transfer_pct
        is distinct from round(
            safe_divide(
                next_market_value - market_value_baseline,
                nullif(market_value_baseline, 0)
            ) * 100,
            2
        )
    or days_since_previous_transfer
        is distinct from date_diff(transfer_date, previous_transfer_date, day)
    or days_to_next_transfer
        is distinct from date_diff(next_transfer_date, transfer_date, day)
    or days_since_prior_valuation
        is distinct from date_diff(transfer_date, prior_valuation_date, day)
    or days_to_next_valuation
        is distinct from date_diff(next_valuation_date, transfer_date, day)
