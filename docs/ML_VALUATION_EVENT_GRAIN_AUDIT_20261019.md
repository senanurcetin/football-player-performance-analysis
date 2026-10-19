# Same-day valuation grain and source-conflict policy — 19 October 2026

> **Later verification on 19 October:** All declared Python source/SQLite checks, including target-coverage parity, ran in the independent **243/243 PASS** full test suite. Credential-free dbt parse recognized the model/test definitions. **No BigQuery target exclusion counts or corrected real-data model scores were obtained.** Earlier isolated-test statements below describe the implementation stage, not the latest test state. [Executed evidence](SENTINELX_OFFLINE_VERIFICATION_20261019.md).

**Scope:** Research-oriented BigQuery/dbt feature integrity for the existing Football Intelligence project. **No productization, model publication, new valuation claims or Power BI changes.**

## Defect and prevention

The prior `ml_player_market_value_training.sql` joined a player-season target directly to `stg_player_valuations` on **player + valuation date**. If the upstream valuation data contained duplicate player-date records, one target could become several rows with the **same `training_row_key`**. Downstream feature aggregates might then be weighted multiple times; the historical model's unique-row and time-split assumptions would be invalid. In both training and current scoring, `ARRAY_AGG ... ORDER BY valuation_date DESC LIMIT 1` also had nondeterministic tie behaviour on a player-date with conflicting EUR values.

Both model sources now use the same pre-aggregation:

- One canonical **player ID + calendar valuation date** is formed from staged rows with a **strictly positive EUR value** and non-NULL valuation date. Identical duplicates collapse to one daily event.
- A date is **usable only when the distinct positive EUR value count is exactly one**. Conflicting positive same-day amounts are excluded rather than resolved with arbitrary MAX/last-row selection. Scoring and training's prior-value features consider only these usable dates.
- The competition ID is included only where its **distinct known ID count is exactly one**. If several valid source competition IDs disagree on an otherwise consistent valuation date, market value is retained and competition context becomes NULL.
- The training label join additionally requires **the canonical date and EUR value to match the player-season target**. Each candidate can match at most one canonical daily valuation row. Excluding a mismatched target is a **dataset-selection change**; whether this removes any real records has not yet been measured.
- `prior_valuation_count` now counts distinct **usable daily valuation events**, not duplicate physical source rows. `prior_highest_market_value_eur` and previous-value baseline use only the canonical daily set.

This is a **source-quality policy**, not a recommendation to replace unknown observations with zero. Competition context can remain missing; a missing previous value still invokes the existing baseline fallback. No change was made to the published model scoring weights or source table schemas.

## Latest player-season target and row-coverage correction — 19 October 2026

Source-only verification found a second problem after initial player-date deduplication: the historical target selector used `ARRAY_AGG` ordered by **date only**, so conflicting market values at the **same latest player-season date** could still be chosen nondeterministically. Also, `tests/assert_ml_training_row_coverage.sql` expected all positive timeline candidates even though canonical source conflicts are intentionally ineligible, creating a guaranteed false coverage failure when the exclusion policy is exercised.

- `ml_player_market_value_training.sql` now groups targets at **player, season, date**, producing NULL target EUR on conflicting positive values. It then selects the latest date, **without falling back to an older date** merely because the newest date conflicts. Its canonical player-date-EUR join excludes such records.
- `assert_ml_training_row_coverage.sql` constructs the **same expected eligible population**, including exact source canonical date/EUR matching, and compares expected/actual keys bidirectionally. A separate raw-candidate audit remains necessary to quantify exclusions and selection bias; this test cannot establish that no records were lost.
- `analyses/audit_ml_valuation_event_grain_20261019.sql` uses the same latest-target policy and reports `conflicted_latest_player_season_targets`. Without current BigQuery results, the number of excluded rows is still **UNKNOWN**.
- `tests/test_ml_target_coverage_parity.py` adds four source/SQLite synthetic checks. A local SQLite demonstration verified that a conflicted latest date is **NULL** while a duplicated consistent date retains one positive EUR value. This is **not** the complete checkout's unit tests nor a dbt compilation.

**Release gate:** After authorized BigQuery source and credentials are available, compile dbt, run `assert_ml_training_row_coverage` and the unique-key tests, inspect the candidate-vs-canonical exclusion summary, and rerun the corrected historical ML evaluation. No production numeric results are asserted from source changes.

## Reproducible verification

Run without BigQuery credentials from a full checkout:

```bash
python -m unittest discover -s tests -p 'test_ml_valuation_event_grain.py' -v
python scripts/check_offline_ci.py
python -m unittest discover -s tests
```

The new test file extracts the **literal CTE from both SQL model files**, compares them for parity, and executes that grouping logic on synthetic player-date valuation fixtures using Python's **SQLite**: exact duplicates, ambiguous EUR amounts, conflicting competition IDs, invalid/missing amounts, and unique supervised-target joins. These tests do **not** validate BigQuery-specific dbt compilation or the real source distribution.

In a separate isolated local SQLite reproduction of the same grouping and target-join logic, **5/5 synthetic cases passed** (not the complete GitHub checkout). The committed suite declares **six tests**, including a source-contract equality check that has not been run in the full repository test harness.

## Governed warehouse checks before any real model retraining

The read-only `analyses/audit_ml_valuation_event_grain_20261019.sql` reports:

- Raw valuation rows and distinct player-date groups.
- Days with repeated source rows; consistent vs. conflicting positive market values.
- Same-day disagreement in competition ID without value disagreement.
- Historical candidate player-season targets and the count that still matches the exact canonical player/date/EUR event.
- The number of candidate labels **excluded** by the new canonical policy (positive conflicts or unmatched date/value). Do not assume this count is zero or attribute it to one root cause without source-row readback.

Run only with the user-authorized, cost-controlled BigQuery/dbt profile. Record project, as-of/source modification time, query output, the pre/post model grain, Git commit SHA and changes to sample counts **before** treating the new source model as accepted. Existing dbt `unique` and `not_null` tests on `training_row_key` remain required; additionally rerun both temporal as-of SQL tests. The query is not a fixture generator and does not mutate data.

**Acceptance status as of 19 October:** Source implemented; complete Python test suite **243/243 PASS** and credential-free dbt parse PASS. **BigQuery mart execution, actual exclusion impact, real-data model refit and empirical quality-gate evaluation remain NOT VERIFIED.** CI remains final-stage opt-in. Power BI has separate prior owner acceptance.
