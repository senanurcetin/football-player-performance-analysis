"""Native Football PBIR transfer-outcome and commercial-valuation presentation guard.

Source-level checks only. Does not render Power BI Desktop or test BigQuery refresh.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSFER = "4c63ad904b1db6e0d156"
MARKET = "292e3d92e92693c05047"
VALUATION = "1f4c5c8000149b2e2be8"
CASES = {
    TRANSFER: {
        "a7e30000000000000001": ("clusteredBarChart", "Position", "Observed transfers",
                                   "fct_transfer_success_labels.position",
                                   "fct_transfer_success_labels.Transfers (365d)"),
        "a7e30000000000000002": ("clusteredColumnChart", "Position", "Average fee (€)",
                                   "fct_transfer_success_labels.position",
                                   "fct_transfer_success_labels.Average Transfer Fee (365d)"),
        "a7e30000000000000003": ("clusteredBarChart", "Position", "Observed success rate (%)",
                                   "fct_transfer_success_labels.position",
                                   "fct_transfer_success_labels.Transfer Success Rate (365d)"),
        "a7e30000000000000004": ("clusteredBarChart", "Follow-up status", "Transfers",
                                   "fct_transfer_fixed_horizon_outcomes.outcome_365d_status",
                                   "fct_transfer_fixed_horizon_outcomes.Transfers by Outcome Status (365d)"),
    },
    MARKET: {
        "0839d8ed3d7479a01f32": ("clusteredBarChart", "Position", "Fee premium / discount (%)",
                                    "fct_transfer_market_value_analysis.position",
                                    "fct_transfer_market_value_analysis.Average Fee Premium Discount %"),
        "5bbe3e0865c55bbeade1": ("clusteredColumnChart", "Transfer season", "Average known fee (€m)",
                                    "fct_transfer_market_value_analysis.transfer_season",
                                    "fct_transfer_market_value_analysis.Average Known Transfer Fee"),
    },
    VALUATION: {
        "4d304949cba7dd247021": ("clusteredBarChart", "Position", "Predicted upside (%)",
                                    "ml_player_market_value_current_predictions.position_tr",
                                    "ml_player_market_value_current_predictions.Average Prediction Upside %"),
        "8b67c00a69b995fd3db6": ("clusteredBarChart", "Position", "Predicted value (€m)",
                                    "ml_player_market_value_current_predictions.position_tr",
                                    "ml_player_market_value_current_predictions.Average Predicted Market Value"),
    },
}
DONUT_ALIASES = {
    (MARKET, "1c4d73ece1a64f57c0fc"): ("Value direction", "Transfers"),
    (VALUATION, "3ccd5a45594119af9bb7"): ("Prediction quality", "Players"),
}


def load(edition, page, id):
    file = (ROOT / "powerbi" / edition / "FootballPlayerAnalysis" /
            "Report" / "definition" / "pages" / page / "visuals" / id / "visual.json")
    return json.loads(file.read_text(encoding="utf-8-sig"))


def literal(node):
    return node["expr"]["Literal"]["Value"].strip("'")


class EditorialSourceContract(unittest.TestCase):
    def test_eight_comparable_charts_are_native_and_unit_labeled(self):
        for page, charts in CASES.items():
            for id, (kind, cat, y, source_cat, source_measure) in charts.items():
                with self.subTest(page=page, id=id):
                    prod, demo = (load(mode, page, id) for mode in ("workspace", "offline-demo"))
                    self.assertEqual(prod, demo)
                    v = prod["visual"]
                    self.assertEqual(v["visualType"], kind)
                    self.assertEqual(v["query"]["queryState"]["Category"]["projections"][0]["queryRef"],
                                     source_cat)
                    self.assertEqual(v["query"]["queryState"]["Y"]["projections"][0]["queryRef"],
                                     source_measure)
                    self.assertEqual(v["query"]["queryState"]["Category"]["projections"][0]["displayName"],
                                     cat)
                    for axis, expected in (("categoryAxis", cat), ("valueAxis", y)):
                        props = v["objects"][axis][0]["properties"]
                        self.assertEqual(literal(props["showAxisTitle"]), "true")
                        self.assertEqual(literal(props["titleText"]), expected)
                        self.assertEqual(literal(props["titleFontSize"]),
                                         "10D" if page == TRANSFER else "11D")
                    self.assertEqual(v["visualContainerObjects"]["background"][0]["properties"]
                                     ["show"]["expr"]["Literal"]["Value"], "true")

    def test_two_compositional_donuts_keep_queries_and_explain_categories(self):
        for (page, id), (category, metric) in DONUT_ALIASES.items():
            with self.subTest(page=page, id=id):
                prod, demo = (load(mode, page, id) for mode in ("workspace", "offline-demo"))
                self.assertEqual(prod, demo)
                v = prod["visual"]
                self.assertEqual(v["visualType"], "donutChart")
                self.assertEqual(v["query"]["queryState"]["Category"]["projections"][0]["displayName"],
                                 category)
                self.assertEqual(v["query"]["queryState"]["Y"]["projections"][0]["displayName"],
                                 metric)

    def test_followup_does_not_equate_missing_with_failure(self):
        v = load("workspace", TRANSFER, "a7e30000000000000004")["visual"]
        alt = literal(v["visualContainerObjects"]["general"][0]["properties"]["altText"]).lower()
        self.assertIn("missing follow-up", alt)
        self.assertIn("not counted as failed", alt)
        self.assertIn("365-day", alt)

    def test_success_and_upside_measures_are_percent_formatted(self):
        cases = (
            ("fct_transfer_success_labels", "Transfer Success Rate (365d)"),
            ("fct_transfer_market_value_analysis", "Average Fee Premium Discount %"),
            ("ml_player_market_value_current_predictions", "Average Prediction Upside %"),
        )
        for mode in ("workspace", "offline-demo"):
            for table, name in cases:
                with self.subTest(mode=mode, table=table, name=name):
                    path = (ROOT / "powerbi" / mode / "FootballPlayerAnalysis" /
                            "Model" / "definition" / "tables" / (table + ".tmdl"))
                    txt = path.read_text(encoding="utf-8-sig")
                    measure = txt.split("measure '" + name + "'", 1)[1].split(
                        "\n\tmeasure ", 1)[0].split("\n\tcolumn ", 1)[0]
                    self.assertIn("formatString: 0.0%", measure)


if __name__ == "__main__":
    unittest.main()
