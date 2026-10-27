# Workintech recovery — isolated warehouse and Power BI source plan (27 October 2026)

**EXECUTION UPDATE (27 October evening):** The authorization/build work described below as future work was subsequently carried out by the Windows owner: 12 sources loaded, 46 dbt models materialized, snapshots and 243 dbt tests passed, seven ML outputs published, and a 31/31 physical Power BI contract passed. The previous procedural text is the *initial plan*, not the current result. See [27 October verified Workintech release record](WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md) and the [Desktop screenshot manifest](assets/screenshots/capture_manifest.json). The owner Desktop imported report has 31 governed plus 34 additional/duplicate BigQuery TMDL table definitions; reconciliation remains open.


**INITIAL MORNING STATUS (now superseded):** At the start of the 27 October recovery, Workintech cloud access, data loading, dbt execution and Power BI refresh had not been verified. See the execution update above for the later authorized build/test results and 13 captured Desktop screens. The text below is a dated planning record, not an authorization for additional billable jobs.

## Recovery evidence on the Windows host

The SentinelX recovery folder is:

`C:\ProgramData\SentinelX\workspace\football-recovery-20261027`

The publisher's `transfermarkt-datasets.duckdb` contains all 12 required raw tables. The 12 original staging SQL statements executed on the real recovered data in a local DuckDB read-only test; 12/12 passed. The publisher snapshot's latest game date is 2026-07-06, not a 27 October production refresh. The original `data-analiz-490513` history and screenshot-to-warehouse transfer keys remain unavailable.

Initial Parquet exports are preserved under `bigquery_raw_parquet/`. A **separate type-harmonized set** is now available under `bigquery_raw_typed_parquet/`, generated with `prepare_typed_bigquery_parquet.py`: 12 tables, source-equivalent row counts and 14 carefully checked integer fields (including `games.game_id`, `club_games.game_id`, `countries.country_id`, `clubs.club_id`, `players.current_club_id`, and seasonal keys). Each cast was checked for unparsable values, leading-zero or canonicalization changes, collisions, null-count drift, and source/target row-count differences. Results are in `bigquery_typed_manifest.json`. The 12 staging SQL sample queries were rerun against the typed files: 12/12 passed.

This proves local Parquet/source compatibility, **not** that BigQuery can execute every downstream model, that the old outputs were reproduced, or that the Workintech service account has usable permissions.

## Isolated target datasets

Workintech credential-file metadata identifies Google Cloud project `workintech-working`. That does not establish authenticated API access. To avoid overwriting any shared Workintech training tables, **never** reuse an existing `football_raw` or `football_mart` dataset for this rebuild. Use a separate namespace:

| Purpose | Proposed dataset (EU) |
| --- | --- |
| Recovered publisher source | `nexus_football_raw` |
| dbt staging | `nexus_football_staging` |
| dbt intermediate | `nexus_football_intermediate` |
| dbt marts / Power BI | `nexus_football_mart` |
| dbt ML | `nexus_football_ml` |
| dbt snapshots | `nexus_football_snapshots` |

The dbt source configuration now supports `DBT_SOURCE_DATASET` with the **existing default `football_raw` preserved**. The dbt profile already supports `DBT_DATASET` with default `football`. When and only when a Workintech project owner verifies scope and authorizes billing, use the following runtime settings **outside GitHub source control**:

```text
DBT_PROJECT_ID=workintech-working
DBT_SOURCE_DATABASE=workintech-working
DBT_SOURCE_DATASET=nexus_football_raw
DBT_DATASET=nexus_football
DBT_KEYFILE=<local authorized service-account JSON path, never committed>
```

The `profiles.yml.example` BigQuery region is EU. The actual dataset location, project-level `bigquery.jobs.create`, dataset read/write IAM and billing limits must be checked before any load/build jobs.

**Cloud load procedure, only after authorization:** create an empty EU `nexus_football_raw` dataset; load each table as a *new* destination from its matching typed Parquet file (12 named tables); reject any already-existing destination; compare full row counts and BigQuery physical types to `bigquery_typed_manifest.json`. Google documents local Parquet uploads with `bq load --source_format=PARQUET PROJECT_ID:DATASET.TABLE LOCAL_FILE`. The CLI normally appends when the table already exists, which is **unsafe** for this migration: preflight the target and refuse any collision. Use a cost- and scope-approved dbt staging sample, then full test/build only after the source checks pass.

References: [BigQuery batch loading](https://cloud.google.com/bigquery/docs/batch-loading-data), [Parquet schema behavior](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-parquet).

## Power BI source copy

A separate, native editable PBIP was prepared on the Windows host:

`C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-workintech\FootballPlayerAnalysis\FootballPlayerAnalysis.pbip`

It retains the Google BigQuery connector and **Import** mode. In this separate copy, 31 TMDL files were rebased from old project `data-analiz-490513` to `workintech-working` (93 source references), and the 22 mart + 9 ML schema references were further isolated to `nexus_football_mart` and `nexus_football_ml`. The original GitHub Power BI PBIP remains intact.

The source copy is **NOT a verified live connection** until the two datasets exist with expected models, Desktop credentials are authorized, and a refresh is observed to succeed. For unattended automatic updates, publish and configure a Power BI Service cloud data-source credential and **scheduled refresh**; the existing Import model does not update itself merely because its query points to BigQuery. The upstream data acquisition/dbt refresh and the Power BI Service model refresh are **separate** scheduled processes. See [Microsoft's BigQuery connector](https://learn.microsoft.com/en-us/power-query/connectors/googlebigquery) and [scheduled refresh](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-scheduled-refresh).

## Release gates held

- Historical screenshot metric parity and original 365-day three-row transfer discrepancy remain unreconciled.
- The recovered public snapshot is not equivalent to lost BigQuery snapshot history.
- Production ML re-training and rolling holdout, Power BI Desktop drillthrough/refresh, and final nine-job CircleCI remain unexecuted.
- No secret/key JSON is in this repository. Do **not** upload or paste the private service-account key. Any required user-side authentication should use the platform's supported credential dialog.

All present local checks are bounded to the source snapshot, type parity, static PBIP, and sample staging SQL; they do not confer permission to query another Google Cloud project.
