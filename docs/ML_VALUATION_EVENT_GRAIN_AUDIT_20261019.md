# Same-day valuation grain and source-conflict policy — 19 October 2026

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

**Acceptance status:** Source implementation and synthetic SQLite reproduction completed. **BigQuery mart rebuild, actual exclusion impact, real-data model refit, quality-gate evaluation and complete repository test execution remain NOT VERIFIED.** CI remains final-stage opt-in by user request. Power BI is outside this research workstream by owner instruction.
