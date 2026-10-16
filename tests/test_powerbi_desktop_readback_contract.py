"""Guard the owner-controlled, read-only Power BI Desktop DAX importer probe.

No Desktop or credentials are required to run this source regression.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_powerbi_desktop_import.ps1"

class DesktopReadbackSourceContract(unittest.TestCase):
    def test_probe_is_checked_in_and_read_only(self):
        source = SCRIPT.read_text(encoding="utf-8-sig")
        self.assertIn("Get-CimInstance Win32_Process", source)
        self.assertIn("Microsoft.PowerBI.AdomdClient.dll", source)
        self.assertIn("[System.Text.Encoding]::Unicode", source)
        self.assertIn('"Data Source=localhost:$port;Connect Timeout=12"', source)
        self.assertIn("EVALUATE", source)
        self.assertIn("COUNTROWS ( fct_club_performance )", source)
        self.assertIn("COUNTROWS ( fct_club_risk_profile )", source)
        self.assertIn("COUNTROWS ( fct_analytics_refresh_audit )", source)
        self.assertIn("[Last Warehouse Audit Label]", source)
        self.assertIn("max_club_win_rate_fraction", source)
        self.assertNotIn("Invoke-WebRequest", source)
        self.assertNotIn("Start-Process", source)
        self.assertNotIn("Refresh()", source)
        self.assertNotIn("SaveChanges", source)
        self.assertIn("portfolio_release = 'HOLD'", source)
        self.assertIn("desktop_visual_acceptance = 'NOT_VERIFIED'", source)

    def test_snapshot_reconciliation_is_opt_in(self):
        source = SCRIPT.read_text(encoding="utf-8-sig")
        self.assertIn("[string]$ExpectedSnapshot = ''", source)
        self.assertIn("if ($ExpectedSnapshot)", source)
        self.assertIn("PASS_SNAPSHOT_COUNTS", source)
        self.assertIn("UNCONFIRMED", source)

if __name__ == "__main__":
    unittest.main()
