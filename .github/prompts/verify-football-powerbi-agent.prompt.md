---
description: Read-only acceptance test for Power BI Evidence QA custom agent
---

# Power BI Evidence QA — manual acceptance

Agent invocation: use a supported IDE agent selector **or** GitHub Copilot CLI with `--agent=powerbi-evidence-qa`. CLI agent selection is valid; do not mark this test NOT RUN merely because no IDE selector was used. The wrapper must record the requested agent ID and CLI exit status independently. If the actual loaded profile cannot be independently confirmed, report agent identity UNVERIFIED separately from the source-review checks. Do not infer successful runtime tests from a read-only answer.

Inspect:
- scripts/check_powerbi_project.py
- scripts/pbir_registry.py
- tests/test_pbir_registry.py
- powerbi/workspace/FootballPlayerAnalysis/Model/definition/relationships.tmdl
- README.md and relevant architecture/model descriptions

Do not edit any files, execute commands, or contact remote services. Instead, answer:

1. Specify which PBIR registry and relationship checks are structural, and why they do not prove a successful Power BI Desktop render.
2. Differentiate modeled real data, synthetic demonstrations, editorial covers and actual screenshots.
3. Explain the Turkish unit B and how to avoid misinterpreting thousand as billion.
4. Explain why a leakage-aware market-value prediction must be compared to an appropriate persistence baseline; do not invent model results.

Provide a source-cited PASS/FAIL/UNVERIFIED table. State clearly what remains unverified (Desktop rendering, fresh BigQuery refresh, new ML experiments). No CI/Actions/CircleCI/Vercel, installs, publication, model retraining or file changes.