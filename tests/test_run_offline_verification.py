"""Contract tests for quota-free offline verification (no cloud credentials)."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

RUNNER = Path(__file__).resolve().parents[1] / 'scripts' / 'run_offline_verification.py'


def load_runner():
    spec = importlib.util.spec_from_file_location('run_offline_verification', RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OfflineVerificationContract(unittest.TestCase):
    def test_failure_is_recorded_and_never_counted_as_pass(self):
        mod = load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / 'dbt_project.yml').write_text('name: synthetic\n')
            with patch.object(mod, 'run') as run:
                run.side_effect = lambda root, label, command, timeout: {
                    'name': label, 'command': command, 'status': 'failed' if 'ml_unit' in label else 'passed',
                    'returncode': 1 if 'ml_unit' in label else 0, 'duration_seconds': 0, 'output_tail': 'fixture'
                }
                summary = mod.run_all(repo, ['ml'], 30)
            self.assertEqual(summary['overall_status'], 'FAIL')
            self.assertFalse(summary['bigquery_verified'])
            self.assertFalse(summary['hosted_ci_triggered_by_this_runner'])
            self.assertEqual(len(summary['results']), 5)

    def test_uncredentialed_source_command_contract(self):
        mod = load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / 'dbt_project.yml').write_text('name: synthetic\n')
            with patch.object(mod, 'run') as run:
                run.side_effect = lambda root, label, command, timeout: {
                    'name': label, 'command': command, 'status': 'passed',
                    'returncode': 0, 'duration_seconds': 0, 'output_tail': 'fixture'
                }
                summary = mod.run_all(repo, ['source'], 30)
            self.assertEqual(summary['overall_status'], 'PASS')
            commands = [' '.join(call.args[2]) for call in run.call_args_list]
            self.assertEqual(len(commands), 4)
            self.assertFalse(any('dbt run' in c or 'actions' in c or 'bigquery' in c for c in commands))


if __name__ == '__main__':
    unittest.main()