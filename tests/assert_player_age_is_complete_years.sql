select
    player_id

from {{ ref('int_player_profile') }}

where birth_date is not null
    and age != date_diff(current_date(), birth_date, year)
        - if(
            format_date('%m%d', current_date()) < format_date('%m%d', birth_date),
            1,
            0
        )
