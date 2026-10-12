"""PBIR NEXUS design and page-registry contracts (source-level, not Desktop proof).

Run with: python -m unittest discover -s tests -p 'test_powerbi_all_dashboard_quality.py'
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = ("workspace", "offline-demo")
PAGES = {
    "5cb4db7e746975558322": "home",
    "d2bc1e6a078c5c5b125c": "performance",
    "24c53960ddc19662d824": "segmentation",
    "25f58efd2bb140e62be9": "club",
    "4c63ad904b1db6e0d156": "transfer_success",
    "292e3d92e92693c05047": "transfer_value",
    "1f4c5c8000149b2e2be8": "market_value",
    "MLModelPerformance": "model_reliability",
    "c83db10673c28e3346ae": "closing",
    "91edaa93bbbdbbc8e854": "transfer_detail",
    "MLPlayerDetail": "prediction_detail",
    "tooltip_transfer_p011": "transfer_tooltip",
    "tooltip_pred_p012": "prediction_tooltip",
}
TOOLTIPS = {"tooltip_transfer_p011", "tooltip_pred_p012"}
DRILLTHROUGHS = {"91edaa93bbbdbbc8e854", "MLPlayerDetail"}
DARK = {"5cb4db7e746975558322", "c83db10673c28e3346ae"}
PAGE_CANVASES = {
    "5cb4db7e746975558322": "#071829",  # Executive home / dark navy
    "d2bc1e6a078c5c5b125c": "#091E33",  # Player performance / data control room
    "24c53960ddc19662d824": "#EDEBFA",  # Segmentation / lavender
    "25f58efd2bb140e62be9": "#E7F2FD",  # Clubs / blue
    "4c63ad904b1db6e0d156": "#E9F1FA",  # Transfer outcomes / neutral
    "292e3d92e92693c05047": "#E8ECF8",  # Transfer market / blue slate
    "1f4c5c8000149b2e2be8": "#E7EFFB",  # Player valuation / blue
    "MLModelPerformance": "#E6EDF9",  # ML reliability / technical blue
    "c83db10673c28e3346ae": "#071829",  # Closing / navy
    "91edaa93bbbdbbc8e854": "#EBEFF9",  # Transfer detail / slate lavender
    "MLPlayerDetail": "#E8EBF6",  # Prediction detail / soft lavender
    "tooltip_transfer_p011": "#E7F0FC",  # Transfer tooltip / pale blue
    "tooltip_pred_p012": "#E8ECFA",  # Prediction tooltip / blue lavender
}
THEME = "NEXUSMidnight-20261012-v2.json"
CHART_TYPES = {
    "clusteredBarChart", "clusteredColumnChart", "lineChart", "scatterChart",
    "donutChart", "treemap", "tableEx", "pivotTable", "card",
}


def obj(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def project(mode: str):
    return ROOT / "powerbi" / mode / "FootballPlayerAnalysis"


def literal_color(page):
    return (
        page["objects"]["background"][0]["properties"]["color"]["solid"]
        ["color"]["expr"]["Literal"]["Value"].strip("'").upper()
    )


class EveryDashboardSourceContract(unittest.TestCase):
    def test_entire_page_registry_and_start_page(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                pages = project(mode) / "Report" / "definition" / "pages"
                manifest = obj(pages / "pages.json")
                ids = manifest["pageOrder"]
                self.assertEqual(len(ids), 13)
                self.assertEqual(set(ids), set(PAGES))
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(ids[0], "5cb4db7e746975558322")
                self.assertEqual(manifest["activePageName"], ids[0])
                self.assertLess(
                    ids.index("MLModelPerformance"),
                    ids.index("c83db10673c28e3346ae"),
                    "Technical ML reliability evidence belongs before closing",
                )
                self.assertEqual(
                    ids.index("c83db10673c28e3346ae"), 8,
                    "Closing must be the last normal full-size presentation page",
                )
                self.assertEqual(
                    {p.parent.name for p in pages.glob("*/page.json")},
                    set(ids),
                )

    def test_every_page_type_background_and_visibility(self):
        for mode in MODES:
            root = project(mode) / "Report" / "definition" / "pages"
            for page_id in PAGES:
                with self.subTest(mode=mode, page=page_id):
                    page = obj(root / page_id / "page.json")
                    self.assertEqual(page["name"], page_id)
                    self.assertEqual(literal_color(page), PAGE_CANVASES[page_id])
                    self.assertNotRegex(
                        page["displayName"],
                        r"[⭐👥🏆💰📊]",
                        "Decorative legacy emoji is not an editorial page title",
                    )
                    if mode == "offline-demo":
                        self.assertTrue(page["displayName"].startswith("[DEMO]"))
                    else:
                        self.assertFalse(page["displayName"].startswith("[DEMO]"))
                    if page_id in TOOLTIPS:
                        self.assertEqual((page["width"], page["height"]), (560, 320))
                        self.assertEqual(page["displayOption"], "ActualSize")
                        self.assertEqual(page["pageBinding"]["type"], "Tooltip")
                        self.assertEqual(page["visibility"], "HiddenInViewMode")
                    else:
                        self.assertEqual((page["width"], page["height"]), (1280, 720))
                        self.assertEqual(page["displayOption"], "FitToPage")
                    if page_id in DRILLTHROUGHS:
                        self.assertEqual(page["visibility"], "HiddenInViewMode")
                        self.assertEqual(page["type"], "Drillthrough")

    def test_registered_nexus_theme_applies_to_all_visual_types(self):
        for mode in MODES:
            report = project(mode) / "Report"
            definition = obj(report / "definition" / "report.json")
            reg = definition["themeCollection"]["customTheme"]
            self.assertEqual(reg["name"], THEME)
            self.assertEqual(reg["type"], "RegisteredResources")
            packages = definition["resourcePackages"]
            registered = next(p for p in packages if p["name"] == "RegisteredResources")
            self.assertIn(
                {"name": THEME, "path": THEME, "type": "CustomTheme"},
                registered["items"],
            )
            theme = obj(report / "StaticResources" / "RegisteredResources" / THEME)
            self.assertEqual(theme["name"], THEME)
            self.assertEqual(theme["dataColors"][0], "#4EA8FF")
            self.assertEqual(theme["foreground"], "#122942")
            self.assertEqual(theme["background"], "#FFFFFF")
            self.assertTrue(CHART_TYPES.issubset(theme["visualStyles"]))
            for typ in CHART_TYPES:
                props = theme["visualStyles"][typ]["*"]
                self.assertEqual(
                    props["background"][0]["color"]["solid"]["color"], "#FFFFFF",
                )
                self.assertEqual(
                    props["border"][0]["color"]["solid"]["color"], "#D3E3F5",
                )
                self.assertGreaterEqual(props["title"][0]["fontSize"], 10)

    def test_tooltip_visuals_fit_and_are_genuine_data_views(self):
        for mode in MODES:
            root = project(mode) / "Report" / "definition" / "pages"
            for page_id in TOOLTIPS:
                with self.subTest(mode=mode, page=page_id):
                    visual_paths = sorted((root / page_id / "visuals").glob("*/visual.json"))
                    self.assertEqual(len(visual_paths), 3)
                    types = set()
                    for path in visual_paths:
                        visual = obj(path)
                        self.assertEqual(visual["name"], path.parent.name)
                        self.assertNotIn("visualContainerObjects", visual)
                        p = visual["position"]
                        self.assertGreater(p["width"], 0)
                        self.assertGreater(p["height"], 0)
                        self.assertGreaterEqual(p["x"], 0)
                        self.assertGreaterEqual(p["y"], 0)
                        self.assertLessEqual(p["x"] + p["width"], 560)
                        self.assertLessEqual(p["y"] + p["height"], 320)
                        types.add(visual["visual"]["visualType"])
                    self.assertIn("scatterChart", types)
                    self.assertIn("multiRowCard", types)

    def test_home_navigation_links_are_registered(self):
        for mode in MODES:
            root = project(mode) / "Report" / "definition" / "pages"
            paths = (root / "5cb4db7e746975558322" / "visuals").glob("*/visual.json")
            targets = []
            for path in paths:
                visual = obj(path).get("visual", {})
                for part in visual.get("visualContainerObjects", {}).get("visualLink", []):
                    props = part.get("properties", {})
                    item = props.get("navigationSection", {}).get("expr", {}).get("Literal")
                    if item:
                        targets.append(item["Value"].strip("'"))
            self.assertGreaterEqual(len(targets), 6)
            self.assertTrue(set(targets).issubset(PAGES))
            self.assertNotIn("tooltip_pred_p012", targets)
            self.assertNotIn("tooltip_transfer_p011", targets)

    def test_data_visuals_have_synchronized_accessible_descriptions(self):
        expected = {
            "24c53960ddc19662d824": [f"a7e1{i:016d}" for i in range(1, 5)],
            "25f58efd2bb140e62be9": [f"a7e2{i:016d}" for i in range(1, 5)],
            "4c63ad904b1db6e0d156": [
                *[f"a7e3{i:016d}" for i in range(1, 5)],
                *[f"a7e4{i:016d}" for i in range(1, 5)],
            ],
            "d2bc1e6a078c5c5b125c": [
                "6c68e020599db75da880", "750474d7071b93a004b5",
                "81f5bb0995b4428b2b0d", "a61aa3c509a6b3e3b1b4",
            ],
            "292e3d92e92693c05047": [
                "0839d8ed3d7479a01f32", "5bbe3e0865c55bbeade1",
                "1c4d73ece1a64f57c0fc", "9c728e8d682165354da4",
            ],
            "1f4c5c8000149b2e2be8": [
                "4d304949cba7dd247021", "8b67c00a69b995fd3db6",
                "3ccd5a45594119af9bb7", "be92253a5130bdec9028",
            ],
            "MLModelPerformance": [
                "44ef7cfce32d97d2bb52", "6a52894b1eadaab185b4",
                "9cac2684a07ca1c85ca6", "162f01fa99bf4b660a1e",
            ],
            "tooltip_pred_p012": ["tt012_scatter_0001", "tt012_stats_0001"],
            "tooltip_transfer_p011": ["tt011_scatter_0001", "tt011_stats_0001"],
        }
        self.assertEqual(sum(len(ids) for ids in expected.values()), 36)
        for page_id, visual_ids in expected.items():
            for visual_id in visual_ids:
                with self.subTest(page=page_id, visual=visual_id):
                    results = []
                    for mode in MODES:
                        path = (project(mode) / "Report" / "definition" /
                                "pages" / page_id / "visuals" / visual_id / "visual.json")
                        node = obj(path)
                        props = node["visual"]["visualContainerObjects"]["general"][0]["properties"]
                        alt = props["altText"]["expr"]["Literal"]["Value"].strip("'")
                        self.assertTrue(20 <= len(alt) <= 250)
                        self.assertNotIn("SYNTHETIC DEMO", alt)
                        results.append(alt)
                    self.assertEqual(results[0], results[1])



    def test_single_registered_resource_location_without_duplicate_old_assets(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                project = ROOT / "powerbi" / mode / "FootballPlayerAnalysis"
                # Current PBIR resourcePackages points to Report/StaticResources.
                # Former project-root mirrors duplicated 9.1MB per edition.
                self.assertFalse(
                    (project / "StaticResources" / "RegisteredResources").exists()
                )
                current = project / "Report" / "StaticResources" / "RegisteredResources"
                self.assertTrue(current.is_dir())
                report = json.loads(
                    (project / "Report" / "definition" / "report.json").read_text(
                        encoding="utf-8-sig"
                    )
                )
                packages = [
                    x for x in report["resourcePackages"]
                    if x["name"] == "RegisteredResources"
                ]
                self.assertEqual(len(packages), 1)
                for item in packages[0]["items"]:
                    self.assertTrue((current / item["path"]).is_file(), item["path"])

    def test_single_nexus_editorial_home_and_closing_with_intact_navigation(self):
        home = "5cb4db7e746975558322"
        closing = "c83db10673c28e3346ae"
        for mode in MODES:
            def read_visual(page, visual_id):
                return json.loads(
                    (ROOT / "powerbi" / mode / "FootballPlayerAnalysis"
                     / "Report" / "definition" / "pages" / page
                     / "visuals" / visual_id / "visual.json").read_text(
                         encoding="utf-8-sig"
                     )
                )
            for page, visual_id, title in [
                (home, "be100000000000000002", "THE GAME, IN DATA."),
                (closing, "be100000000000000009", "EVIDENCE DRIVES DECISIONS."),
            ]:
                with self.subTest(mode=mode, page=page):
                    v = read_visual(page, visual_id)
                    self.assertEqual(
                        v["visual"]["objects"]["general"][0]["properties"]
                        ["paragraphs"][0]["textRuns"][0]["value"], title,
                    )
            for visual_id in [
                "18a7cb26e6d2e25c2688", "6f2ba3d04798d16080ed",
                "8265664407e23bc40e16", "87d5ca309c5c9145d3ba",
                "e05ec85d07e31d70040e", "f3c57a30e5671c050a79",
            ]:
                v = read_visual(home, visual_id)
                self.assertEqual(v["visual"]["visualType"], "actionButton")
                self.assertIn("action", v["visual"]["objects"])
                for config in v["visual"]["objects"]["text"]:
                    t = config["properties"].get("text", {}).get(
                        "expr", {}
                    ).get("Literal", {}).get("Value", "")
                    self.assertNotRegex(t, r"[📊👥🏆💰🔄⭐]")

    def test_legacy_presentation_artifacts_are_not_shipped(self):
        legacy_gallery = ROOT / "docs" / "assets" / "screenshots"
        self.assertFalse(legacy_gallery.exists())
        self.assertFalse(
            (ROOT / "docs" / "assets" / "football-analytics-cover.svg").exists()
        )

    def test_primary_analytics_keep_nexus_accents_not_old_green(self):
        primary = {
            "d2bc1e6a078c5c5b125c": [
                "6c68e020599db75da880", "750474d7071b93a004b5",
                "81f5bb0995b4428b2b0d", "a61aa3c509a6b3e3b1b4",
            ],
            "292e3d92e92693c05047": [
                "0839d8ed3d7479a01f32", "5bbe3e0865c55bbeade1",
                "1c4d73ece1a64f57c0fc", "9c728e8d682165354da4",
            ],
            "1f4c5c8000149b2e2be8": [
                "4d304949cba7dd247021", "8b67c00a69b995fd3db6",
                "3ccd5a45594119af9bb7", "be92253a5130bdec9028",
            ],
            "MLModelPerformance": [
                "44ef7cfce32d97d2bb52", "6a52894b1eadaab185b4",
                "9cac2684a07ca1c85ca6", "162f01fa99bf4b660a1e",
            ],
        }
        legacy = ("#285D3D", "#F6FBF5", "#EAF6E8",
                  "#8BC99A", "#6FA56D", "#296393", "#496B98")
        for mode in MODES:
            for page, ids in primary.items():
                for visual_id in ids:
                    with self.subTest(mode=mode, page=page, visual=visual_id):
                        path = (project(mode) / "Report" / "definition" /
                                "pages" / page / "visuals" / visual_id / "visual.json")
                        node = obj(path)
                        self.assertTrue(node["visual"]["query"]["queryState"])
                        raw = path.read_text(encoding="utf-8-sig").upper()
                        for bad in legacy:
                            self.assertNotIn(bad, raw)

    def test_ml_dashboard_no_legacy_green_accent(self):
        legacy = ("#F6FBF5", "#EAF6E8")
        ml_visuals = (
            "1129c5d18f0c86361eb8",
            "2beada4d32fcdc1ff094",
            "31824c579723a8252662",
            "3ccd5a45594119af9bb7",
        )
        for mode in MODES:
            for visual_id in ml_visuals:
                path = (project(mode) / "Report" / "definition" / "pages" /
                        "1f4c5c8000149b2e2be8" / "visuals" / visual_id / "visual.json")
                content = path.read_text(encoding="utf-8-sig").upper()
                for color in legacy:
                    with self.subTest(mode=mode, visual=visual_id, color=color):
                        self.assertNotIn(color, content)




if __name__ == "__main__":
    unittest.main()
