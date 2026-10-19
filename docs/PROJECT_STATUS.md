# Current project status

**Evidence snapshot: 17 October 2026 | NEXUS Football Intelligence**

> **Source integration — 19 October 2026 (`main`):**
> [Numeric-contract PR #78](https://github.com/senanurcetin/football-player-performance-analysis/pull/78) was **merged** at `0aaec6f8d3f8f28d3cd55c7ca648a05dd3364bb0`. [Research and documentation PR #79](https://github.com/senanurcetin/football-player-performance-analysis/pull/79) was then **merged** at `f63ee20a4c4fb8a43b6a99e468a6e325ea244f8e`. Both merges used `[skip ci]`; **hosted CI was not intentionally run**. Earlier isolated synthetic-only ML research checks reported **33/33 tests** and 93% coverage, but the actual combined repository suite, #78 regression suite, current BigQuery freshness, real-data historical model backtests and Power BI Desktop runtime acceptance **have not been executed or independently verified for this integration**. Merging the source is not production model approval or portfolio release. Overall release state remains **REVIEW PENDING**.

## Ordered verification gates — 19 October 2026

The owner requested **verify everything before Power BI and final CI**. Source integration and isolated synthetic checks do **not** satisfy the following remaining prerequisites:

| Gate | Required verification | Recorded state |
| --- | --- | --- |
| A — complete checkout | Run Python full unit discovery, `scripts/check_offline_ci.py`, `scripts/check_ml_pipeline.py`, docs/link integrity, original PR #78–#84 regression tests, and source-level BigQuery/dbt/Jinja compile | **BLOCKED:** this ChatGPT container cannot resolve GitHub for a full clone; the authorized Desktop Commander `Senanur` device is **offline** as of this check. Prior isolated passes are not full-checkout evidence |
| B — authorized warehouse | Authenticate approved BigQuery project, inspect freshness/source timestamps, run both as-of tests, canonical training-key coverage, event-grain/conflict/exclusion audit and existing dbt checks | **BLOCKED:** provider-native BigQuery connector is **DISABLED_BY_ADMIN**; no alternate authenticated warehouse runtime is connected in this session |
| C — real historical ML | Rerun corrected train/tune/calibration/holdout pipeline on current verified data; report persistence baseline, MAE, WAPE, segment coverage, uncertainty and promotion gates | **NOT RUN:** source-grain and calibrated-predictor changes may change historical model metrics |
| D — Power BI | After A–C, retain owner's previous visual acceptance, and recheck refreshed comparable KPI populations as necessary before final signoff | **DEFERRED by owner order**; no new Desktop execution claimed |
| E — final CI | After A–D, run the explicitly authorized final opt-in CircleCI and only then consider manual production publication | **NOT TRIGGERED** in this verification effort |

**Independent GitHub workflow incident:** [ML Production scheduled run #39237422384](https://github.com/senanurcetin/football-player-performance-analysis/actions/runs/39237422384) began on **19 October 2026 at 10:26 UTC** and **FAILED** during `Configure BigQuery credentials`: GitHub secret `GCP_SERVICE_ACCOUNT_JSON` was empty. GitHub confirms all later source-freshness, dbt build, ML train/publish and verification steps were **SKIPPED**. This is **not** a credentialed BigQuery test failure or a model failure; no model publication occurred in that run. To respect verification-before-CI, the weekly schedule was removed, and the workflow now needs explicit **manual `confirm_final_release=true`** plus repository variable **`ENABLE_ML_PRODUCTION=true`**. This change does not launch a CI run or provide Google Cloud credentials.

This is the canonical record of verification status. Dated plans and incidents are preserved in the [historical archive](archive/README.md); their earlier acceptance statements do not supersede this page.

## Documentation and repository research audit — 18 October 2026

The active document navigation and technical descriptions were consolidated through **PR #79, merged into `main` on 19 October 2026**. Three redundant/obsolete active handoffs (`FOOTBALL_INTELLIGENCE_PRODUCT.md`, `POWER_BI_PORTFOLIO_PRODUCTION_CONTRACT.md`, `ci-recovery.md`) were retired after their still-applicable native PBIR, design, data-provenance and CI safety requirements were moved into the existing canonical references. A previously missing [KPI dictionary](KPI_DICTIONARY.md) was added and sourced to actual DAX/dbt metric definitions. CI statements in [the runbook](RUNBOOK.md), [ML methodology](PLAYER_MARKET_VALUE_ML.md) and [CI policy](CI_RELEASE_GATE_POLICY.md) now distinguish manual GitHub validation, the historical weekly ML production configuration (now removed), and CircleCI final opt-in.

**Extended GitHub-tree navigation QA (19 October 2026):** fetched the recursive tree for the pre-merge PR #79 source snapshot (**2,277 files, 3,424 tree entries**) and remotely inspected **all 48 tracked Markdown files** and **242 internal Markdown, image and directory links**; all link destinations resolve to tracked files or directories (three initial directory-looking exceptions were confirmed to be valid folders). The [19 historical archive files](archive/README.md) remain preserved. This is a real source-tree navigation audit but **not** an execution of `scripts/check_docs_integrity.py` or the complete repository test suite.

## Historical model calibration identity safeguard — 19 October 2026

**Source merged:** [PR #83](https://github.com/senanurcetin/football-player-performance-analysis/pull/83) merged into `main` at `ef08082e7987b1cc688ef6668532147b303c87de` using `[skip ci]`. New empirical validation has **not** been performed. Source review identified that historical v5 holdout inference previously **refit the estimator on calibration-season labels** after computing interval residuals on a different, pre-calibration model. The research fix reuses the same fitted estimator and pre-calibration persistence fill for both calibration and held-out test, records the exact fit/calibration row counts and requires matching evidence when auditing saved evaluation artifacts. **Real model performance, sample acceptance and interval coverage must be rerun and are NOT VERIFIED**. No current source-data refresh, warehouse operation or Power BI work is implied. See [ML reliability methodology](ML_RELIABILITY_EVALUATION_20261018.md).

## Training coverage and latest-date source consistency — 19 October 2026

Source inspection identified a **potential false-negative dbt row-coverage gate**: the existing test expected even player-season valuations intentionally removed by the new unambiguous-source contract. The updated test compares only eligible canonical player/date/EUR events. The ML model and source-collision audit now reject **conflicting EUR values at the latest target date** deterministically, rather than arbitrarily taking one or backfilling an older date. A synthetic SQLite example reproduced the desired behavior. **The actual database exclusion count, dbt compilation and full repository test suite have NOT been run.** Power BI and hosted CI are deferred until evidence-based upstream ML/data checks can be executed.

## Valuation source event-grain hardening — 19 October 2026

**Source merged:** [PR #82](https://github.com/senanurcetin/football-player-performance-analysis/pull/82) merged into `main` at `a614db1b34eaf6079b5289f040b2ced69c2f2837` using `[skip ci]`. The **training and scoring dbt models** now derive prior values from a common, positive and unambiguous player-date valuation event instead of raw possibly duplicate source rows. The training target matches on player, date **and EUR amount**, protecting unique player-season keys against duplicate same-day valuations. Disputed EUR amounts are excluded rather than arbitrarily selected, while ambiguous competition IDs are missing. A separate read-only SQL profile measures affected records. Isolated SQLite reconstruction of the grouping and label-join rules passed **5/5 synthetic tests**; **no actual BigQuery sample, execution, model retraining or full repository test result** has been measured. See [event-grain audit](ML_VALUATION_EVENT_GRAIN_AUDIT_20261019.md).

**Owner scope instruction:** Power BI was accepted by the user for this workstream and is no longer being developed here. This acknowledgement does not imply new Desktop or live source verification. Remaining engineering priorities focus on ML reliability, dbt lineage and warehouse data quality.

## ML as-of data quality improvements — 19 October 2026

**Source merged:** [PR #81](https://github.com/senanurcetin/football-player-performance-analysis/pull/81) landed on `main` at `337dd2d48e0edaae9ee8f6b7bd6f85d7e21c616a` with `[skip ci]`. This adds two unexecuted, read-only dbt event-time tests, one unexecuted lineage audit, and enhanced Python input/season contracts. An isolated synthetic reconstruction passed **4 tests** and eight remote SQL/source-contract checks passed. The **full repository suite and authorized BigQuery tests were not run** during integration; source merge does not itself approve empirical model performance or source freshness.

The post-merge quality branch adds training/scoring season and identifier checks, nonnegative prior-market-value enforcement, two warehouse-bound **read-only** singular dbt tests for target/feature date chronology and a research-only historical feature-lineage profiling query. The source SQL files are **not executed** on BigQuery; no source freshness or updated model metrics are claimed. A small isolated input-contract reproduction passed **4/4 local tests**, not a full project checkout. The full regression suite remains pending; the source review and CI-last workflow remain intact.

## Model diagnostic safeguards — 19 October 2026

**Integration record:** Follow-up [PR #80](https://github.com/senanurcetin/football-player-performance-analysis/pull/80) merged into `main` at `779409bf96a19b34d92fdd025ac35898f77260a1` using `[skip ci]`. The merge was verified against the remote `main` head; no hosted CI status checks were reported for that commit. These safeguards have not been evaluated with new authenticated warehouse data, and they do not upgrade production or Desktop acceptance.

A small post-integration research correction protects the player-grouped MAE-skill bootstrap from an undefined ratio in some legitimate cluster resamples. The point estimate remains reportable while an invalid unconditional confidence interval is recorded as **not estimable** (null bounds, explicit status and affected replicate count). The offline audit CLI now refuses output paths that overlap either predictions or metadata inputs. Targeted synthetic numerical behavior was reproduced without BigQuery; full project tests and final CI remain outstanding. See [ML evaluation methodology](ML_RELIABILITY_EVALUATION_20261018.md).

## Visual capture comparison — 18 October 2026

**KONTROL EDİLDİ (limited scope):** All **13/13 production screenshot PNGs** match the dated capture manifest SHA-256 and image-size records. Historical visual measures verified against the June BigQuery documentation: player dimension **47,702**, transfers **40,208**, known-fee coverage **64.2%**, current ML scoring population **7,841**, and decision-ready complement **72.9%**. This is **static historical screenshot/value reconciliation only**; details are recorded in [Power BI historical value audit](POWER_BI_HISTORICAL_VALUE_AUDIT_20261018.md).

**Reference KPI contract corrected (19 October 2026):** `powerbi/MEASURES.dax` was brought into agreement with production PBIR's 365-day maturity cutoff; production PBIR, screenshot artifacts and source tables were not altered. Seven credential-free source-contract tests now exist on `main`, but were not run as part of the complete repository unit test suite.

**Source regression verification (19 October 2026):** The actual production TMDL measures, three report-card JSON bindings, dbt label SQL and read-only diagnostic query were fetched from the PR #79 source before integration. **Six direct source-level assertions passed** for maturity cutoff, observed-only numerator, shared denominator, label-mart difference, KPI binding, and SQL equivalence. New repeatable credential-free Python unit tests were added as `tests/test_transfer_365d_source_contract.py`; they have **not** been run as part of the full repository suite.

**PARTIALLY EXPLAINED AT SOURCE LEVEL (19 October 2026):** The 365-day panel displays **8,581** records using an explicit Power BI **as-of maturity cutoff**, while the historical `fct_transfer_success_labels` has **8,584** observed labels without that cutoff. Native PBIR and dbt definitions are **not equivalent**. The 3-record delta is **not yet independently proven** to consist of immature labels because authenticated warehouse readback remains unavailable. Both player-detail pages show unselected-player/error placeholders in the saved images. No new Power BI Desktop interaction or authorized fresh BigQuery query ran. The overall acceptance state **remains REVIEW PENDING**, independent of verified screenshot checks.

## Verified vs. pending

| Area | Verified evidence | Still open | Status |
|---|---|---|---|
| Repository | Historic screenshot baseline `f3a84d9`; PR #78 merged at `0aaec6f8`, PR #79 merged at `f63ee20a` on 19 October | Full combined checkout tests, authenticated warehouse checks, final approved CI only when authorized | **SOURCE MERGED — acceptance remains pending** |
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
