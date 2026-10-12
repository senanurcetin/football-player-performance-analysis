"""Source-level regression checks for the *editable* 365-day Power BI visuals.

These checks inspect PBIR JSON for the two genuine report projects.
They are NOT proof of Power BI Desktop render, DAX refresh or warehouse parity.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = "4c63ad904b1db6e0d156"
EXPECTED = {
    "a7e30000000000000001": ("Observed transfers by position · 365d", "#4EA8FF"),
    "a7e30000000000000002": ("Average transfer fee by position · 365d", "#8F9BFF"),
    "a7e30000000000000003": ("Observed success rate by position · 365d", "#487FD8"),
    "a7e30000000000000004": ("365d outcome follow-up status", "#8F9BFF"),
}


ADDITIONAL_PAGES = {
    "24c53960ddc19662d824": {
        "a7e10000000000000001": "Players by Position",
        "a7e10000000000000002": "Age Group Distribution",
        "a7e10000000000000003": "Goals by Club",
        "a7e10000000000000004": "Market Value by Position",
    },
    "25f58efd2bb140e62be9": {
        "a7e20000000000000001": "Club Win Rate",
        "a7e20000000000000002": "Goal Difference by Club",
        "a7e20000000000000003": "Competition Matches",
        "a7e20000000000000004": "Goals by Competition",
    },
}


def visual(mode, name, page=PAGE):
    path = (ROOT / "powerbi" / mode / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / page / "visuals" / name / "visual.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def literal(obj):
    return obj["expr"]["Literal"]["Value"]


class TransferDashboardDesignTests(unittest.TestCase):
    def test_real_data_visuals_have_nexus_styles_and_nonempty_queries(self):
        for mode in ("offline-demo", "workspace"):
            for name, (title, color) in EXPECTED.items():
                with self.subTest(mode=mode, name=name):
                    node = visual(mode, name)
                    ui = node["visual"]
                    props = ui["visualContainerObjects"]["title"][0]["properties"]
                    self.assertEqual(literal(props["text"]), "'" + title + "'")
                    self.assertEqual(literal(props["fontSize"]), "13D")
                    self.assertEqual(
                        literal(props["fontColor"]["solid"]["color"]), "'#122942'"
                    )
                    self.assertEqual(
                        literal(ui["objects"]["dataPoint"][0]["properties"]
                                ["defaultColor"]["solid"]["color"]), "'" + color + "'"
                    )
                    self.assertEqual(
                        literal(ui["objects"]["labels"][0]["properties"]["fontSize"]),
                        "11D",
                    )
                    self.assertTrue(ui["query"]["queryState"])
                    self.assertNotIn("visualContainerObjects", node)

    def test_segmentation_and_club_charts_have_consistent_native_pbir_styles(self):
        for page, expected in ADDITIONAL_PAGES.items():
            for name, title in expected.items():
                with self.subTest(page=page, name=name):
                    offline = visual("offline-demo", name, page)
                    workspace = visual("workspace", name, page)
                    self.assertEqual(offline, workspace)
                    v = offline["visual"]
                    self.assertIn(v["visualType"], (
                        "clusteredBarChart", "clusteredColumnChart", "donutChart"
                    ))
                    self.assertTrue(v["query"]["queryState"])
                    props = v["visualContainerObjects"]["title"][0]["properties"]
                    self.assertEqual(literal(props["text"]), "'" + title + "'")
                    self.assertEqual(literal(props["fontSize"]), "13D")
                    self.assertEqual(
                        literal(props["fontColor"]["solid"]["color"]), "'#122942'"
                    )
                    self.assertEqual(
                        literal(v["visualContainerObjects"]["border"][0]
                                ["properties"]["radius"]), "12D"
                    )
                    labels = v["objects"]["labels"][0]["properties"]
                    self.assertEqual(literal(labels["fontSize"]), "11D")
                    self.assertEqual(
                        literal(labels["color"]["solid"]["color"]), "'#122942'"
                    )

    def test_offline_and_workspace_have_identical_report_visuals(self):
        for name in EXPECTED:
            with self.subTest(name=name):
                self.assertEqual(visual("offline-demo", name), visual("workspace", name))


if __name__ == "__main__":
    unittest.main()
