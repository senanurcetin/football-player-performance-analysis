"""Native PBIR editorial contrast between player cohorts and club-league analysis.

These source contracts do not replace actual Microsoft Power BI Desktop screenshots
or cross-filter, tooltip and BigQuery refresh acceptance.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAGES={
    "24c53960ddc19662d824":{
        "kind":"cohorts",
        "layout":[(105,151,754,252),(882,151,351,252),
                  (105,452,532,219),(660,452,573,219)],
        "ids":[f"a7e1000000000000000{x}" for x in range(1,5)],
        "query":[
            "Count(dim_players.player_id)",
            "Count(dim_players.player_id)",
            "Sum(fct_player_performance.total_goals)",
            "Sum(fct_player_performance.market_value_in_eur)",
        ],
        "labels":("01    /    COMPOSITION OF THE PLAYER POOL",
                  "02    /    CLUB OUTPUT + POSITION VALUE"),
        "heading":"ROSTER COHORTS",
        "footer":"b8a00000000000000002",
        "disclosure":"de9a00000000000000011",
    },
    "25f58efd2bb140e62be9":{
        "kind":"clubs",
        "layout":[(105,151,721,252),(849,151,384,252),
                  (105,452,542,219),(670,452,563,219)],
        "ids":[f"a7e2000000000000000{x}" for x in range(1,5)],
        "query":[
            "Average(fct_club_performance.win_rate)",
            "Sum(fct_club_performance.goal_difference)",
            "Sum(fct_competition_performance.matches_played)",
            "Sum(fct_competition_performance.total_goals)",
        ],
        "labels":("01    /    CLUB RESULTS AND OUTCOMES",
                  "02    /    COMPETITION VOLUME"),
        "heading":"COMPETITION INTELLIGENCE",
        "footer":"b8a00000000000000003",
        "disclosure":"de9a00000000000000012",
    },
}
def file(edition,page,id):
    return (ROOT/"powerbi"/edition/"FootballPlayerAnalysis"/"Report"/
            "definition"/"pages"/page/"visuals"/id/"visual.json")
def read(edition,page,id):
    return json.loads(file(edition,page,id).read_text(encoding="utf-8-sig"))
def coords(node):
    p=node["position"];return tuple(p[k] for k in ("x","y","width","height"))
def intersects(a,b):
    x,y,w,h=coords(a);xx,yy,ww,hh=coords(b)
    return max(x,xx)<min(x+w,xx+ww) and max(y,yy)<min(y+h,yy+hh)
def vid(page,role):
    return hashlib.sha1(f"NEXUS|editorial|{page}|{role}".encode()).hexdigest()[:20]
def text_of(node):
    return node["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"][0]["value"]
def literal(val):
    return val["expr"]["Literal"]["Value"]

class CohortLeagueEditorialTests(unittest.TestCase):
    def test_distinct_hero_charts_keep_original_metric_roles(self):
        for page,cfg in PAGES.items():
            for edition in ("workspace","offline-demo"):
                nodes=[read(edition,page,id) for id in cfg["ids"]]
                for i,(node,rect,metric) in enumerate(zip(nodes,cfg["layout"],cfg["query"])):
                    with self.subTest(page=page,edition=edition,chart=i):
                        self.assertEqual(coords(node),rect)
                        self.assertIn(node["visual"]["visualType"],
                                      ("clusteredBarChart","clusteredColumnChart"))
                        query=node["visual"]["query"]["queryState"]
                        values=[p["queryRef"] for field in query.values()
                                for p in field.get("projections",[])]
                        self.assertIn(metric,values)
                        ui=node["visual"]["visualContainerObjects"]["title"][0]["properties"]
                        self.assertEqual(literal(ui["fontSize"]),
                                         "15D" if i==0 else "12D")
                        labels=node["visual"]["objects"]["labels"][0]["properties"]
                        self.assertEqual(literal(labels["fontSize"]),
                                         "12D" if i==0 else "10D")
                        self.assertLessEqual(rect[0]+rect[2],1280)
                        self.assertLessEqual(rect[1]+rect[3],671)
                self.assertGreater(cfg["layout"][0][2],cfg["layout"][1][2])
                for i,n in enumerate(nodes):
                    for other in nodes[i+1:]:
                        self.assertFalse(intersects(n,other),(edition,page))
                self.assertEqual(read(edition,page,cfg["footer"])["position"]["y"],679)

    def test_real_cohort_semantics_are_not_claimed_as_unsupervised_model_clusters(self):
        page="24c53960ddc19662d824"
        for edition in ("workspace","offline-demo"):
            nodes=[read(edition,page,id) for id in PAGES[page]["ids"]]
            fields=[list(x["visual"]["query"]["queryState"]) for x in nodes]
            self.assertEqual(fields,[["Category","Y"]]*4)
            main=nodes[0]["visual"]["query"]["queryState"]
            self.assertEqual(main["Category"]["projections"][0]["queryRef"],"dim_players.position")
            age=nodes[1]["visual"]["query"]["queryState"]
            self.assertEqual(age["Category"]["projections"][0]["queryRef"],"dim_players.Age Group")
            strap=text_of(read(edition,page,vid(page,"strap")))
            self.assertIn("ROSTER COHORTS",strap)
            self.assertNotIn("cluster model",strap.lower())

    def test_editorial_labels_and_source_disclosure_clear_analysis_panels(self):
        for page,cfg in PAGES.items():
            for edition in ("workspace","offline-demo"):
                layers=[]
                for role,expected in (("section-one",cfg["labels"][0]),
                                      ("section-two",cfg["labels"][1])):
                    n=read(edition,page,vid(page,role))
                    self.assertEqual(n["visual"]["visualType"],"textbox")
                    self.assertEqual(text_of(n),expected)
                    self.assertFalse(n["visual"].get("query"))
                    layers.append(n)
                self.assertEqual(coords(layers[0]),(105,117,765,27))
                self.assertEqual(coords(layers[1]),(105,417,760,27))
                self.assertFalse(intersects(layers[0],layers[1]))
                rule1=read(edition,page,vid(page,"top-rule"))
                rule2=read(edition,page,vid(page,"bottom-rule"))
                self.assertEqual(coords(rule1),(105,145,97,2))
                self.assertEqual(coords(rule2),(105,445,97,2))
                charts=[read(edition,page,id) for id in cfg["ids"]]
                for label in layers+[rule1,rule2]:
                    for chart in charts:
                        self.assertFalse(intersects(label,chart),(page,edition))
                topline=read(edition,page,vid(page,"strap"))
                self.assertTrue(text_of(topline).startswith(cfg["heading"]))
                if edition=="offline-demo":
                    marks=list((file(edition,page,cfg["ids"][0]).parents[1]).glob("de9a*/visual.json"))
                    self.assertEqual(len(marks),1)
                    self.assertFalse(intersects(topline,json.loads(marks[0].read_text(encoding="utf-8-sig"))))

    def test_source_parity_on_edited_visuals_and_all_new_nondata_labels(self):
        for page,cfg in PAGES.items():
            ids=cfg["ids"]+[vid(page,role) for role in (
                "strap","section-one","section-two","hint","top-rule","bottom-rule")]
            for id in ids:
                with self.subTest(page=page,id=id):
                    self.assertEqual(read("workspace",page,id),read("offline-demo",page,id))

if __name__=="__main__":
    unittest.main()
