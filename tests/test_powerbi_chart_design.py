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
        "a7e10000000000000003": "Player Goals by Club",
        "a7e10000000000000004": "Total Market Value by Position",
    },
    "25f58efd2bb140e62be9": {
        "a7e20000000000000001": "Club Win Rate",
        "a7e20000000000000002": "Goal Difference by Club",
        "a7e20000000000000003": "Matches by Competition",
        "a7e20000000000000004": "Goals by Competition",
    },
}


ASYMMETRIC_LAYOUT = {
    "24c53960ddc19662d824": [
        (105, 151, 754, 252), (882, 151, 351, 252),
        (105, 452, 532, 219), (660, 452, 573, 219),
    ],
    "25f58efd2bb140e62be9": [
        (105, 151, 721, 252), (849, 151, 384, 252),
        (105, 452, 542, 219), (670, 452, 563, 219),
    ],
}


TRANSFER_SUCCESS_LAYOUT = [
    (105, 191, 630, 220), (759, 191, 474, 220),
    (105, 432, 670, 239), (799, 432, 434, 239),
]

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
                    self.assertEqual(literal(props["fontSize"]),
                                     "15D" if name.endswith("01") else "12D")
                    self.assertEqual(
                        literal(props["fontColor"]["solid"]["color"]), "'#122942'"
                    )
                    self.assertEqual(
                        literal(v["visualContainerObjects"]["border"][0]
                                ["properties"]["radius"]), "12D"
                    )
                    labels = v["objects"]["labels"][0]["properties"]
                    self.assertEqual(literal(labels["fontSize"]),
                                     "12D" if name.endswith("01") else "10D")
                    self.assertEqual(
                        literal(labels["color"]["solid"]["color"]), "'#122942'"
                    )
                    for axis in ("categoryAxis", "valueAxis"):
                        self.assertEqual(
                            literal(v["objects"][axis][0]["properties"]["titleFontSize"]),
                            "11D", "Axis titles should remain readable on 1280×720 report pages"
                        )

    def test_distinct_page_compositions_are_valid_and_data_bound(self):
        for page, expected in ADDITIONAL_PAGES.items():
            rects = []
            for i, name in enumerate(expected):
                offline = visual("offline-demo", name, page)
                workspace = visual("workspace", name, page)
                self.assertEqual(offline["position"], workspace["position"])
                position = offline["position"]
                rect = tuple(position[k] for k in ("x", "y", "width", "height"))
                self.assertEqual(rect, ASYMMETRIC_LAYOUT[page][i])
                self.assertLessEqual(position["x"] + position["width"], 1280)
                self.assertLessEqual(position["y"] + position["height"], 671,
                                     "Native charts must clear the footer starting at y=679")
                rects.append(rect)
                self.assertEqual(
                    offline["visual"]["query"]["queryState"],
                    workspace["visual"]["query"]["queryState"],
                )
            for i, (x, y, w, h) in enumerate(rects):
                for x2, y2, w2, h2 in rects[i + 1:]:
                    self.assertTrue(
                        x + w <= x2 or x2 + w2 <= x
                        or y + h <= y2 or y2 + h2 <= y,
                        f"Overlapping native PBIR charts on {page}",
                    )

    def test_clarified_chart_titles_describe_real_aggregates(self):
        contracts = (
            ("24c53960ddc19662d824", "a7e10000000000000003",
             "Sum(fct_player_performance.total_goals)"),
            ("24c53960ddc19662d824", "a7e10000000000000004",
             "Sum(fct_player_performance.market_value_in_eur)"),
            ("25f58efd2bb140e62be9", "a7e20000000000000001",
             "Average(fct_club_performance.win_rate)"),
            ("25f58efd2bb140e62be9", "a7e20000000000000003",
             "Sum(fct_competition_performance.matches_played)"),
        )
        for page, visual_id, metric in contracts:
            for mode in ("workspace", "offline-demo"):
                with self.subTest(page=page, visual=visual_id, mode=mode):
                    state = visual(mode, visual_id, page)["visual"]["query"]["queryState"]
                    self.assertEqual(
                        [p["queryRef"] for p in state["Y"]["projections"]],
                        [metric],
                        "Chart titles must represent the currently bound statistic",
                    )

    def test_transfer_success_has_distinct_evidence_first_geometry(self):
        for mode in ("offline-demo", "workspace"):
            for i, name in enumerate(EXPECTED):
                node = visual(mode, name)
                self.assertTrue(node["visual"]["query"]["queryState"])
                position = node["position"]
                rect = tuple(position[k] for k in ("x", "y", "width", "height"))
                self.assertEqual(rect, TRANSFER_SUCCESS_LAYOUT[i])
                self.assertLessEqual(position["x"] + position["width"], 1280)
                self.assertLessEqual(
                    position["y"] + position["height"], 671,
                    "Transfer-outcomes panels must clear the footer starting at y=679"
                )

    def test_offline_and_workspace_have_identical_report_visuals(self):
        for name in EXPECTED:
            with self.subTest(name=name):
                self.assertEqual(visual("offline-demo", name), visual("workspace", name))


if __name__ == "__main__":
    unittest.main()
