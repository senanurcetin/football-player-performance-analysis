"""Post-cutover filesystem integrity checks for the owner-accepted NEXUS Football Desktop PBIP.

No Power BI launch, refresh or screenshot capture. The Windows-specific tests
skip outside the authorized user's Desktop workstation.
"""
from pathlib import Path
import hashlib,json
import unittest

REPO=Path(__file__).resolve().parents[1]
QA=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-full-dedup-qa-20261028\FootballPlayerAnalysis")
ACTIVE=Path(r"C:\Users\MONSTER\Documents\NEXUS-Football-PBI\FootballPlayerAnalysis")
AUDIT=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027\workintech_pbip_production_promotion_20261028.json")
VERSION=REPO/"powerbi/workintech-20261028/FootballPlayerAnalysis"

def files(root):
    return {p.relative_to(root).as_posix():p for p in root.rglob("*") if p.is_file()}
def same(a,b):
    return hashlib.sha256(a.read_bytes()).digest()==hashlib.sha256(b.read_bytes()).digest()

class OwnerAcceptedPBIPProductionSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not AUDIT.is_file() or not ACTIVE.is_dir() or not QA.is_dir():
            raise unittest.SkipTest("Owner's Windows accepted PBIP directories unavailable.")
        cls.audit=json.loads(AUDIT.read_text("utf8"))

    def test_promoted_model_structure_and_rollback(self):
        a=self.audit
        self.assertEqual(a["status"],"OWNER_ACCEPTED_PBIP_PROMOTED_SOURCE_VERIFIED")
        self.assertEqual(a["post_upgrade"]["bigquery_imports"],34)
        self.assertEqual(a["post_upgrade"]["relationships"],87)
        self.assertEqual(a["post_upgrade"]["pages"],13)
        self.assertEqual(a["post_upgrade"]["visuals"],308)
        self.assertEqual(a["pre_upgrade"]["bigquery_imports"],65)
        backup=Path(a["complete_original_rollback_folder"])
        self.assertTrue((backup/"FootballPlayerAnalysis.pbip").is_file())
        self.assertTrue((backup/"Model/.pbi/cache.abf").is_file())

    def test_active_is_identical_to_tested_QA(self):
        a=files(ACTIVE)
        q=files(QA)
        self.assertEqual(a.keys(),q.keys())
        for name,path in q.items():
            self.assertTrue(same(path,a[name]),name)

    def test_versioned_source_is_same_as_accepted_active(self):
        if not VERSION.is_dir():
            raise unittest.SkipTest("Dated repository source edition missing")
        a=files(ACTIVE)
        v=files(VERSION)
        self.assertEqual(a.keys(),v.keys())
        for name,path in v.items():
            self.assertTrue(same(path,a[name]),name)

    def test_cache_is_not_stale_and_screen_capture_not_requested(self):
        self.assertFalse((ACTIVE/"Model/.pbi").exists())
        self.assertFalse((ACTIVE/"Report/.pbi").exists())
        self.assertFalse(self.audit["additional_screenshots_requested"])
        self.assertTrue(self.audit["qa_files_byte_identical_to_active"])
        self.assertFalse(self.audit["external_powerbi_runtime_post_promotion_verified"])

if __name__=="__main__":
    unittest.main()
