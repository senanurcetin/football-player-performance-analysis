with ranked_values as (

    select
        player_id,
        valuation_date,
        market_value_in_eur,
        current_club_id,
        current_club_name,
        player_club_domestic_competition_id,

        row_number() over (
            partition by player_id
            order by valuation_date asc
        ) as first_value_rank,

        row_number() over (
            partition by player_id
            order by valuation_date desc
        ) as latest_value_rank

    from {{ ref('stg_player_valuations') }}

    where market_value_in_eur is not null
),

summary as (

    select
        player_id,

        min(valuation_date) as first_valuation_date,
        max(valuation_date) as latest_valuation_date,

        max(market_value_in_eur) as highest_market_value,

        max(case when first_value_rank = 1 then market_value_in_eur end) as first_market_value,
        max(case when latest_value_rank = 1 then market_value_in_eur end) as current_market_value,

        max(case when latest_value_rank = 1 then current_club_id end) as latest_club_id,
        max(case when latest_value_rank = 1 then current_club_name end) as latest_club_name

    from ranked_values

    group by player_id
)

select
    player_id,
    first_valuation_date,
    latest_valuation_date,

    first_market_value,
    current_market_value,
    highest_market_value,

    current_market_value - first_market_value as market_value_growth,

    round(
        safe_divide(current_market_value - first_market_value, nullif(first_market_value, 0)) * 100,
        2
    ) as market_value_growth_pct,

    latest_club_id,
    latest_club_name

from summary