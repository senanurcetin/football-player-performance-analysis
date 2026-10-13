# NEXUS Football Intelligence — Power BI product handoff

**Product:** Football Intelligence Workbench  
**Native deliverable:** one editable Power BI project (PBIR/PBIP) in two **data-source editions**, not duplicate slides.  
**Status:** **SOURCE DESIGN READY / DESKTOP ACCEPTANCE ON HOLD**. Last source work: 13 October 2026.

## What the product enables

| User question | Native report experience | Evidence constraint |
| --- | --- | --- |
| Which player profiles show durable form? | Performance, per-90 analysis, segmentation and player detail | Interpret minutes and sample size before ranking |
| Which clubs and leagues warrant investigation? | Club/league comparisons and competition activity | Selection, season and source coverage can bias results |
| What happened after a transfer? | Transfer Success (365d), fee/value analysis and transfer detail | Observed 365-day outcomes; **not** predicted success or causal uplift |
| How credible are valuations? | Market Value Prediction, model reliability and player prediction drillthrough | Report model estimates and out-of-time quality separately from facts |

The visible story runs Home → Player Performance → Segmentation → Club & League → Transfer Success (365d) → Transfer & Market Value → Market Value Prediction → ML Model Reliability → Closing. Player Transfer Detail and Player Prediction Detail are hidden drillthrough pages; Transfer and Prediction Tooltip pages are hidden hover surfaces.

## Art direction and UX contract

NEXUS **deep navy** `#071829`, hero `#091E33`, primary blue `#4EA8FF`, lavender `#8F9BFF` and indigo `#487FD8`; white data surfaces, accessible navy labels and amber/rose risk colors. Editorial Home/Closing are dark. Intermediate pages deliberately vary between deep blue, ice blue, lavender and slate rather than repeating a single card layout.

The editable native visuals in both drillthrough detail pages have had legacy green/teal/gray literals normalized to NEXUS colors; chart/category/metric/query bindings and navigation links are retained. The production Home/Closing tab titles are plain-text `Home` and `Closing`. Demo tabs retain their prominent `[DEMO]` labels.

## Product editions and safe operating model

| Edition | Open this file | Intended use |
| --- | --- | --- |
| Production | `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` | Authenticated Google BigQuery marts, governed performance/transfer/valuation analysis |
| Offline demo | `powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` | Credential-free **synthetic** UI and interaction demonstrations |

The offline demo uses fictional fixture tables and must *never* be described as containing real athlete outcomes or production model evaluations. Do not mix demo screenshots with production KPI claims. The observed transfer-success contract is **365 days**, with a **20-percentage-point** value-growth threshold; use eligible/observed denominators and follow-up coverage when interpreting rates.

## Quality gates before external launch

1. **Static source check, no CI quota**: from repository root run `python scripts/check_powerbi_project.py`, `python scripts/check_powerbi_offline_demo.py`, `python scripts/audit_powerbi_visuals.py`, `python scripts/audit_powerbi_layout.py`, and `python scripts/check_powerbi_nexus_product.py`. Review warnings and unintended data overlaps. These checks do not execute DAX or certify rendering.
2. **Power BI Desktop**: open and refresh the offline demo. Confirm all **11 full-size** pages and **2 tooltip** pages, 33 fixture tables, navigation, hidden drillthroughs, axis units, row context, fonts, clipping and contrast at 100%.
3. **Production evidence**: authenticate BigQuery separately. Reconcile 365-day labels, market-value units, source freshness, per-90 rankings, data coverage, ML error/baseline and uncertainty to warehouse/ML sources. No production publication on synthetic evidence.
4. **Publish only actual native renders**: after Desktop acceptance capture current screenshots with commit/ref and data source, visibly mark demo captures `SYNTHETIC DEMO`, and replace HOLD in release notes only after signoff.

## Packaging and release discipline

- Ship the **editable report** and this handoff, not an extra PowerPoint/PDF export or fabricated image.
- Keep the two data-source editions separate. The repeated report is intentional, while duplicated static asset mirrors and old green-era galleries are excluded.
- CI is intentionally not invoked for this work. The `[skip ci]` commits are **not** evidence of passing tests.
- Final customer/portfolio publication remains **on hold** until real Power BI Desktop refresh, rendering and measurement validation are recorded in [the visual QA release gate](POWER_BI_VISUAL_QA.md).

**Related specifications:** [NEXUS design system](BI_DESIGN_SYSTEM.md) · [Report modernization plan](POWER_BI_ALL_DASHBOARDS_PLAN.md) · [Power BI modeling](POWER_BI_MODELING.md).

**Production refresh troubleshooting:** [club-risk table schema and error triage](POWER_BI_CLUB_RISK_REFRESH_TRIAGE.md). The previously reported six-row production error is not confirmed resolved.
