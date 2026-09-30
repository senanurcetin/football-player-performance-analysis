select

    player_id,

    transfer_date,

    trim(transfer_season) as transfer_season,

    from_club_id,
    to_club_id,

    trim(from_club_name) as from_club_name,
    trim(to_club_name) as to_club_name,

    cast(transfer_fee as numeric) as transfer_fee,
    cast(market_value_in_eur as numeric) as market_value_in_eur,

    trim(player_name) as player_name

from {{ source('football_raw', 'transfers') }}

where player_id is not null
