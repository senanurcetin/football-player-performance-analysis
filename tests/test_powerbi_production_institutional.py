"""Production-only NEXUS Power BI architecture and source safety contracts.

Only powerbi/workspace may be released. The separate offline fixtures retain
truthful provenance internally and are NOT a substitute for connected data.
These tests never launch Power BI Desktop, hosted CI, or warehouse jobs.
"""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRODUCTION=ROOT/"powerbi"/"workspace"/"FootballPlayerAnalysis"
INTERNAL=ROOT/"powerbi"/"offline-demo"/"FootballPlayerAnalysis"
TRANSFER="4c63ad904b1db6e0d156"
MARKET="292e3d92e92693c05047"
VALUATION="1f4c5c8000149b2e2be8"
PAGES={
    TRANSFER:{
        "cards":{
            "a7e40000000000000003":(105,102,365,78),
            "a7e40000000000000002":(486,102,216,78),
            "a7e40000000000000001":(718,102,216,78),
            "a7e40000000000000004":(950,102,283,78),
        },
        "charts":{
            "a7e30000000000000003":(105,222,706,229),
            "a7e30000000000000004":(827,222,406,229),
            "a7e30000000000000001":(105,500,542,171),
            "a7e30000000000000002":(663,500,570,171),
        },
        "hero":"a7e30000000000000003",
        "sidebar":[],
    },
    MARKET:{
        "cards":{
            "1c46895062519f70d69a":(105,105,224,82),
            "757b5b68c3d0a6fba94a":(339,105,167,82),
            "8055f62b9b64c1af3607":(516,105,152,82),
            "366b475ae757c1657879":(678,105,153,82),
            "e55be8bdbcb32fe34d4a":(841,105,134,82),
        },
        "charts":{
            "0839d8ed3d7479a01f32":(105,222,546,221),
            "5bbe3e0865c55bbeade1":(665,222,305,221),
            "1c4d73ece1a64f57c0fc":(105,470,235,201),
            "9c728e8d682165354da4":(355,470,615,201),
            "13ccac612fab8060cf67":(985,470,248,201),
        },
        "hero":"0839d8ed3d7479a01f32",
        "sidebar":["67570d322368ec10a26c","fe3412c355304a9a3162",
                   "203b4d9871242427cf32","fc1a64c02f7fb0bab2b1"],
    },
    VALUATION:{
        "cards":{
            "76310c62691d5137e80b":(105,105,237,82),
            "f1258f389ac53495cf15":(355,105,133,82),
            "31824c579723a8252662":(501,105,155,82),
            "5d8a66ac8a1bbc4956b2":(669,105,160,82),
            "cf652160ede9f0b73bfe":(842,105,133,82),
        },
        "charts":{
            "8b67c00a69b995fd3db6":(105,222,550,215),
            "3ccd5a45594119af9bb7":(669,222,301,215),
            "4d304949cba7dd247021":(105,478,321,193),
            "be92253a5130bdec9028":(440,478,530,193),
        },
        "hero":"8b67c00a69b995fd3db6",
        "sidebar":["2beada4d32fcdc1ff094","1129c5d18f0c86361eb8",
                   "f5bddd9e5957e2fca806","4fc5a507c6edea97772c"],
    },
}
PATTERN=re.compile(r"\bdemo\b|\bsynthetic\b|\bfake\b|\bsahte\b|\bnot real data\b",re.I)
def path(mode,page,id):
    project=PRODUCTION if mode=="workspace" else INTERNAL
    return project/"Report"/"definition"/"pages"/page/"visuals"/id/"visual.json"
def read(mode,page,id):
    return json.loads(path(mode,page,id).read_text(encoding="utf-8-sig"))
def rect(j):
    p=j["position"];return tuple(p[k] for k in ("x","y","width","height"))
def collides(a,b):
    x,y,w,h=rect(a);xx,yy,ww,hh=rect(b)
    return max(x,xx)<min(x+w,xx+ww) and max(y,yy)<min(y+h,yy+hh)
def literal(x):return x["expr"]["Literal"]["Value"]
def uid(page,name):
    return hashlib.sha1(f"NEXUS|institutional|{page}|{name}".encode()).hexdigest()[:20]

