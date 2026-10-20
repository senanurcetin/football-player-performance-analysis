"""Fail-closed synthetic tests for transfer-key SQL and CSV evidence."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_transfer_365d_reconciliation import audit_export

HEADERS=["transfer_key","capture_date","effective_cutoff_date","horizon_rows",
         "label_rows","dax_observed","in_success_labels","discrepancy_reason"]
BASE={"capture_date":"2026-10-17","effective_cutoff_date":"2026-09-30",
      "horizon_rows":"1","label_rows":"1","dax_observed":"false",
      "in_success_labels":"true","discrepancy_reason":"label_before_maturity_cutoff"}

class Transfer365dKeyReconciliationTests(unittest.TestCase):
    def csv(self,d,rows):
        p=Path(d)/"discrepancies.csv"
        with p.open("w",newline="",encoding="utf8") as f:
            w=csv.DictWriter(f,fieldnames=HEADERS)
            w.writeheader()
            w.writerows(rows)
        return p
    def test_synthetic_three_illustrative_keys(self):
        with tempfile.TemporaryDirectory() as d:
            records=[dict(BASE,transfer_key=x) for x in ["mock1","mock2","mock3"]]
            result=audit_export(self.csv(d,records),"2026-10-17")
            self.assertEqual(result["discordant_or_duplicate_keys"],3)
            self.assertEqual(result["classification_counts"]["label_before_maturity_cutoff"],3)
            self.assertEqual(result["status"],"validated_export_only")
            self.assertIn("Not BigQuery",result["note"])
    def test_empty_csv_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"Empty export"):
                audit_export(self.csv(d,[]),"2026-10-17")
    def test_duplicate_transfer_keys_fail(self):
        with tempfile.TemporaryDirectory() as d:
            row=dict(BASE,transfer_key="mock")
            with self.assertRaisesRegex(ValueError,"Duplicate transfer_key"):
                audit_export(self.csv(d,[row,row]),"2026-10-17")
    def test_capture_date_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as d:
            row=dict(BASE,transfer_key="mock",capture_date="2026-10-18")
            with self.assertRaisesRegex(ValueError,"capture_date"):
                audit_export(self.csv(d,[row]),"2026-10-17")
    def test_label_flag_must_agree_with_counts(self):
        with tempfile.TemporaryDirectory() as d:
            row=dict(BASE,transfer_key="mock",in_success_labels="false")
            with self.assertRaisesRegex(ValueError,"label flag"):
                audit_export(self.csv(d,[row]),"2026-10-17")
    def test_wrong_maturity_reason_fails(self):
        with tempfile.TemporaryDirectory() as d:
            row=dict(BASE,transfer_key="mock",dax_observed="true")
            with self.assertRaisesRegex(ValueError,"maturity classification"):
                audit_export(self.csv(d,[row]),"2026-10-17")
    def test_cutoff_cannot_follow_capture(self):
        with tempfile.TemporaryDirectory() as d:
            row=dict(BASE,transfer_key="mock",effective_cutoff_date="2026-10-18")
            with self.assertRaisesRegex(ValueError,"after capture"):
                audit_export(self.csv(d,[row]),"2026-10-17")

    def test_valid_flags_cannot_claim_spurious_difference(self):
        with tempfile.TemporaryDirectory() as d:
            row=dict(BASE,transfer_key="mock",label_rows="0",
                     in_success_labels="false",discrepancy_reason="unexpected_inconsistency")
            with self.assertRaisesRegex(ValueError,"Spurious discrepancy"):
                audit_export(self.csv(d,[row]),"2026-10-17")

    def test_query_uses_read_only_source_and_key_grain(self):
        sql=(ROOT/"analyses/audit_transfer_365d_row_level_20261020.sql").read_text("utf8").lower()
        for target in ("ref('fct_transfer_fixed_horizon_outcomes')",
                       "ref('fct_transfer_success_labels')",
                       "full outer join","effective_cutoff_date",
                       "date_add(h.target_365d_date, interval 30 day)",
                       "label_before_maturity_cutoff",
                       "order by discrepancy_reason, transfer_key"):
            with self.subTest(target=target): self.assertIn(target,sql)
        for forbidden in ("create or replace table ","delete from ","insert into "):
            self.assertNotIn(forbidden,sql)

if __name__=="__main__":
    unittest.main()
