# NEXUS Football — Workintech semantic model deduplication pilot

**FOLLOW-UP COMPLETED — 28 October:** [Full 31-source deduplication in an isolated QA PBIP](WORKINTECH_FULL_DEDUP_QA_20261028.md) now passes six additional static regression tests (34 unique imports, 87 valid join relationships, no missing endpoints or join type mismatches). The original pilot and active Power BI source remain preserved. Power BI Desktop model-engine load and DAX semantic equivalence remain unverified.


**Evidence:** 27 October 2026. **Decision:** an isolated three-table source-code pilot passed offline checks; no changes were made to the owner's active Power BI model. No new screenshots are required or requested.

## Pilot changes (sandbox only)

The following three tables were removed **only in an independently copied PBIP project**:

| Redundant semantic table | Retained physical BigQuery source | Field compatibility |
| --- | --- | --- |
| \`fct_agent_portfolio (2)\` | \`workintech-working.nexus_football_mart.fct_agent_portfolio\` | 17 columns, names/types matched |
| \`fct_data_coverage_bias (2)\` | \`workintech-working.nexus_football_mart.fct_data_coverage_bias\` | 21 columns, names/types matched |
| \`fct_transfer_cohort_performance (2)\` | \`workintech-working.nexus_football_mart.fct_transfer_cohort_performance\` | 20 columns, names/types matched |

Each redundant table was checked for absence of relationships, Power BI visual/query references, DAX measures and textual references in all other source-side files. In the sandbox, only its table definition, its corresponding \`ref table\` and \`PBI_QueryOrder\` entry in \`model.tmdl\`, and its diagram node were adjusted.

**Result:** 13/13 pages, 308/308 visuals, and original relationship definitions were preserved. All other source files remained byte-for-byte identical. The versioned repository PBIP and owner's active PBIP were **not** edited by this pilot. This is *not* a claim of successful Desktop runtime model loading; the pilot needs further non-screenshot validation before promotion.

**Audit JSON:** \`C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-dedup-pilot-20261027\safe_three_table_dedup_pilot.json\`

**Isolated PBIP:** \`C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-dedup-pilot-20261027\FootballPlayerAnalysis\FootballPlayerAnalysis.pbip\`

## Remaining model migration complexity

The original project includes **65 BigQuery-connected semantic tables:** 31 governed, 31 second imports of the same physical sources, and three additional tables not represented among the governed 31.

There are **158 original TMDL relationships**, of which **80** touch \`(2)\` imports. The relationship migration matrix partitions those 80 as follows:

| Category | Relationships | Release action |
| --- | ---: | --- |
| Identical endpoint pair and relationship attributes already exist on governed tables | 29 | Potential to remove the redundant relation only after end-to-end filter equivalence |
| Same endpoints but **different cross-filter behavior** | 2 | Explicitly decide and test filter direction before consolidation; never silently overwrite |
| Generated \`LocalDateTable_...\` relationships attached to duplicates | 40 | Validate associated date-hierarchy, variation and table metadata before removal |
| Novel relationships not present in governed graph | 9 | Retain or explicitly migrate to unique governed endpoints with cardinality/fanout checks |
| **Total affected** | **80** | **Do not bulk delete remaining duplicates** |

The **two cross-filter differences** affect relationships from \`ml_player_market_value_current_predictions\` and \`ml_player_market_value_scoring\` to \`dim_players\` on \`player_id\`. Removing or merging these without specifying filter behavior risks changing which player/ML rows appear in reports.

Among the nine non-date novel links are relationships for \`fct_player_rolling_form\`, \`fct_player_match_performance\`, the national-team dimension, current-predictions-to-scoring, and feature-drift-to-importance. The three additional tables can thus be business-useful rather than automatic garbage.

**Detailed report:** \`C:\ProgramData\SentinelX\workspace\football-recovery-20261027\workintech_relationship_migration_plan.json\`

## Reproducible, screenshot-free checks

From the repository root:

\`\`\`powershell
python scripts/pilot_workintech_safe_dedup.py --dry-run
python scripts/plan_workintech_relationship_migration.py
python -m unittest discover -s tests -p test_workintech_dedup_planning.py
\`\`\`

The first command plans but makes no changes. Running the pilot script without \`--dry-run\` creates a **fresh isolated QA copy** in the documented recovery directory, and refuses to overwrite any pre-existing QA copy. Never point it at the owner-edited Desktop PBIP as its output. The second command generates only the relationship matrix. The tests inspect source structure, duplicate compatibility, exception counts and no-screenshot/no-active-mutation safeguards.

**Five focused regression tests passed** in the local offline environment.

## Gates before controlled production promotion

1. Produce a complete mapping for all 40 auto-date relations (including \`ref table\`, variations, relationships and diagrams).
2. Resolve the two ML cross-filter differences based on desired player-selection semantics.
3. Preserve nine unique relationships or explicitly replace them with demonstrably equivalent model paths.
4. Run model-engine/TMDL loading and semantic query equivalence checks against the unchanged active report, without user screenshot requests; *source validation alone is insufficient*.
5. Preserve full rollback and version history, measure definitions, 13 pages and 308 visuals.
6. Only then stage a separately reversible Desktop report upgrade. Never mutate BigQuery datasets to solve PBIP relationship duplication.

**Current conclusion:** isolated pilot passes static safety checks. Wider duplicate consolidation and commercial-release approval remain blocked pending relationship and runtime validation.
