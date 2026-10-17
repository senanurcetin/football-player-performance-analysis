"""Ensure the published documentation remains internally navigable."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from check_docs_integrity import validate

class DocumentationIntegrityTests(unittest.TestCase):
    def test_markdown_links_and_heading_anchors(self):
        result=validate()
        self.assertEqual(result["missing_targets"],0)
        self.assertEqual(result["broken_anchors"],0)
    def test_historical_archive_separate_from_current_guides(self):
        self.assertGreaterEqual(validate()["archived_powerbi_documents"],19)
