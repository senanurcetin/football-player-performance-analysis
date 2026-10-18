# Power BI historical screenshot/value reconciliation — 18 October 2026

**Scope:** Static, read-only visual and historical metric comparison for the established NEXUS Football Intelligence project. No new product or visual design, Power BI Service deployment, BigQuery refresh, or new source claims.

**Status: CONTROLLED / CHECKED for recorded image integrity and the matched historical KPIs below. NOT approved as a complete 13-page runtime or current-data acceptance.**

## Provenance and image integrity

- **Source:** `docs/assets/screenshots/capture_manifest.json`, 17 October 2026 screenshots attributed to production-connected PBIP source commit `db0819bbcea5aca852e2c06366fb4245bcc39d1e`.
- **Executed 18 October 2026:** fetched each of the **13 actual GitHub PNG binary files**; computed SHA-256 directly from decoded bytes and inspected PNG IHDR dimensions. **13/13 SHA-256 checks match the committed manifest; 13/13 sizes match 2177 × 1229**. Thus recorded images have **not changed** relative to the 17 October capture manifest. This is screenshot-integrity evidence, not proof of current warehouse freshness or Power BI runtime behavior.
- Visually inspected seven representative production screenshot pages, including both known-problem drillthrough details; numeric readings below are transcribed from those images and compared to `docs/DATA_QUALITY.md`. Filtered/mart populations are **not** equated across different grains.

## Historical values compared

| Visual / dimension | Read from screenshot (17 Oct) | Documented June warehouse snapshot | Assessment |
| --- | --- | --- | --- |
| Player Segmentation: counts by position | 12,885 attack + 15,209 defender + 5,521 goalkeeper + 13,625 midfield + 461 missing + 1 blank = **47,702** | `dim_players` **47,702** | **MATCH — checked** |
| Player Segmentation: counts by age | 5,840 + 10,249 + 10,281 + 8,951 + 12,381 = **47,702** | `dim_players` **47,702** | **MATCH — checked** |
| Transfer & Market Value: transactions | **40,208** | `fct_transfers` **40,208** | **MATCH — checked** |
| Transfer & Market Value: known transfer fee rate | **64.2%** | **25,821 / 40,208 = 64.216%** | **MATCH at displayed rounding — checked** |
| Transfer & Market Value: known fees total | **€9.8 billion** (rounded display) | Older repo README reports **€9,803.9 million** (historical reported value, not independently queried) | **CONSISTENT AT DISPLAY ROUNDING; not revalidated against BigQuery** |
| Player Market Value Prediction: scored players | **7,841** | ML current scoring rows **7,841** | **MATCH — checked** |
| Player Market Value Prediction: decision-ready | **72.9%** | Historical limited-quality share **27.09%**, complement **72.91%** | **MATCH at displayed rounding — checked** |
| Transfer Success 365d: visible rate | **8,581 observed / 36,571 eligible = 23.46%**, shown as **23%** | The denominator is *not* documented as the same fixed-horizon mart grain | **INTERNAL DISPLAY CONSISTENCY checked; cross-mart match NOT established** |
| Transfer Success 365d: observed rows | **8,581** in visual | **8,584** historical `fct_transfer_success_labels` rows | **3-record difference — unresolved**. May be filter/relationship/refresh effects; no cause asserted |
| Transfer Success 365d: eligible population | **36,571** in visual | `fct_transfer_fixed_horizon_outcomes` has **39,780** total historical transfers | **Different documented grains/filters; no equality asserted** |
| ML Model Reliability: feature count | **24** | 16 numeric + 8 categorical configured by `scripts/train_player_market_value.py` | **MATCH — checked** |
| ML Model Reliability: “Highest R²” / “Lowest WAPE” | **0.999** / **1.0** | Historical overall held-out R² **0.9756** / WAPE **12.51%** | **Not comparable:** screenshot explicitly shows extrema across segments; source document describes overall ensemble. Neither is proof of model improvement |
| Player Performance: 14,163 players | **14,163** in performance view | Player dimension **47,702** | **Not comparable** without confirming active-performance population/filter definitions |

Values under different population filters are not proof of changed input records. In particular, **do not silently replace 8,581 with 8,584 or mark 365-day label counts reconciled** without inspecting `fct_transfer_success_labels`, downstream Power BI relationships, visual/slicer filters and capture/warehouse snapshot dates.

## Explicit acceptance boundaries

| Scope | Status |
| --- | --- |
| Screenshot files unchanged against manifest | **KONTROL EDİLDİ — 13/13** |
| Comparable historical KPI values in screenshot vs documentation | **KONTROL EDİLDİ — matches listed above** |
| 365-day transfer-success full population reconciliation | **BEKLİYOR — 3-row difference** |
| Power BI Desktop navigation, player-selected drillthrough and tooltip invocation | **BEKLİYOR — desktop runtime unavailable** |
| Two screenshot player-detail error panels / unselected state | **HATA GÖZLEMLENDİ — not accepted** |
| Fresh BigQuery marts, latest source timestamps, row-grain reconciliation and live KPI testing | **DOĞRULANMADI — no authorized BigQuery runtime exposed** |
| Full release/portfolio sign-off | **BEKLİYOR** |

## Reproduction when source access returns

1. Refresh `football_mart` in a governed, explicitly authorized and cost-controlled BigQuery environment; record as-of time, source modification/event dates, project, commit and relevant row counts.
2. Compare `COUNT(*)` from `fct_transfer_success_labels` against **the exact filtered row set Power BI uses**, not against unrelated fixed-horizon populations; isolate the three missing/extra keys via anti-joins, documenting their filter reasons and historical as-of dates.
3. Confirm 365-day observed positive labels, coverage denominator and 20-percentage-point increase rule.
4. Open the existing production-connected PBIP, check both player-selected detail pages (remove visual error states) and actual tooltip behavior; capture evidence and obtain the author's acceptance.

**Verdict:** The requested “Power BI kontrol edildi” is supportable **only for screenshot integrity and historical matching values**, not for the 365-day discrepancy or for the full Power BI live/runtime release gate.
