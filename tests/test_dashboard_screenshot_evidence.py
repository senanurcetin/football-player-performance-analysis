"""Tests for the genuine Power BI screenshot asset manifest."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from verify_dashboard_screenshots import validate

class ScreenshotEvidenceTests(unittest.TestCase):
    def test_manifest_and_images(self):
        self.assertEqual(validate()["captures"],13)
    def test_curated_portfolio(self):
        self.assertEqual(validate()["framed"],9)
