"""NEXUS Football PBIR UX guard: source assertions only, not a Desktop render test."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = "5cb4db7e746975558322"
ANALYTIC = (
    "d2bc1e6a078c5c5b125c", "24c53960ddc19662d824",
    "25f58efd2bb140e62be9", "4c63ad904b1db6e0d156",
    "292e3d92e92693c05047", "1f4c5c8000149b2e2be8",
)
HOME_LINKS = (
    ("e05ec85d07e31d70040e", "d2bc1e6a078c5c5b125c", "01  PLAYER PERFORMANCE"),
    ("18a7cb26e6d2e25c2688", "24c53960ddc19662d824", "02  PLAYER SEGMENTATION"),
    ("8265664407e23bc40e16", "25f58efd2bb140e62be9", "03  CLUBS & LEAGUES"),
    ("f3c57a30e5671c050a79", "4c63ad904b1db6e0d156", "04  TRANSFER OUTCOMES · 365D"),
    ("6f2ba3d04798d16080ed", "292e3d92e92693c05047", "05  TRANSFER MARKET & VALUE"),
    ("87d5ca309c5c9145d3ba", "1f4c5c8000149b2e2be8", "06  PLAYER VALUATION"),
    ("b7e00000000000000001", "MLModelPerformance", "07  MODEL RELIABILITY"),
)
CHARTS = {
    "24c53960ddc19662d824": {
        "a7e10000000000000001": ("Position", "Players"),
        "a7e10000000000000002": ("Age band", "Players"),
        "a7e10000000000000003": ("Club", "Goals"),
        "a7e10000000000000004": ("Position", "Market value (€)"),
    },
    "25f58efd2bb140e62be9": {
        "a7e20000000000000001": ("Club", "Win rate"),
        "a7e20000000000000002": ("Club", "Goal difference"),
        "a7e20000000000000003": ("Competition", "Matches"),
        "a7e20000000000000004": ("Competition", "Goals"),
    },
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def value(expr):
    return expr["expr"]["Literal"]["Value"].strip("'")


def visual(edition, page, vid):
    return load(ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
                "Report" / "definition" / "pages" / page / "visuals" / vid / "visual.json")


class DesignUnguardedRegression(unittest.TestCase):
    def test_home_has_seven_readable_clickable_destinations(self):
        for edition in ("workspace", "offline-demo"):
            y_values = []
            for vid, destination, label in HOME_LINKS:
                with self.subTest(edition=edition, label=label):
                    node = visual(edition, HOME, vid)
                    v = node["visual"]
                    self.assertEqual(v["visualType"], "actionButton")
                    link = v["visualContainerObjects"]["visualLink"][0]["properties"]
                    self.assertEqual(value(link["type"]), "PageNavigation")
                    self.assertEqual(value(link["navigationSection"]), destination)
                    default = next(x for x in v["objects"]["text"]
                                   if x.get("selector", {}).get("id") == "default")
                    self.assertEqual(value(default["properties"]["text"]), label)
                    self.assertTrue(v["visualContainerObjects"]["general"][0]["properties"]["altText"])
                    self.assertEqual(value(v["objects"]["fill"][0]["properties"]["show"]), "true")
                    p = node["position"]
                    self.assertEqual((p["x"], p["width"], p["height"]), (59, 392, 34))
                    self.assertLessEqual(p["y"] + p["height"], 695)
                    y_values.append(p["y"])
            self.assertEqual(y_values, sorted(y_values))
            self.assertEqual(len(set(y_values)), 7)

    def test_letter_navigation_is_explained_on_six_analytical_pages(self):
        for edition in ("workspace", "offline-demo"):
            for i, page in enumerate(ANALYTIC, 1):
                with self.subTest(edition=edition, page=page):
                    bg = visual(edition, page, "b8a" + str(i).zfill(17))
                    legend = visual(edition, page, "b8b" + str(i).zfill(17))
                    self.assertEqual(bg["visual"]["visualType"], "shape")
                    self.assertEqual(legend["visual"]["visualType"], "textbox")
                    self.assertEqual(bg["position"]["y"], 679)
                    self.assertLessEqual(bg["position"]["y"] + bg["position"]["height"], 720)
                    self.assertEqual(legend["position"]["y"], 687)
                    self.assertEqual(legend["position"]["height"], 25)
                    run = legend["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"][0]
                    for word in ("HOME", "PERFORMANCE", "SEGMENTS", "CLUBS", "TRANSFERS", "VALUATION"):
                        self.assertIn(word, run["value"])
                    self.assertEqual(
                        value(legend["visual"]["visualContainerObjects"]["background"][0]["properties"]["show"]),
                        "false"
                    )

    def test_chart_axes_are_understandable_without_mutating_queries(self):
        for page, charts in CHARTS.items():
            for vid, (category, metric) in charts.items():
                prod = visual("workspace", page, vid)
                demo = visual("offline-demo", page, vid)
                with self.subTest(page=page, id=vid):
                    self.assertEqual(prod, demo)
                    v = prod["visual"]
                    self.assertTrue(v["query"]["queryState"])
                    self.assertIn(v["visualType"], ("clusteredBarChart", "clusteredColumnChart"))
                    for obj, expected in (("categoryAxis", category), ("valueAxis", metric)):
                        props = v["objects"][obj][0]["properties"]
                        self.assertEqual(value(props["showAxisTitle"]), "true")
                        self.assertEqual(value(props["titleText"]), expected)
                        self.assertEqual(value(props["titleFontSize"]), "11D")
        self.assertEqual(
            visual("workspace", "25f58efd2bb140e62be9",
                   "a7e20000000000000004")["visual"]["visualType"], "clusteredBarChart"
        )

    def test_club_rate_has_percentage_display_but_still_uses_same_source(self):
        for edition in ("workspace", "offline-demo"):
            path = ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Model" / "definition" / "tables" / "fct_club_performance.tmdl"
            source = path.read_text(encoding="utf-8-sig")
            block = source.split("column win_rate\n", 1)[1].split("\n\tcolumn ", 1)[0]
            self.assertIn("dataType: double", block)
            self.assertIn("formatString: 0.0%", block)
            self.assertIn("sourceColumn: win_rate", block)


if __name__ == "__main__":
    unittest.main()
