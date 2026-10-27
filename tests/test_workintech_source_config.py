"""Fail-closed offline safeguards for a portable dbt raw-source dataset."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "models" / "staging" / "sources.yml"
PROFILE = ROOT / "profiles.yml.example"
MIGRATION = ROOT / "docs" / "WORKINTECH_MIGRATION_20261027.md"


class WorkintechSourcePortabilityTests(unittest.TestCase):
    def test_existing_warehouse_default_is_unchanged(self):
        text = SOURCE.read_text(encoding="utf8")
        self.assertIn("name: football_raw", text)
        self.assertIn("env_var('DBT_SOURCE_DATABASE', target.database)", text)
        self.assertEqual(
            text.count('schema: "{{ env_var(\'DBT_SOURCE_DATASET\', \'football_raw\') }}"'),
            1,
        )

    def test_dbt_target_dataset_is_independently_configurable(self):
        text = PROFILE.read_text(encoding="utf8")
        self.assertIn("env_var('DBT_PROJECT_ID')", text)
        self.assertIn("env_var('DBT_DATASET', 'football')", text)
        self.assertIn("env_var('DBT_KEYFILE')", text)

    def test_workintech_migration_requires_separate_namespace(self):
        text = MIGRATION.read_text(encoding="utf8")
        self.assertIn("nexus_football_raw", text)
        self.assertIn("nexus_football_mart", text)
        self.assertIn("nexus_football_ml", text)
        self.assertIn("NOT VERIFIED", text)
        self.assertIn("No cloud writes", text)

    def test_staging_sources_remain_unchanged(self):
        sqls = sorted((ROOT / "models" / "staging").glob("stg_*.sql"))
        self.assertEqual(len(sqls), 12)
        for file in sqls:
            sql = file.read_text(encoding="utf8")
            self.assertIn("{{ source('football_raw',", sql, file.name)


if __name__ == "__main__":
    unittest.main()
