"""Native PBIR Home/Closing interaction-state contract.

Source-only: hover/focus rendering, keyboard behavior and logo sharpness
must still be inspected in Power BI Desktop.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = "5cb4db7e746975558322"
CLOSING = "c83db10673c28e3346ae"
HOME_LINKS = (
    ("e05ec85d07e31d70040e", "d2bc1e6a078c5c5b125c", "01  PLAYER PERFORMANCE"),
    ("18a7cb26e6d2e25c2688", "24c53960ddc19662d824", "02  PLAYER SEGMENTATION"),
    ("8265664407e23bc40e16", "25f58efd2bb140e62be9", "03  CLUBS & LEAGUES"),
    ("f3c57a30e5671c050a79", "4c63ad904b1db6e0d156", "04  TRANSFER OUTCOMES · 365D"),
    ("6f2ba3d04798d16080ed", "292e3d92e92693c05047", "05  TRANSFER MARKET & VALUE"),
    ("87d5ca309c5c9145d3ba", "1f4c5c8000149b2e2be8", "06  PLAYER VALUATION"),
    ("b7e00000000000000001", "MLModelPerformance", "07  MODEL RELIABILITY"),
)


def read(edition: str, page: str, visual_id: str) -> dict:
    path = (ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / page / "visuals" /
            visual_id / "visual.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def literal(expr: dict) -> str:
    return expr["expr"]["Literal"]["Value"].strip("'")


def state(visual: dict, group: str, selection: str) -> dict:
    entries = visual["objects"][group]
    return next(entry["properties"] for entry in entries
                if entry.get("selector", {}).get("id") == selection)


class HomeClosingNavigationStateTests(unittest.TestCase):
    def test_all_home_module_links_have_explicit_labels_in_every_state(self):
        positions = ((68,412),(431,412),(68,482),(431,482),
                     (68,552),(431,552),(68,622))
        for (visual_id, destination, label), (x,y) in zip(HOME_LINKS, positions):
            prod = read("workspace", HOME, visual_id)
            demo = read("offline-demo", HOME, visual_id)
            with self.subTest(module=label):
                self.assertEqual(prod, demo)
                node = prod["visual"]
                self.assertEqual(node["visualType"], "actionButton")
                props = node["visualContainerObjects"]["visualLink"][0]["properties"]
                self.assertEqual(literal(props["type"]), "PageNavigation")
                self.assertEqual(literal(props["navigationSection"]), destination)
                self.assertTrue(node["visualContainerObjects"]["general"][0]
                                ["properties"]["altText"])
                self.assertEqual(tuple(prod["position"][key]
                                       for key in ("x", "y", "width", "height")),
                                 (x, y, 347, 54))
                for mode in ("default", "hover", "selected"):
                    t = state(node, "text", mode)
                    self.assertEqual(literal(t["text"]), label)
                    self.assertEqual(literal(t["fontSize"]), "13D")
                    self.assertTrue(literal(t["fontColor"]["solid"]["color"]).startswith("#"))
                    f = state(node, "fill", mode)
                    self.assertEqual(
                        literal(f["fillColor"]["solid"]["color"]),
                        {"default": "#173451",
                         "hover": "#245078",
                         "selected": "#285E9D"}[mode],
                    )

    def test_closing_return_action_is_clear_and_preserves_home_destination(self):
        for edition in ("workspace", "offline-demo"):
            node = read(edition, CLOSING, "b9a00000000000000002")
            with self.subTest(edition=edition):
                visual = node["visual"]
                self.assertEqual(visual["visualType"], "actionButton")
                link = visual["visualContainerObjects"]["visualLink"][0]["properties"]
                self.assertEqual(literal(link["navigationSection"]), HOME)
                self.assertEqual(literal(link["type"]), "PageNavigation")
                self.assertEqual(
                    literal(visual["visualContainerObjects"]["general"][0]
                            ["properties"]["altText"]),
                    "Return to Football Intelligence Home",
                )
                for mode in ("default", "hover", "selected"):
                    t = state(visual, "text", mode)
                    self.assertEqual(literal(t["text"]), "←  BACK TO HOME")
                    self.assertEqual(literal(t["fontSize"]), "14D")
                self.assertEqual(
                    literal(state(visual, "fill", "selected")
                            ["fillColor"]["solid"]["color"]), "#285E9D")


if __name__ == "__main__":
    unittest.main()
