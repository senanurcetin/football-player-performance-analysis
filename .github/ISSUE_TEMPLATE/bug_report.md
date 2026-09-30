---
name: Bug report
about: Report incorrect data, a failing test, or a broken model
title: "fix: "
labels: bug
assignees: ''
---

## Describe the Bug

<!-- A clear and concise description of what is wrong. -->

## Affected Model or Component

<!-- Which dbt model, ML script, Power BI page, or CI workflow is affected? -->

- Model: `fct_example`
- Layer: staging / intermediate / mart / ml / power-bi / ci

## Steps to Reproduce

```bash
dbt run --select fct_example
dbt test --select fct_example
```

<!-- Or describe the steps in the Power BI report that trigger the issue. -->

## Expected Behavior

<!-- What should happen? -->

## Actual Behavior

<!-- What actually happens? Include error messages or test output. -->

## Environment

- dbt version:
- Python version:
- BigQuery project:
- OS:

## Additional Context

<!-- Any other context — related models, known data quality issues, recent changes. -->
