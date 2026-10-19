-- Research-only read-only BigQuery diagnostic for ambiguous valuation events.
-- Never derive empirical "rows changed" from this source file alone.
-- Requires authorized BigQuery/dbt execution and source snapshot timestamp.
--
-- Report exact duplicates vs. conflicting same-day valuations and how many
-- historical target keys would be excluded by the canonical event rule.
with raw_valuation_days as (

    select
        player_id,
        valuation_date,
        count(*) as source_rows,
        countif(market_value_in_eur > 0) as valid_source_rows,
        count(distinct if(market_value_in_eur > 0, market_value_in_eur, null))
            as distinct_positive_eur_values,
        count(distinct if(market_value_in_eur > 0,
            player_club_domestic_competition_id, null))
            as distinct_competition_ids,
        max(if(market_value_in_eur > 0, market_value_in_eur, null))
            as max_positive_eur_value
    from {{ ref('stg_player_valuations') }}
    where player_id is not null and valuation_date is not null
    group by player_id, valuation_date

),

target_candidate_by_date as (

    select
        player_id,
        season,
        season_market_value_date as target_market_value_date,
        case when count(distinct season_market_value) = 1
            then max(season_market_value)
        end as target_market_value_eur
    from {{ ref('fct_player_career_timeline') }}
    where season_market_value > 0
        and season_market_value_date <= current_date()
    group by player_id, season, target_market_value_date

),

timeline_target_days as (

    select
        player_id,
        season,
        array_agg(
            struct(target_market_value_date, target_market_value_eur)
            order by target_market_value_date desc limit 1
        )[offset(0)] as target
    from target_candidate_by_date
    group by player_id, season

),

target_membership as (

    select
        t.player_id,
        t.season,
        t.target.target_market_value_date as target_market_value_date,
        t.target.target_market_value_eur as target_market_value_eur,
        d.source_rows,
        d.distinct_positive_eur_values,
        d.max_positive_eur_value,
        d.distinct_competition_ids,
        d.distinct_positive_eur_values = 1
            and d.max_positive_eur_value = t.target.target_market_value_eur
            as is_canonical_target
    from timeline_target_days t
    left join raw_valuation_days d
        on t.player_id = d.player_id
        and t.target.target_market_value_date = d.valuation_date

)

select
    (select count(*) from {{ ref('stg_player_valuations') }})
        as raw_valuation_rows,
    (select count(*) from raw_valuation_days)
        as player_date_valuation_groups,
    (select countif(source_rows > 1) from raw_valuation_days)
        as multirow_player_dates,
    (select countif(valid_source_rows > 1
        and distinct_positive_eur_values = 1) from raw_valuation_days)
        as duplicated_consistent_positive_days,
    (select countif(distinct_positive_eur_values > 1) from raw_valuation_days)
        as conflicting_positive_value_days,
    (select countif(distinct_positive_eur_values = 1
        and distinct_competition_ids > 1) from raw_valuation_days)
        as conflicting_competition_only_days,
    (select count(*) from timeline_target_days)
        as candidate_player_season_targets,
    (select countif(target.target_market_value_eur is null)
        from timeline_target_days)
        as conflicted_latest_player_season_targets,
    (select countif(is_canonical_target) from target_membership)
        as matched_unambiguous_targets,
    (select countif(is_canonical_target is not true) from target_membership)
        as excluded_ambiguous_or_unmatched_targets
