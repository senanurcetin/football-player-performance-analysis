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


def visual(mode, name):
    path = (ROOT / "powerbi" / mode / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / PAGE / "visuals" / name / "visual.json")
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

    def test_offline_and_workspace_have_identical_report_visuals(self):
        for name in EXPECTED:
            with self.subTest(name=name):
                self.assertEqual(visual("offline-demo", name), visual("workspace", name))


if __name__ == "__main__":
    unittest.main()
