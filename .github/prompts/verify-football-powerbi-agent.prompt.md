---
description: Read-only acceptance test for Power BI Evidence QA custom agent
---

# Power BI Evidence QA — manual acceptance

Select Power BI Evidence QA manually in a supported GitHub Copilot IDE. If selection cannot be confirmed, record NOT RUN.

Inspect:
- scripts/check_powerbi_project.py
- scripts/pbir_registry.py
- tests/test_pbir_registry.py
- powerbi/workspace/FootballPlayerAnalysis/Model/definition/relationships.tmdl
- README.md and relevant architecture/model descriptions

Without commands, edits or remote services:

1. Specify which PBIR registry and relationship checks are structural, and why they do not prove a successful Power BI Desktop render.
2. Differentiate modeled real data, synthetic demonstrations, editorial covers and actual screenshots.
3. Explain the Turkish unit B and how to avoid misinterpreting thousand as billion.
4. Explain why a leakage-aware market-value prediction must be compared to an appropriate persistence baseline; do not invent model results.

Provide a source-cited PASS/FAIL/UNVERIFIED table. State clearly what remains unverified (Desktop rendering, fresh BigQuery refresh, new ML experiments). No CI/Actions/CircleCI/Vercel, installs, publication, model retraining or file changes.