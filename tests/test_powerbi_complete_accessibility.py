"""Accessibility contract for all native NEXUS Power BI query-bound visuals.

Static PBIR validation, not proof that Power BI Desktop screen readers work.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "powerbi"
TOOL_PATH = ROOT / "scripts" / "backfill_powerbi_accessibility.py"
SPEC = importlib.util.spec_from_file_location("powerbi_a11y_tool", TOOL_PATH)
assert SPEC and SPEC.loader
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


class AllNativeDataVisualA11yTests(unittest.TestCase):
    def test_all_query_bound_visuals_have_sensible_accessible_descriptions(self):
        shared = {}
        for edition in ("workspace", "offline-demo"):
            root = PKG / edition / "FootballPlayerAnalysis" / "Report" / "definition" / "pages"
            count = 0
            descriptions = {}
            for path in sorted(root.glob("*/visuals/*/visual.json")):
                node = json.loads(path.read_text(encoding="utf-8-sig"))
                if not node.get("visual", {}).get("query", {}).get("queryState"):
                    continue
                count += 1
                props = node["visual"]["visualContainerObjects"]["general"][0]["properties"]
                item = props["altText"]["expr"]["Literal"]["Value"]
                alt = item.strip("'")
                with self.subTest(edition=edition, visual=node["name"]):
                    self.assertGreaterEqual(len(alt), 20)
                    self.assertLessEqual(len(alt), 250)
                    self.assertEqual(alt, alt.strip())
                    self.assertNotIn("SYNTHETIC DEMO", alt)
                    self.assertNotIn("2026-06-21", alt)
                    self.assertEqual(node["name"], path.parent.name)
                    self.assertEqual(len(node.get("position", {})) >= 4, True)
                descriptions[(path.parents[2].name, path.parent.name)] = alt
            self.assertEqual(count, 89)
            shared[edition] = descriptions
        self.assertEqual(shared["workspace"], shared["offline-demo"])

    def test_accessibility_backfill_is_idempotent(self):
        outcome = TOOL.audit(ROOT, apply=False)
        for edition in ("workspace", "offline-demo"):
            self.assertEqual(outcome[edition]["data_visuals"], 89)
            self.assertEqual(outcome[edition]["missing_before"], 0)
            self.assertEqual(outcome[edition]["modified"], 0)

    def test_accessibility_labels_do_not_introduce_fabricated_numbers(self):
        example = {
            "visual": {
                "visualType": "card",
                "query": {"queryState": {"Values": {"projections": [{
                    "field": {"Measure": {"Property": "Total Goals"}}
                }]}}},
            }
        }
        self.assertEqual(
            TOOL.accessible_description(example),
            "Key performance indicator: Total Goals. Calculated from the current report filter context.",
        )
        self.assertTrue(TOOL.update_visual(example))
        self.assertFalse(TOOL.update_visual(example), "Must not overwrite a human-authored altText")
        self.assertEqual(example["visual"]["visualType"], "card")


if __name__ == "__main__":
    unittest.main()
