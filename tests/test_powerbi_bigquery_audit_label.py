"""Source contract for the real BigQuery quality-audit label on the Home page.

This does not prove a successful Power BI Desktop import/refresh or render.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = "5cb4db7e746975558322"
VISUAL = "fa9241e97af65797688c"
TABLE = "fct_analytics_refresh_audit"
MEASURE = "Last Warehouse Audit Label"


def edition(mode: str) -> Path:
    return ROOT / "powerbi" / mode / "FootballPlayerAnalysis"


class WarehouseAuditVisualTests(unittest.TestCase):
    def test_audit_label_is_a_dynamic_source_measure_in_both_editions(self):
        results = []
        for mode in ("workspace", "offline-demo"):
            tmdl = (edition(mode) / "Model" / "definition" / "tables" / f"{TABLE}.tmdl").read_text(
                encoding="utf-8-sig"
            )
            self.assertIn(f"measure '{MEASURE}' =", tmdl)
            self.assertIn("MAX ( fct_analytics_refresh_audit[audit_generated_at_utc] )", tmdl)
            self.assertIn("ISBLANK ( LatestAuditUtc )", tmdl)
            self.assertIn("DATEDIFF ( LatestAuditUtc, UTCNOW (), DAY )", tmdl)
            self.assertIn("AuditAgeDays > 90", tmdl)
            self.assertIn('"HISTORICAL / "', tmdl)
            self.assertIn('FORMAT ( LatestAuditUtc, "dd MMM yyyy", "en-US" )', tmdl)
            self.assertIn('"AUDIT / NOT AVAILABLE"', tmdl)
            self.assertNotIn("2026-06-21", tmdl, "Do not hard-code today's known audit date into the semantic layer")
            if mode == "workspace":
                self.assertIn("GoogleBigQuery.Database([UseStorageApi=false])", tmdl)
                self.assertIn('Name="football_mart"', tmdl)
            else:
                self.assertIn("#table", tmdl)
            results.append(tmdl.split("\tcolumn audit_key", 1)[0])
        self.assertEqual(results[0], results[1], "Shared measures must be semantically identical")

    def test_home_date_is_data_bound_and_not_static_advertising(self):
        visuals = []
        for mode in ("workspace", "offline-demo"):
            path = (edition(mode) / "Report" / "definition" / "pages" / HOME /
                    "visuals" / VISUAL / "visual.json")
            node = json.loads(path.read_text(encoding="utf-8-sig"))
            self.assertEqual(node["visual"]["visualType"], "card")
            self.assertEqual(node["position"]["x"], 950)
            self.assertEqual(node["position"]["y"], 73)
            self.assertEqual(node["position"]["width"], 250)
            self.assertEqual(node["position"]["height"], 35)
            project = node["visual"]["query"]["queryState"]["Values"]["projections"][0]
            measure = project["field"]["Measure"]
            self.assertEqual(measure["Expression"]["SourceRef"]["Entity"], TABLE)
            self.assertEqual(measure["Property"], MEASURE)
            self.assertEqual(project["queryRef"], f"{TABLE}.{MEASURE}")
            self.assertEqual(project["nativeQueryRef"], MEASURE)
            self.assertFalse(node["visual"]["visualContainerObjects"]["background"][0]["properties"]["show"]["expr"]["Literal"]["Value"] == "true")
            self.assertNotIn("RESEARCH ATLAS", json.dumps(node))
            self.assertNotIn("2026-06-21", json.dumps(node))
            alt = node["visual"]["visualContainerObjects"]["general"][0]["properties"]["altText"]["expr"]["Literal"]["Value"]
            self.assertIn("not a real-time feed", alt)
            visuals.append(node)
        self.assertEqual(visuals[0], visuals[1], "Production/fixture only differ in their data partitions")


if __name__ == "__main__":
    unittest.main()
