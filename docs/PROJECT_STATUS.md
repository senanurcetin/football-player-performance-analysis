# Current project status

**Evidence snapshot: 17 October 2026 | NEXUS Football Intelligence**

> **Engineering addendum — 18 October 2026 (on draft PR #79, not yet on main):**
> Two open and unmerged feature PRs carry additional model-validation source work: [numeric contract #78](https://github.com/senanurcetin/football-player-performance-analysis/pull/78) and [research reliability #79](https://github.com/senanurcetin/football-player-performance-analysis/pull/79), with #79 based on #78. An offline reconstruction of the new ML research modules passed **33/33 synthetic Python tests**, with **93% combined statement coverage**, on 18 October 2026. The original GitHub checkout and the standalone #78 numeric-contract tests were not run together. **The full repository suite, current BigQuery freshness, actual historical research backtests and Power BI Desktop acceptance have not been executed or independently verified for these changes.** No production model or portfolio release has been approved. The table below remains the 17 October base evidence and release stays **REVIEW PENDING**.

This is the canonical record of verification status. Dated plans and incidents are preserved in the [historical archive](archive/README.md); their earlier acceptance statements do not supersede this page.

## Documentation and repository research audit — 18 October 2026

The active document navigation and technical descriptions were consolidated **on draft PR #79, not merged into `main`**. Three redundant/obsolete active handoffs (`FOOTBALL_INTELLIGENCE_PRODUCT.md`, `POWER_BI_PORTFOLIO_PRODUCTION_CONTRACT.md`, `ci-recovery.md`) were retired after their still-applicable native PBIR, design, data-provenance and CI safety requirements were moved into the existing canonical references. A previously missing [KPI dictionary](KPI_DICTIONARY.md) was added and sourced to actual DAX/dbt metric definitions. CI statements in [the runbook](RUNBOOK.md), [ML methodology](PLAYER_MARKET_VALUE_ML.md) and [CI policy](CI_RELEASE_GATE_POLICY.md) now distinguish manual GitHub validation, scheduled ML production and CircleCI final opt-in.

**Extended GitHub-tree navigation QA (19 October 2026):** fetched the recursive tree for draft PR #79 (**2,277 files, 3,424 tree entries**) and remotely inspected **all 48 tracked Markdown files** and **242 internal Markdown, image and directory links**; all link destinations resolve to tracked files or directories (three initial directory-looking exceptions were confirmed to be valid folders). The [19 historical archive files](archive/README.md) remain preserved. This is a real source-tree navigation audit but **not** an execution of `scripts/check_docs_integrity.py` or the complete repository test suite.

## Visual capture comparison — 18 October 2026

**KONTROL EDİLDİ (limited scope):** All **13/13 production screenshot PNGs** match the dated capture manifest SHA-256 and image-size records. Historical visual measures verified against the June BigQuery documentation: player dimension **47,702**, transfers **40,208**, known-fee coverage **64.2%**, current ML scoring population **7,841**, and decision-ready complement **72.9%**. This is **static historical screenshot/value reconciliation only**; details are recorded in [Power BI historical value audit](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md).

**PARTIALLY EXPLAINED AT SOURCE LEVEL (19 October 2026):** The 365-day panel displays **8,581** records using an explicit Power BI **as-of maturity cutoff**, while the historical `fct_transfer_success_labels` has **8,584** observed labels without that cutoff. Native PBIR and dbt definitions are **not equivalent**. The 3-record delta is **not yet independently proven** to consist of immature labels because authenticated warehouse readback remains unavailable. Both player-detail pages show unselected-player/error placeholders in the saved images. No new Power BI Desktop interaction or authorized fresh BigQuery query ran. The overall acceptance state **remains REVIEW PENDING**, independent of verified screenshot checks.

## Verified vs. pending

| Area | Verified evidence | Still open | Status |
|---|---|---|---|
| Repository | 17 October screenshot baseline on `main` commit `f3a84d9`; two follow-on draft PRs (#78 numeric contract, #79 research/docs) open on 18 October | Full repository checkout test, code review, controlled merge and final CI | **Source on draft branches; not merged** |
| Power BI sources | 13 editable PBIR pages: 9 presentation, 2 drillthrough, 2 tooltips; source layout and binding audits passed | Final interaction acceptance | Source verified / runtime partial |
| Desktop screenshots | Genuine captures dated 17 October; 13/13 PNG SHA-256 and dimensions checked on 18 October, comparable historical metrics matched | Player-detail errors, 365-day 3-row population reconciliation after differing DAX/dbt definitions, Desktop runtime | **KONTROL EDİLDİ** — historical image integrity / matching metrics only; full acceptance pending |
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
