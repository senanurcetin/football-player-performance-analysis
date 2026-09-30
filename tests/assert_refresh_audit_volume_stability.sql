with ranked_audits as (
    select
        *,
        row_number() over (order by audit_generated_at_utc desc, audit_key desc) as audit_recency
    from {{ ref('fct_analytics_refresh_audit') }}
),

latest as (
    select * from ranked_audits where audit_recency = 1
),

previous as (
    select * from ranked_audits where audit_recency = 2
),

volume_checks as (
    select 'historical_transfer_rows' as metric_name, l.historical_transfer_rows as latest_value, p.historical_transfer_rows as previous_value
    from latest l cross join previous p
    union all
    select 'match_rows', l.match_rows, p.match_rows from latest l cross join previous p
    union all
    select 'player_match_rows', l.player_match_rows, p.player_match_rows from latest l cross join previous p
    union all
    select 'source_transfer_rows', l.source_transfer_rows, p.source_transfer_rows from latest l cross join previous p
)

select *
from volume_checks
where previous_value > 0
  and abs(safe_divide(latest_value - previous_value, previous_value)) > 0.50
