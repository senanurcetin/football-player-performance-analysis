"""Offline geometry auditor regression tests; independent of Desktop and CI."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_powerbi_layout import audit_report, overlap_fraction, rectangle


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class PBIRLayoutAuditTests(unittest.TestCase):
    def test_rectangles_and_exact_touch_are_not_overlaps(self):
        self.assertIsNone(rectangle({"x": 0, "y": 0, "width": -1, "height": 5}))
        self.assertIsNone(rectangle({"x": 0, "y": 0, "width": float("nan"), "height": 5}))
        self.assertEqual(overlap_fraction((0, 0, 50, 50), (50, 0, 50, 50)), 0)
        self.assertEqual(overlap_fraction((0, 0, 50, 50), (25, 0, 50, 50)), 0.5)

    def test_report_flags_data_overlap_but_ignores_decorative_background(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "powerbi" / "workspace" / "FootballPlayerAnalysis" / "Report" / "definition" / "pages" / "page-1"
            write_json(root / "page.json", {"name": "page-1", "displayName": "Analysis", "width": 100, "height": 100})
            fixtures = {
                "chart-a": ({"x": 0, "y": 0, "width": 60, "height": 60}, {"Y": {"projections": [1]}}),
                "chart-b": ({"x": 30, "y": 0, "width": 60, "height": 60}, {"Y": {"projections": [1]}}),
                "background": ({"x": 0, "y": 0, "width": 100, "height": 100}, {}),
                "outside": ({"x": 91, "y": 60, "width": 20, "height": 20}, {}),
            }
            for name, (position, query) in fixtures.items():
                write_json(root / "visuals" / name / "visual.json",
                           {"name": name, "position": position,
                            "visual": {"visualType": "shape" if not query else "barChart",
                                       "query": {"queryState": query}}})
            result = audit_report(Path(folder), "workspace", 0.15)
            page = result["pages"][0]
            warnings = page["warnings"]
            self.assertEqual(result["page_count"], 1)
            self.assertEqual(page["data_visuals"], 2)
            self.assertEqual(len([w for w in warnings if w["type"] == "data_visual_overlap"]), 1)
            self.assertEqual(len([w for w in warnings if w["type"] == "out_of_bounds"]), 1)
            self.assertEqual(result["warning_count"], 2)

    def test_empty_project_returns_clear_error(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                audit_report(Path(folder), "offline-demo")


if __name__ == "__main__":
    unittest.main()
