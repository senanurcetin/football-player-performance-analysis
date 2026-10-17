# NEXUS Football Intelligence — Production Architecture Rebuild

> **Archived historical record — 17 October 2026.** This document preserves prior engineering decisions and evidence; it is not the current delivery status. For current verified vs. pending checks, see [Project status](../../PROJECT_STATUS.md) and the [documentation index](../../README.md).


**Date:** 13 October 2026
**Status:** Source redesign stage 1 complete; Desktop visual acceptance, real refresh and publication **HOLD**.
**Presentation artifact:** `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`
**Warehouse:** `data-analiz-490513` / `football_mart` and `football_ml` via the **existing** `GoogleBigQuery.Database([UseStorageApi=false])` partitions.
**No Desktop UI was opened for this change. No hosted CI was run.**

## Release boundary and truthful provenance

The releaseable report is **only** `powerbi/workspace/FootballPlayerAnalysis/`: real model partitions reference the original BigQuery datasets. No page title or visible text in this 13-page production edition uses demo, synthetic, fake, or test-data labels; this is an explicit automated regression invariant.

The `powerbi/offline-demo/` edition remains an **internal, non-publishable fixture** for offline deterministic regression coverage. Its truthful synthetic-data notices stay in place **only in that internal test artifact**. It must not be published, exported as genuine football findings, used for portfolio screenshots or substituted when BigQuery is not accessible. Hiding a fixture's actual data source would be misleading. The README now links only the connected production PBIP as the report to present.

## Brand, typography and layout system

- Shell: original NEXUS navy `#091E33` and dark cover `#071829`; retained official original wordmark resources and editorial signature.
- Dominant data accent: `#4EA8FF` NEXUS blue; secondary comparison: `#8F9BFF`; accessible chart copy on white analytical surfaces: `#122942`.
- 1280×720 native editable report canvas; fixed left navigation and original BigQuery-bound filters, active state, footer and drillthrough remain intact.
- No faux real-time figures, fictitious trend values, floating giant logo replacements or generic repeated equal-weight cards.
- Visual hierarchy now follows **question → primary signal → contextual evidence → source/sample cautions**. Source-only checks cannot certify the actual rendered look.

## Stage 1 — Three purpose-built full-size analyses

| Page | Primary evidence | Secondary / commercial evidence | Avoided misinterpretation |
| --- | --- | --- | --- |
| **Transfer Outcomes — 365d** | 706×229 observed success rate by position plus 365×78 outcome coverage lead card | 406×229 follow-up status, lower transfer-count and known-fee charts | Unknown or unobserved outcomes are **not** counted as observed failures |
| **Transfer & Market Value** | 546×221 fee premium/discount by position with a 224×82 premium KPI | 305×221 known-fee-by-season trend; unchanged transaction table, value-direction donut and transfer count panel; fixed season/position/fee-status filters | Premium is relative to the source baseline and known-fee coverage; not proven trading profit |
| **Player Valuation** | 237×82 decision-ready rate lead and 550×215 predicted-value-by-position graph | 301×215 quality distribution; lower upside by position plus full bound player estimate table, keeping prediction lower/upper intervals | Prediction is **not** a realized transfer price; intervals and quality grades are required reading context |

All original data visual IDs, native chart types, filter field projections, measured values, DAX and semantic table definitions are preserved. The previous flat arrays of four/five equal KPI tiles are weighted according to the actual business question. New chapter captions/rules are **editable native text and shapes**, never bound to fictitious measures. Chart data remains entirely governed by the original warehouse-linked model.

### Explicit old content error removed

The prior Valuation sidebar contained **six older paragraphs**, including ungrounded statements about which position carries the highest market value, unsupported claims that the model 'correctly captures' a finding, and misleading confidence-language. Those paragraphs were completely removed in both source editions. The replacement is a restrained interpretation protocol emphasizing prior/predicted comparison, quality labels, lower/upper range and model evaluation.

The technical phrase 'BIGQUERY CONNECTION REQUIRED' on the production Home was replaced with the quieter editorial copy 'NEXUS / EVIDENCE-LED FOOTBALL ANALYTICS'; **the BigQuery connection itself was not changed**.

## Engineering checks

The new `tests/test_powerbi_production_institutional.py` tests:
- all 13 production page names and visible text are free of sample/test-data claims;
- four critical production TMDL partitions retain the existing real Google BigQuery project, schemas and original table names;
- the three redesigned page layouts are bounded, non-overlapping and have weighted hero evidence with intact field bindings;
- matched chart/card sources remain identical in internal regression and production editions (except source partitions and dedicated provenance);
- ungrounded business guidance and overlapping explanatory headings cannot recur.

**Windows local evidence (latest branch):** `python -m unittest discover -s tests -p 'test_powerbi_*.py' -q` — **98/98 PASS** including 5 new production contracts. Additional source handoff, diff invariant and YAML/Jinja checks must be recorded before merging.

## Remaining product work

1. Convert **ML Reliability**, detail and tooltip experiences into the same institutional hierarchy, without inventing statistics.
2. Review/finish **Home, Closing, Performance, Segmentation, Club & League** to a genuinely unified standard, not another blanket recolor.
3. When the user is ready, run **actual** Power BI Desktop page-by-page screenshot QA and **real BigQuery refresh**. The user explicitly requested **no on-screen Power BI actions during this stage**.
4. Verify BigQuery refresh, table loads, accurate percentages, 13 page visuals, keyboard and filter context, cropped label legibility and snapshot-date disclosures.
5. Keep CircleCI `run_final_ci=false` and release `HOLD` until the complete acceptance is signed off. Only then run hosted CI on the final main commit.

**Do not treat source test PASS as a claim that the redesigned pages have been rendered, visually approved or refreshed successfully in Power BI Desktop.**
