{% snapshot snap_club_profiles %}

{{ config(
    target_schema=target.schema ~ '_snapshots',
    unique_key='club_id',
    strategy='check',
    check_cols=[
        'club_name',
        'domestic_competition_id',
        'squad_size',
        'average_age',
        'coach_name',
        'net_transfer_record'
    ],
    invalidate_hard_deletes=true
) }}

select
    club_id,
    club_name,
    domestic_competition_id,
    squad_size,
    average_age,
    coach_name,
    net_transfer_record

from {{ ref('stg_clubs') }}

{% endsnapshot %}
