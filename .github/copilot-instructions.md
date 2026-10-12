# GitHub Copilot instructions — Football Player Performance Analysis

## Project identity
This repository is a dbt/BigQuery football analytics project with a Power BI/PBIR dashboard and a separate leakage-aware market-value ML study. Read `README.md`, `docs/ARCHITECTURE.md`, existing SQL tests, and the relevant `powerbi/` sources before changes. README numbers and dashboard screenshots are historical published evidence, not automatically updated by code changes.

## Core invariants
- Do not change fact/model grain, join keys, season filters, financial units, or metric definitions to make a chart attractive. A Turkish `B` on current visuals represents **bin (thousand)**, not billion.
- For Power BI edits preserve report page metadata, visual IDs and valid PBIR JSON/schema. Do not treat an editorial cover as a real dashboard capture; avoid generating screenshots as proof of rendering.
- Distinguish real Transfermarkt/BigQuery marts from synthetic offline demo models. Keep synthetic-demo labels where demonstration data appears.
- Prevent target leakage: split player valuation chronologically and distinguish current-value persistence from predictive signal for future value **changes**.
- Attribute upstream dbt model work correctly; do not claim inherited models were originally written here.

## Safe verification
- Run `python -m compileall -q scripts` and `python scripts/check_offline_ci.py` for dbt/sql/source checks when local requirements are available.
- Inspect `scripts/check_powerbi_project.py` and `scripts/check_powerbi_offline_demo.py` for the applicable offline report validation; run only after checking arguments and existing dependencies.
- Avoid calling BigQuery, dbt cloud builds, paid APIs, model retraining or Power BI Desktop unless explicitly authorized. An offline PBIR structural check does not prove visual fidelity or that real measures refresh correctly.
- Keep changes scoped, add deterministic tests for program logic where feasible, and report actual commands, results and still-unverified claims.

## Coordination
- `.github/agents/powerbi-evidence-qa.agent.md` is the opt-in agent for report integrity.
- Do not modify unrelated portfolio assets, licenses, CI or other concurrent PRs. Never auto-merge.
