"""Reject unused third-party visual dependencies in the free Desktop portfolio PBIP.

This checks PBIR source, not successful Desktop rendering or an online sharing license.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Power BI first-party visual types currently used by NEXUS Football.
NATIVE = {
    "actionButton", "advancedSlicerVisual", "card", "clusteredBarChart",
    "clusteredColumnChart", "donutChart", "image", "lineStackedColumnComboChart",
    "multiRowCard", "pivotTable", "scatterChart", "shape", "slicer",
    "tableEx", "textbox", "treemap",
}


class FreeDesktopNativeVisualTests(unittest.TestCase):
    def test_no_registered_unused_external_visuals(self) -> None:
        for edition in ("workspace", "offline-demo"):
            report = ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Report"
            definition = json.loads((report / "definition" / "report.json").read_text(encoding="utf-8-sig"))
            with self.subTest(edition=edition):
                self.assertEqual(definition.get("publicCustomVisuals", []), [])

    def test_all_source_visual_types_are_first_party(self) -> None:
        for edition in ("workspace", "offline-demo"):
            report = ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Report"
            paths = sorted((report / "definition" / "pages").glob("*/visuals/*/visual.json"))
            self.assertGreaterEqual(len(paths), 300)
            found = set()
            for path in paths:
                visual = json.loads(path.read_text(encoding="utf-8-sig"))["visual"]
                visual_type = visual["visualType"]
                found.add(visual_type)
                with self.subTest(edition=edition, path=str(path.relative_to(ROOT))):
                    self.assertIn(visual_type, NATIVE)
            self.assertIn("advancedSlicerVisual", found)
            self.assertIn("card", found)
            self.assertIn("scatterChart", found)


if __name__ == "__main__":
    unittest.main()
