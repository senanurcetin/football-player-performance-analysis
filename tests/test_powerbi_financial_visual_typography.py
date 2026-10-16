"""Source-only finance and valuation typography guard for paired editable PBIR reports.

No Power BI Desktop rendering, DAX, connector refresh or interaction tests.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET = "292e3d92e92693c05047"
VALUATION = "1f4c5c8000149b2e2be8"
VISUALS = {
    MARKET: {
        "9c728e8d682165354da4": "tableEx",
        "0839d8ed3d7479a01f32": "clusteredBarChart",
        "5bbe3e0865c55bbeade1": "clusteredColumnChart",
        "1c4d73ece1a64f57c0fc": "donutChart",
    },
    VALUATION: {
        "be92253a5130bdec9028": "tableEx",
        "4d304949cba7dd247021": "clusteredBarChart",
        "8b67c00a69b995fd3db6": "clusteredBarChart",
        "3ccd5a45594119af9bb7": "donutChart",
    },
}
FOOTERS = {
    MARKET: "b8a00000000000000005",
    VALUATION: "b8a00000000000000006",
}


def read(edition: str, page: str, visual_id: str) -> dict:
    path = (ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / page /
            "visuals" / visual_id / "visual.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def literal(value: dict) -> str:
    return value["expr"]["Literal"]["Value"]


class FinancialVisualReadabilityTests(unittest.TestCase):
    def test_native_visual_typography_and_edition_parity(self):
        for page, cases in VISUALS.items():
            for visual_id, kind in cases.items():
                with self.subTest(page=page, visual=visual_id):
                    prod = read("workspace", page, visual_id)
                    demo = read("offline-demo", page, visual_id)
                    self.assertEqual(prod, demo)
                    node = prod["visual"]
                    self.assertEqual(node["visualType"], kind)
                    self.assertTrue(node["query"]["queryState"])
                    ui = node["visualContainerObjects"]
                    self.assertEqual(literal(ui["title"][0]["properties"]["fontSize"]), "13D")
                    objects = node["objects"]

                    if kind == "tableEx":
                        header = objects["columnHeaders"][0]["properties"]
                        values = objects["values"][0]["properties"]
                        self.assertEqual(literal(header["fontSize"]), "10D")
                        self.assertEqual(literal(values["fontSize"]), "10D")
                        self.assertEqual(literal(objects["grid"][0]["properties"]
                                                 ["rowPadding"]), "4D")
                        self.assertEqual(literal(header["wordWrap"]), "true")
                        self.assertEqual(
                            literal(header["backColor"]["solid"]["color"]), "'#10283F'")
                        self.assertEqual(
                            literal(header["fontColor"]["solid"]["color"]), "'#FFFFFF'")
                        self.assertGreaterEqual(
                            len(node["query"]["queryState"]["Values"]["projections"]), 7)
                    elif kind == "donutChart":
                        for obj, color_field in (
                            ("legend", "labelColor"), ("labels", "color")
                        ):
                            props = objects[obj][0]["properties"]
                            self.assertEqual(literal(props["fontSize"]), "9D")
                            self.assertEqual(
                                literal(props[color_field]["solid"]["color"]), "'#ECF4FF'")
                    else:
                        self.assertEqual(
                            literal(objects["labels"][0]["properties"]["fontSize"]), "10D")
                        for axis in ("categoryAxis", "valueAxis"):
                            self.assertEqual(
                                literal(objects[axis][0]["properties"]["titleFontSize"]),
                                "11D")

    def test_evidence_visuals_clear_footer_without_moving(self):
        for page, cases in VISUALS.items():
            for mode in ("workspace", "offline-demo"):
                footer = read(mode, page, FOOTERS[page])["position"]
                self.assertEqual(footer["y"], 679)
                for visual_id in cases:
                    position = read(mode, page, visual_id)["position"]
                    with self.subTest(page=page, edition=mode, visual=visual_id):
                        self.assertLessEqual(
                            position["y"] + position["height"], footer["y"] - 8)


if __name__ == "__main__":
    unittest.main()
