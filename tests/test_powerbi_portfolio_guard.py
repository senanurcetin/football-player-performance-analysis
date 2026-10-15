"""Production-only portfolio guard: English labels, brand and BigQuery sources."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from check_powerbi_portfolio import check

class PowerBIPortfolioGuardTests(unittest.TestCase):
    def test_english_production_brand_and_bigquery_integrity(self):
        r=check()
        self.assertEqual(r["status"],"PASS","; ".join(r["errors"]))
        self.assertEqual(r["pages"],13)
        self.assertGreaterEqual(r["visuals"],300)
        self.assertGreaterEqual(r["bigquery_source_tables"],30)

if __name__=="__main__":
    unittest.main()
