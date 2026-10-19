"""Offline source-contract guard for the two non-equivalent 365-day populations.

Reads native production PBIR/TMDL, the dbt label mart and the read-only audit
SQL only. It does not initialize Power BI, credentials, dbt or BigQuery.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "powerbi/workspace/FootballPlayerAnalysis/Model/definition/tables"
PAGE = (
    ROOT / "powerbi/workspace/FootballPlayerAnalysis/Report/definition/pages"
    / "4c63ad904b1db6e0d156/visuals"
)


def measure_source(tmdl: str, name: str) -> str:
    """Isolate one native measure without inspecting unrelated measures."""
    pattern = rf"\tmeasure '{re.escape(name)}' =\s*(.*?)(?=\n\tmeasure |\n\tcolumn |\Z)"
    result = re.search(pattern, tmdl, flags=re.S)
    if result is None:
        raise AssertionError(f"Missing native DAX measure: {name}")
    return result.group(1)


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


class Transfer365dSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmdl = (MODEL / "fct_transfer_fixed_horizon_outcomes.tmdl").read_text(
            encoding="utf-8-sig"
        )
        cls.label_sql = (
            ROOT / "models/marts/fct_transfer_success_labels.sql"
        ).read_text(encoding="utf-8-sig")
        cls.audit_sql = (
            ROOT / "analyses/audit_transfer_365d_capture_20261018.sql"
        ).read_text(encoding="utf-8-sig")

    def test_native_eligible_denominator_uses_maturity_cutoff(self) -> None:
        dax = normalized(measure_source(self.tmdl, "Eligible Transfers (365d)"))
        self.assertIn("distinctcount(fct_transfer_fixed_horizon_outcomes[transfer_key])", dax)
        self.assertIn("today()", dax)
        self.assertIn("max(fct_transfer_fixed_horizon_outcomes[source_latest_valuation_date])", dax)
        self.assertIn("target_365d_date]+30<=sourcecutoff", dax)
        self.assertNotIn("has_365d_outcome]=true()", dax)

    def test_native_observed_numerator_requires_matured_outcome(self) -> None:
        dax = normalized(measure_source(self.tmdl, "Observed Transfers (365d)"))
        self.assertIn("distinctcount(fct_transfer_fixed_horizon_outcomes[transfer_key])", dax)
        self.assertIn("today()", dax)
        self.assertIn("max(fct_transfer_fixed_horizon_outcomes[source_latest_valuation_date])", dax)
        self.assertIn("target_365d_date]+30<=sourcecutoff", dax)
        self.assertIn("has_365d_outcome]=true()", dax)

    def test_native_coverage_uses_the_matched_numerator_and_denominator(self) -> None:
        dax = normalized(measure_source(self.tmdl, "Outcome Coverage (365d)"))
        self.assertIn("[observedtransfers(365d)]", dax)
        self.assertIn("[eligibletransfers(365d)]", dax)

    def test_dbts_success_labels_are_not_maturity_filtered(self) -> None:
        sql = normalized(self.label_sql)
        self.assertIn("whereoutcomes.has_365d_outcome", sql)
        self.assertNotIn("source_latest_valuation_date", sql)
        self.assertNotIn("target_365d_date", sql)

    def test_captured_page_cards_bind_to_native_matured_dax_measures(self) -> None:
        expected = {
            "a7e40000000000000001": "Eligible Transfers (365d)",
            "a7e40000000000000002": "Observed Transfers (365d)",
            "a7e40000000000000003": "Outcome Coverage (365d)",
        }
        for visual_id, measure in expected.items():
            with self.subTest(visual_id=visual_id):
                source = json.loads(
                    (PAGE / visual_id / "visual.json").read_text(encoding="utf-8-sig")
                )
                content = json.dumps(source, ensure_ascii=False)
                self.assertIn(
                    f"fct_transfer_fixed_horizon_outcomes.{measure}",
                    content,
                )

    def test_readonly_sql_matches_dax_maturity_filter_and_distinct_grain(self) -> None:
        sql = normalized(self.audit_sql)
        self.assertIn("pbi_capture_as_of_date", sql)
        self.assertIn('date_add(h.target_365d_date,interval30day)', sql)
        self.assertIn("<=c.effective_cutoff_date", sql)
        self.assertIn("least(", sql)
        self.assertIn("max(source_latest_valuation_date)", sql)
        self.assertIn("count(distinctif(", sql)
        without_comments = re.sub(r"--[^\n]*", "", self.audit_sql).lower()
        self.assertNotRegex(
            without_comments,
            r"\b(?:create|drop|alter|truncate|insert\s+into|update|delete\s+from|merge\s+into)\b",
        )


if __name__ == "__main__":
    unittest.main()
