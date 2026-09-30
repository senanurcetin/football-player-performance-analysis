select
    performance.player_id,
    performance.season,
    performance.competition_id

from {{ ref('int_player_season_performance') }} performance

left join {{ ref('stg_player_valuations') }} valuations
    on performance.player_id = valuations.player_id
    and performance.season_market_value_date = valuations.valuation_date

where
    (performance.season_market_value is null)
        != (performance.season_market_value_date is null)
    or (
        performance.season_market_value is not null
        and (
            valuations.player_id is null
            or performance.season_market_value is distinct from valuations.market_value_in_eur
        )
    )
