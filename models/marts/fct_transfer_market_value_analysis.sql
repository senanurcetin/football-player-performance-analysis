{{ config(
    partition_by={
        "field": "transfer_date",
        "data_type": "date",
        "granularity": "year"
    },
    cluster_by=["player_id", "to_club_id", "from_club_id"]
) }}

with transfers as (

    select
        to_hex(
            md5(
                to_json_string(
                    struct(
                        player_id,
                        transfer_date,
                        transfer_season,
                        from_club_id,
                        to_club_id,
                        from_club_name,
                        to_club_name,
                        transfer_fee,
                        market_value_in_eur,
                        player_name
                    )
                )
            )
        ) as transfer_key,

        *

    from {{ ref('stg_transfers') }}
),

ordered_transfers as (

    select
        *,

        row_number() over (
            partition by player_id
            order by
                transfer_date,
                transfer_key
        ) as transfer_sequence_number,

        count(*) over (
            partition by player_id
        ) as player_transfer_count,

        count(transfer_fee) over (
            partition by player_id
        ) as known_fee_transfer_count,

        sum(transfer_fee) over (
            partition by player_id
            order by
                transfer_date,
                transfer_key
            rows between unbounded preceding and current row
        ) as cumulative_known_transfer_fee,

        lag(transfer_date) over (
            partition by player_id
            order by
                transfer_date,
                transfer_key
        ) as previous_transfer_date,

        lead(transfer_date) over (
            partition by player_id
            order by
                transfer_date,
                transfer_key
        ) as next_transfer_date

    from transfers
),

valuation_context as (

    select
        transfers.transfer_key,

        array_agg(
            if(
                valuations.valuation_date <= transfers.transfer_date,
                struct(
                    valuations.valuation_date,
                    valuations.market_value_in_eur,
                    valuations.current_club_id,
                    valuations.current_club_name,
                    valuations.player_club_domestic_competition_id as competition_id
                ),
                null
            )
            ignore nulls
            order by
                if(
                    valuations.valuation_date <= transfers.transfer_date,
                    valuations.valuation_date,
                    null
                ) desc
            limit 1
        )[safe_offset(0)] as prior_valuation,

        array_agg(
            if(
                valuations.valuation_date > transfers.transfer_date,
                struct(
                    valuations.valuation_date,
                    valuations.market_value_in_eur,
                    valuations.current_club_id,
                    valuations.current_club_name,
                    valuations.player_club_domestic_competition_id as competition_id
                ),
                null
            )
            ignore nulls
            order by
                if(
                    valuations.valuation_date > transfers.transfer_date,
                    valuations.valuation_date,
                    null
                ) asc
            limit 1
        )[safe_offset(0)] as next_valuation

    from ordered_transfers transfers

    left join {{ ref('stg_player_valuations') }} valuations
        on transfers.player_id = valuations.player_id

    group by transfers.transfer_key
),

enriched as (

    select
        transfers.*,

        players.player_name as dimension_player_name,
        players.position,
        players.sub_position,
        players.birth_date,
        players.country_of_citizenship,

        coalesce(nullif(transfers.from_club_name, ''), from_clubs.club_name)
            as best_available_from_club_name,
        coalesce(nullif(transfers.to_club_name, ''), to_clubs.club_name)
            as best_available_to_club_name,

        valuation_context.prior_valuation,
        valuation_context.next_valuation,

        prior_competitions.competition_name as prior_competition_name,
        prior_competitions.country_name as prior_competition_country_name,
        prior_competitions.confederation as prior_competition_confederation,

        next_competitions.competition_name as next_competition_name,
        next_competitions.country_name as next_competition_country_name,
        next_competitions.confederation as next_competition_confederation,

        market_values.first_valuation_date,
        market_values.latest_valuation_date,
        market_values.first_market_value,
        market_values.current_market_value,
        market_values.highest_market_value,
        market_values.market_value_growth as career_market_value_growth,
        market_values.market_value_growth_pct as career_market_value_growth_pct,

        transfer_summary.total_transfer_fee,
        transfer_summary.avg_transfer_fee,
        transfer_summary.max_transfer_fee

    from ordered_transfers transfers

    left join valuation_context
        on transfers.transfer_key = valuation_context.transfer_key

    left join {{ ref('dim_players') }} players
        on transfers.player_id = players.player_id

    left join {{ ref('dim_clubs') }} from_clubs
        on transfers.from_club_id = from_clubs.club_id

    left join {{ ref('dim_clubs') }} to_clubs
        on transfers.to_club_id = to_clubs.club_id

    left join {{ ref('dim_competitions') }} prior_competitions
        on valuation_context.prior_valuation.competition_id
            = prior_competitions.competition_id

    left join {{ ref('dim_competitions') }} next_competitions
        on valuation_context.next_valuation.competition_id
            = next_competitions.competition_id

    left join {{ ref('int_player_market_value_summary') }} market_values
        on transfers.player_id = market_values.player_id

    left join {{ ref('int_transfer_summary') }} transfer_summary
        on transfers.player_id = transfer_summary.player_id
),

calculated as (

    select
        *,

        coalesce(market_value_in_eur, prior_valuation.market_value_in_eur)
            as market_value_baseline,

        case
            when market_value_in_eur is not null then transfer_date
            else prior_valuation.valuation_date
        end as market_value_baseline_date,

        case
            when market_value_in_eur is not null then 'transfer_record'
            when prior_valuation.market_value_in_eur is not null then 'latest_prior_valuation'
            else 'unavailable'
        end as market_value_baseline_source

    from enriched
)

