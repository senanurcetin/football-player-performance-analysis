{{ config(cluster_by=["position", "competition_id"]) }}

with scoring_context as (

    select max(season) as scoring_season

    from {{ ref('stg_games') }}

    where game_date <= current_date()
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

    cross join scoring_context

    where games.season = scoring_context.scoring_season
        and appearances.appearance_date <= current_date()
),

performance_features as (

    select
        player_id,
        max(season) as season,
        count(distinct game_id) as matches_before_target,
        count(distinct competition_id) as competitions_played_before_target,
        coalesce(sum(minutes_played), 0) as minutes_before_target,
        coalesce(sum(goals), 0) as goals_before_target,
        coalesce(sum(assists), 0) as assists_before_target,
        coalesce(sum(yellow_cards), 0) as yellow_cards_before_target,
        coalesce(sum(red_cards), 0) as red_cards_before_target,

        round(
            safe_divide(sum(goals), nullif(sum(minutes_played), 0)) * 90,
            4
        ) as goals_per_90_before_target,

        round(
            safe_divide(sum(assists), nullif(sum(minutes_played), 0)) * 90,
            4
        ) as assists_per_90_before_target,

        max(appearance_date) as feature_last_appearance_date

    from season_appearances

    group by player_id
),

valuation_features as (

    select
        players.player_id,
        count(valuations.valuation_date) as prior_valuation_count,
        max(valuations.market_value_in_eur) as prior_highest_market_value_eur,

        array_agg(
            if(
                valuations.valuation_date is not null,
                struct(
                    valuations.valuation_date as valuation_date,
                    valuations.market_value_in_eur as market_value_in_eur,
                    valuations.player_club_domestic_competition_id
                        as competition_id
                ),
                null
            )
            ignore nulls
            order by valuations.valuation_date desc
            limit 1
        )[safe_offset(0)] as previous_valuation

    from performance_features players

    left join {{ ref('stg_player_valuations') }} valuations
        on players.player_id = valuations.player_id
        and valuations.valuation_date <= current_date()

    group by players.player_id
)

select
    cast(performance.player_id as string) as scoring_row_key,
    performance.player_id,
    players.player_name,
    performance.season,

    valuations.previous_valuation.competition_id as competition_id,
    valuations.previous_valuation.competition_id is not null
        as has_competition_context,

    players.position,
    players.sub_position,
    players.preferred_foot,
    players.height_in_cm,
    players.country_of_citizenship,

    competitions.competition_type,
    competitions.country_name as competition_country_name,
    competitions.confederation,

    case
        when date_diff(current_date(), players.birth_date, year)
            - cast(
                format_date('%m%d', current_date())
                    < format_date('%m%d', players.birth_date)
                as int64
            ) between 10 and 60
            then date_diff(current_date(), players.birth_date, year)
                - cast(
                    format_date('%m%d', current_date())
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
        current_date(),
        valuations.previous_valuation.valuation_date,
        day
    ) as days_since_previous_market_value,
    valuations.prior_valuation_count,
    valuations.prior_highest_market_value_eur,

    current_date() as prediction_as_of_date

from performance_features performance

left join valuation_features valuations
    on performance.player_id = valuations.player_id

left join {{ ref('dim_players') }} players
    on performance.player_id = players.player_id

left join {{ ref('dim_competitions') }} competitions
    on valuations.previous_valuation.competition_id = competitions.competition_id
