select
    p.player_id,
    p.player_name,

    p.position,
    p.sub_position,
    p.preferred_foot,

    p.country_of_birth,
    p.country_of_citizenship,

    p.birth_date,

    date_diff(current_date(), p.birth_date, year)
        - if(
            format_date('%m%d', current_date()) < format_date('%m%d', p.birth_date),
            1,
            0
        ) as age,

    p.height_in_cm,
    p.agent_name,

    p.current_club_id,
    p.current_club_name,

    p.international_caps,
    p.international_goals,

    p.market_value_in_eur,

    perf.matches_played,
    perf.total_goals,
    perf.total_assists,
    perf.total_minutes_played,
    perf.goals_per_match,
    perf.assists_per_match,
    perf.goals_per_90,
    perf.assists_per_90,

    mv.first_market_value,
    mv.current_market_value,
    mv.highest_market_value,
    mv.market_value_growth,
    mv.market_value_growth_pct,

    tr.transfer_count,
    tr.total_transfer_fee,
    tr.latest_transfer_fee

from {{ ref('stg_players') }} p

left join {{ ref('int_player_performance_summary') }} perf
    on p.player_id = perf.player_id

left join {{ ref('int_player_market_value_summary') }} mv
    on p.player_id = mv.player_id

left join {{ ref('int_transfer_summary') }} tr
    on p.player_id = tr.player_id
