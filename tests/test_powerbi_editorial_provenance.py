"""Guard native NEXUS editorial covers and honest, unobtrusive demo labeling.

This test checks source structure only, not actual Power BI Desktop rendering.
"""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
HOME="5cb4db7e746975558322"
CLOSING="c83db10673c28e3346ae"
CROP="nexus-wordmark-crop.svg"
LINKS=(
 ("e05ec85d07e31d70040e",68,412),
 ("18a7cb26e6d2e25c2688",431,412),
 ("8265664407e23bc40e16",68,482),
 ("f3c57a30e5671c050a79",431,482),
 ("6f2ba3d04798d16080ed",68,552),
 ("87d5ca309c5c9145d3ba",431,552),
 ("b7e00000000000000001",68,622),
)
def base(mode):
 return ROOT/"powerbi"/mode/"FootballPlayerAnalysis"/"Report"/"definition"/"pages"
def read(path):
 return json.loads(path.read_text(encoding="utf-8-sig"))
def vid(mode,page,name):
 return read(base(mode)/page/"visuals"/name/"visual.json")
def xywh(p):
 return p["x"],p["y"],p["width"],p["height"]
def overlaps(a,b):
 ax,ay,aw,ah=xywh(a);bx,by,bw,bh=xywh(b)
 return max(ax,bx)<min(ax+aw,bx+bw) and max(ay,by)<min(ay+ah,by+bh)

class EditorialSourceTests(unittest.TestCase):
 def test_home_editorial_grid_retains_native_page_links(self):
  for mode in ("workspace","offline-demo"):
   home=base(mode)/HOME
   logo=vid(mode,HOME,"b6a00000000000000001")
   self.assertEqual(xywh(logo["position"]),(88,49,187,89))
   self.assertEqual(
    logo["visual"]["objects"]["general"][0]["properties"]["imageUrl"]
    ["expr"]["ResourcePackageItem"]["ItemName"], CROP)
   for name,x,y in LINKS:
    node=vid(mode,HOME,name)
    with self.subTest(mode=mode,visual=name):
     self.assertEqual(xywh(node["position"]),(x,y,347,54))
     self.assertEqual(node["visual"]["visualType"],"actionButton")
     self.assertTrue(node["visual"]["visualContainerObjects"]["visualLink"])
     self.assertFalse(overlaps(node["position"],logo["position"]))
   for label in ("be100000000000000001","be100000000000000002","be100000000000000003"):
    self.assertFalse(overlaps(vid(mode,HOME,label)["position"],logo["position"]))
   closing_logo=vid(mode,CLOSING,"b6a00000000000000009")
   self.assertEqual(
    closing_logo["visual"]["objects"]["general"][0]["properties"]["imageUrl"]
    ["expr"]["ResourcePackageItem"]["ItemName"],CROP)
   for label in ("be100000000000000008","be100000000000000009","be10000000000000000a"):
    self.assertFalse(overlaps(vid(mode,CLOSING,label)["position"],closing_logo["position"]))

 def test_tabs_clean_but_offline_source_explicit_and_production_never_mislabeled(self):
  production=base("workspace");offline=base("offline-demo")
  allpages={p.parent.name for p in production.glob("*/page.json")}
  self.assertEqual(allpages,{p.parent.name for p in offline.glob("*/page.json")})
  self.assertEqual(len(allpages),13)
  for pid in allpages:
   real=read(production/pid/"page.json")
   sample=read(offline/pid/"page.json")
   with self.subTest(page=pid):
    self.assertEqual(real["displayName"],sample["displayName"])
    self.assertFalse(real["displayName"].startswith("[DEMO]"))
    self.assertFalse(list((production/pid/"visuals").glob("de9a*/visual.json")))
    labels=list((offline/pid/"visuals").glob("de9a*/visual.json"))
    if sample["width"]==560:
     self.assertFalse(labels)
     continue
    self.assertEqual(len(labels),1)
    node=read(labels[0])
    run=node["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"][0]
    self.assertEqual(run["value"],"SYNTHETIC DATA  /  NOT REAL")
    self.assertEqual(run["textStyle"]["fontSize"],"8pt")
    self.assertGreaterEqual(node["position"]["x"],1022)
    self.assertLessEqual(node["position"]["x"]+node["position"]["width"],1280)
    self.assertLessEqual(node["position"]["y"]+node["position"]["height"],720)

if __name__=="__main__":
 unittest.main()
