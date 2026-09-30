with expected as (

    select
        concat(
            cast(player_id as string),
            '-',
            cast(season as string)
        ) as training_row_key

    from {{ ref('fct_player_career_timeline') }}

    where season_market_value > 0
        and season_market_value_date <= current_date()

    group by
        player_id,
        season
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

select *
from missing_expected

union all

select *
from unexpected_actual
