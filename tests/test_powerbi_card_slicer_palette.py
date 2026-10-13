"""Guard NEXUS card and slicer colors without changing native data bindings.

These source-only checks cannot establish actual Power BI Desktop rendering.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "292e3d92e92693c05047",
    "MLModelPerformance",
    "1f4c5c8000149b2e2be8",
)
LEGACY = ("#F6FBF5", "#EAF6E8", "#20323F", "#296393", "#75B5EB", "#4E91CC")
STYLES = {"card", "slicer"}


def visuals(mode, page):
    base = (ROOT / "powerbi" / mode / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / page / "visuals")
    return {
        p.parent.name: json.loads(p.read_text(encoding="utf-8-sig"))
        for p in base.glob("*/visual.json")
    }


def lit(obj):
    return obj["expr"]["Literal"]["Value"].strip("'")


class NexusCardSlicerPaletteTests(unittest.TestCase):
    def test_card_and_slicer_visuals_are_nexus_colored_and_data_bound(self):
        count = {"workspace": 0, "offline-demo": 0}
        for page in PAGES:
            prod = visuals("workspace", page)
            demo = visuals("offline-demo", page)
            for mode, nodes in (("workspace", prod), ("offline-demo", demo)):
                for vid, node in nodes.items():
                    visual = node["visual"]
                    if visual.get("visualType") not in STYLES:
                        continue
                    if not visual.get("query", {}).get("queryState"):
                        continue
                    with self.subTest(edition=mode, page=page, visual=vid):
                        self.assertEqual(node, (prod if mode == "offline-demo" else demo)[vid])
                        raw = json.dumps(visual, ensure_ascii=False)
                        for old in LEGACY:
                            self.assertNotIn(old, raw)
                        ui = visual["visualContainerObjects"]
                        title = ui["title"][0]["properties"]
                        self.assertGreaterEqual(int(lit(title["fontSize"]).rstrip("D")), 11)
                        self.assertEqual(
                            lit(title["fontColor"]["solid"]["color"]), "#122942")
                        if visual["visualType"] == "slicer":
                            items = visual["objects"]["items"][0]["properties"]
                            self.assertEqual(lit(items["textSize"]), "10D")
                            self.assertEqual(
                                lit(items["background"]["solid"]["color"]),
                                "#FFFFFF")
                        count[mode] += 1
        self.assertEqual(count["workspace"], 29)
        self.assertEqual(count["offline-demo"], 29)


if __name__ == "__main__":
    unittest.main()
