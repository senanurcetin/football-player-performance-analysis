"""NEXUS 2.0 executive report theme and portfolio-production source contract.

Offline checks are not evidence of Power BI Desktop rendering or BigQuery refresh.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = ("workspace", "offline-demo")
THEME = Path(
    "FootballPlayerAnalysis/Report/StaticResources/"
    "RegisteredResources/NEXUSMidnight-20261012-v2.json"
)
EXPECTED_SERIES = [
    "#4EA8FF",
    "#00E0FF",
    "#8F9BFF",
    "#6E55C6",
    "#76B8FF",
    "#B9C5CE",
    "#376DBE",
    "#B3A4F6",
]


class NexusPortfolioIdentityContract(unittest.TestCase):
    def test_both_editions_share_approved_executive_theme(self):
        themes = []
        for edition in EDITIONS:
            path = ROOT / "powerbi" / edition / THEME
            theme = json.loads(path.read_text(encoding="utf-8-sig"))
            self.assertEqual(theme["dataColors"], EXPECTED_SERIES)
            self.assertEqual(theme["tableAccent"], "#4EA8FF")
            self.assertEqual(theme["backgroundLight"], "#F4F8FD")
            for kind, definition in theme["visualStyles"].items():
                with self.subTest(edition=edition, visual=kind):
                    config = definition["*"]
                    border = config.get("border", [])
                    for rule in border:
                        color = rule.get("color", {}).get("solid", {}).get("color")
                        if color is not None:
                            self.assertEqual(color, "#DCE8F5")
                        if "radius" in rule:
                            self.assertEqual(rule["radius"], 10)
            themes.append(theme)
        self.assertEqual(themes[0], themes[1])

    def test_production_keeps_registered_official_nexus_logo(self):
        path = (
            ROOT
            / "powerbi/workspace/FootballPlayerAnalysis/"
            "Report/definition/report.json"
        )
        report = json.loads(path.read_text(encoding="utf-8-sig"))
        items = report["resourcePackages"][0]["items"]
        self.assertTrue(
            any(
                item["name"] == "NEXUS_Official_Transparent_Logo.png"
                and item["type"] == "Image"
                for item in items
            )
        )

    def test_production_page_names_are_not_fixture_labeled(self):
        pages = (
            ROOT / "powerbi/workspace/FootballPlayerAnalysis/"
            "Report/definition/pages"
        )
        labels = []
        for path in pages.glob("*/page.json"):
            page = json.loads(path.read_text(encoding="utf-8-sig"))
            labels.append(page["displayName"])
            self.assertFalse(page["displayName"].startswith("[DEMO]"))
        self.assertEqual(len(labels), 13)


if __name__ == "__main__":
    unittest.main()
