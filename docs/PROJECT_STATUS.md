# Current project status

**Evidence snapshot: 17 October 2026 | NEXUS Football Intelligence**

> **Engineering addendum — 18 October 2026 (on draft PR #79, not yet on main):**
> Two open and unmerged feature PRs carry additional model-validation source work: [numeric contract #78](https://github.com/senanurcetin/football-player-performance-analysis/pull/78) and [research reliability #79](https://github.com/senanurcetin/football-player-performance-analysis/pull/79), with #79 based on #78. The independent walk-forward runner has **12/12 passing synthetic offline walk-forward tests** in an isolated local environment; isolated artifact lineage helper scenarios also passed. **The full repository suite, current BigQuery freshness, actual historical research backtests and Power BI Desktop acceptance have not been executed or independently verified for these changes.** No production model or portfolio release has been approved. The table below remains the 17 October base evidence and release stays **REVIEW PENDING**.

This is the canonical record of verification status. Dated plans and incidents are preserved in the [historical archive](archive/README.md); their earlier acceptance statements do not supersede this page.

## Verified vs. pending

| Area | Verified evidence | Still open | Status |
|---|---|---|---|
| Repository | Screenshot baseline on `main` commit `f3a84d9` includes new README and real screenshots; historic branches cleaned; no open PR at last check | New release CI, if required | Source delivered |
| Power BI sources | 13 editable PBIR pages: 9 presentation, 2 drillthrough, 2 tooltips; source layout and binding audits passed | Final interaction acceptance | Source verified / runtime partial |
| Desktop screenshots | Genuine production-connected Desktop image captures dated 17 October, with imported historical data visible across nine primary pages | Owner review; full screen interaction verification | Captured / pending approval |
| Player detail | Two actual unselected-state screenshots preserved in technical evidence | Check/fix visuals with errors, test selected player context | Open |
| Production freshness | BigQuery marts referenced by editable production PBIP | New authenticated refresh, error/row counts, source-date and KPI reconciliation | Not independently verified |
| ML | Documented historical v5 ensemble and persistence-baseline comparison | New training/validation if new evaluation results are claimed | Historical metrics only |
| Automated validation | 158/158 Python unit tests and Power BI static preflight passed after the documentation restructuring | Rerun for new documentation and source changes; external CI separately | Local snapshot passed |
| Public deployment | Versioned PBIP sources published | Live Power BI hosting and owner release signoff | Not certified |

**Release decision: REVIEW PENDING.** Authentic project screenshots can illustrate historical imported model data with provenance. They do not prove live data, a current refresh, a production deployment or a fully accepted product.

## Genuine capture provenance

- [Actual Power BI Desktop gallery](assets/screenshots/README.md)
- [Capture SHA-256 manifest](assets/screenshots/capture_manifest.json)
- [Canonical production PBIP](../powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip)
- [Asset integrity script](../scripts/verify_dashboard_screenshots.py)

Nine presentation pages were captured with visible KPIs and charts. Two player drillthrough pages include missing selection and visual-error placeholders, so their PNGs remain technical evidence only. Two hidden tooltips were also captured.

**Capture timestamp is not event-data freshness.** Source event dates and the original warehouse audit timestamp must be checked separately.

## Final release conditions

1. **Warehouse refresh:** authenticate with authorized BigQuery access, refresh the production PBIP and record source timestamps, errors and model row counts.
2. **Metric reconciliation:** verify counts, club win-rate scale, observed 365-day transfer denominators and ML prediction population against governed marts.
3. **Desktop inspection:** review nine main pages, two selected/unselected player drillthroughs and two tooltip invocations; verify visuals, filters, links, formatting and accessibility.
4. **Test execution:** rerun Python, PBIR, warehouse/source and release checks; keep dated command output and Git SHA.
5. **User acceptance:** obtain explicit visual signoff; use final opt-in CI only when appropriate under the [CI release policy](CI_RELEASE_GATE_POLICY.md).

The [Desktop handoff](POWER_BI_DESKTOP_HANDOFF.md) and [current visual QA checklist](POWER_BI_VISUAL_QA.md) provide detailed instructions. Missing evidence must be labeled **not verified**, never automatically counted as PASS.

## Scope and governance

Dbt validation metrics dated **June 2026** and historical ML evaluation numbers are previous snapshots, not newly rerun October tests. Preserve provenance through [Data quality](DATA_QUALITY.md), [model methodology](PLAYER_MARKET_VALUE_ML.md) and the [reviewer brief](hiring-summary.md).

Future updates must include evidence date, source commit, environment and result; keep old experiments in the [archive](archive/README.md). The README and other reviewer-facing material should link here rather than duplicate evolving acceptance claims.
