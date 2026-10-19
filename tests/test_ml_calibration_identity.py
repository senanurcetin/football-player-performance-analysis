"""Prevent train-time refitting from invalidating split-conformal backtests.

No Google Cloud calls or trained artifacts are needed. These source-integrity
checks inspect the production v5 main() AST; they do not claim model performance.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "scripts/train_player_market_value.py"


def main_ast() -> ast.FunctionDef:
    source = ast.parse(SOURCE.read_text(encoding="utf-8"))
    for statement in source.body:
        if isinstance(statement, ast.FunctionDef) and statement.name == "main":
            return statement
    raise AssertionError("Production train_player_market_value.main() not found")


class CalibratedHoldoutIdentity(unittest.TestCase):
    def test_no_calibration_season_refit_for_heldout_pipeline(self):
        main = main_ast()
        fit_targets = [
            node.func.value.id
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "fit"
            and isinstance(node.func.value, ast.Name)
        ]
        self.assertEqual(fit_targets.count("tuning_pipeline"), 1)
        self.assertEqual(fit_targets.count("calibration_pipeline"), 1)
        self.assertEqual(fit_targets.count("final_pipeline"), 1)
        self.assertNotIn("pipeline", fit_targets)

    def test_holdout_reuses_exact_prefitted_calibration_pipeline(self):
        main = main_ast()
        alias_assignments = [
            node
            for node in main.body
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "pipeline" for t in node.targets)
        ]
        self.assertEqual(len(alias_assignments), 1)
        self.assertIsInstance(alias_assignments[0].value, ast.Name)
        self.assertEqual(alias_assignments[0].value.id, "calibration_pipeline")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertLess(source.index("calibration_pipeline.fit("),
                        source.index("pipeline = calibration_pipeline"))
        self.assertLess(source.index("pipeline = calibration_pipeline"),
                        source.index("pipeline.predict(test["))

    def test_same_baseline_fill_used_for_calibration_and_test(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn(
            "calibration_baseline_fill = float(calibration_training[TARGET].median())",
            source,
        )
        self.assertIn(".fillna(calibration_baseline_fill)", source)
        self.assertIn("baseline_fill = calibration_baseline_fill", source)
        self.assertNotIn("pipeline.fit(train[", source)

    def test_reports_actual_fit_and_calibration_provenance(self):
        source = SOURCE.read_text(encoding="utf-8")
        for field in (
            '"evaluation_fit_rows": int(len(calibration_training))',
            '"evaluation_fit_season_max": int(calibration_training["season"].max())',
            '"calibration_rows": int(len(calibration))',
            '"calibration_and_test_share_fitted_predictor": True',
        ):
            with self.subTest(field=field):
                self.assertIn(field, source)


if __name__ == "__main__":
    unittest.main()
