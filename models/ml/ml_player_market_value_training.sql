{{ config(
    partition_by={"field": "target_market_value_date", "data_type": "date", "granularity": "year"},
    cluster_by=["season", "position", "competition_id"]
) }}

with timeline_targets as (

    select
        timeline.player_id,
        timeline.season,

        array_agg(
            struct(
                timeline.season_market_value_date as target_market_value_date,
                timeline.season_market_value as target_market_value_eur
            )
            order by timeline.season_market_value_date desc
            limit 1
        )[offset(0)] as target

    from {{ ref('fct_player_career_timeline') }} timeline

    where timeline.season_market_value > 0
        and timeline.season_market_value_date <= current_date()

    group by
        timeline.player_id,
        timeline.season
),

targets as (

    select
        timeline_targets.player_id,
        timeline_targets.season,
        timeline_targets.target.target_market_value_date,
        timeline_targets.target.target_market_value_eur,
        valuations.player_club_domestic_competition_id as competition_id

    from timeline_targets

    inner join {{ ref('stg_player_valuations') }} valuations
        on timeline_targets.player_id = valuations.player_id
        and timeline_targets.target.target_market_value_date = valuations.valuation_date
),

season_appearances as (

    select
        appearances.player_id,
        appearances.competition_id,
        appearances.appearance_date,
        appearances.minutes_played,
        appearances.goals,
        appearances.assists,
        appearances.yellow_cards,
        appearances.red_cards,
        games.game_id,
        games.season

    from {{ ref('stg_appearances') }} appearances

    inner join {{ ref('stg_games') }} games
        on appearances.game_id = games.game_id
),

performance_features as (

    select
        targets.player_id,
        targets.season,

        count(distinct appearances.game_id) as matches_before_target,
        count(distinct appearances.competition_id)
            as competitions_played_before_target,
        coalesce(sum(appearances.minutes_played), 0) as minutes_before_target,
        coalesce(sum(appearances.goals), 0) as goals_before_target,
        coalesce(sum(appearances.assists), 0) as assists_before_target,
        coalesce(sum(appearances.yellow_cards), 0) as yellow_cards_before_target,
        coalesce(sum(appearances.red_cards), 0) as red_cards_before_target,

        round(
            safe_divide(
                sum(appearances.goals),
                nullif(sum(appearances.minutes_played), 0)
            ) * 90,
            4
        ) as goals_per_90_before_target,

        round(
            safe_divide(
                sum(appearances.assists),
                nullif(sum(appearances.minutes_played), 0)
            ) * 90,
            4
        ) as assists_per_90_before_target,

        max(appearances.appearance_date) as feature_last_appearance_date

    from targets

    left join season_appearances appearances
        on targets.player_id = appearances.player_id
        and targets.season = appearances.season
        and appearances.appearance_date < targets.target_market_value_date

    group by
        targets.player_id,
        targets.season
),

valuation_features as (

    select
        targets.player_id,
        targets.season,

        count(valuations.valuation_date) as prior_valuation_count,
        max(valuations.market_value_in_eur) as prior_highest_market_value_eur,

        array_agg(
            if(
                valuations.valuation_date is not null,
                struct(
                    valuations.valuation_date as valuation_date,
                    valuations.market_value_in_eur as market_value_in_eur
                ),
                null
            )
            ignore nulls
            order by valuations.valuation_date desc
            limit 1
        )[safe_offset(0)] as previous_valuation

    from targets

    left join {{ ref('stg_player_valuations') }} valuations
        on targets.player_id = valuations.player_id
        and valuations.valuation_date < targets.target_market_value_date

    group by
        targets.player_id,
        targets.season
)

select
    concat(
        cast(targets.player_id as string),
        '-',
        cast(targets.season as string)
    ) as training_row_key,

    targets.player_id,
    players.player_name,
    targets.season,
    targets.competition_id,
    targets.competition_id is not null as has_competition_context,

    players.position,
    players.sub_position,
    players.preferred_foot,
    players.height_in_cm,
    players.country_of_citizenship,

    competitions.competition_type,
    competitions.country_name as competition_country_name,
    competitions.confederation,

    case
        when date_diff(targets.target_market_value_date, players.birth_date, year)
            - cast(
                format_date('%m%d', targets.target_market_value_date)
                    < format_date('%m%d', players.birth_date)
                as int64
            ) between 10 and 60
            then date_diff(targets.target_market_value_date, players.birth_date, year)
                - cast(
                    format_date('%m%d', targets.target_market_value_date)
                        < format_date('%m%d', players.birth_date)
                    as int64
                )
    end as age_at_target_date,

    performance.matches_before_target,
    performance.competitions_played_before_target,
    performance.minutes_before_target,
    performance.goals_before_target,
    performance.assists_before_target,
    performance.yellow_cards_before_target,
    performance.red_cards_before_target,
    performance.goals_per_90_before_target,
    performance.assists_per_90_before_target,
    performance.feature_last_appearance_date,

    valuations.previous_valuation.valuation_date as previous_market_value_date,
    valuations.previous_valuation.market_value_in_eur as previous_market_value_eur,
    valuations.previous_valuation.market_value_in_eur is not null
        as has_previous_market_value,
    date_diff(
        targets.target_market_value_date,
        valuations.previous_valuation.valuation_date,
        day
    ) as days_since_previous_market_value,
    valuations.prior_valuation_count,
    valuations.prior_highest_market_value_eur,

    targets.target_market_value_date,
    targets.target_market_value_eur

from targets

left join performance_features performance
    on targets.player_id = performance.player_id
    and targets.season = performance.season

left join valuation_features valuations
    on targets.player_id = valuations.player_id
    and targets.season = valuations.season

left join {{ ref('dim_players') }} players
    on targets.player_id = players.player_id

left join {{ ref('dim_competitions') }} competitions
    on targets.competition_id = competitions.competition_id
