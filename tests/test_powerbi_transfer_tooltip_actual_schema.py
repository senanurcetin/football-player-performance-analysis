"""The contextual transfer tooltip must use the real position field."""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]

class TooltipFieldContract(unittest.TestCase):
    def test_tooltip_field_survives_warehouse_schema(self):
        files=[]
        for edition in ("workspace","offline-demo"):
            base=ROOT/"powerbi"/edition/"FootballPlayerAnalysis"
            path=base/"Report"/"definition"/"pages"/"tooltip_transfer_p011"/"visuals"/"tt011_scatter_0001"/"visual.json"
            v=json.loads(path.read_text(encoding="utf-8-sig"))
            proj=v["visual"]["query"]["queryState"]
            s=json.dumps(proj)
            self.assertNotIn("position_tr",s)
            self.assertIn("fct_transfer_market_value_analysis.position",s)
            files.append(proj)
        self.assertEqual(files[0],files[1])
if __name__=="__main__":
    unittest.main()
