# NEXUS Football — Autonomous Offline Quality Gate (27 October 2026)

**MIGRATION EVIDENCE ADDENDUM:** [Sandbox-only three-table removal and full relationship migration matrix](WORKINTECH_DEDUP_PILOT_20261027.md). Of 158 original model relationships, 80 refer to duplicate imports (29 identical, 2 cross-filter disagreements, 40 auto-date links, 9 new non-date links). The offline gate now records these counts; no production consolidation or extra screenshot is authorized.


**Status: RELEASE HOLD for commercial production; source and structural audits executed without new screenshots.**

This assessment uses the actual, owner-edited Workintech PBIP source, the versioned repository copy, and the original typed Kaggle Parquet archive. **No additional screenshot from the owner is required at any phase of this workflow, including future development acceptance.** Screenshots captured on 27 October remain historical visual evidence, not a substitute for independently verified post-fix Desktop rendering.

## Verified current scope

| Area | Verified | Decision/interpretation |
| --- | --- | --- |
| Power BI source structure | 13 pages, 308 visual files | Structural integrity passed; live post-fix Desktop rendering was not directly observed |
| Governed BI source contract | 31 expected BigQuery table definitions | Original physical table/column checks passed in the separate owner-executed warehouse job |
| Extra imported BI tables | **31 duplicated physical sources + 3 additional physical sources** = 34 | **31 of these extra table definitions participate in relationships**; do not remove or rename them without migration mapping |
| Raw games | **88,958 rows, 88,958 distinct game IDs** | No duplicated game IDs or orphan appearance-to-game references in the checked source |
| Orphan appearances | **2 appearances**, both for missing \`player_id=380365\` in September 2018 | Preserve provenance; investigate join coverage and do not invent a player identity |
| Competition dictionary gaps | **1,214 games** refer to POCP/CGB/COL1/KLUB/UKRS, absent from publisher's 65 competition records | Previously handled by five explicit *unknown metadata* entries; never invent league/country facts |
| Valuations | 656,301 rows; **zero contradictory same-player same-date EUR values**; one nonpositive value | Existing ML training filters require positive targets |
| Transfers | **475 future-dated rows as of 27 October 2026** | They may be future effective/planned transfers; the 365-day observed outcomes SQL already excludes \`is_future_transfer\` |
| Source freshness | Latest match **6 July 2026** | Historical football analysis, **not** a live present-day fixture feed |
| Screenshots | **13/13 archival PNG hashes verified** | No new screenshot capture or upload requested |

### Risk classification

**P1: Semantic duplication.** The 31 governed model tables share underlying BigQuery physical tables with 31 additional imports. Relationship graph analysis identified 31 extra definitions with at least one relationship endpoint. The report also contains three physical imports outside the 31-table governed contract: \`dim_national_teams\`, \`fct_player_match_performance\`, \`fct_player_rolling_form\`. Some of those are related too. This is a semantic migration problem, not a simple file clean-up; blindly deleting them could alter filter propagation and break visuals.

**P1: Source identity coverage.** Two September 2018 appearances refer to a player missing from the source player master. The absolute impact is small, but joins to a dimension can silently discard these events. Add an explicit exception report or unknown-key policy before claiming 100% identity coverage. Do not generate a fictitious player.

**P2: Known publisher competition gaps.** Five additional source codes cover 1,214 games. The existing staging reference-completion approach preserves the games while leaving absent descriptive attributes NULL.

**P2: Temporal business semantics.** There are 475 transfers dated after the evidence date, but downstream observed 365-day outcomes filter them using \`where not is_future_transfer\`. Future dates do not prove a realized transfer; the distinction must remain enforced. The source contains one nonpositive valuation; the ML target selector requires values greater than zero.

**ML release trust boundary.** Historical time-split evaluation, group-level uncertainty, feature leakage and drift controls require evidence on actual holdout outputs before a commercial player-valuation decision. A passed local unit test is not proof of expected real-world forecast accuracy.

## New repeatable, screenshot-free checks

1. \`scripts/audit_workintech_semantic_model.py\` — graph/duplicate inventory of BigQuery imports, relationships and explicit PBIR references. Writes dependency evidence; never deletes a table.
2. \`scripts/profile_workintech_source_quality.py\` — reads the local publisher Parquet archive with DuckDB and measures row-count parity, match keys, orphaned appearance relationships, valuation grain, chronology and source metadata gaps.
3. \`scripts/run_workintech_offline_release_gate.py\` — runs the two audits, validates 13 existing PNG hashes and creates a **RELEASE_HOLD** / explicit-gate evidence record, without BigQuery jobs or fresh screenshots.
4. \`tests/test_workintech_professional_readiness.py\` — regression checks ensuring that release-hold risks cannot be concealed by accidental file deletion or changes in the future-transfer / positive-target SQL guards.

In the authorized Windows development environment, from the repository root:

\`\`\`powershell
python scripts/audit_workintech_semantic_model.py
python scripts/profile_workintech_source_quality.py
python scripts/run_workintech_offline_release_gate.py
python -m unittest discover -s tests -p test_workintech_professional_readiness.py
\`\`\`

Local evidence JSON (outside Git): \`C:\ProgramData\SentinelX\workspace\football-recovery-20261027\workintech_semantic_dependency_audit.json\`, \`workintech_source_quality_20261027.json\`, \`workintech_offline_release_gate.json\`. No service-account keys, JWTs or OAuth contents are copied into these reports.

## Safe next engineering actions

1. **Model migration plan:** categorize extra tables by physical source, relationship endpoints, DAX dependencies and potential selected-player drillthrough dependencies. Work on an isolated copy; preserve the active 13-page model. Eliminate duplication only after equivalent query/filter contracts pass.
2. **Source-quality exceptions:** persist the two orphan appearance IDs as explicit exceptions and retain documented unknown competition references. Add alerts only for newly detected anomalies.
3. **Temporal ML/transfer evidence:** preserve future-transfer exclusion and positive/unique label gates. Compare actual model evaluation metrics against a player-grouped chronological holdout.
4. **BI/report quality:** apply proven PBIR source fixes and audit visualization configurations without asking for new screenshots. **Do not claim live visual verification unless programmatically observed in the same Power BI Desktop session.**
5. **Operational readiness:** publish and schedule service refresh only after the existing model/reconciliation and IAM boundaries have been accepted. This audit does not authorize billable cloud operations or CI runs.

**Decision:** This is an advanced professional analytics architecture **with unresolved production-release conditions**, not yet an independently accepted live commercial analytics service.
