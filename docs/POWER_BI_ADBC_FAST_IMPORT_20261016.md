# Power BI ADBC V2 fast Import — authenticated Desktop acceptance

**Date:** 16 October 2026 · **Repo:** `football-player-performance-analysis` · **Release:** HOLD until all 13 visual pages pass.

## Actual bottleneck and evidence

The production report's original full Import attempted to load all 33 BigQuery mart/model tables with legacy `GoogleBigQuery.Database([UseStorageApi=false])`. A long-running reload was canceled via Power BI Desktop's own Cancel UI after its local Analysis Services diagnostic showed blocked queries, while BigQuery itself had completed several jobs. The 13 report pages were unable to render without a completed local model import.

Cross-reference checks on the actual PBIR report definitions and all other semantic model measures showed two large imported tables were not used by existing visual bindings or DAX calculations:

- `fct_player_match_performance`, approximately 1,124,618 source rows.
- `fct_player_rolling_form`, approximately 1,011,990 source rows.

Their nine associated relationships and two auto-date tables existed only to support those unused tables. The source BigQuery marts are preserved; this is **model pruning**, not data deletion.

## Authentic, separate QA test (performed before changing production source)

The genuine `powerbi/workspace` PBIP was copied to a separate local QA directory. In that **production-data test copy**, the two unused tables, their nine relationships and two generated date tables were removed, and **31 retained BigQuery partitions** were updated to:

```powerquery
Source = GoogleBigQuery.Database([Implementation="2.0", UseStorageApi=false])
```

This opts into Microsoft's Arrow Database Connectivity (ADBC) implementation while explicitly **keeping the billable BigQuery Storage Read API disabled**, consistent with the project's minimal-budget constraint. The actual warehouse project remains `data-analiz-490513` and both the `football_mart` and `football_ml` datasets remain the unchanged data sources.

On the actual Windows user's Power BI Desktop, the QA variant completed its import and its loading dialog closed. A read-only live DAX connection returned `READY_FOR_VISUAL_QA` with the following genuine model counts:

| Power BI semantic table | Loaded rows |
| --- | ---: |
| `dim_clubs` | 9,032 |
| `fct_club_performance` | 3,270 |
| `fct_club_risk_profile` | 5,714 |
| `fct_player_performance` | 28,736 |
| `fct_analytics_refresh_audit` | 17 |
| `ml_player_market_value_current_predictions` | 7,841 |

`MAX(fct_club_performance[win_rate])` was **1.0**, confirming the necessary percentage-point-to-fraction normalization. The actual audit label evaluated to **`HISTORICAL / 21 JUN 2026`**. This is a historical evidence label, not a claim that football event data are current.

This result proves *actual Desktop import and basic semantic DAX readiness of the cloned version*; it does **not** prove all 13 native report pages, slicers and tooltips render without error.

## New production-source configuration

The same **proven** model-pruning and ADBC v2 configuration is applied to both source editions:
- Production: `powerbi/workspace/FootballPlayerAnalysis` — 31 real BigQuery Import partitions, 13 report pages, all original official NEXUS artwork and business metrics.
- Internal synthetic fixture: `powerbi/offline-demo/FootballPlayerAnalysis` — corresponding model pruning, still **internal-only synthetic QA**, never described as real results.

Reproducible builder:
```powershell
python scripts/optimize_powerbi_adbc_import.py
python scripts/optimize_powerbi_adbc_import.py --apply
python -m unittest discover -s tests -p "test_powerbi_*.py" -q
python scripts/check_powerbi_release_handoff.py --output powerbi-handoff.json
```

The optimizer is idempotent on an already optimized tree; `--apply` is for an authorized, isolated Git working branch. The full pre-optimization report can always be recovered from the previous Git commit and is not committed as a second edition.

## Explicit acceptance limits

An already open Power BI Desktop report will **not reliably hot reload** changed TMDL partitions. Confirm any unsaved user changes before closing/reopening the new production `.pbip`. After a fresh authenticated refresh, independently confirm the six counts above; test 13 pages (9 visible, two hidden drillthroughs, two hover tooltips), filters, navigation, labels, actual logo crop, and no `Missing_References` errors. Capture only actual render evidence. `portfolio_release` stays HOLD until signoff.

**Upstream:** https://learn.microsoft.com/en-us/power-query/connectors/google-bigquery (Microsoft official ADBC upgrade instructions).
