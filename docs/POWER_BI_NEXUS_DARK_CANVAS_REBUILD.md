# NEXUS Football — Dark Analytical Canvas Rebuild

**Date:** 14 October 2026
**Production:** `powerbi/workspace/FootballPlayerAnalysis`, retaining existing BigQuery partitions.
**Separate synthetic QA edition:** `powerbi/offline-demo/FootballPlayerAnalysis`, retained as a transparently labeled internal test fixture; it must never be passed off as production data.
**Release:** HOLD. Hosted CI remains disabled until all final product acceptance gates.

## Design problem and implemented direction

The previous report had a navy NEXUS outer canvas containing disconnected white or pale-blue charts. These rectangles looked pasted onto a dark background and degraded the visual unity of the report. This source-level package replaces chart surface and axis-label presentation across the analytical and detail pages with a deliberately integrated dark composition:

- Native data-bound chart backgrounds: **NEXUS graphite navy `#10283F`** instead of bright white, near-white or greenish off-white.
- Native chart title and data-label ink: **`#ECF4FF`**, bright enough to remain legible on navy.
- Secondary axes: muted legible steel blue **`#AFC5DD`**; supporting values `#B9D1E8`.
- Outlines: restrained deep-blue borders such as `#294761`, `#345A7A`, `#46648B`, rather than conspicuous light-blue boxes.
- NEXUS blue and lavender original data-series palettes and previously rebuilt editorial navigation/brand signature remain intact.
- Native table column-header backing colors (including ML Reliability) remain deliberately dark with white type; a first-pass accidental header-background recolor was detected in source tests and corrected before this change was accepted.

**What was actually changed:** 36 native data-bound analytical visuals in each of production and QA fixture editions (72 native visual JSON files). The exact set is defined by editable PBIR chart/table types, not by hardcoded placeholder images. The rework is a foundational dark-surfaces pass within an ongoing complete professional redesign, not the final structural transformation of all pages.

## Data, model and provenance

No `queryState`, DAX, Power Query M, registered NEXUS logo resource, visual page navigation, BigQuery connector, source credentials, or semantic model partition is changed. The live dataset still points to the existing BigQuery project, with its separately documented warehouse freshness checks.

**Public/professional deliverable:** the `workspace` production PBIP. It contains no synthetic/demo banners or tags and must only be presented with actual verified production data. The standalone `offline-demo` fixture is **not** a customer-facing deliverable; its truthful synthetic-data provenance stays explicit so that synthetic data is not misrepresented as authentic. Do not include its mock metrics or screenshots in client materials.

## Executed local acceptance

- `python -m unittest discover -s tests -p 'test_powerbi_*.py' -q`: **98/98 PASS**.
- `python scripts/check_powerbi_release_handoff.py`: **6/6 PASS**, `source_checks=PASS`, **0** reported layout warnings.
- Original native query bindings and geometry preserved by the source conversion script; only explicit presentation dictionaries were modified.
- **CircleCI was not invoked.** The default final-CI parameter remains disabled.

## Open quality gates

The user requested **no Desktop opening or screen interaction** during this development. Accordingly this is source-level styling and test evidence, **not a real visual screenshot acceptance**. Real Windows/Desktop render/label/wrapping QA remains required before release. Also outstanding: remaining page-specific chart-composition redesign, production refresh zero errors, meaningful KPI reconciliation on the loaded report, and final opt-in CI.
