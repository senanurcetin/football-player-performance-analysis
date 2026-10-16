"""NEXUS Football PBIR accessibility and selection-safe dashboard regression.

The QA is source-level: actual Power BI Desktop screenshot acceptance is separate.
"""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EDITIONS=("workspace","offline-demo")
DARK={"#10283F","#193650","#122942","#173451"}
LIGHT={"#FFFFFF","#EFF7FF","#ECF4FF"}
GUARDS={
 "MLPlayerDetail":("ml_player_market_value_current_predictions",{
 "344404596767b453caa1":"Selected Player Previous Value",
 "7c2359c2094f3a53c59a":"Selected Player Prediction Value",
 "80e11d3dbddb28959833":"Selected Player Prediction Change %",
 }),
 "91edaa93bbbdbbc8e854":("fct_transfer_market_value_analysis",{
 "037321fd29d601484f33":"Selected Player Post-Transfer Change %",
 "5461e67d0b8a9eaf9ab0":"Selected Player Transfer Count",
 "eabd04a7df43ed2d10e4":"Selected Player Known Fee",
 }),
}

def project(edition):
 return ROOT/"powerbi"/edition/"FootballPlayerAnalysis"

def node(edition,page,ident):
 f=project(edition)/"Report"/"definition"/"pages"/page/"visuals"/ident/"visual.json"
 return json.loads(f.read_text(encoding="utf-8-sig"))

def color(obj,section,key):
 v=obj[section][0]["properties"][key]["solid"]["color"]["expr"]["Literal"]["Value"]
 return v.strip("'")

class ScreenshotBackedAccessibility(unittest.TestCase):
 def test_all_thirteen_pages_and_dark_table_rows(self):
  for edition in EDITIONS:
   pages=project(edition)/"Report"/"definition"/"pages"
   self.assertEqual(len(list(pages.glob("*/page.json"))),13)
   count=0
   for f in pages.glob("*/visuals/*/visual.json"):
    n=json.loads(f.read_text(encoding="utf-8-sig"))
    v=n["visual"]
    if v["visualType"] not in ("tableEx","pivotTable"):continue
    props=v["objects"]
    a=color(props,"values","backColorPrimary")
    b=color(props,"values","backColorSecondary")
    c=color(props,"values","fontColorPrimary")
    d=color(props,"values","fontColorSecondary")
    with self.subTest(edition=edition,visual=n["name"]):
     self.assertIn(a,DARK)
     self.assertIn(b,DARK)
     self.assertIn(c,LIGHT)
     self.assertIn(d,LIGHT)
    count+=1
   self.assertGreaterEqual(count,8)

 def test_detail_logos_are_above_opaque_foreground_shapes(self):
  for edition in EDITIONS:
   for page in GUARDS:
    folder=project(edition)/"Report"/"definition"/"pages"/page/"visuals"
    images=[json.loads(f.read_text(encoding="utf-8-sig")) for f in folder.glob("*/visual.json") if json.loads(f.read_text(encoding="utf-8-sig"))["visual"]["visualType"]=="image"]
    self.assertEqual(len(images),1)
    image=images[0]
    self.assertEqual(image["visual"]["objects"]["general"][0]["properties"]["imageUrl"]["expr"]["ResourcePackageItem"]["ItemName"],"NEXUS_Official_Transparent_Logo.png")
    self.assertGreater(image["position"]["z"],9500)

 def test_kpis_are_blank_when_no_detail_player_filter_exists(self):
  for edition in EDITIONS:
   for page,(table,items) in GUARDS.items():
    src=(project(edition)/"Model"/"definition"/"tables"/(table+".tmdl")).read_text(encoding="utf-8-sig")
    for ident,name in items.items():
     with self.subTest(edition=edition,measure=name):
      self.assertRegex(src,r"(?s)measure '"+re.escape(name)+r"' =\n\s*IF \( HASONEVALUE \( "+table+r"\[player_id\] \),.*?BLANK \(\) \)")
      v=node(edition,page,ident)["visual"]
      self.assertEqual(v["query"]["queryState"]["Values"]["projections"][0]["field"]["Measure"]["Property"],name)

 def test_prediction_quality_uses_native_warehouse_english_status(self):
  for edition in EDITIONS:
   table="ml_player_market_value_current_predictions"
   tmdl=(project(edition)/"Model"/"definition"/"tables"/(table+".tmdl")).read_text(encoding="utf-8-sig")
   self.assertIn("column prediction_quality_status",tmdl)
   self.assertIn("sourceColumn: prediction_quality_status",tmdl)
   self.assertNotIn("column 'Quality Label EN'",tmdl)
   found=0
   for page in ("1f4c5c8000149b2e2be8","MLPlayerDetail"):
    for f in (project(edition)/"Report"/"definition"/"pages"/page/"visuals").glob("*/visual.json"):
     raw=f.read_text(encoding="utf-8-sig")
     if table not in raw:continue
     self.assertNotIn("Quality Label EN",raw)
     self.assertNotIn(table+".kalite_etiketi_tr",raw)
     if table+".prediction_quality_status" in raw:found+=1
   self.assertGreaterEqual(found,5)

if __name__=="__main__":
 unittest.main()
