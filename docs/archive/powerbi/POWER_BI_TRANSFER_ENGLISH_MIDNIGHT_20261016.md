# NEXUS Football — Transfer page English & Midnight V3 refinement

> **Archived historical record — 17 October 2026.** This document preserves prior engineering decisions and evidence; it is not the current delivery status. For current verified vs. pending checks, see [Project status](../../PROJECT_STATUS.md) and the [documentation index](../../README.md).


**Source implementation date:** 16 October 2026. **Publication:** HOLD pending fresh Power BI Desktop reload, authenticated refresh and image review.

## Why this change is necessary

The owner's real Power BI Desktop screenshots showed a pale filter rail and KPI cards inconsistent with the NEXUS Midnight canvas, crowded fee values, and Turkish data labels in the "Value Direction" legend despite an English report design.

### Authenticated production warehouse evidence

A bounded, **read-only** BigQuery aggregate compared the existing source fields `yon_etiketi_tr` and `market_value_direction_after_transfer` in `data-analiz-490513.football_mart.fct_transfer_market_value_analysis`:

| Historical data label | Real English warehouse value | Rows |
| --- | --- | ---: |
| Belirsiz | unavailable | 18,388 |
| Arttı | increase | 7,934 |
| Düştü | decrease | 7,473 |
| Değişmedi | unchanged | 6,413 |
| **Total** | | **40,208** |

These are **the same source rows**, not an artificial translation lookup or simulated dataset. The warehouse CLI printed a nonfatal local ADC cache-write warning, but the query returned results with exit code 0. These observations are historical and do not establish current-season updates.

## PBIR source modifications

Both production (`powerbi/workspace`) and *internal QA-only* (`powerbi/offline-demo`) editions receive identical source changes:

- Four native data visual bindings per edition (transfer page donut, evidence table, direction slicer, and transfer-detail donut) use the **actual English** `market_value_direction_after_transfer` column in place of the Turkish `yon_etiketi_tr` categories. Their chart types, measures, row grain and geometry are unchanged.
- On the Transfer page, six native metric cards and four slicers use consistent graphite `#10283F` surfaces, `#294761` hairline borders, and readable `#EAF3FF` headings. Slicer header/item surfaces and right-hand 290×618 rail background are darkened together to avoid white-on-navy contrast discontinuity.
- The narrow known-fee-total KPI switches display units from **EUR millions to EUR billions** (`labelDisplayUnits` from 1,000,000 to 1,000,000,000). This changes *presentation only*, not the imported EUR data, aggregation, exchange rates or DAX measure.
- Smaller value type is used in narrow transfer-count and total-fee cards to reduce truncation, while retaining their titles.
- Existing DAX fallback labels now use **All seasons** and **No player selected**, and the dynamic transfer title uses "Transfer & Market Value" instead of a Turkish phrase. Original warehouse rows are untouched.

The Turkish `yon_etiketi_tr` column remains in the BigQuery source/model as original historical evidence, even though the four public-facing visuals no longer bind to it. Do not overwrite, delete or translate the historical source data.

**Note:** Power BI Desktop application chrome and native error messages may remain in the language configured on the local PC; changing native report labels alone does not change the Desktop application's language.

## Validation

- Real mapping checked by read-only BigQuery (40,208 grouped records, four exact category pairs).
- `tests/test_powerbi_transfer_english_midnight.py` verifies both PBIR editions, first-party visual bindings, actual source field, light-on-dark contrast selection and compact EUR billions display setting.
- Updated the old card/slicer regression to distinguish the Transfer page's midnight style from other pages' original pale style; kept source binding parity assertions.
- No source-only test establishes that the card value or dropdown appears correctly after Power BI Desktop imports and renders the latest PBIR revision.

**Final acceptance remains** re-open current genuine PBIP from the latest commit; refresh authenticated BigQuery, review all 13 pages, interactions, tooltip and original logo crop, take only genuine screenshots, and confirm no `Missing_References`/field errors. Do not publish fixture data as real.
