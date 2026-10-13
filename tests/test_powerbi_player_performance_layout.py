"""Guard Player Performance KPI rhythm and footer-safe chart geometry.

Static PBIR checks only: does not certify Power BI Desktop clipping,
cross-filter interactions, or real BigQuery refresh.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = "d2bc1e6a078c5c5b125c"
KPI_IDS = (
    "c49bad3782a43cdac710",  # Total Players
    "52a25425ec00bcc0a8b1",  # Total Goals
    "fd59ca45d88b6eb6b521",  # Total Assists
    "303c777d36178076aa39",  # Avg Minutes / Match
    "6cb1590ae40874c838b7",  # Avg G+A per 90
)
CHARTS = {
    "6c68e020599db75da880": ("scatterChart", 219),
    "dd91e16c6d11d504a577": ("pivotTable", 220),
}
FOOTER_ID = "b8a00000000000000001"
MODES = ("workspace", "offline-demo")


def visuals(mode: str) -> dict[str, dict]:
    root = (ROOT / "powerbi" / mode / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / PAGE / "visuals")
    return {
        path.parent.name: json.loads(path.read_text(encoding="utf-8-sig"))
        for path in root.glob("*/visual.json")
    }


def intersects_x(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["width"] and
            b["x"] < a["x"] + a["width"])


class PlayerPerformanceEditorialTests(unittest.TestCase):
    def test_five_kpis_form_a_consistent_nexus_strip(self):
        for mode in MODES:
            nodes = visuals(mode)
            cards = [nodes[vid] for vid in KPI_IDS]
            with self.subTest(mode=mode):
                for i, card in enumerate(cards):
                    self.assertEqual(card["visual"]["visualType"], "card")
                    self.assertEqual(
                        tuple(card["position"][k] for k in ("x", "y", "width", "height")),
                        (157 + 212 * i, 118, 200, 64),
                    )
                    if i:
                        previous = cards[i - 1]["position"]
                        self.assertEqual(
                            card["position"]["x"] -
                            (previous["x"] + previous["width"]), 12)
                title = cards[3]["visual"]["visualContainerObjects"]["title"][0][
                    "properties"]["text"]["expr"]["Literal"]["Value"]
                self.assertEqual(title, "'Avg Minutes / Match'")
                self.assertLessEqual(cards[-1]["position"]["x"] + 200, 1280)

    def test_data_visuals_end_before_footer_not_under_it(self):
        for mode in MODES:
            nodes = visuals(mode)
            footer = nodes[FOOTER_ID]["position"]
            with self.subTest(mode=mode):
                self.assertEqual(footer["y"], 679)
                for vid, node in nodes.items():
                    visual = node.get("visual", {})
                    if not visual.get("query", {}).get("queryState"):
                        continue
                    position = node["position"]
                    if intersects_x(position, footer):
                        with self.subTest(mode=mode, visual=vid):
                            self.assertLessEqual(
                                position["y"] + position["height"],
                                footer["y"] - 8,
                                f"{vid} intrudes into or crowds the footer band",
                            )
                for vid, (type_name, height) in CHARTS.items():
                    self.assertEqual(nodes[vid]["visual"]["visualType"], type_name)
                    self.assertEqual(nodes[vid]["position"]["height"], height)

    def test_same_visual_geometry_and_analytics_in_both_editions(self):
        production = visuals("workspace")
        synthetic = visuals("offline-demo")
        for vid in (*KPI_IDS, *CHARTS):
            with self.subTest(visual=vid):
                self.assertEqual(production[vid]["position"], synthetic[vid]["position"])
                self.assertEqual(
                    production[vid]["visual"]["query"],
                    synthetic[vid]["visual"]["query"],
                )


if __name__ == "__main__":
    unittest.main()
