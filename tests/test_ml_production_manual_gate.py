"""Source-only regression tests for the explicit final-stage ML publish gate.

Does not run CI, contact BigQuery, read credentials or publish anything.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / ".github/workflows/ml-production.yml"


class MLPublicationManualGate(unittest.TestCase):
    def setUp(self):
        self.source = FILE.read_text(encoding="utf-8")

    def test_no_schedule_or_push_based_publish_trigger(self):
        header = self.source.split("permissions:", 1)[0]
        self.assertIn("workflow_dispatch:", header)
        self.assertNotRegex(header, r"(?m)^\s+(?:schedule|push|pull_request):")

    def test_manual_run_requires_explicit_confirmation(self):
        self.assertIn("confirm_final_release:", self.source)
        self.assertIn("required: true", self.source)
        self.assertIn("default: false", self.source)
        self.assertIn("type: boolean", self.source)

    def test_publish_job_requires_variable_and_run_confirmation(self):
        self.assertIn("vars.ENABLE_ML_PRODUCTION == 'true'", self.source)
        self.assertIn("inputs.confirm_final_release == true", self.source)
        self.assertRegex(
            self.source,
            re.compile(r"(?m)^  train-score-publish:\n(?:.*\n){0,4}"
                       r"    if: vars.ENABLE_ML_PRODUCTION == 'true' "
                       r"&& inputs.confirm_final_release == true"),
        )


if __name__ == "__main__":
    unittest.main()
