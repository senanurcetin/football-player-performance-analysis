# NEXUS Football — CI-last release policy

> **Updated 19 October 2026:** Offline Python tests **243/243 on the original checkout and 246/246 after repository hygiene tests**, source/dbt parse and structural checks PASS via SentinelX; **BigQuery table tests, corrected real-data model evaluation and final hosted CI remain NOT RUN**. This document is a release policy and historical CI incident record, not a new CI pass. See [Project status](PROJECT_STATUS.md).

**Current decision (13 October 2026):** development, source repairs, real Desktop acceptance and local tests come **before** any new CircleCI verification run.

## Workflow boundary (updated against checked-in YAML, 19 October 2026)

- **CircleCI:** the sole nine-job workflow requires `run_final_ci=true`; ordinary branch pushes may register empty pipelines but must not be called test passes.
- **GitHub `dbt CI`:** `.github/workflows/dbt-ci.yml` has **only `workflow_dispatch`**; even manual `offline-preflight` needs `ENABLE_GITHUB_ACTIONS_CI=true`; warehouse `validate` additionally needs `ENABLE_BIGQUERY_CI=true` and permitted credentials. PR/schedule-specific YAML steps are presently unreachable via the configured event set.
- **GitHub `ML Production`:** `.github/workflows/ml-production.yml` previously scheduled weekly but now has **manual dispatch only**. A manually invoked job requires both the repository variable `ENABLE_ML_PRODUCTION=true` and the per-run Boolean input `confirm_final_release=true`. This does not rely on `ENABLE_GITHUB_ACTIONS_CI`. It may incur BigQuery charges and publish model tables; activate only after the full research, source, Desktop and final CI gates pass. On 19 October 2026 the old scheduled run **failed before any BigQuery work**, because the GitHub secret `GCP_SERVICE_ACCOUNT_JSON` was empty. No new CI was triggered as part of this change.
- GitHub status with no check results is **NOT RUN/UNKNOWN**, never PASS. For current results and exact source proof see [Project status](PROJECT_STATUS.md).

## Trigger policy

`.circleci/config.yml` defines a boolean `run_final_ci` pipeline parameter with `default: false`. The only CircleCI workflow (`verify-offline-source`) has a `when: << pipeline.parameters.run_final_ci >>` guard:

- Ordinary GitHub branch or pull-request pushes do not run the nine CircleCI **jobs** by default, even though CircleCI might still register an empty/filtered **pipeline** event.
- Do not set the parameter to `true`, rerun a workflow, or manually trigger CircleCI until the completion criteria below have been met.
- If the required source/config edits themselves create commits, append `[skip ci]` to their messages and squash-merge titles while this policy is active; this is an extra safeguard, not a replacement for the workflow guard.
- The gate is designed for manual or API-based CircleCI runs. At the final stage, explicitly trigger the *current production branch* with `run_final_ci=true`, then require all nine job checks to pass. Do not use a shared token in committed scripts or markdown.
- The configuration does not disable GitHub Actions or external integrations outside the single CircleCI workflow. Inspect project-level triggers if a new pipeline still consumes credits.

The `run_final_ci` mechanism uses CircleCI's documented boolean pipeline-parameter and workflow-level `when` syntax.

## Local source, data and owner acceptance — required before CI

1. **Close source defects and planned development.** Review actual PBIR pages and assets, check native navigation, labels, chart bounds, custom fonts and demo provenance. Do not replace source PBIR with mockups.
2. **Run offline source checks locally from the repo root**, recording exit codes and error output, rather than triggering CI:
   ```powershell
   python -m compileall -q scripts
   python scripts/check_offline_ci.py
   python -m unittest discover -s tests -p 'test_powerbi_audit.py' -v
   python -m unittest discover -s tests -p 'test_powerbi_chart_design.py' -v
   python scripts/audit_powerbi_visuals.py --mode both
   python scripts/check_powerbi_project.py
   python scripts/check_powerbi_offline_demo.py
   python scripts/check_powerbi_release_handoff.py --output powerbi-handoff.json
   ```
   Install `PyYAML==6.0.3` and `Jinja2==3.1.6` for the offline dbt/Jinja check. The separate ML deterministic check is `python scripts/check_ml_pipeline.py` with the repository's `requirements-ml.txt`. All test failures must be triaged and fixed before requesting a hosted run.
3. **Open production PBIP in Microsoft Power BI Desktop.** Confirm all 13 report surfaces (9 visible + 2 hidden drillthrough + 2 hidden tooltips) including labels, formatting, navigation, real logo and clipped content at 100% zoom.
4. **Refresh real BigQuery data** and reconcile representative KPI metrics with governed warehouse sources. Resolve actual conversion issues in `fct_club_risk_profile` if present. Check `fct_club_performance.win_rate` after the new production fraction-normalization step. The offline-demo fixture cannot substitute for real warehouse evidence.
5. **Review evidence**, including successful local test output, committed changes, production row/refresh count, screenshots, known issue list and verified source-to-report metric values. Resolve material issues before requesting final CI.
6. **Only then run CircleCI once** with `run_final_ci=true` on the final commit; investigate anything other than nine successful job results. Keep portfolio publication on **HOLD** until CI and Desktop/BigQuery sign-off both pass.

## Existing CI failure — do not misclassify

At the decision point, GitHub commit `87b9459c2250fe3e099192d966e6e1c8aeaeb070` reported **8 successful and 1 failing** CircleCI job:
- Failed: `ci/circleci: dbt-source-preflight` — https://circleci.com/gh/senanurcetin/football-player-performance-analysis/569
- Other eight jobs: successful.

The same preflight job was failing on the immediately preceding main commit. Its current job covers **offline YAML/Jinja syntax, Python compileall, native PBIR audit/design tests, and production/demo PBIP source checks**. The detailed historical CircleCI job log was unavailable, but an **actual local checkout on Windows (Python 3.11.9)** reproduced a specific failing step: `test_powerbi_chart_design.py::test_transfer_success_has_distinct_evidence_first_geometry` expected two 260px lower chart heights, while **both actual native PBIR visual heights are 239px**, ending at y=671 before the footer. This invalid source assertion is corrected in the subsequent preflight repair.

The same local sweep found one additional issue outside that CircleCI failure: ML Reliability's native Home button intersected the NEXUS logo (button x=182–301, logo x=92–266). The button was moved to x=1040 without changing its Home route; a coordinate regression guards the fix. The market-page overlap auditor also found an older transfer-count chart almost hidden behind the transaction table (**87.45%** of its area), spilling below the footer. The preserved chart is now a native NEXUS-colored panel at x=985, y=470, 248×201 beside the table with unchanged query bindings.

**Local verification on the repaired branch:** Python compilation PASS; `scripts/check_offline_ci.py` PASS (11 YAML / 51 SQL-Jinja source files); **80/80** Power BI unittests PASS; `check_powerbi_project.py`, `check_powerbi_offline_demo.py` and full `check_powerbi_release_handoff.py` PASS; `audit_powerbi_layout.py` reports **zero warnings across both editions**. The handoff correctly records `source_checks=PASS`, while `powerbi_desktop_refresh=NOT_VERIFIED`, `bigquery_production_reconciliation=NOT_VERIFIED`, and `portfolio_release=HOLD`. This is local evidence, not a new CircleCI success status; the hosted job remains unverified until final opt-in.

## CI trigger and release state

This source change gates **future** CircleCI jobs only. It does not retroactively repair the existing failed status, prove CircleCI can still start after manual opt-in, or verify real Power BI runtime and BigQuery credentials. Those proofs remain separate acceptance criteria.
