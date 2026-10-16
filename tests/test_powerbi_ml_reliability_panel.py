"""ML reliability visual integrity guard for the editable NEXUS Football PBIR.

Source-only assertions; no Power BI Desktop refresh, DAX verification, or
screen-reader behavior is certified by these tests.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = "MLModelPerformance"
PANEL = "71c3ed6cba191ccd868d"
GUIDE = "301e05093c138fc6b673"
FILTERS = "b2a67d30746260fc1f21"
FEATURES = "6a52894b1eadaab185b4"


def visual(edition, vid):
    path = (ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / PAGE / "visuals" / vid / "visual.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def contrast(fg, bg):
    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                  for c in channels]
        return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
    a, b = sorted([luminance(fg), luminance(bg)], reverse=True)
    return (a + 0.05) / (b + 0.05)


class ModelQualityEditorialTests(unittest.TestCase):
    def test_both_editions_share_accessible_dark_sidebar(self):
        nodes = {edition: {id: visual(edition, id) for id in (PANEL, GUIDE, FILTERS, FEATURES)}
                 for edition in ("workspace", "offline-demo")}
        self.assertEqual(nodes["workspace"], nodes["offline-demo"])
        for edition, selected in nodes.items():
            with self.subTest(edition=edition):
                panel = selected[PANEL]
                background = panel["visual"]["objects"]["fill"][0]["properties"]["fillColor"]["solid"]["color"]
                self.assertEqual(background["expr"]["Literal"]["Value"], "'#10283F'")
                guide = selected[GUIDE]
                self.assertEqual(guide["visual"]["visualType"], "textbox")
                self.assertLessEqual(
                    guide["position"]["y"] + guide["position"]["height"],
                    panel["position"]["y"] + panel["position"]["height"],
                )
                paragraphs = guide["visual"]["objects"]["general"][0]["properties"]["paragraphs"]
                combined = " ".join(run["value"] for p in paragraphs for run in p["textRuns"]).lower()
                self.assertIn("baseline", combined)
                self.assertIn("r²", combined)
                self.assertIn("not causal", combined)
                self.assertIn("segment sample sizes", combined)
                self.assertNotIn("<15%", combined)
                self.assertNotIn("r²>0.95", combined)
                self.assertNotIn("önemli", combined)
                for p in paragraphs:
                    for run in p["textRuns"]:
                        self.assertGreaterEqual(contrast(run["textStyle"]["color"], "#102B47"), 4.5)
                self.assertEqual(
                    guide["visual"]["visualContainerObjects"]["background"][0]
                         ["properties"]["show"]["expr"]["Literal"]["Value"],
                    "false",
                )
                filter_color = selected[FILTERS]["visual"]["objects"]["general"][0]["properties"][
                    "paragraphs"][0]["textRuns"][0]["textStyle"]["color"]
                self.assertGreaterEqual(contrast(filter_color, "#102B47"), 4.5)
                fields = selected[FEATURES]["visual"]["query"]["queryState"]["Values"]["projections"]
                types = [p for p in fields if p["queryRef"] ==
                         "ml_player_market_value_feature_importance.feature_type"]
                self.assertEqual([f["displayName"] for f in types], ["Feature Type"])


if __name__ == "__main__":
    unittest.main()
