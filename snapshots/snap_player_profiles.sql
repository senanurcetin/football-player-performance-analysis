{% snapshot snap_player_profiles %}

{{ config(
    target_schema=target.schema ~ '_snapshots',
    unique_key='player_id',
    strategy='check',
    check_cols=[
        'player_name',
        'current_club_id',
        'position',
        'sub_position',
        'agent_name',
        'market_value_in_eur',
        'contract_expiration_date'
    ],
    invalidate_hard_deletes=true
) }}

select
    player_id,
    player_name,
    current_club_id,
    position,
    sub_position,
    agent_name,
    market_value_in_eur,
    contract_expiration_date

from {{ ref('stg_players') }}

{% endsnapshot %}
