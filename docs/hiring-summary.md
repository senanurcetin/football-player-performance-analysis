# Reviewer brief — Football Player Performance Analytics

**Project type:** Workintech educational team project (collaborative, not individual authorship). **Scope:** analytics engineering, BI and leakage-aware player valuation ML. **Provenance:** an extended fork of earlier collaborative dbt work; upstream authorship and added work are separated in the [README attribution](../README.md).

## Business decision

Translate Transfermarkt player and club data into consistent performance metrics, drill-through reporting and forecasts that can be compared with a simple previous-value baseline.

| Review question | Evidence |
|---|---|
| Does the warehouse layer have a governed scope? | **46 dbt models**, **241/241 tests**, **46/46 model descriptions** in the documented June 15, 2026 validation snapshot; [status](PROJECT_STATUS.md) |
| Does valuation beat persistence? | v5 ensemble **R² 0.9756** vs prior-value baseline **0.9704**; MAE **€781,409** vs **€867,156**; [model comparison](../README.md#market-value-modeling-and-limitations) |
| How much skill remains after asking about value *change*? | A distinct time-split Kaggle study reports much weaker R² on **change** (about **0.22**), and explains why high level-value R² is deceptive: [study](https://www.kaggle.com/code/senanuretin/your-market-value-r2-is-mostly-last-year-s-price) |
| What does the BI report look like? | [Current genuine screenshot gallery](assets/screenshots/README.md), [release acceptance summary](../README.md#release-acceptance-status), and [visual QA requirements](POWER_BI_VISUAL_QA.md) |
| Can the workflow be reproduced? | [dbt and ML quick start](../README.md#reproduction), [models](../models/), [tests](../tests/) |

## Contribution boundaries

The project was developed as a team during the Workintech training program. This repository inherits source definitions and part of the dbt model layer. The README attributes **28 of 46 models** to the upstream work and describes the additional 16 models, singular tests, semantic layer, snapshots, ML pipeline and Power BI reporting in this fork. Do not present all inherited models as newly authored.

## Interpretation limits

These are historical snapshots of public dataset experiments, not a live transfer-market pricing system. A strong R² on price **level** is not equivalent to strong prediction of future price **changes**; preserve the different dataset/split/model versions when comparing the two results.

**Full project:** [Architecture, BI, evaluation and licensing](../README.md).
