"""Source-only navigation and logo-clearance checks for the NEXUS Football PBIR report.

Does not certify Power BI Desktop rendering or screen-reader behavior.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = "5cb4db7e746975558322"
ML = "MLModelPerformance"
CLOSING = "c83db10673c28e3346ae"
ROUTES = {
    HOME: "Home",
    "d2bc1e6a078c5c5b125c": "Player performance",
    "24c53960ddc19662d824": "Player segmentation",
    "25f58efd2bb140e62be9": "Club and league analysis",
    "4c63ad904b1db6e0d156": "365-day transfer outcomes",
    "292e3d92e92693c05047": "Transfer market and value",
    "1f4c5c8000149b2e2be8": "Player valuation",
}
PAGE_NAVS = {
    "d2bc1e6a078c5c5b125c": "09bf21c11a70757a57c0 0f7cf5410eb31b2391d5 23992e439de0c00e249e 27d3e38984b47d9a0035 390168d8d044211d642a 8b879cc2280c1040d01d f76fa3148960cce74b0a",
    "24c53960ddc19662d824": "0c43269b0c9319b1be66 50ffce215b1b0e8b686a 5a3d44c6a9d52a4dc801 73d4a571a0ee5382e00c 7f40ccf849183b1a81c5 bd77b4ffc16de500c460 c8225fb9b8b21567a4d3",
    "25f58efd2bb140e62be9": "8efbd730d0a500d3839e 9ea3936f85b7de4494ba c73317e5130ac087477d d6b60644e70102d023b0 e74c97c74255c1ae037b ed3aa423b847ddd5b11b f84560c2cea21499342e",
    "4c63ad904b1db6e0d156": "13a235a6a8731c9ec7d3 23f7b8d2575487a746c6 2809bd10c6e4d9050b48 40bba15935c1704b7478 43949b48092a00078341 cbb9e7fe659384c8b7da ff4cb16decd3ab839c9b",
    "292e3d92e92693c05047": "0698c7ffda0b2cbc24d3 1102af207033124b9ba0 15f0381e694e6d0e47b2 3e43b5550b68868592c4 4e2154358a954e715be2 81c18ca56ca64541c82c abdba8d90058a14de682",
    "1f4c5c8000149b2e2be8": "1a48c54182e0a6ce5908 4285ce549e336ae01d80 73b2d8e9160a21070042 a1eee51704b0a301a746 af9690e590450aedd696 c724abf1000713890098 eb8a442880d089a13a09",
}
BACK = {ML: "b9a00000000000000001", CLOSING: "b9a00000000000000002"}
LOGO = "b6a00000000000000009"
COPY = ("be100000000000000008", "be100000000000000009", "be10000000000000000a")


def load(mode, page, vid):
    path = (ROOT / "powerbi" / mode / "FootballPlayerAnalysis" / "Report" /
            "definition" / "pages" / page / "visuals" / vid / "visual.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def lit(data):
    return data["expr"]["Literal"]["Value"].strip("'")


def overlaps(a, b):
    a, b = a["position"], b["position"]
    return (max(a["x"], b["x"]) < min(a["x"] + a["width"], b["x"] + b["width"])
            and max(a["y"], b["y"]) < min(a["y"] + a["height"], b["y"] + b["height"]))


class NavigationAndHeroTests(unittest.TestCase):
    def test_six_rails_have_full_descriptions_and_original_routes(self):
        for mode in ("workspace", "offline-demo"):
            for page, ids in PAGE_NAVS.items():
                targets = []
                for vid in ids.split():
                    with self.subTest(mode=mode, page=page, visual=vid):
                        node = load(mode, page, vid)
                        v = node["visual"]
                        self.assertEqual(v["visualType"], "actionButton")
                        props = v["visualContainerObjects"]["visualLink"][0]["properties"]
                        target = lit(props["navigationSection"])
                        self.assertEqual(lit(props["type"]), "PageNavigation")
                        self.assertIn(target, ROUTES)
                        self.assertEqual(
                            lit(v["visualContainerObjects"]["general"][0]["properties"]["altText"]),
                            f"Navigate to {ROUTES[target]} page",
                        )
                        targets.append(target)
                self.assertEqual(set(targets), set(ROUTES))
                self.assertEqual(len(targets), 7)

    def test_model_reliability_and_closing_have_native_home_links(self):
        for mode in ("workspace", "offline-demo"):
            for page, vid in BACK.items():
                with self.subTest(mode=mode, page=page):
                    node = load(mode, page, vid)
                    v = node["visual"]
                    self.assertEqual(v["visualType"], "actionButton")
                    self.assertEqual(
                        lit(v["visualContainerObjects"]["visualLink"][0]["properties"]["navigationSection"]),
                        HOME,
                    )
                    self.assertEqual(
                        lit(v["visualContainerObjects"]["general"][0]["properties"]["altText"]),
                        "Return to Football Intelligence Home",
                    )
                    self.assertGreater(node["position"]["width"], 100)

    def test_closing_brand_copy_cannot_cover_canonical_logo(self):
        for mode in ("workspace", "offline-demo"):
            image = load(mode, CLOSING, LOGO)
            self.assertEqual(image["visual"]["visualType"], "image")
            for vid in COPY:
                with self.subTest(mode=mode, visual=vid):
                    text = load(mode, CLOSING, vid)
                    self.assertEqual(text["visual"]["visualType"], "textbox")
                    self.assertFalse(overlaps(text, image),
                                     "Closing headline/logo should not occupy the same pixels")

    def test_reliability_home_button_clears_masthead_title_and_logo(self):
        for mode in ("workspace", "offline-demo"):
            back = load(mode, ML, BACK[ML])
            self.assertEqual(
                (back["position"]["x"], back["position"]["y"],
                 back["position"]["width"], back["position"]["height"]),
                (1040, 16, 119, 34),
                "Home control must not cover NEXUS logo or editorial masthead",
            )
            self.assertLessEqual(
                back["position"]["x"] + back["position"]["width"], 1280)
            for vid in ("0b669b19792b26683032", "d739c4fef0c04c55f4e3",
                        "b6a00000000000000008"):
                self.assertFalse(
                    overlaps(back, load(mode, ML, vid)),
                    f"Reliability Home control must clear header element {vid}",
                )


if __name__ == "__main__":
    unittest.main()
