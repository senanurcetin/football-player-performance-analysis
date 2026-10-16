"""NEXUS v3 theme source checks; not a Power BI Desktop render test."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = [
    ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Report"
    for edition in ("workspace", "offline-demo")
]
THEME = "NEXUSMidnight-20261016-v3.json"
INK = "#ECF4FF"
SURFACE = "#10283F"
BORDER = "#294761"
PALETTE = ("#4EA8FF", "#8F9BFF", "#00E0FF", "#6E55C6")


def rgb(color: str) -> tuple[float, float, float]:
    return tuple(int(color[i : i + 2], 16) / 255 for i in (1, 3, 5))


def luminance(color: str) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(component) for component in rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    lighter, darker = sorted((luminance(a), luminance(b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class NexusMidnightV3Tests(unittest.TestCase):
    def test_production_and_fixture_share_exact_theme(self) -> None:
        payloads = [
            json.loads((report / "StaticResources" / "RegisteredResources" / THEME).read_text())
            for report in REPORTS
        ]
        self.assertEqual(payloads[0], payloads[1])
        self.assertEqual(payloads[0]["name"], THEME)
        self.assertEqual(tuple(payloads[0]["dataColors"][:4]), PALETTE)

    def test_report_manifests_use_v3_without_touching_partitions(self) -> None:
        for report in REPORTS:
            with self.subTest(report=report):
                manifest = json.loads((report / "definition" / "report.json").read_text())
                self.assertEqual(manifest["themeCollection"]["customTheme"]["name"], THEME)
                package = next(x for x in manifest["resourcePackages"] if x["name"] == "RegisteredResources")
                self.assertIn(
                    {"name": THEME, "path": THEME, "type": "CustomTheme"},
                    package["items"],
                )

    def test_fallback_chart_surfaces_are_dark_and_readable(self) -> None:
        for report in REPORTS:
            theme = json.loads((report / "StaticResources" / "RegisteredResources" / THEME).read_text())
            self.assertEqual(theme["foreground"], INK)
            self.assertEqual(theme["background"], "#091E33")
            self.assertGreaterEqual(contrast(INK, SURFACE), 7.0)
            self.assertGreaterEqual(contrast("#B9D1E8", SURFACE), 7.0)
            for visual_type, selectors in theme["visualStyles"].items():
                with self.subTest(report=report, visual_type=visual_type):
                    props = selectors["*"]
                    self.assertEqual(props["background"][0]["color"]["solid"]["color"], SURFACE)
                    self.assertEqual(props["border"][0]["color"]["solid"]["color"], BORDER)
                    self.assertEqual(props["title"][0]["fontColor"]["solid"]["color"], INK)


if __name__ == "__main__":
    unittest.main()
