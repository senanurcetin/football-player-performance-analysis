# NEXUS Football Intelligence — Workintech accepted source (28 October 2026)

This is the versioned PBIP source corresponding byte-for-byte to the 34-BigQuery-source model promoted to the owner's existing Documents/NEXUS-Football-PBI path on 28 October 2026 after the owner reported successful testing.

**Open:** [FootballPlayerAnalysis.pbip](FootballPlayerAnalysis/FootballPlayerAnalysis.pbip)

**Model:** 34 BigQuery source tables (31 governed and three additional unique), 87 TMDL relationships, 77 TMDL table files, 13 report pages and 308 visuals. The 31 duplicated imports and 40 redundant automatic date tables were removed from the earlier 65-source edition in an isolated QA process. The nine unique business relationships were retained and mapped to governed endpoints.

**Acceptance:** The owner confirmed the tested report worked. The on-disk promotion was byte-verified and reversible; no post-cutover Power BI Desktop runtime test was independently performed by the assistant. No additional screenshots were requested.

**Rollback:** The previous active PBIP, including its original local model cache, is retained under C:\Users\MONSTER\Documents\NEXUS-Football-PBI\Backups\FootballPlayerAnalysis-pre-dedup-acceptance-20261028-010708-743756.

**Full evidence:** [28 October production source promotion](../../docs/WORKINTECH_PRODUCTION_PROMOTION_20261028.md) and [34-source static QA checks](../../docs/WORKINTECH_FULL_DEDUP_QA_20261028.md).

The older version is preserved in [workintech-20261027](../workintech-20261027/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip). This report source contains no Google service account credentials or local binary model cache. Power BI Service publication, scheduled refresh and commercial data-quality approval are separate operational gates.
