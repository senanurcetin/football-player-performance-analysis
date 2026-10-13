"""Guard the published NEXUS canvas documentation against PBIR source drift.

Source-only: this is not a Power BI Desktop render or BigQuery refresh test.
"""
from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "BI_DESIGN_SYSTEM.md"
START = "<!-- CURRENT_PBIR_CANVASES_START -->"
END = "<!-- CURRENT_PBIR_CANVASES_END -->"
ROW = re.compile(
    r"\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*`(#[0-9A-Fa-f]{6})`\s*\|"
)
EDITIONS = ("workspace", "offline-demo")


def documented_pages(text: str) -> list[tuple[str, str, str, str]]:
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("Missing or duplicated current canvas contract markers")
    section = text.split(START, 1)[1].split(END, 1)[0]
    return [match.groups() for line in section.splitlines()
            if (match := ROW.fullmatch(line.strip()))]


def page_background(page: dict) -> str:
    return (
        page["objects"]["background"][0]["properties"]["color"]
        ["solid"]["color"]["expr"]["Literal"]["Value"]
        .strip("'").upper()
    )


class CanvasDocumentationContractTests(unittest.TestCase):
    def test_canonical_table_matches_both_editable_pbir_editions(self):
        rows = documented_pages(DOC.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 13)
        self.assertEqual(len({page_id for page_id, _, _, _ in rows}), 13)
        self.assertEqual(
            Counter(color for _, _, _, color in rows),
            {"#071829": 2, "#091E33": 9, "#E7F0FC": 1, "#E8ECFA": 1},
        )

        for edition in EDITIONS:
            pages = ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Report" / "definition" / "pages"
            self.assertEqual(
                {p.parent.name for p in pages.glob("*/page.json")},
                {page_id for page_id, _, _, _ in rows},
            )
            for page_id, display_name, _, documented_color in rows:
                with self.subTest(edition=edition, page_id=page_id):
                    page = json.loads(
                        (pages / page_id / "page.json").read_text(encoding="utf-8-sig")
                    )
                    expected_name = display_name
                    self.assertEqual(page["displayName"], expected_name)
                    self.assertEqual(page_background(page), documented_color)


if __name__ == "__main__":
    unittest.main()
