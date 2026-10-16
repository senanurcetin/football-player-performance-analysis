"""Live-schema-backed regression for the October 2026 prediction report mismatch.

The list below comes from inspected football_ml.INFORMATION_SCHEMA.COLUMNS;
no synthetic player rows or predictive outputs are used by this test.
"""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL="ml_player_market_value_current_predictions"
BAD={"position_tr","age_group_tr","upside_kategori_tr"}
VISUALS=[
 ("1f4c5c8000149b2e2be8","2beada4d32fcdc1ff094"),
 ("1f4c5c8000149b2e2be8","4d304949cba7dd247021"),
 ("1f4c5c8000149b2e2be8","8b67c00a69b995fd3db6"),
 ("1f4c5c8000149b2e2be8","be92253a5130bdec9028"),
 ("MLPlayerDetail","3770c9c902136555047c"),
 ("MLPlayerDetail","eab0c803a967ea780284"),
 ("tooltip_pred_p012","tt012_scatter_0001"),
]

class GenuinePredictionSchemaTests(unittest.TestCase):
    def test_removed_missing_bigquery_columns_and_updated_dax(self):
        for edition in ("workspace","offline-demo"):
            base=ROOT/"powerbi"/edition/"FootballPlayerAnalysis"
            text=(base/"Model"/"definition"/"tables"/f"{MODEL}.tmdl").read_text(encoding="utf-8-sig")
            with self.subTest(edition=edition):
                for key in BAD:
                    self.assertNotIn(f"sourceColumn: {key}",text)
                    self.assertNotIn(f"column {key}\n",text)
                self.assertIn(f"{MODEL}[position]",text)
                self.assertNotIn(f"{MODEL}[position_tr]",text)

    def test_prediction_pages_and_tooltip_bind_to_real_position(self):
        for edition in ("workspace","offline-demo"):
            base=ROOT/"powerbi"/edition/"FootballPlayerAnalysis"/"Report"/"definition"/"pages"
            for page,ident in VISUALS:
                path=base/page/"visuals"/ident/"visual.json"
                node=json.loads(path.read_text(encoding="utf-8-sig"))
                raw=json.dumps(node)
                with self.subTest(edition=edition,page=page,visual=ident):
                    self.assertIn(f"{MODEL}.position",raw)
                    self.assertNotIn("position_tr",raw)
                    self.assertEqual(node["name"],ident)

if __name__=="__main__":
    unittest.main()
