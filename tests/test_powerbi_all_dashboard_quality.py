"""PBIR NEXUS design and page-registry contracts (source-level, not Desktop proof).

Run with: python -m unittest tests.test_powerbi_all_dashboard_quality
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
                    self.assertEqual(literal_color(page),
                        "#071829" if page_id in DARK else (
                            "#091E33" if page_id == "d2bc1e6a078c5c5b125c"
                            else "#EAF1FA"
                        ))
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


if __name__ == "__main__":
    unittest.main()
