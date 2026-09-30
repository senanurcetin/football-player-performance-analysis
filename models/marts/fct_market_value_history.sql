select

    mv.player_id,

    p.player_name,
    p.position,
    p.sub_position,

    mv.valuation_date,

    mv.market_value_in_eur,

    mv.current_club_id,
    mv.current_club_name,

    mv.player_club_domestic_competition_id as competition_id,

    mv.current_club_id is not null as has_club_context,
    mv.player_club_domestic_competition_id is not null
        as has_competition_context

from {{ ref('stg_player_valuations') }} mv

left join {{ ref('dim_players') }} p
    on mv.player_id = p.player_id
