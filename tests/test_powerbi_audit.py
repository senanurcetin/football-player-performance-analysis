"""Offline PBIR page-registry contract tests using synthetic report definitions.

No BigQuery connection or Power BI Desktop is required. The fixtures verify
what this structural audit can prove, not whether visuals render correctly.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_powerbi_visuals import audit


class PbirRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.base = self.root / "powerbi" / "workspace" / "FootballPlayerAnalysis"
        self.pages = self.base / "Report" / "definition" / "pages"
        self.pages.mkdir(parents=True)
        (self.base / "Model" / "definition" / "tables").mkdir(parents=True)
        self.write_page("home")
        self.write_registry(["home"], "home")

    def write_json(self, path: Path, value: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_page(self, name: str):
        self.write_json(
            self.pages / name / "page.json",
            {"name": name, "displayName": "Home", "width": 1280, "height": 720},
        )

    def write_registry(self, ordered: list[str], active: str | None):
        self.write_json(
            self.pages / "pages.json",
            {"pageOrder": ordered, "activePageName": active},
        )

    def errors(self):
        return audit(self.root, "workspace")["errors"]

    def test_complete_page_registry_is_valid(self):
        self.assertEqual(self.errors(), [])

    def test_missing_active_page_is_a_failure(self):
        self.write_registry(["home"], "not-a-page")
        self.assertTrue(any("Active PBIR page" in e for e in self.errors()))

    def test_empty_registry_does_not_crash_and_is_a_failure(self):
        self.write_registry([], None)
        errs = self.errors()
        self.assertTrue(any("pageOrder is empty" in e for e in errs))
        self.assertTrue(any("omitted from pageOrder" in e for e in errs))

    def test_duplicate_registered_page_ids_are_rejected(self):
        self.write_registry(["home", "home"], "home")
        self.assertTrue(any("Duplicate page identifiers" in e for e in self.errors()))

    def test_unregistered_hidden_page_directory_is_a_failure(self):
        self.write_page("hidden-detail")
        self.assertTrue(any("omitted from pageOrder: hidden-detail" in e for e in self.errors()))

    def test_nonexistent_registered_page_is_a_failure(self):
        self.write_registry(["home", "missing-page"], "home")
        self.assertTrue(any("pageOrder references absent page missing-page" in e for e in self.errors()))

    def test_data_visual_without_query_is_reported(self):
        self.write_json(
            self.pages / "home" / "visuals" / "broken-chart" / "visual.json",
            {"name": "broken-chart", "visual": {"visualType": "barChart"}},
        )
        self.assertTrue(any("data visual has no queryState" in e for e in self.errors()))


if __name__ == "__main__":
    unittest.main()
