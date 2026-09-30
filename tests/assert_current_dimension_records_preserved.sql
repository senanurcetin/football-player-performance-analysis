with player_differences as (

    (
        select
            player_id,
            player_name,
            position,
            sub_position,
            birth_date,
            country_of_birth,
            country_of_citizenship,
            height_in_cm,
            preferred_foot,
            agent_name,
            current_club_id,
            current_club_name,
            last_season
        from {{ ref('stg_players') }}

        except distinct

        select
            dimension.player_id,
            dimension.player_name,
            dimension.position,
            dimension.sub_position,
            dimension.birth_date,
            dimension.country_of_birth,
            dimension.country_of_citizenship,
            dimension.height_in_cm,
            dimension.preferred_foot,
            dimension.agent_name,
            dimension.current_club_id,
            dimension.current_club_name,
            dimension.last_season
        from {{ ref('dim_players') }} dimension
        inner join {{ ref('stg_players') }} staging
            on dimension.player_id = staging.player_id
    )

    union all

    (
        select
            dimension.player_id,
            dimension.player_name,
            dimension.position,
            dimension.sub_position,
            dimension.birth_date,
            dimension.country_of_birth,
            dimension.country_of_citizenship,
            dimension.height_in_cm,
            dimension.preferred_foot,
            dimension.agent_name,
            dimension.current_club_id,
            dimension.current_club_name,
            dimension.last_season
        from {{ ref('dim_players') }} dimension
        inner join {{ ref('stg_players') }} staging
            on dimension.player_id = staging.player_id

        except distinct

        select
            player_id,
            player_name,
            position,
            sub_position,
            birth_date,
            country_of_birth,
            country_of_citizenship,
            height_in_cm,
            preferred_foot,
            agent_name,
            current_club_id,
            current_club_name,
            last_season
        from {{ ref('stg_players') }}
    )
),

club_differences as (

    (
        select
            club_id,
            club_code,
            club_name,
            domestic_competition_id,
            total_market_value,
            squad_size,
            average_age,
            foreigners_number,
            foreigners_percentage,
            national_team_players,
            stadium_name,
            stadium_seats,
            net_transfer_record,
            coach_name,
            last_season
        from {{ ref('stg_clubs') }}

        except distinct

        select
            dimension.club_id,
            dimension.club_code,
            dimension.club_name,
            dimension.domestic_competition_id,
            dimension.total_market_value,
            dimension.squad_size,
            dimension.average_age,
            dimension.foreigners_number,
            dimension.foreigners_percentage,
            dimension.national_team_players,
            dimension.stadium_name,
            dimension.stadium_seats,
            dimension.net_transfer_record,
            dimension.coach_name,
            dimension.last_season
        from {{ ref('dim_clubs') }} dimension
        inner join {{ ref('stg_clubs') }} staging
            on dimension.club_id = staging.club_id
    )

    union all

    (
        select
            dimension.club_id,
            dimension.club_code,
            dimension.club_name,
            dimension.domestic_competition_id,
            dimension.total_market_value,
            dimension.squad_size,
            dimension.average_age,
            dimension.foreigners_number,
            dimension.foreigners_percentage,
            dimension.national_team_players,
            dimension.stadium_name,
            dimension.stadium_seats,
            dimension.net_transfer_record,
            dimension.coach_name,
            dimension.last_season
        from {{ ref('dim_clubs') }} dimension
        inner join {{ ref('stg_clubs') }} staging
            on dimension.club_id = staging.club_id

        except distinct

        select
            club_id,
            club_code,
            club_name,
            domestic_competition_id,
            total_market_value,
            squad_size,
            average_age,
            foreigners_number,
            foreigners_percentage,
            national_team_players,
            stadium_name,
            stadium_seats,
            net_transfer_record,
            coach_name,
            last_season
        from {{ ref('stg_clubs') }}
    )
),

competition_differences as (

    (
        select *
        from {{ ref('stg_competitions') }}

        except distinct

        select *
        from {{ ref('dim_competitions') }}
    )

    union all

    (
        select *
        from {{ ref('dim_competitions') }}

        except distinct

        select *
        from {{ ref('stg_competitions') }}
    )
)

select 'dim_players' as model_name
from player_differences

union all

select 'dim_clubs' as model_name
from club_differences

union all

select 'dim_competitions' as model_name
from competition_differences
