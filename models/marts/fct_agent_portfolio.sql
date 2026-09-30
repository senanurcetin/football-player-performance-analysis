with player_transfer_summary as (

    select
        player_id,
        count(*) as transfer_count,
        count(transfer_fee) as known_fee_transfer_count,
        sum(transfer_fee) as total_known_transfer_fee,
        max(transfer_fee) as max_known_transfer_fee

    from {{ ref('fct_transfers') }}

    group by player_id
)

select
    players.agent_name,
    count(*) as player_count,
    countif(performance.has_current_market_value) as players_with_current_market_value,
    sum(performance.market_value_in_eur) as total_current_market_value,
    round(avg(performance.market_value_in_eur), 2) as avg_current_market_value,
    approx_quantiles(performance.market_value_in_eur, 100 ignore nulls)[safe_offset(50)]
        as median_current_market_value,
    max(performance.market_value_in_eur) as max_current_market_value,
    sum(performance.matches_played) as total_player_matches,
    sum(performance.total_goals) as total_player_goals,
    sum(performance.total_assists) as total_player_assists,
    sum(transfers.transfer_count) as total_transfer_records,
    sum(transfers.known_fee_transfer_count) as known_fee_transfer_records,
    sum(transfers.total_known_transfer_fee) as total_known_transfer_fee,
    max(transfers.max_known_transfer_fee) as max_known_transfer_fee,
    round(
        100 * safe_divide(
            sum(transfers.known_fee_transfer_count),
            sum(transfers.transfer_count)
        ),
        2
    ) as transfer_fee_coverage_pct,
    countif(players.player_profile_completeness_status = 'complete') as complete_profile_players,
    round(
        100 * safe_divide(
            countif(players.player_profile_completeness_status = 'complete'),
            count(*)
        ),
        2
    ) as complete_profile_player_pct

from {{ ref('dim_players') }} players

left join {{ ref('fct_player_performance') }} performance
    on players.player_id = performance.player_id

left join player_transfer_summary transfers
    on players.player_id = transfers.player_id

where players.agent_name is not null
    and players.player_record_type = 'current_profile'

group by players.agent_name
