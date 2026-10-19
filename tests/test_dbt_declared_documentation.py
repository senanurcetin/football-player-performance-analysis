"""Offline dbt documentation regressions."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_declared_documentation import audit

class DeclaredDocumentationTests(unittest.TestCase):
    def test_repo_model_documentation_complete(self):
        result, errors = audit(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(result["sql_models"], result["yaml_models"])
        self.assertGreater(result["declared_columns"], 0)

    def test_empty_column_description_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            model=root/"models"/"staging"
            model.mkdir(parents=True)
            (model/"one.sql").write_text("select 1 as id",encoding="utf-8")
            (model/"schema.yml").write_text(
                "version: 2\nmodels:\n  - name: one\n    description: Fixture\n"
                "    columns:\n      - name: id\n        description: ''\n",encoding="utf-8")
            _,errors=audit(root)
            self.assertTrue(any("Missing declared column description" in e for e in errors),errors)

    def test_unlisted_sql_model_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"models").mkdir()
            (root/"models"/"unlisted.sql").write_text("select 1",encoding="utf-8")
            _,errors=audit(root)
            self.assertTrue(any("Undocumented SQL model" in e for e in errors),errors)

if __name__ == "__main__":
    unittest.main()
