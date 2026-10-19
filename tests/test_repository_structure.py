"""Repository layout and documentation hygiene (no network or cloud jobs)."""
from __future__ import annotations

import hashlib
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT, check=True, stdout=subprocess.PIPE,
    )
    return [
        item.decode("utf-8") for item in result.stdout.split(b"\x00")
        if item
    ]


class RepositoryStructureContract(unittest.TestCase):
    def test_canonical_analytics_directories_and_powerbi_editions(self) -> None:
        folders = (
            "models/staging", "models/intermediate", "models/marts",
            "models/ml", "tests", "analyses", "snapshots", "scripts",
            "notebooks", "powerbi/workspace", "powerbi/offline-demo",
            "docs/assets/screenshots", "docs/archive/powerbi",
            ".github/workflows", ".circleci",
        )
        for folder in folders:
            with self.subTest(folder=folder):
                self.assertTrue((ROOT / folder).is_dir(), folder)
        self.assertTrue(
            (ROOT / "powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip").is_file()
        )
        self.assertTrue(
            (ROOT / "docs/PROJECT_STATUS.md").is_file()
        )

    def test_no_generated_runtime_outputs_or_temporary_files_tracked(self) -> None:
        for filename in tracked_files():
            pure = Path(filename.replace("\\", "/"))
            segments = [part.lower() for part in pure.parts]
            base = pure.name.lower()
            with self.subTest(path=filename):
                self.assertFalse(
                    any(p in {
                        "__pycache__", ".venv", "venv", ".pytest_cache",
                        ".ipynb_checkpoints", "target", "dbt_packages",
                        "logs", ".pbi", "artifacts",
                    } for p in segments),
                    f"Generated directory tracked: {filename}",
                )
                self.assertFalse(
                    base.startswith(("_temp_", "_temporary_"))
                    or base.endswith((".pyc", ".log", ".bak", ".abf"))
                    or base in {".env", "application_default_credentials.json"},
                    f"Temporary or credential file tracked: {filename}",
                )

    def test_active_documentation_has_no_duplicate_files(self) -> None:
        docs = [
            ROOT / p for p in tracked_files()
            if p.startswith("docs/") and p.endswith(".md")
            and "/archive/" not in p
        ]
        hashes: dict[str, Path] = {}
        for path in docs:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertNotIn(
                    digest, hashes,
                    f"Duplicate active docs: {hashes.get(digest)} and {path}",
                )
                hashes[digest] = path


if __name__ == "__main__":
    unittest.main()
