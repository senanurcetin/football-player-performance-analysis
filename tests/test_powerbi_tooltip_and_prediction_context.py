"""Native NEXUS tooltip and prediction-detail source contracts.

These are static PBIR checks; rendering/hover/scroll and BigQuery behavior
require Power BI Desktop acceptance.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLTIPS = {
    "tooltip_transfer_p011": {
        "header": ("tt011_header_0001", "TRANSFER / FEE VS VALUE"),
        "scatter": ("tt011_scatter_0001", "Fee vs Premium / Discount (%)"),
        "stats": ("tt011_stats_0001", "Transfer Metrics"),
        "canvas": "#091E33",
    },
    "tooltip_pred_p012": {
        "header": ("tt012_header_0001", "MODEL / PLAYER VALUATION"),
        "scatter": ("tt012_scatter_0001", "Predicted Value vs Upside (%)"),
        "stats": ("tt012_stats_0001", "Prediction Metrics"),
        "canvas": "#091E33",
    },
}
DETAIL = "MLPlayerDetail"
DETAIL_TEXT = "6415c9236337687a024b"


def location(mode: str, page: str) -> Path:
    return (ROOT / "powerbi" / mode / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / page)


def obj(file: Path) -> dict:
    return json.loads(file.read_text(encoding="utf-8-sig"))


def literal(value: dict) -> str:
    return value["expr"]["Literal"]["Value"].strip("'")


class ContextualTooltipDesignTests(unittest.TestCase):
    def test_tooltip_geometry_and_nexus_surface(self):
        for page, spec in TOOLTIPS.items():
            for mode in ("workspace", "offline-demo"):
                with self.subTest(page=page, mode=mode):
                    base = location(mode, page)
                    definition = obj(base / "page.json")
                    self.assertEqual((definition["width"], definition["height"]),
                                     (560, 320))
                    self.assertEqual(definition["visibility"], "HiddenInViewMode")
                    background = (definition["objects"]["background"][0]["properties"]
                                  ["color"]["solid"]["color"])
                    self.assertEqual(literal(background), spec["canvas"])
                    for name in ("header", "scatter", "stats"):
                        vid, _ = spec[name]
                        visual = obj(base / "visuals" / vid / "visual.json")
                        box = visual["position"]
                        self.assertGreaterEqual(box["x"], 0)
                        self.assertGreaterEqual(box["y"], 0)
                        self.assertLessEqual(box["x"] + box["width"], 560)
                        self.assertLessEqual(box["y"] + box["height"], 320)
                        self.assertNotIn("#2E6B45", json.dumps(visual))
                        self.assertNotIn("#F6FBF5", json.dumps(visual))
                        self.assertNotIn("#536A60", json.dumps(visual))
                        self.assertNotIn("#8BC99A", json.dumps(visual))

    def test_all_tooltip_visuals_have_consistent_style_and_query_parity(self):
        for page, spec in TOOLTIPS.items():
            for kind in ("header", "scatter", "stats"):
                vid, title = spec[kind]
                prod = obj(location("workspace", page) /
                           "visuals" / vid / "visual.json")
                demo = obj(location("offline-demo", page) /
                           "visuals" / vid / "visual.json")
                with self.subTest(page=page, kind=kind):
                    self.assertEqual(prod, demo)
                    visual = prod["visual"]
                    ui = visual["visualContainerObjects"]
                    if kind == "header":
                        self.assertEqual(visual["visualType"], "textbox")
                        run = (visual["objects"]["general"][0]["properties"]
                               ["paragraphs"][0]["textRuns"][0])
                        self.assertEqual(run["value"], title)
                        self.assertEqual(run["textStyle"]["fontSize"], "11pt")
                        self.assertEqual(
                            literal(ui["background"][0]["properties"]["color"]
                                    ["solid"]["color"]), "#173451")
                    else:
                        self.assertIn(visual["visualType"],
                                      ("scatterChart", "multiRowCard"))
                        self.assertTrue(visual["query"]["queryState"])
                        self.assertEqual(
                            literal(ui["title"][0]["properties"]["text"]), title)
                        self.assertEqual(
                            literal(ui["title"][0]["properties"]["fontSize"]), "11D")
                        self.assertEqual(
                            literal(ui["title"][0]["properties"]["fontColor"]
                                    ["solid"]["color"]), "#ECF4FF")
                        self.assertEqual(
                            literal(ui["background"][0]["properties"]["color"]
                                    ["solid"]["color"]), "#10283F")
                        if kind == "scatter":
                            for axis in ("categoryAxis", "valueAxis"):
                                p = visual["objects"][axis][0]["properties"]
                                self.assertEqual(literal(p["fontSize"]), "9D")
                                self.assertEqual(
                                    literal(p["labelColor"]["solid"]["color"]),
                                    "#B9D1E8")
                            self.assertEqual(
                                literal(visual["objects"]["legend"][0]
                                        ["properties"]["fontSize"]), "9D")
                        else:
                            self.assertEqual(
                                literal(visual["objects"]["cardTitle"][0]
                                        ["properties"]["fontSize"]), "9D")

    def test_prediction_detail_disclaims_uncertainty_and_avoids_corrupt_copy(self):
        for mode in ("workspace", "offline-demo"):
            page = location(mode, DETAIL)
            self.assertEqual(obj(page / "page.json")["visibility"],
                             "HiddenInViewMode")
            visual = obj(page / "visuals" / DETAIL_TEXT / "visual.json")
            paragraphs = visual["visual"]["objects"]["general"][0]["properties"]["paragraphs"]
            texts = [item["textRuns"][0]["value"] for item in paragraphs]
            self.assertEqual(len(texts), 7)
            copy = " ".join(texts).lower()
            self.assertIn("not realized profit", copy)
            self.assertIn("not guarantees", copy)
            self.assertNotIn("li taşır", copy)
            self.assertNotIn("high confidence about that player", copy)
            for para in paragraphs[2:]:
                self.assertEqual(para["textRuns"][0]["textStyle"]["fontSize"], "9pt")
            self.assertEqual(visual["position"]["width"], 265)
            self.assertEqual(visual["position"]["height"], 252)


if __name__ == "__main__":
    unittest.main()
