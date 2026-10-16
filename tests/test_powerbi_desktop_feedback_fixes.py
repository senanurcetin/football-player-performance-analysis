"""Screenshot-driven Power BI acceptance invariants (static PBIR, no Desktop render)."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = ("workspace", "offline-demo")
PAGES = (
    "d2bc1e6a078c5c5b125c",
    "24c53960ddc19662d824",
    "25f58efd2bb140e62be9",
    "4c63ad904b1db6e0d156",
    "292e3d92e92693c05047",
    "1f4c5c8000149b2e2be8",
    "MLModelPerformance",
    "91edaa93bbbdbbc8e854",
    "MLPlayerDetail",
)
ANALYTIC = PAGES[:6]
FOOTER_VISUALS = {
    ANALYTIC[0]: "6c68e020599db75da880 750474d7071b93a004b5 dd91e16c6d11d504a577",
    ANALYTIC[1]: "a7e10000000000000003 a7e10000000000000004",
    ANALYTIC[2]: "a7e20000000000000003 a7e20000000000000004",
    ANALYTIC[3]: "a7e30000000000000003 a7e30000000000000004",
    ANALYTIC[4]: "9c728e8d682165354da4 1c4d73ece1a64f57c0fc",
    ANALYTIC[5]: "be92253a5130bdec9028 4d304949cba7dd247021",
}
DETAIL_BACKDROPS = {
    "91edaa93bbbdbbc8e854": "118f94f2f8b3315a1894",
    "MLPlayerDetail": "f6e6c24f28601197ba4a",
}
KPI_IDS = (
    "303c777d36178076aa39", "52a25425ec00bcc0a8b1",
    "6cb1590ae40874c838b7", "c49bad3782a43cdac710",
    "fd59ca45d88b6eb6b521",
)


def pbir(edition, page, vid=None):
    base = (ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / page)
    return json.loads((base / ("visuals/" + vid + "/visual.json" if vid else "page.json"))
                      .read_text(encoding="utf-8-sig"))


def val(node):
    return node["expr"]["Literal"]["Value"].strip("'")


class DesktopFeedbackSourceContract(unittest.TestCase):
    def test_all_nine_full_size_analysis_backgrounds_share_navy(self):
        for edition in EDITIONS:
            for page in PAGES:
                with self.subTest(edition=edition, page=page):
                    source = pbir(edition, page)
                    bg = source["objects"]["background"][0]["properties"]["color"]["solid"]["color"]
                    self.assertEqual(val(bg), "#091E33")

    def test_legacy_pastel_fullscreen_shapes_are_gone(self):
        for edition in EDITIONS:
            for page, vid in DETAIL_BACKDROPS.items():
                with self.subTest(edition=edition, page=page):
                    node = pbir(edition, page, vid)
                    self.assertEqual(node["position"]["width"], 1280)
                    self.assertEqual(node["position"]["height"], 720)
                    fill = node["visual"]["objects"]["fill"][0]["properties"]["fillColor"]["solid"]["color"]
                    self.assertEqual(val(fill), "#091E33")

    def test_nav_footer_fits_page_and_not_under_bottom_charts(self):
        for edition in EDITIONS:
            for index, (page, ids) in enumerate(FOOTER_VISUALS.items(), 1):
                with self.subTest(edition=edition, page=page):
                    footer = pbir(edition, page, "b8a" + str(index).zfill(17))
                    legend = pbir(edition, page, "b8b" + str(index).zfill(17))
                    self.assertEqual(footer["position"]["y"], 679)
                    self.assertEqual(footer["position"]["height"], 39)
                    self.assertEqual(legend["position"]["y"], 683)
                    self.assertEqual(legend["position"]["height"], 35)
                    run = legend["visual"]["objects"]["general"][0]["properties"][
                        "paragraphs"][0]["textRuns"][0]
                    self.assertGreaterEqual(int(run["textStyle"]["fontSize"].rstrip("pt")), 10)
                    self.assertEqual(run["textStyle"]["color"], "#F1F7FF")
                    for vid in ids.split():
                        visual = pbir(edition, page, vid)
                        bottom = visual["position"]["y"] + visual["position"]["height"]
                        self.assertLessEqual(bottom, 671.0001)

    def test_performance_cards_have_dark_background_and_clear_labels(self):
        for edition in EDITIONS:
            for vid in KPI_IDS:
                with self.subTest(edition=edition, card=vid):
                    node = pbir(edition, ANALYTIC[0], vid)["visual"]
                    self.assertEqual(node["visualType"], "card")
                    background = node["visualContainerObjects"]["background"][0]["properties"]
                    self.assertEqual(val(background["color"]["solid"]["color"]), "#102B47")
                    self.assertEqual(val(background["transparency"]), "0D")
                    self.assertEqual(val(node["objects"]["labels"][0]["properties"]["color"]
                                         ["solid"]["color"]), "#FFFFFF")
                    self.assertEqual(val(node["visualContainerObjects"]["title"][0]["properties"]
                                         ["fontColor"]["solid"]["color"]), "#D2E5FB")

    def test_palette_and_offline_disclosure_do_not_get_confused(self):
        expected = ["#4EA8FF", "#8F9BFF", "#00CBEA", "#6E55C6",
                    "#76B8FF", "#B9C5CE", "#376DBE", "#B3A4F6"]
        for edition in EDITIONS:
            resource = (ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
                        "Report" / "StaticResources" / "RegisteredResources" /
                        "NEXUSMidnight-20261012-v2.json")
            self.assertEqual(json.loads(resource.read_text(encoding="utf-8"))["dataColors"],
                             expected)
        demo_page = ROOT / "powerbi" / "offline-demo" / "FootballPlayerAnalysis" / "Report" / "definition" / "pages" / ANALYTIC[0]
        self.assertTrue((demo_page / "visuals/de9a00000000000000010/visual.json").exists())
        prod_page = ROOT / "powerbi" / "workspace" / "FootballPlayerAnalysis" / "Report" / "definition" / "pages" / ANALYTIC[0]
        self.assertFalse((prod_page / "visuals/de9a00000000000000010/visual.json").exists())


if __name__ == "__main__":
    unittest.main()
