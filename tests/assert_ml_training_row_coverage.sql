-- Singular dbt coverage test: expected = strictly eligible canonical targets.
-- Do not demand training rows for conflicted/unmatched source values; those
-- are deliberately excluded by ml_player_market_value_training.sql.
-- Separately audit exclusion counts, which can reveal harmful selection bias.
with candidate_by_date as (

    select
        player_id,
        season,
        season_market_value_date as target_market_value_date,
        case
            when count(distinct season_market_value) = 1
                then max(season_market_value)
        end as target_market_value_eur
    from {{ ref('fct_player_career_timeline') }}
    where season_market_value > 0
        and season_market_value_date <= current_date()
    group by player_id, season, target_market_value_date

),

latest_target as (

    select
        player_id,
        season,
        array_agg(
            struct(target_market_value_date, target_market_value_eur)
            order by target_market_value_date desc limit 1
        )[offset(0)] as target
    from candidate_by_date
    group by player_id, season

),

canonical_valuation_days as (

    select
        player_id,
        valuation_date,
        max(market_value_in_eur) as canonical_market_value_eur
    from {{ ref('stg_player_valuations') }}
    where valuation_date is not null
        and market_value_in_eur > 0
    group by player_id, valuation_date
    having count(distinct market_value_in_eur) = 1

),

expected as (

    select
        concat(cast(t.player_id as string), '-', cast(t.season as string))
            as training_row_key
    from latest_target t
    inner join canonical_valuation_days v
        on t.player_id = v.player_id
        and t.target.target_market_value_date = v.valuation_date
        and t.target.target_market_value_eur = v.canonical_market_value_eur

),

actual as (

    select training_row_key
    from {{ ref('ml_player_market_value_training') }}

),

missing_expected as (

    select *
    from expected
    except distinct
    select *
    from actual

),

unexpected_actual as (

    select *
    from actual
    except distinct
    select *
    from expected

)

select * from missing_expected
union all
select * from unexpected_actual
