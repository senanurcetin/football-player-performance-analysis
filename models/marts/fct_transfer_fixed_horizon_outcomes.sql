{{ config(
    partition_by={"field": "transfer_date", "data_type": "date", "granularity": "year"},
    cluster_by=["player_id", "to_club_id", "transfer_year"]
) }}

with source_limits as (

    select max(valuation_date) as latest_valuation_date

    from {{ ref('stg_player_valuations') }}
), 

transfers as (

    select *

    from {{ ref('fct_transfer_market_value_analysis') }}

    where not is_future_transfer
),

valuation_windows as (

    select
        transfers.transfer_key,

        array_agg(
            if(
                abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 90 day), day)) <= 30,
                struct(valuations.valuation_date, valuations.market_value_in_eur),
                null
            )
            ignore nulls
            order by
                if(
                    abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 90 day), day)) <= 30,
                    abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 90 day), day)),
                    null
                ),
                valuations.valuation_date
            limit 1
        )[safe_offset(0)] as outcome_90d,

        array_agg(
            if(
                abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 180 day), day)) <= 30,
                struct(valuations.valuation_date, valuations.market_value_in_eur),
                null
            )
            ignore nulls
            order by
                if(
                    abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 180 day), day)) <= 30,
                    abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 180 day), day)),
                    null
                ),
                valuations.valuation_date
            limit 1
        )[safe_offset(0)] as outcome_180d,

        array_agg(
            if(
                abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 365 day), day)) <= 30,
                struct(valuations.valuation_date, valuations.market_value_in_eur),
                null
            )
            ignore nulls
            order by
                if(
                    abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 365 day), day)) <= 30,
                    abs(date_diff(valuations.valuation_date, date_add(transfers.transfer_date, interval 365 day), day)),
                    null
                ),
                valuations.valuation_date
            limit 1
        )[safe_offset(0)] as outcome_365d

    from transfers

    left join {{ ref('stg_player_valuations') }} valuations
        on transfers.player_id = valuations.player_id
        and valuations.valuation_date between date_add(transfers.transfer_date, interval 60 day)
            and date_add(transfers.transfer_date, interval 395 day)

    group by transfers.transfer_key
),

performance_windows as (

    select
        transfers.transfer_key,
        countif(
            appearances.appearance_date between date_sub(transfers.transfer_date, interval 180 day)
                and date_sub(transfers.transfer_date, interval 1 day)
        ) as pre_180d_appearances,
        sum(
            if(
                appearances.appearance_date between date_sub(transfers.transfer_date, interval 180 day)
                    and date_sub(transfers.transfer_date, interval 1 day),
                appearances.minutes_played,
                0
            )
        ) as pre_180d_minutes,
        sum(
            if(
                appearances.appearance_date between date_sub(transfers.transfer_date, interval 180 day)
                    and date_sub(transfers.transfer_date, interval 1 day),
                appearances.goals,
                0
            )
        ) as pre_180d_goals,
        sum(
            if(
                appearances.appearance_date between date_sub(transfers.transfer_date, interval 180 day)
                    and date_sub(transfers.transfer_date, interval 1 day),
                appearances.assists,
                0
            )
        ) as pre_180d_assists,
        countif(
            appearances.appearance_date between transfers.transfer_date
                and date_add(transfers.transfer_date, interval 180 day)
        ) as post_180d_appearances,
        sum(
            if(
                appearances.appearance_date between transfers.transfer_date
                    and date_add(transfers.transfer_date, interval 180 day),
                appearances.minutes_played,
                0
            )
        ) as post_180d_minutes,
        sum(
            if(
                appearances.appearance_date between transfers.transfer_date
                    and date_add(transfers.transfer_date, interval 180 day),
                appearances.goals,
                0
            )
        ) as post_180d_goals,
        sum(
            if(
                appearances.appearance_date between transfers.transfer_date
                    and date_add(transfers.transfer_date, interval 180 day),
                appearances.assists,
                0
            )
        ) as post_180d_assists

    from transfers

    left join {{ ref('stg_appearances') }} appearances
        on transfers.player_id = appearances.player_id
        and appearances.appearance_date between date_sub(transfers.transfer_date, interval 180 day)
            and date_add(transfers.transfer_date, interval 180 day)

    group by transfers.transfer_key
)

