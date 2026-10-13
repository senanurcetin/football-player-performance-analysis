"""Unit tests for CI-free Power BI handoff report semantics."""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_powerbi_release_handoff import decision, layout_warnings, run_check


class PowerBIHandoffTests(unittest.TestCase):
    def test_layout_parser_handles_auditor_footer(self):
        self.assertEqual(layout_warnings('[{"warning_count": 2}, {"warning_count": 1}]\nSource-only audit'), 3)
        self.assertEqual(layout_warnings('[{"warning_count": 0}]'), 0)
        self.assertIsNone(layout_warnings('unexpected'))
        self.assertIsNone(layout_warnings('{}'))

    def test_source_gate_fails_closed(self):
        self.assertEqual(decision([]), 'FAIL')
        self.assertEqual(decision([{"status": "PASS"}, {"status": "FAIL"}]), 'FAIL')
        self.assertEqual(decision([{"status": "UNKNOWN"}]), 'FAIL')
        self.assertEqual(decision([{"status": "PASS"}, {"status": "WARN"}]), 'WARN')
        self.assertEqual(decision([{"status": "PASS"}]), 'PASS')

    def test_runner_marks_layout_warnings_without_claiming_desktop(self):
        sample = subprocess.CompletedProcess(args=[], returncode=0,
                    stdout='[{"warning_count": 4}]\nSource-only audit', stderr='')
        with tempfile.TemporaryDirectory() as folder, patch('subprocess.run', return_value=sample):
            result = run_check(Path(folder), 'visual_layout', ('scripts/audit_powerbi_layout.py',), 60)
        self.assertEqual(result['status'], 'WARN')
        self.assertEqual(result['warning_count'], 4)

    def test_runner_fails_on_malformed_layout_result(self):
        sample = subprocess.CompletedProcess(args=[], returncode=0, stdout='not json', stderr='')
        with tempfile.TemporaryDirectory() as folder, patch('subprocess.run', return_value=sample):
            result = run_check(Path(folder), 'visual_layout', ('scripts/audit_powerbi_layout.py',), 60)
        self.assertEqual(result['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
