with expected as (

    select
        club_id,
        count(distinct game_id) as matches_played,
        countif(is_win = 1) as wins,
        countif(is_win = 0 and own_goals = opponent_goals) as draws,
        countif(is_win = 0 and own_goals != opponent_goals) as losses,
        sum(own_goals) as goals_scored,
        sum(opponent_goals) as goals_conceded

    from {{ ref('stg_club_games') }}

    group by club_id
)

select
    coalesce(expected.club_id, actual.club_id) as club_id

from expected

full outer join {{ ref('int_club_performance_summary') }} actual
    on expected.club_id = actual.club_id

where expected.club_id is null
    or actual.club_id is null
    or expected.matches_played != actual.matches_played
    or expected.wins != actual.wins
    or expected.draws != actual.draws
    or expected.losses != actual.losses
    or expected.goals_scored != actual.goals_scored
    or expected.goals_conceded != actual.goals_conceded