select
    transfers.transfer_key,
    transfers.player_id,
    transfers.player_name,
    transfers.position,
    transfers.sub_position,
    transfers.age_at_transfer,
    case
        when transfers.age_at_transfer is null then 'unknown'
        when transfers.age_at_transfer < 21 then 'under_21'
        when transfers.age_at_transfer < 25 then '21_to_24'
        when transfers.age_at_transfer < 29 then '25_to_28'
        when transfers.age_at_transfer < 33 then '29_to_32'
        else '33_plus'
    end as age_band_at_transfer,
    transfers.transfer_date,
    transfers.transfer_year,
    transfers.transfer_season,
    transfers.from_club_id,
    transfers.from_club_name,
    transfers.to_club_id,
    transfers.to_club_name,
    transfers.transfer_fee,
    transfers.market_value_baseline,
    transfers.fee_market_value_difference,
    transfers.fee_market_value_difference_pct,
    case
        when transfers.fee_market_value_difference_pct is null then 'unavailable'
        when transfers.fee_market_value_difference_pct < -20 then 'discount_20_plus'
        when transfers.fee_market_value_difference_pct <= 20 then 'within_20_pct'
        else 'premium_20_plus'
    end as fee_premium_band,
    transfers.valuation_context_change,
    transfers.has_known_transfer_fee,
    transfers.has_fee_market_value_comparison,

    date_add(transfers.transfer_date, interval 90 day) as target_90d_date,
    valuation_windows.outcome_90d.valuation_date as valuation_90d_date,
    valuation_windows.outcome_90d.market_value_in_eur as market_value_90d,
    date_diff(valuation_windows.outcome_90d.valuation_date, transfers.transfer_date, day)
        as days_to_90d_valuation,
    valuation_windows.outcome_90d.market_value_in_eur - transfers.market_value_baseline
        as market_value_change_90d,
    round(
        safe_divide(
            valuation_windows.outcome_90d.market_value_in_eur - transfers.market_value_baseline,
            nullif(transfers.market_value_baseline, 0)
        ) * 100,
        2
    ) as market_value_change_90d_pct,
    valuation_windows.outcome_90d.valuation_date is not null
        and transfers.market_value_baseline is not null as has_90d_outcome,
    case
        when transfers.market_value_baseline is null then 'missing_baseline'
        when valuation_windows.outcome_90d.valuation_date is not null
            then 'observed'
        when date_add(transfers.transfer_date, interval 120 day)
            > least(current_date(), source_limits.latest_valuation_date) then 'not_yet_observable'
        else 'missing_followup'
    end as outcome_90d_status,

    date_add(transfers.transfer_date, interval 180 day) as target_180d_date,
    valuation_windows.outcome_180d.valuation_date as valuation_180d_date,
    valuation_windows.outcome_180d.market_value_in_eur as market_value_180d,
    date_diff(valuation_windows.outcome_180d.valuation_date, transfers.transfer_date, day)
        as days_to_180d_valuation,
    valuation_windows.outcome_180d.market_value_in_eur - transfers.market_value_baseline
        as market_value_change_180d,
    round(
        safe_divide(
            valuation_windows.outcome_180d.market_value_in_eur - transfers.market_value_baseline,
            nullif(transfers.market_value_baseline, 0)
        ) * 100,
        2
    ) as market_value_change_180d_pct,
    valuation_windows.outcome_180d.valuation_date is not null
        and transfers.market_value_baseline is not null as has_180d_outcome,
    case
        when transfers.market_value_baseline is null then 'missing_baseline'
        when valuation_windows.outcome_180d.valuation_date is not null
            then 'observed'
        when date_add(transfers.transfer_date, interval 210 day)
            > least(current_date(), source_limits.latest_valuation_date) then 'not_yet_observable'
        else 'missing_followup'
    end as outcome_180d_status,

    date_add(transfers.transfer_date, interval 365 day) as target_365d_date,
    valuation_windows.outcome_365d.valuation_date as valuation_365d_date,
    valuation_windows.outcome_365d.market_value_in_eur as market_value_365d,
    date_diff(valuation_windows.outcome_365d.valuation_date, transfers.transfer_date, day)
        as days_to_365d_valuation,
    valuation_windows.outcome_365d.market_value_in_eur - transfers.market_value_baseline
        as market_value_change_365d,
    round(
        safe_divide(
            valuation_windows.outcome_365d.market_value_in_eur - transfers.market_value_baseline,
            nullif(transfers.market_value_baseline, 0)
        ) * 100,
        2
    ) as market_value_change_365d_pct,
    valuation_windows.outcome_365d.valuation_date is not null
        and transfers.market_value_baseline is not null as has_365d_outcome,
    case
        when transfers.market_value_baseline is null then 'missing_baseline'
        when valuation_windows.outcome_365d.valuation_date is not null
            then 'observed'
        when date_add(transfers.transfer_date, interval 395 day)
            > least(current_date(), source_limits.latest_valuation_date) then 'not_yet_observable'
        else 'missing_followup'
    end as outcome_365d_status,

    performance_windows.pre_180d_appearances,
    performance_windows.pre_180d_minutes,
    performance_windows.pre_180d_goals,
    performance_windows.pre_180d_assists,
    performance_windows.post_180d_appearances,
    performance_windows.post_180d_minutes,
    performance_windows.post_180d_goals,
    performance_windows.post_180d_assists,
    performance_windows.pre_180d_appearances > 0 as has_pre_180d_performance,
    performance_windows.post_180d_appearances > 0 as has_post_180d_performance,
    performance_windows.post_180d_minutes - performance_windows.pre_180d_minutes
        as minutes_change_post_vs_pre_180d,
    performance_windows.post_180d_goals - performance_windows.pre_180d_goals
        as goals_change_post_vs_pre_180d,
    performance_windows.post_180d_assists - performance_windows.pre_180d_assists
        as assists_change_post_vs_pre_180d,
    source_limits.latest_valuation_date as source_latest_valuation_date

from transfers

left join valuation_windows using (transfer_key)
left join performance_windows using (transfer_key)
cross join source_limits
