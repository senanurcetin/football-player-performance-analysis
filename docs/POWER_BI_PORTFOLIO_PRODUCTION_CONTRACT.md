# NEXUS Football Intelligence — Portfolio Production Contract

> **As of 17 October 2026:** Real screenshots are captured; full warehouse reconciliation and player detail QA remain release blockers. See [Project status](PROJECT_STATUS.md).

**Edition to present publicly:** `powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip`.

## Audience and design

The presentation language is English. The visual identity uses the official approved **NEXUS Identity 2.0** transparent wordmark from Google Drive's `Logo/NEXUS_Identity_2_0` package, within an editorial, restrained midnight-blue/cyan/blue/lavender palette. The report should look like a coherent, professional football research product, not a standard starter dashboard. The actual image already registered in the production report is `NEXUS_Official_Transparent_Logo.png`; the official vector is kept in Drive. The user's Power BI Desktop is **not** to be opened until final acceptance.

## Real-data contract

- All production visuals must remain bound to the **BigQuery-based semantic model**. The production Power Query source uses `GoogleBigQuery.Database`; no substitute local CSV, fixture, fake financial values or generated scorecards may be added as a replacement.
- Every page must be English, including hidden drillthroughs and tooltip pages. Fix remaining Turkish captions without changing report query bindings. Presentation must not have visible starter, demo or synthetic-watermark labels.
- Explicitly distinguish historical observed outcomes, source coverage, retrospective market value, model predictions and prediction uncertainty. Do not pretend that ML model estimates are guaranteed returns.
- Keep analytical units, axes, denominators and filters unambiguous. Avoid overdecorated dashboards that obscure interpretation.
- BigQuery mart last-modified metadata is not the same as the event-data's newest date; don't advertise the warehouse as live/current-season until validated.

## Source-level preflight

Run:

```powershell
python scripts/check_powerbi_portfolio.py
python -m unittest discover -s tests -p 'test_powerbi_*.py' -q
python scripts/check_powerbi_release_handoff.py
```

The new portfolio guard verifies production English headings and textbox copy, 13 page definitions, genuine BigQuery table sources and registration of the official transparent logo. This is a **static** check and does not test refresh or screenshot aesthetics.

## Internal fixtures are not production

The `powerbi/offline-demo` development-only directory contains deterministic synthetic fixtures and explicit provenance markers. It is deliberately **not** the portfolio report. Never copy those fixture partitions into the production Power BI model, suppress their provenance while presenting their metrics, or confuse their QA tests with an actual BigQuery refresh. A production portfolio can have no user-visible demo banners while the repository honestly retains separate test fixtures.

## Final acceptance

Before capturing portfolio screenshots, open **only** the current production PBIP and confirm zero refresh errors, effective Google authentication, and meaningful nonblank, source-grounded visuals. Verify 13 page surfaces including contextual tooltip/drillthrough interactions, new NEXUS logo scaling and spacing, clean chart labels, table overflow, source freshness and 100% zoom. A Power BI license purchase is not required to design and locally view editable native visuals.

Release remains **HOLD** until this real Desktop acceptance and the final opt-in CircleCI control complete. Do not run hosted CI while work is still in progress.
