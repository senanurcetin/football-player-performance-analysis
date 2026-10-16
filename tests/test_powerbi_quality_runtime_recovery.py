"""Runtime-screenshot regressions: real English prediction quality, NEXUS palette, safe headers.

Power BI Desktop screenshots and refreshed runtime rendering are a separate acceptance gate.
"""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODEL="ml_player_market_value_current_predictions"
QUALITY_PAGES={"1f4c5c8000149b2e2be8","MLPlayerDetail"}
BG_COLORS={"#4EA8FF","#B9D1E8"}

class PredictionVisualRecovery(unittest.TestCase):
 def test_failed_quality_visuals_bind_actual_bigquery_status(self):
  # Current real warehouse mapping confirmed: 4,393 high, 2,124 limited, 1,324 medium.
  for ed in ("workspace","offline-demo"):
   base=ROOT/"powerbi"/ed/"FootballPlayerAnalysis"
   model=(base/"Model"/"definition"/"tables"/f"{MODEL}.tmdl").read_text(encoding="utf-8-sig")
   self.assertNotIn("column 'Quality Label EN'",model)
   self.assertIn("sourceColumn: prediction_quality_status",model)
   matched=[]
   for page in QUALITY_PAGES:
    for f in (base/"Report"/"definition"/"pages"/page/"visuals").glob("*/visual.json"):
     obj=json.loads(f.read_text(encoding="utf-8-sig"))
     raw=json.dumps(obj,ensure_ascii=False)
     self.assertNotIn("Quality Label EN",raw)
     if f"{MODEL}.prediction_quality_status" in raw:
      matched.append((page,obj["name"],obj["visual"]["visualType"]))
      self.assertNotIn("kalite_etiketi_tr",raw)
   types={x[2] for x in matched}
   self.assertGreaterEqual(len(matched),5)
   self.assertTrue({"slicer","donutChart","tableEx"}<=types)

 def test_no_old_green_accents_in_any_visual(self):
  for ed in ("workspace","offline-demo"):
   root=ROOT/"powerbi"/ed/"FootballPlayerAnalysis"/"Report"/"definition"/"pages"
   for f in root.glob("*/visuals/*/visual.json"):
    src=f.read_text(encoding="utf-8-sig").upper()
    with self.subTest(edition=ed,page=f.parts[-4],visual=f.parent.name):
     self.assertNotIn("#6FA56D",src)
     self.assertNotIn("#C8F5C0",src)

 def test_section_baselines_have_separation_and_no_unsupported_players_suffix(self):
  for ed in ("workspace","offline-demo"):
   root=ROOT/"powerbi"/ed/"FootballPlayerAnalysis"
   tmdl=(root/"Model"/"definition"/"tables"/f"{MODEL}.tmdl").read_text(encoding="utf-8-sig")
   self.assertNotIn('formatString: #,0 "players"',tmdl)
   # A section text box no longer abuts the panel immediately below it.
   ids=[
    ("1f4c5c8000149b2e2be8","8da25ab32fbd958908ef"),
    ("1f4c5c8000149b2e2be8","5e7cd7527cf8eb60c9b0"),
    ("MLModelPerformance","64ed84274aaddf3d3d40"),
    ("MLModelPerformance","32c5eed7d446f28a36b5"),
    ("d2bc1e6a078c5c5b125c","bf4f1b4c68e1ed47e84d")
   ]
   for page,id in ids:
    path=root/"Report"/"definition"/"pages"/page/"visuals"/id/"visual.json"
    obj=json.loads(path.read_text(encoding="utf-8-sig"))
    with self.subTest(edition=ed,visual=id):
     self.assertLessEqual(obj["position"]["y"],185 if id=="8da25ab32fbd958908ef" else (440 if id in ("5e7cd7527cf8eb60c9b0","32c5eed7d446f28a36b5") else 189))
     self.assertGreaterEqual(obj["position"]["height"],23)

if __name__=="__main__":
 unittest.main()
