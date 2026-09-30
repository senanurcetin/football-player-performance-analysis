select
    analysis.transfer_key

from {{ ref('fct_transfer_market_value_analysis') }} analysis

where
    (
        analysis.prior_valuation_date is null
        and exists (
            select 1
            from {{ ref('stg_player_valuations') }} valuations
            where valuations.player_id = analysis.player_id
                and valuations.valuation_date <= analysis.transfer_date
        )
    )
    or (
        analysis.prior_valuation_date is not null
        and (
            analysis.prior_valuation_date > analysis.transfer_date
            or not exists (
                select 1
                from {{ ref('stg_player_valuations') }} valuations
                where valuations.player_id = analysis.player_id
                    and valuations.valuation_date = analysis.prior_valuation_date
                    and valuations.market_value_in_eur
                        is not distinct from analysis.prior_market_value
            )
            or exists (
                select 1
                from {{ ref('stg_player_valuations') }} valuations
                where valuations.player_id = analysis.player_id
                    and valuations.valuation_date > analysis.prior_valuation_date
                    and valuations.valuation_date <= analysis.transfer_date
            )
        )
    )
    or (
        analysis.next_valuation_date is null
        and exists (
            select 1
            from {{ ref('stg_player_valuations') }} valuations
            where valuations.player_id = analysis.player_id
                and valuations.valuation_date > analysis.transfer_date
        )
    )
    or (
        analysis.next_valuation_date is not null
        and (
            analysis.next_valuation_date <= analysis.transfer_date
            or not exists (
                select 1
                from {{ ref('stg_player_valuations') }} valuations
                where valuations.player_id = analysis.player_id
                    and valuations.valuation_date = analysis.next_valuation_date
                    and valuations.market_value_in_eur
                        is not distinct from analysis.next_market_value
            )
            or exists (
                select 1
                from {{ ref('stg_player_valuations') }} valuations
                where valuations.player_id = analysis.player_id
                    and valuations.valuation_date < analysis.next_valuation_date
                    and valuations.valuation_date > analysis.transfer_date
            )
        )
    )
