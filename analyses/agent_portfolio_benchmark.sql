select *

from {{ ref('fct_agent_portfolio') }}

where player_count >= 5
    and transfer_fee_coverage_pct >= 50

order by total_current_market_value desc