select
    transfer_key,

    player_id,
    coalesce(nullif(player_name, ''), dimension_player_name) as player_name,
    position,

    case position
        when 'Attack' then 'Forvet'
        when 'Defender' then 'Defans'
        when 'Goalkeeper' then 'Kaleci'
        when 'Midfield' then 'Orta Saha'
        when 'Missing' then 'Bilinmiyor'
        else coalesce(position, 'Bilinmiyor')
    end as pozisyon_tr,

    sub_position,
    birth_date,
    country_of_citizenship,

    date_diff(transfer_date, birth_date, year)
        - if(
            format_date('%m%d', transfer_date) < format_date('%m%d', birth_date),
            1,
            0
        ) as age_at_transfer,

    transfer_date,
    extract(year from transfer_date) as transfer_year,
    extract(month from transfer_date) as transfer_month,
    transfer_season,
    transfer_date > current_date() as is_future_transfer,

    transfer_sequence_number,
    player_transfer_count,
    known_fee_transfer_count,
    transfer_sequence_number = player_transfer_count as is_latest_transfer,

    previous_transfer_date,
    date_diff(transfer_date, previous_transfer_date, day) as days_since_previous_transfer,
    next_transfer_date,
    date_diff(next_transfer_date, transfer_date, day) as days_to_next_transfer,

    from_club_id,
    best_available_from_club_name as from_club_name,
    to_club_id,
    best_available_to_club_name as to_club_name,

    transfer_fee,
    cumulative_known_transfer_fee,
    total_transfer_fee,
    avg_transfer_fee,
    max_transfer_fee,

    case
        when transfer_fee is null then 'unknown'
        when transfer_fee = 0 then 'zero_fee'
        else 'paid'
    end as fee_status,
    transfer_fee is not null as has_known_transfer_fee,

    market_value_in_eur as transfer_record_market_value,
    market_value_in_eur is not null as has_transfer_record_market_value,
    market_value_baseline_date,
    market_value_baseline,
    market_value_baseline_source,
    market_value_baseline is not null as has_market_value_baseline,
    transfer_fee is not null and market_value_baseline is not null
        as has_fee_market_value_comparison,
    date_diff(transfer_date, market_value_baseline_date, day)
        as days_since_market_value_baseline,

    transfer_fee - market_value_baseline as fee_market_value_difference,

    round(
        safe_divide(
            transfer_fee - market_value_baseline,
            nullif(market_value_baseline, 0)
        ) * 100,
        2
    ) as fee_market_value_difference_pct,

    round(
        safe_divide(transfer_fee, nullif(market_value_baseline, 0)),
        4
    ) as fee_to_market_value_ratio,

    prior_valuation.valuation_date as prior_valuation_date,
    prior_valuation.market_value_in_eur as prior_market_value,
    prior_valuation.current_club_id as prior_valuation_club_id,
    prior_valuation.current_club_name as prior_valuation_club_name,
    prior_valuation.competition_id as prior_valuation_competition_id,
    prior_competition_name,
    prior_competition_country_name,
    prior_competition_confederation,
    prior_valuation.valuation_date is not null as has_prior_valuation,
    date_diff(transfer_date, prior_valuation.valuation_date, day)
        as days_since_prior_valuation,

    next_valuation.valuation_date as next_valuation_date,
    next_valuation.market_value_in_eur as next_market_value,
    next_valuation.current_club_id as next_valuation_club_id,
    next_valuation.current_club_name as next_valuation_club_name,
    next_valuation.competition_id as next_valuation_competition_id,
    next_competition_name,
    next_competition_country_name,
    next_competition_confederation,
    next_valuation.valuation_date is not null as has_next_valuation,
    date_diff(next_valuation.valuation_date, transfer_date, day)
        as days_to_next_valuation,

    next_valuation.market_value_in_eur - market_value_baseline
        as market_value_change_after_transfer,

    round(
        safe_divide(
            next_valuation.market_value_in_eur - market_value_baseline,
            nullif(market_value_baseline, 0)
        ) * 100,
        2
    ) as market_value_change_after_transfer_pct,

    next_valuation.market_value_in_eur is not null
        and market_value_baseline is not null
        as has_post_transfer_value_change,

    case
        when next_valuation.market_value_in_eur is null
            or market_value_baseline is null then 'unavailable'
        when next_valuation.market_value_in_eur > market_value_baseline then 'increase'
        when next_valuation.market_value_in_eur < market_value_baseline then 'decrease'
        else 'unchanged'
    end as market_value_direction_after_transfer,

    case
        when next_valuation.market_value_in_eur is null
            or market_value_baseline is null then 'Belirsiz'
        when next_valuation.market_value_in_eur > market_value_baseline then 'Arttı'
        when next_valuation.market_value_in_eur < market_value_baseline then 'Düştü'
        else 'Değişmedi'
    end as yon_etiketi_tr,

    case
        when prior_valuation.competition_id is null
            or next_valuation.competition_id is null then 'unavailable'
        when prior_valuation.competition_id = next_valuation.competition_id
            then 'same_competition'
        when prior_competition_country_name is not null
            and next_competition_country_name is not null
            and prior_competition_country_name != next_competition_country_name
            then 'country_change'
        else 'competition_change'
    end as valuation_context_change,

    first_valuation_date,
    latest_valuation_date,
    first_market_value,
    current_market_value,
    highest_market_value,
    career_market_value_growth,
    career_market_value_growth_pct

from calculated
