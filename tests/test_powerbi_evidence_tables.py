"""Screenshot-oriented table layout and labeling checks for native Football PBIR.

Source tests, not Power BI Desktop rendering acceptance.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET = "292e3d92e92693c05047"
VALUATION = "1f4c5c8000149b2e2be8"
TABLES = {
    MARKET: {
        "id": "9c728e8d682165354da4",
        "title": "Transfer transaction details",
        "labels": {
            "fct_transfer_market_value_analysis.transfer_fee": "Fee (€)",
            "fct_transfer_market_value_analysis.market_value_baseline": "Baseline (€)",
            "fct_transfer_market_value_analysis.fee_market_value_difference_pct": "Fee delta (%)",
            "fct_transfer_market_value_analysis.yon_etiketi_tr": "Fee/value direction",
        },
    },
    VALUATION: {
        "id": "be92253a5130bdec9028",
        "title": "Player valuation estimates",
        "labels": {
            "ml_player_market_value_current_predictions.position": "Position",
            "ml_player_market_value_current_predictions.previous_market_value_eur": "Prior (€)",
            "ml_player_market_value_current_predictions.predicted_market_value_eur": "Predicted (€)",
            "ml_player_market_value_current_predictions.prediction_delta_vs_previous_pct": "Change (%)",
            "ml_player_market_value_current_predictions.prediction_lower_eur": "Lower (€)",
            "ml_player_market_value_current_predictions.prediction_upper_eur": "Upper (€)",
        },
    },
}


def visual(edition, page, id):
    path = (ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / page / "visuals" / id / "visual.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rect(v):
    p = v["position"]
    return p["x"], p["y"], p["width"], p["height"]


class EditorialTableTests(unittest.TestCase):
    def test_table_sources_preserved_and_business_headers_short(self):
        for page, spec in TABLES.items():
            production = visual("workspace", page, spec["id"])
            synthetic = visual("offline-demo", page, spec["id"])
            with self.subTest(page=page):
                self.assertEqual(production, synthetic)
                v = production["visual"]
                self.assertEqual(v["visualType"], "tableEx")
                self.assertEqual(v["visualContainerObjects"]["title"][0]["properties"]
                                 ["text"]["expr"]["Literal"]["Value"], "'" + spec["title"] + "'")
                fields = v["query"]["queryState"]["Values"]["projections"]
                actual = {x["queryRef"]: x["displayName"] for x in fields}
                for source, label in spec["labels"].items():
                    self.assertEqual(actual[source], label)
                self.assertTrue(v["visualContainerObjects"]["general"][0]["properties"]
                                ["altText"]["expr"]["Literal"]["Value"])

    def test_market_table_uses_wide_empty_region_without_overlapping_donut(self):
        for edition in ("workspace", "offline-demo"):
            table = visual(edition, MARKET, TABLES[MARKET]["id"])
            donut = visual(edition, MARKET, "1c4d73ece1a64f57c0fc")
            footer = visual(edition, MARKET, "b8a00000000000000005")
            tx, ty, tw, th = rect(table)
            dx, dy, dw, dh = rect(donut)
            self.assertEqual((tx, ty, tw, th), (355, 470, 615, 201))
            self.assertGreaterEqual(tx - (dx + dw), 12)
            self.assertLessEqual(tx + tw, 975)
            self.assertLessEqual(max(ty + th, dy + dh), footer["position"]["y"] - 4)

    def test_transfer_count_chart_is_visible_beside_the_market_evidence_table(self):
        """A hidden legacy chart was covering the table and entering the footer."""
        chart_id = "13ccac612fab8060cf67"
        production = visual("workspace", MARKET, chart_id)
        synthetic = visual("offline-demo", MARKET, chart_id)
        self.assertEqual(production, synthetic)
        for mode in ("workspace", "offline-demo"):
            chart = visual(mode, MARKET, chart_id)
            table = visual(mode, MARKET, TABLES[MARKET]["id"])
            donut = visual(mode, MARKET, "1c4d73ece1a64f57c0fc")
            heading = visual(mode, MARKET, "4a534f1eb6b015ddfe63")
            footer = visual(mode, MARKET, "b8a00000000000000005")
            with self.subTest(mode=mode):
                self.assertEqual(chart["visual"]["visualType"], "clusteredColumnChart")
                self.assertEqual(rect(chart), (985, 470, 248, 201))
                cx, cy, cw, ch = rect(chart)
                tx, ty, tw, th = rect(table)
                dx, dy, dw, dh = rect(donut)
                self.assertGreaterEqual(cx - (tx + tw), 12)
                self.assertGreaterEqual(cx - (dx + dw), 12)
                self.assertLessEqual(cx + cw, 1280)
                self.assertLessEqual(cy + ch, footer["position"]["y"] - 8)
                # A former 256px findings textbox at x985/y436 overlapped the
                # native chart and gave synthetic data ungrounded business claims.
                self.assertEqual(heading["visual"]["visualType"], "textbox")
                self.assertEqual(rect(heading), (985, 436, 270, 24))
                hx, hy, hw, hh = rect(heading)
                self.assertLessEqual(hy + hh, cy - 8)
                paragraphs = heading["visual"]["objects"]["general"][0]["properties"]["paragraphs"]
                self.assertEqual(len(paragraphs), 1)
                self.assertEqual(
                    paragraphs[0]["textRuns"][0]["value"],
                    "TRANSFERS BY POSITION",
                )
                header_bg = heading["visual"]["visualContainerObjects"]["background"][0]["properties"]
                self.assertEqual(
                    header_bg["color"]["solid"]["color"]["expr"]["Literal"]["Value"],
                    "'#173451'",
                )
                v = chart["visual"]
                self.assertEqual(
                    v["visualContainerObjects"]["title"][0]["properties"]
                    ["text"]["expr"]["Literal"]["Value"],
                    "'Transfers by Position'",
                )
                self.assertEqual(
                    v["visualContainerObjects"]["title"][0]["properties"]
                    ["fontSize"]["expr"]["Literal"]["Value"], "13D")
                state = v["query"]["queryState"]
                self.assertEqual(
                    state["Y"]["projections"][0]["queryRef"],
                    "fct_transfer_market_value_analysis.Transfer Count")
                self.assertEqual(
                    state["Category"]["projections"][0]["queryRef"],
                    "fct_transfer_market_value_analysis.position")

    def test_valuation_bottom_visuals_clear_navigation(self):
        for edition in ("workspace", "offline-demo"):
            table = visual(edition, VALUATION, TABLES[VALUATION]["id"])
            chart = visual(edition, VALUATION, "4d304949cba7dd247021")
            footer = visual(edition, VALUATION, "b8a00000000000000006")
            self.assertAlmostEqual(table["position"]["y"] + table["position"]["height"], 671)
            self.assertAlmostEqual(chart["position"]["y"] + chart["position"]["height"], 671)
            for node in (table, chart):
                self.assertLessEqual(node["position"]["y"] + node["position"]["height"],
                                     footer["position"]["y"] - 4)


if __name__ == "__main__":
    unittest.main()