class ProductionInstitutionalContracts(unittest.TestCase):
    def test_visuals_are_recomposed_with_data_bindings_and_no_data_collisions(self):
        for page,config in PAGES.items():
            for mode in ("workspace","offline-demo"):
                cards=[read(mode,page,k) for k in config["cards"]]
                charts=[read(mode,page,k) for k in config["charts"]]
                for id,expected in (*config["cards"].items(),*config["charts"].items()):
                    with self.subTest(page=page,mode=mode,id=id):
                        j=read(mode,page,id)
                        self.assertEqual(rect(j),expected)
                        self.assertTrue(j["visual"].get("query",{}).get("queryState"))
                        self.assertLessEqual(expected[0]+expected[2],1280)
                        self.assertLessEqual(expected[1]+expected[3],671)
                for i,j in enumerate(cards+charts):
                    for other in (cards+charts)[i+1:]:
                        self.assertFalse(collides(j,other),(page,mode,j["name"],other["name"]))
                for sid in config["sidebar"]:
                    s=read(mode,page,sid)
                    self.assertTrue(s["visual"]["query"]["queryState"])
                    for j in cards+charts:
                        self.assertFalse(collides(s,j))
                main=read(mode,page,config["hero"])
                supporting=[j["position"]["width"] for j in charts
                            if j["name"] != config["hero"] and
                            j["visual"]["visualType"] != "tableEx"]
                self.assertGreater(main["position"]["width"], max(supporting))
                for id in config["cards"]:
                    node=read(mode,page,id)["visual"]
                    props=node["visualContainerObjects"]["title"][0]["properties"]
                    self.assertGreaterEqual(int(literal(props["fontSize"]).rstrip("D")),11)

    def test_parallel_native_source_editions_preserve_chart_binding_parity(self):
        for page,cfg in PAGES.items():
            for id in (*cfg["cards"],*cfg["charts"]):
                with self.subTest(page=page,id=id):
                    prod=read("workspace",page,id)
                    internal=read("offline-demo",page,id)
                    self.assertEqual(prod,internal)

    def test_small_editorial_copy_keeps_hero_context_separate(self):
        transfer_section=read("workspace",TRANSFER,uid(TRANSFER,"chapter-two"))
        caution=read("workspace",TRANSFER,uid(TRANSFER,"caveat"))
        self.assertFalse(collides(transfer_section,caution))
        for page,id,context in (
            (MARKET,"2c2a798c4c5103212a5f",uid(MARKET,"context")),
            (VALUATION,"138f5a3ce7d3131d27a0",uid(VALUATION,"context")),
        ):
            self.assertFalse(collides(read("workspace",page,id),read("workspace",page,context)))
        statement=read("workspace",VALUATION,"8750cd592dd7e9595f60")
        paragraphs=statement["visual"]["objects"]["general"][0]["properties"]["paragraphs"]
        copy="\n".join(run["value"] for p in paragraphs for run in p["textRuns"])
        for concept in ("Prediction is not", "prior and predicted",
                        "lower/upper intervals", "quality flags"):
            self.assertIn(concept,copy)
        self.assertNotIn("Forwards carry",copy)
        self.assertNotIn("correctly captures",copy)

    def test_no_sample_or_fake_labels_in_any_production_visible_page_text(self):
        pages=PRODUCTION/"Report"/"definition"/"pages"
        listed=list(pages.glob("*/page.json"))
        self.assertEqual(len(listed),13)
        for meta in listed:
            page=json.loads(meta.read_text(encoding="utf-8-sig"))
            self.assertNotRegex(page["displayName"],PATTERN)
        for f in pages.glob("*/visuals/*/visual.json"):
            visual=json.loads(f.read_text(encoding="utf-8-sig"))["visual"]
            objects=visual.get("objects",{})
            visible=[]
            for group in objects.get("general",[]):
                for para in group.get("properties",{}).get("paragraphs",[]):
                    visible.extend(run.get("value","") for run in para.get("textRuns",[]))
            for title in visual.get("visualContainerObjects",{}).get("title",[]):
                visible.append(title.get("properties",{}).get("text",{}).
                               get("expr",{}).get("Literal",{}).get("Value",""))
            for text in visible:
                with self.subTest(visual=f.parent.name):
                    self.assertNotRegex(text,PATTERN)
        self.assertTrue(INTERNAL.exists(),"Internal data fixtures must remain explicitly separate")

    def test_production_models_retain_live_bigquery_partitions(self):
        for table,schema in (
            ("fct_transfer_fixed_horizon_outcomes","football_mart"),
            ("fct_transfer_market_value_analysis","football_mart"),
            ("ml_player_market_value_current_predictions","football_ml"),
            ("fct_club_risk_profile","football_mart"),
        ):
            p=PRODUCTION/"Model"/"definition"/"tables"/f"{table}.tmdl"
            source=p.read_text(encoding="utf-8-sig")
            with self.subTest(table=table):
                self.assertIn("GoogleBigQuery.Database([UseStorageApi=false])",source)
                self.assertIn("data-analiz-490513",source)
                self.assertIn(f'{schema}_Schema',source)
                self.assertIn(f'[Name="{table}",Kind="Table"]',source)
                self.assertIn(f"partition {table} = m",source)
                self.assertNotIn("Table.FromRecords(",source)

if __name__=="__main__":
    unittest.main()
