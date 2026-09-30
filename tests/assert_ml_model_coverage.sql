with validations as (

    select
        'training_has_rows' as validation_name,
        (select count(*) from {{ ref('ml_player_market_value_training') }}) > 0
            as passed

    union all

    select
        'scoring_has_rows',
        (select count(*) from {{ ref('ml_player_market_value_scoring') }}) > 0

    union all

    select
        'scoring_uses_latest_observed_season',
        (
            select min(season) = max(season)
                and max(season) = (
                    select max(season)
                    from {{ ref('stg_games') }}
                    where game_date <= current_date()
                )
            from {{ ref('ml_player_market_value_scoring') }}
        )
)

select *

from validations

where not passed
