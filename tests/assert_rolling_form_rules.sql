select appearance_id

from {{ ref('fct_player_rolling_form') }}

where rolling_5_appearances not between 1 and 5
    or rolling_5_minutes < minutes_played
    or rolling_5_goals < goals
    or rolling_5_assists < assists
    or rolling_5_starts not between 0 and rolling_5_appearances
    or rolling_5_captain_appearances not between 0 and rolling_5_appearances
    or rolling_5_goals_per_90 is distinct from round(
        safe_divide(rolling_5_goals, nullif(rolling_5_minutes, 0)) * 90,
        4
    )
    or rolling_5_assists_per_90 is distinct from round(
        safe_divide(rolling_5_assists, nullif(rolling_5_minutes, 0)) * 90,
        4
    )
