"""Evidence-first pilot layout for the editable Player Performance PBIR page.

Source checks only; Power BI Desktop rendering, actual slicer interactions,
semantic DAX and BigQuery refresh require separate verification.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAGE="d2bc1e6a078c5c5b125c"
EDITIONS=("workspace","offline-demo")
CARD_LAYOUT={
    "6cb1590ae40874c838b7":((257,113,278,74),"fct_player_performance.G+A per 90","'G+A / 90'"),
    "52a25425ec00bcc0a8b1":((547,113,160,74),"fct_player_performance.Toplam Gol","'Total Goals'"),
    "fd59ca45d88b6eb6b521":((719,113,160,74),"fct_player_performance.Toplam Asist","'Total Assists'"),
    "303c777d36178076aa39":((891,113,174,74),"fct_player_performance.Ortalama Dakika","'Minutes / Match'"),
    "c49bad3782a43cdac710":((1077,113,198,74),"dim_players.Total Players","'Players'"),
}
CHART_LAYOUT={
    "a61aa3c509a6b3e3b1b4":((257,220,510,223),"clusteredBarChart",
                              "fct_player_performance.Player G+A per 90"),
    "8b91d598c732aba58217":((780,220,243,223),"treemap",
                              "Average(fct_player_performance.goals_per_90)"),
    "81f5bb0995b4428b2b0d":((1036,220,240,223),"treemap",
                              "Average(fct_player_performance.assists_per_90)"),
    "6c68e020599db75da880":((86,474,343,197),"scatterChart",
                              "Sum(fct_player_performance.goals_per_90)"),
    "750474d7071b93a004b5":((440,474,327,197),
                              "lineStackedColumnComboChart",
                              "fct_player_performance.Avg G+A per 90"),
    "dd91e16c6d11d504a577":((779,474,496,197),"pivotTable",
                              "fct_player_performance.player_name"),
}
EDITORIAL=(
    "lens-title","lens-sub","filter-heading","section-rank",
    "section-evidence","metric-caution","kpi-rate-accent","evidence-divider",
)
FOOTER_ID="b8a00000000000000001"
def node(mode,id):
    file=(ROOT/"powerbi"/mode/"FootballPlayerAnalysis"/"Report"/
          "definition"/"pages"/PAGE/"visuals"/id/"visual.json")
    return json.loads(file.read_text(encoding="utf-8-sig"))
def vid(role):
    return hashlib.sha1(("NEXUS|performance|pilot|"+role).encode()).hexdigest()[:20]
def coords(x):
    p=x["position"]
    return tuple(p[k] for k in ("x","y","width","height"))
def collide(a,b):
    x,y,w,h=coords(a);xx,yy,ww,hh=coords(b)
    return max(x,xx)<min(x+w,xx+ww) and max(y,yy)<min(y+h,yy+hh)
def lit(obj):return obj["expr"]["Literal"]["Value"]

class PlayerPerformanceEditorialTests(unittest.TestCase):
    def test_weighted_kpis_promote_rate_not_repeated_equal_cards(self):
        for mode in EDITIONS:
            for id,(rect,metric,title) in CARD_LAYOUT.items():
                with self.subTest(edition=mode,kpi=id):
                    n=node(mode,id);v=n["visual"]
                    self.assertEqual(v["visualType"],"card")
                    self.assertEqual(coords(n),rect)
                    self.assertEqual(v["query"]["queryState"]["Values"]["projections"][0]["queryRef"],metric)
                    self.assertEqual(lit(v["visualContainerObjects"]["title"][0]["properties"]["text"]),title)
                    size="26D" if id=="6cb1590ae40874c838b7" else "19D"
                    self.assertEqual(lit(v["objects"]["labels"][0]["properties"]["fontSize"]),size)
                    self.assertEqual(lit(v["visualContainerObjects"]["background"][0]["properties"]
                                         ["color"]["solid"]["color"]),"\'#102B47\'")
            main_width=CARD_LAYOUT["6cb1590ae40874c838b7"][0][2]
            self.assertGreater(main_width,max(s[0][2] for key,s in CARD_LAYOUT.items()
                                             if key!="6cb1590ae40874c838b7"))
            ordered=sorted([node(mode,k) for k in CARD_LAYOUT],key=lambda x:x["position"]["x"])
            self.assertEqual([coords(i)[0] for i in ordered],[257,547,719,891,1077])

    def test_evidence_first_hero_and_all_original_analytics_are_data_bound(self):
        primary_width=CHART_LAYOUT["a61aa3c509a6b3e3b1b4"][0][2]
        self.assertGreaterEqual(primary_width,2*CHART_LAYOUT["8b91d598c732aba58217"][0][2])
        for mode in EDITIONS:
            for id,(rect,typ,metric) in CHART_LAYOUT.items():
                with self.subTest(edition=mode,chart=id):
                    n=node(mode,id);v=n["visual"]
                    self.assertEqual(v["visualType"],typ)
                    self.assertEqual(coords(n),rect)
                    projections=[p["queryRef"] for role in v["query"]["queryState"].values()
                                 for p in role.get("projections",[])]
                    self.assertIn(metric,projections)
                    self.assertLessEqual(n["position"]["x"]+n["position"]["width"],1280)
                    self.assertLessEqual(n["position"]["y"]+n["position"]["height"],671)
            for i,a in enumerate(CHART_LAYOUT):
                for b in list(CHART_LAYOUT)[i+1:]:
                    self.assertFalse(collide(node(mode,a),node(mode,b)),(mode,a,b))
            for card in CARD_LAYOUT:
                for chart in CHART_LAYOUT:
                    self.assertFalse(collide(node(mode,card),node(mode,chart)),(mode,card,chart))

    def test_sidebar_filter_and_footer_clearance(self):
        for mode in EDITIONS:
            sidebar=("9517a386b552cbd899cb","2b3c87b0e98089ca4858")
            foot=node(mode,FOOTER_ID)
            self.assertEqual(foot["position"]["y"],679)
            for sid in sidebar:
                v=node(mode,sid)
                self.assertTrue(v["visual"]["query"]["queryState"])
                for id in (*CARD_LAYOUT,*CHART_LAYOUT):
                    self.assertFalse(collide(v,node(mode,id)),(mode,sid,id))
            for id in (*CARD_LAYOUT,*CHART_LAYOUT):
                p=node(mode,id)["position"]
                self.assertLessEqual(p["y"]+p["height"],foot["position"]["y"]-8)

    def test_editorial_copy_and_brand_rules_exist_without_queries(self):
        for mode in EDITIONS:
            for role in EDITORIAL:
                with self.subTest(edition=mode,role=role):
                    n=node(mode,vid(role))
                    self.assertIn(n["visual"]["visualType"],("textbox","shape"))
                    self.assertFalse(n["visual"].get("query"))
            headline=node(mode,vid("section-rank"))
            subtitle=node(mode,vid("section-evidence"))
            self.assertEqual(coords(headline),(257,185,728,31))
            self.assertEqual(coords(subtitle),(86,443,1020,27))
            self.assertEqual(coords(node(mode,vid("kpi-rate-accent"))),(257,109,278,3))
            self.assertEqual(coords(node(mode,vid("evidence-divider"))),(86,471,1189,1))
            self.assertFalse(collide(subtitle,node(mode,vid("evidence-divider"))))
            descriptive_subtitle=node(mode,"404e0a1723e792a7d69c")
            self.assertEqual(coords(descriptive_subtitle),(257,77,735,31))
            if mode=="offline-demo":
                watermark=node(mode,"de9a00000000000000010")
                self.assertFalse(collide(descriptive_subtitle,watermark),
                                 "Source description must not overlap synthetic disclosure")

    def test_source_parity_for_unchanged_models_and_recomposed_positions(self):
        for id in (*CARD_LAYOUT,*CHART_LAYOUT):
            with self.subTest(id=id):
                self.assertEqual(node("workspace",id),node("offline-demo",id))
        for role in EDITORIAL:
            with self.subTest(role=role):
                self.assertEqual(node("workspace",vid(role)),node("offline-demo",vid(role)))

if __name__=="__main__":
    unittest.main()
