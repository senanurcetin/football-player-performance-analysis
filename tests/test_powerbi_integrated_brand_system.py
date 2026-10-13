"""Source contracts for restrained NEXUS brand signatures in native PBIR.

These inspect editable Power BI sources, not a claimed Desktop render.
"""
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME="5cb4db7e746975558322"
CLOSING="c83db10673c28e3346ae"
ANALYTIC=(
("d2bc1e6a078c5c5b125c","b6a00000000000000002"),
("24c53960ddc19662d824","b6a00000000000000003"),
("25f58efd2bb140e62be9","b6a00000000000000004"),
("4c63ad904b1db6e0d156","b6a00000000000000005"),
("292e3d92e92693c05047","b6a00000000000000006"),
("1f4c5c8000149b2e2be8","b6a00000000000000007"),
("MLModelPerformance","b6a00000000000000008"),
)
DRILL=(
("91edaa93bbbdbbc8e854","b6a00000000000000010"),
("MLPlayerDetail","b6a00000000000000011"),
)
COVERS=((HOME,"b6a00000000000000001",(88,49,187,89)),
        (CLOSING,"b6a00000000000000009",(92,76,185,88)))
def folder(edition,page):
    return ROOT/"powerbi"/edition/"FootballPlayerAnalysis"/"Report"/"definition"/"pages"/page/"visuals"
def read(edition,page,visual):
    return json.loads((folder(edition,page)/visual/"visual.json").read_text(encoding="utf-8-sig"))
def id_for(page,role):
    return hashlib.sha1(f"NEXUS|brand|{page}|{role}".encode()).hexdigest()[:20]
def pos(j):
    p=j["position"];return p["x"],p["y"],p["width"],p["height"]
def overlaps(a,b):
    x,y,w,h=pos(a);a0,a1,a2,a3=pos(b)
    return max(x,a0)<min(x+w,a0+a2) and max(y,a1)<min(y+h,a1+a3)
def value(expr):
    return expr["expr"]["Literal"]["Value"].strip("'")

class IntegratedBrandVisualTests(unittest.TestCase):
    def test_covers_have_small_signature_lockups_and_open_editorial_space(self):
        for page,logo,expected in COVERS:
            for edition in ("workspace","offline-demo"):
                with self.subTest(page=page,edition=edition):
                    brand=read(edition,page,logo)
                    self.assertEqual(pos(brand),expected)
                    res=brand["visual"]["objects"]["general"][0]["properties"]["imageUrl"]["expr"]["ResourcePackageItem"]
                    self.assertEqual(res["ItemName"],"nexus-wordmark-crop.svg")
                    self.assertAlmostEqual(expected[2]/expected[3],535/255,delta=0.01)
                    surface=read(edition,page,id_for(page,"signature-surface"))
                    self.assertEqual(surface["visual"]["visualType"],"shape")
                    self.assertEqual(value(surface["visual"]["objects"]["fill"][0]["properties"]
                                          ["fillColor"]["solid"]["color"]),"#020B16")
                    sx,sy,sw,sh=pos(surface)
                    bx,by,bw,bh=pos(brand)
                    self.assertGreaterEqual(bx,sx)
                    self.assertGreaterEqual(by,sy)
                    self.assertLessEqual(bx+bw,sx+sw)
                    self.assertLessEqual(by+bh,sy+sh)
                    for role in ("signature-rail","signature-divider",
                                 "editorial-hairline","editorial-accent"):
                        element=read(edition,page,id_for(page,role))
                        self.assertEqual(element["visual"]["visualType"],"shape")
                        self.assertTrue(element["position"]["width"] > 0)
                    if page==HOME:
                        for vid in ("be100000000000000001","be100000000000000002",
                                    "be100000000000000003"):
                            self.assertFalse(overlaps(brand,read(edition,page,vid)))
                        self.assertFalse(overlaps(read(edition,page,"be100000000000000001"),
                                                  read(edition,page,id_for(page,"research-context"))))
                    else:
                        for vid in ("be100000000000000008","be100000000000000009",
                                    "be10000000000000000a"):
                            self.assertFalse(overlaps(brand,read(edition,page,vid)))
                        self.assertFalse(overlaps(read(edition,page,"be100000000000000008"),
                                                  read(edition,page,id_for(page,"decision-context"))))

    def test_analytic_and_drillthrough_headers_share_proportional_branding(self):
        for page,logo in ANALYTIC+DRILL:
            is_detail=(page,logo) in DRILL
            expect=(127,2,128,61) if is_detail else (102,2,140,67)
            for edition in ("workspace","offline-demo"):
                with self.subTest(page=page,edition=edition):
                    brand=read(edition,page,logo)
                    self.assertEqual(pos(brand),expect)
                    self.assertAlmostEqual(expect[2]/expect[3],535/255,delta=0.02)
                    panel=read(edition,page,id_for(page,"header-signature"))
                    divider=read(edition,page,id_for(page,"header-divider"))
                    self.assertEqual(panel["visual"]["visualType"],"shape")
                    self.assertEqual(divider["visual"]["visualType"],"shape")
                    self.assertFalse(overlaps(brand,divider))
                    self.assertEqual(value(divider["visual"]["objects"]["fill"][0]["properties"]
                                           ["fillColor"]["solid"]["color"]),"#4EA8FF")
                    if is_detail:
                        back_id="01f3112b131ccb5d9561" if page==DRILL[0][0] else "76e0de69a53b01cccf21"
                        self.assertFalse(overlaps(brand,read(edition,page,back_id)))
                        self.assertFalse(overlaps(panel,read(edition,page,back_id)))

    def test_all_new_brand_elements_match_exactly_across_real_and_synthetic_editions(self):
        for page,_ in ((p,i) for p,i in ANALYTIC+DRILL):
            for role in ("header-signature","header-divider"):
                vid=id_for(page,role)
                with self.subTest(page=page,role=role):
                    self.assertEqual(read("workspace",page,vid),
                                     read("offline-demo",page,vid))
        for page in (HOME,CLOSING):
            for role in ("signature-surface","signature-rail","signature-divider",
                         "editorial-hairline","editorial-accent"):
                vid=id_for(page,role)
                self.assertEqual(read("workspace",page,vid),
                                 read("offline-demo",page,vid))
        for page,roles in ((HOME,("research-context","field-guide-index")),
                           (CLOSING,("decision-context",))):
            for role in roles:
                vid=id_for(page,role)
                self.assertEqual(read("workspace",page,vid),
                                 read("offline-demo",page,vid))
        for role in ("section-rail","section-caption",
                     "section-0","section-1","section-2","rail-line-0","rail-line-1"):
            vid=id_for(CLOSING,role)
            self.assertEqual(read("workspace",CLOSING,vid),
                             read("offline-demo",CLOSING,vid))

if __name__=="__main__":
    unittest.main()
