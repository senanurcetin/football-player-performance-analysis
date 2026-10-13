"""Guard ML Reliability table legibility without changing analytic bindings.

Static PBIR source assertions; no Desktop rendering or BigQuery data checks.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = "MLModelPerformance"
TABLES = {
    "6a52894b1eadaab185b4": ("Feature Importance", 4, (105, 212, 425, 230)),
    "9cac2684a07ca1c85ca6": ("Quality Gates", 5, (545, 212, 425, 230)),
    "44ef7cfce32d97d2bb52": ("Segment Performance", 8, (105, 470, 870, 225)),
}
HEADER_COLORS = {
    "Feature Importance": "#122942",
    "Quality Gates": "#122942",
    "Segment Performance": "#173451",
}



def load(edition: str, visual_id: str) -> dict:
    path = (ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / PAGE / "visuals" /
            visual_id / "visual.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def literal(property_value: dict) -> str:
    return property_value["expr"]["Literal"]["Value"]


class ModelReliabilityTableTypographyTests(unittest.TestCase):
    def test_three_native_tables_in_both_editions_remain_legible(self):
        for visual_id, (title, field_count, bounds) in TABLES.items():
            production = load("workspace", visual_id)
            synthetic = load("offline-demo", visual_id)
            with self.subTest(table=title):
                self.assertEqual(production, synthetic)
                node = production["visual"]
                self.assertEqual(node["visualType"], "tableEx")
                self.assertEqual(production["name"], visual_id)
                position = production["position"]
                self.assertEqual(tuple(position[key] for key in
                                       ("x", "y", "width", "height")), bounds)
                self.assertEqual(
                    len(node["query"]["queryState"]["Values"]["projections"]),
                    field_count,
                )
                objects = node["objects"]
                self.assertEqual(
                    literal(node["visualContainerObjects"]["title"][0]
                            ["properties"]["fontSize"]), "13D")
                self.assertEqual(
                    literal(node["visualContainerObjects"]["title"][0]
                            ["properties"]["text"]), f"'{title}'")
                self.assertEqual(
                    literal(objects["columnHeaders"][0]["properties"]["fontSize"]), "10D")
                self.assertEqual(
                    literal(objects["values"][0]["properties"]["fontSize"]), "10D")
                self.assertEqual(
                    literal(objects["grid"][0]["properties"]["rowPadding"]), "4D")
                self.assertEqual(
                    literal(objects["columnHeaders"][0]["properties"]["wordWrap"]),
                    "true",
                )
                header = objects["columnHeaders"][0]["properties"]
                self.assertEqual(header["backColor"]["solid"]["color"]["expr"]
                                 ["Literal"]["Value"], f"'{HEADER_COLORS[title]}'")
                self.assertEqual(header["fontColor"]["solid"]["color"]["expr"]
                                 ["Literal"]["Value"], "'#FFFFFF'")


if __name__ == "__main__":
    unittest.main()
