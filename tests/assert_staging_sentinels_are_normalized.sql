select 'stg_appearances.player_current_club_id' as failing_field

from {{ ref('stg_appearances') }}

where player_current_club_id < 0

union all

select 'stg_game_events.minute' as failing_field

from {{ ref('stg_game_events') }}

where minute < 0

union all

select 'stg_game_events.event_description' as failing_field

from {{ ref('stg_game_events') }}

where event_description = ''

union all

select 'stg_game_lineups.position' as failing_field

from {{ ref('stg_game_lineups') }}

where position = ''

union all

select 'stg_players.height_in_cm' as failing_field

from {{ ref('stg_players') }}

where height_in_cm not between 100 and 250
