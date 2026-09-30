## Summary

<!-- What does this PR do? One or two sentences. -->

## Type of Change

- [ ] `feat` — new model, metric, or dashboard page
- [ ] `fix` — corrects incorrect logic or a failing test
- [ ] `refactor` — restructure without behavior change
- [ ] `docs` — documentation only
- [ ] `ci` — workflow or automation change
- [ ] `chore` — tooling, dependency, or config update

## Models Changed

<!-- List any dbt models added, modified, or removed. -->

| Model | Type | Change |
|---|---|---|
| `fct_example` | mart | added |

## Tests

- [ ] `dbt build` passes locally
- [ ] All new models have `not_null` and `unique` tests on primary keys
- [ ] New fact models have a grain assertion
- [ ] `dbt test` passes with 0 errors and 0 warnings

## Documentation

- [ ] All new models have descriptions in `schema.yml`
- [ ] All new columns have descriptions in `schema.yml`
- [ ] `docs/` updated if architecture or KPI definitions changed

## Breaking Changes

<!-- Does this change break any downstream model, metric, or Power BI measure? If yes, describe the impact. -->

None / <!-- describe -->

## Notes for Reviewer

<!-- Anything the reviewer should pay particular attention to. -->
