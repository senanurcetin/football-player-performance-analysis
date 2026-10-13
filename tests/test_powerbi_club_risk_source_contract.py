"""Club-risk Power BI schema contract: source only, never a live refresh."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = "fct_club_risk_profile"
SPEC = {
    "club_id": "int64",
    "club_name": "string",
    "total_incoming_transfers": "int64",
    "transfers_with_known_fee": "int64",
    "known_fee_coverage_pct": "double",
    "observed_365d_transfers": "int64",
    "outcome_365d_coverage_pct": "double",
    "avg_overpay_pct": "double",
    "successful_transfers": "int64",
    "unsuccessful_transfers": "int64",
    "transfer_success_rate_pct": "double",
    "meets_minimum_sample_size": "boolean",
    "transfer_risk_category": "string",
}
M_TYPES = {"int64": "Int64.Type", "double": "number", "boolean": "logical",
           "string": "text"}


def source(mode):
    path = (ROOT / "powerbi" / mode / "FootballPlayerAnalysis" /
            "Model" / "definition" / "tables" / (TABLE + ".tmdl"))
    return path.read_text(encoding="utf-8-sig")


def schema(text):
    out = {}
    for block in text.split("\n\tcolumn ")[1:]:
        name = block.splitlines()[0].strip()
        typ = re.search(r"^\s*dataType: (\w+)", block, flags=re.M)
        src = re.search(r"^\s*sourceColumn: (\S+)", block, flags=re.M)
        out[name] = (typ.group(1) if typ else None, src.group(1) if src else None)
    return out


class ClubRiskSourceContract(unittest.TestCase):
    def test_native_model_types_are_explicit_and_identical(self):
        for mode in ("workspace", "offline-demo"):
            with self.subTest(mode=mode):
                actual = schema(source(mode))
                self.assertEqual(set(actual), set(SPEC))
                for name, data_type in SPEC.items():
                    self.assertEqual(actual[name], (data_type, name))

    def test_production_partition_is_the_bigquery_mart_not_synthetic(self):
        model = source("workspace")
        self.assertIn("GoogleBigQuery.Database([UseStorageApi=false])", model)
        self.assertIn('Name="football_mart",Kind="Schema"', model)
        self.assertIn('Name="fct_club_risk_profile",Kind="Table"', model)
        self.assertNotIn("#table(", model)

    def test_demo_fixture_is_local_typed_and_distinct(self):
        demo = source("offline-demo")
        self.assertIn("#table(", demo)
        self.assertNotIn("GoogleBigQuery.Database", demo)
        for name, data_type in SPEC.items():
            self.assertIn(f'#"{name}" = {M_TYPES[data_type]}', demo)
        rows = re.findall(r'^\s*\{\d+, "Demo [^"]+".*\},?\s*$', demo, flags=re.M)
        self.assertEqual(len(rows), 6)
        self.assertFalse(any(re.search(r',\s*"\d+\.\d+"', row) for row in rows))
        for row in rows:
            self.assertRegex(row, r',\s*false,\s*"insufficient_data"\}')

    def test_dbt_source_references_all_expected_columns(self):
        sql = (ROOT / "models" / "marts" / (TABLE + ".sql")).read_text(
            encoding="utf-8-sig")
        for name in SPEC:
            with self.subTest(column=name):
                self.assertRegex(sql, r"\b" + re.escape(name) + r"\b")
        self.assertIn("safe_divide", sql.lower())
        self.assertIn("observed_365d_transfers >= 30", sql)


if __name__ == "__main__":
    unittest.main()
