with expected as (

    select
        player_id,
        min(valuation_date) as first_valuation_date,
        max(valuation_date) as latest_valuation_date,
        array_agg(market_value_in_eur order by valuation_date asc limit 1)[offset(0)]
            as first_market_value,
        array_agg(market_value_in_eur order by valuation_date desc limit 1)[offset(0)]
            as current_market_value,
        max(market_value_in_eur) as highest_market_value,
        array_agg(current_club_id order by valuation_date desc limit 1)[offset(0)]
            as latest_club_id,
        array_agg(current_club_name order by valuation_date desc limit 1)[offset(0)]
            as latest_club_name

    from {{ ref('stg_player_valuations') }}

    where market_value_in_eur is not null

    group by player_id
)

select
    coalesce(expected.player_id, actual.player_id) as player_id

from expected

full outer join {{ ref('int_player_market_value_summary') }} actual
    on expected.player_id = actual.player_id

where expected.player_id is null
    or actual.player_id is null
    or expected.first_valuation_date != actual.first_valuation_date
    or expected.latest_valuation_date != actual.latest_valuation_date
    or expected.first_market_value != actual.first_market_value
    or expected.current_market_value != actual.current_market_value
    or expected.highest_market_value != actual.highest_market_value
    or expected.latest_club_id is distinct from actual.latest_club_id
    or expected.latest_club_name is distinct from actual.latest_club_name
