# NEXUS Football — Power BI Desktop production handoff

**LATEST OWNER DESKTOP HANDOFF (27 OCTOBER):** See [27 October verified Workintech release record](WORKINTECH_STATUS_AND_VISUAL_RELEASE_20261027.md). The active owner-edited Power BI file is C:\Users\MONSTER\Documents\NEXUS-Football-PBI\FootballPlayerAnalysis\FootballPlayerAnalysis.pbip. A separate [versioned Workintech source edition](../powerbi/workintech-20261027/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip) and [13 current Desktop captures](assets/screenshots/README.md) are in this repository. The older data-analiz-490513 and main-repository instructions below are **legacy environment instructions**, not the current Workintech target. Avoid importing another copy of the 31 governed tables using Navigator.


**Historical report path:** powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip
**Historical warehouse:** Google BigQuery data-analiz-490513.football_mart
**Current Workintech edition:** [separate October 27 PBIP](../powerbi/workintech-20261027/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip), source project workintech-working; 31 contract tables and 34 additional imported connector definitions marked for review.
**19 October 2026:** Original Desktop captures are available and the owner accepted the existing BI workstream. Full Python/PBIP source preflight PASS; **current authenticated BigQuery refresh and any newly selected-player runtime inspection remain unverified**, so project-wide release stays **REVIEW PENDING**. See [Project status](PROJECT_STATUS.md).

The `workspace` PBIP is the real-data edition. The `offline-demo` PBIP uses deterministic synthetic `#table` fixtures; do not treat its values as actual player or club results.

## 1. Download and local preflight

1. Clone or download the latest **main** of `senanurcetin/football-player-performance-analysis`. Keep the complete repository including the Report, Model and resource directories.
2. From the repository root, run the CI-free source checks:

   ```powershell
   python scripts/check_powerbi_release_handoff.py --output powerbi-handoff.json
   ```

3. Inspect the JSON `source_checks` outcome: `PASS`, `WARN` or `FAIL`. Layout geometry warnings remain warnings requiring inspection; check errors are release blockers. Git SHA is recorded when Git is available.
4. The output always marks `powerbi_desktop_refresh` and `bigquery_production_reconciliation` as `NOT_VERIFIED`, and `portfolio_release` as `HOLD`. Even a source `PASS` does not establish actual visual or BigQuery success.

The script calls the repository's existing project, demo, visual-bindings, layout and NEXUS audits, followed by Python Power BI unittests. It consumes no hosted GitHub Actions minutes and does not change warehouse records.

## 2. Open the real-data PBIP

1. Open `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip` in an up-to-date Power BI Desktop with PBIP/PBIR support.
2. Authorize the Google BigQuery connector using your own permitted credentials. The project source uses `GoogleBigQuery.Database([UseStorageApi=false])`.
3. Select **Transform data**, inspect source and Applied Steps, and then **Close & Apply / Refresh**. Record refreshed table counts, error count and time. Do not change BigQuery project or dataset names merely to make arbitrary data load.
4. The earlier six-error `dim_clubs` defect was a **synthetic fixture** type mismatch and was corrected in source. It is unrelated to an unverified six-error report involving the **production** club-risk table.

## 3. P0: production `fct_club_risk_profile`

1. If refresh errors persist: **Transform data → fct_club_risk_profile → Applied Steps**; inspect the failed column with **Keep Errors / View Errors**. Record exact step, column, message and `club_id` if available.
2. Follow the read-only BigQuery checks in [POWER_BI_CLUB_RISK_REFRESH_TRIAGE.md](archive/powerbi/POWER_BI_CLUB_RISK_REFRESH_TRIAGE.md) with the authorized account.
3. Reconcile the warehouse against the TMDL's **13 columns**. Percentage measures use **0–100 percentage points**, not 0–1 fractions. NULL can be meaningful; never replace it by zero without evidence.
4. Distinguish permissions, missing objects, column-type drift and conversion errors before making any transformation or dbt change.
5. Refresh again and document **0 conversion errors**, row count, distinct club keys and reconciled risk-category metrics. A successful source-only test cannot replace this step.

### Independent check — club win-rate percentage scale

The upstream `int_club_performance_summary.sql` emits `win_rate` as percentage **points** (for example `40.0` for 8 wins in 20 matches). The production Power Query `fct_club_performance` partition now includes a **Win Rate Fraction** step that divides only `win_rate` by 100, preserving nulls; `formatString: 0.0%` should then render 0.4 as 40.0%. The synthetic demo already contains fractions and has **no** conversion step.

After refreshing the **production workspace PBIP**, select a known club with nonzero matches and confirm that displayed Club Win Rate agrees with **100 × wins ÷ matches**, not 100 times that percentage. Inspect the `Win Rate Fraction` Applied Step, row counts and any null/error rows; preserve the distinct production/demo source paths. This is not signed off until a real BigQuery-to-Desktop check succeeds.
## 4. Desktop acceptance

| Surface | Expected evidence |
| --- | --- |
| 9 visible report pages | Current real-data charts, units and titles; NEXUS navy backgrounds readable at 100% zoom |
| 2 hidden drillthrough pages | Entry point, filter context, clear table labels |
| 2 tooltip pages | 560×320 hover content not clipped |
| Navigation | Home, left rail, footer, Closing return, filters and keyboard focus work |
| Branding | Original/cropped NEXUS logo renders without SVG failures or overlap |
| Transfers | 365-day observed outcomes (20 percentage-point criterion) distinct from ML predictions |
| Warehouse | Zero refresh errors; KPI totals reconcile to governed BigQuery marts |
| Sign-off | Version/commit, data source, refresh time, actual screenshots and blockers recorded |

For the independent **offline-demo** acceptance, open `powerbi/offline-demo/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`, refresh its 33 fixture partitions **without** BigQuery credentials, and confirm `dim_clubs` 6 rows / 0 errors. Preserve **SYNTHETIC DEMO / NOT REAL DATA** on screenshots.

## 5. Evidence and confidentiality

Record the Power BI Desktop build, Git SHA, table/column, Applied Step, full error text, row counts, refresh timestamp, and real 100%-zoom Desktop screenshots. Do not share OAuth tokens, connection secrets or unrestricted confidential data.

**Release rule:** Source preflight passing is necessary but insufficient. Keep **HOLD** until Desktop rendering, actual BigQuery refresh and metric reconciliation are independently verified.
