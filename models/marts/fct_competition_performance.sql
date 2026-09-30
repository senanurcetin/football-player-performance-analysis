select

    competition_id,

    competition_name,

    competition_type,



    country_name,

    confederation,

    matches_played,

    total_goals,

    avg_goals_per_match,

    club_participation_count,

    avg_attendance

from {{ ref('int_competition_summary') }}