select *

from {{ ref('fct_data_coverage_bias') }}

where coverage_bias_risk in ('high_bias_risk', 'insufficient_sample')

order by maximum_material_missingness_pct desc, transfer_count desc
