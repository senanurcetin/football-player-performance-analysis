"""Regressions for the genuine English transfer reporting and midnight rail.

This is PBIR source-only; no screenshot or Desktop visual success is asserted.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAGE="292e3d92e92693c05047"
CARDS={"1c46895062519f70d69a","757b5b68c3d0a6fba94a","8055f62b9b64c1af3607",
       "366b475ae757c1657879","e55be8bdbcb32fe34d4a","aad67df1af591a835827"}
SLICERS={"67570d322368ec10a26c","fe3412c355304a9a3162",
         "203b4d9871242427cf32","fc1a64c02f7fb0bab2b1"}
RAIL="f3e7a16b6aa733c5f5d4"
ENGLISH_DIRECTION="market_value_direction_after_transfer"


def source(edition):
    return ROOT/"powerbi"/edition/"FootballPlayerAnalysis"


def node(edition,page,ident):
    path=source(edition)/"Report"/"definition"/"pages"/page/"visuals"/ident/"visual.json"
    return json.loads(path.read_text(encoding="utf-8-sig"))


def color(component,area,part,property):
    props=component[area][0]["properties"]
    return props[part]["solid"]["color"]["expr"]["Literal"]["Value"].strip("'")


class ProductionTransferNightUX(unittest.TestCase):
    def test_native_kpis_and_slicers_in_midnight_palette(self):
        for edition in ("workspace","offline-demo"):
            for ident in CARDS|SLICERS:
                v=node(edition,PAGE,ident)["visual"]
                with self.subTest(edition=edition,ident=ident):
                    self.assertEqual(v["visualType"],"card" if ident in CARDS else "slicer")
                    self.assertEqual(color(v["visualContainerObjects"],"background","color",None),"#10283F")
                    self.assertEqual(color(v["visualContainerObjects"],"border","color",None),"#294761")
                    self.assertEqual(color(v["visualContainerObjects"],"title","fontColor",None),"#EAF3FF")
                    self.assertTrue(v["query"]["queryState"])
                    if ident in SLICERS:
                        for field in ("items","header"):
                            self.assertEqual(color(v["objects"],field,"background",None),"#10283F")
                            self.assertEqual(color(v["objects"],field,"fontColor",None),"#EAF3FF")
            rail=node(edition,PAGE,RAIL)
            self.assertEqual(rail["visual"]["visualType"],"shape")
            self.assertEqual(color(rail["visual"]["objects"],"fill","fillColor",None),"#10283F")
            total=node(edition,PAGE,"e55be8bdbcb32fe34d4a")["visual"]["objects"]["labels"][0]["properties"]
            self.assertEqual(total["labelDisplayUnits"]["expr"]["Literal"]["Value"],"1000000000D")

    def test_turkish_legend_categories_replaced_with_real_english_column(self):
        ids=[
            (PAGE,"1c4d73ece1a64f57c0fc"),
            (PAGE,"9c728e8d682165354da4"),
            (PAGE,"fc1a64c02f7fb0bab2b1"),
            ("91edaa93bbbdbbc8e854","e5dae0006cde1b7f40ff"),
        ]
        for edition in ("workspace","offline-demo"):
            for page,ident in ids:
                data=node(edition,page,ident)["visual"]
                raw=json.dumps(data,ensure_ascii=False)
                with self.subTest(edition=edition,page=page,ident=ident):
                    self.assertIn("fct_transfer_market_value_analysis."+ENGLISH_DIRECTION,raw)
                    self.assertNotIn("yon_etiketi_tr",raw)
            model=(source(edition)/"Model"/"definition"/"tables"/"fct_transfer_market_value_analysis.tmdl").read_text(encoding="utf-8-sig")
            self.assertIn("sourceColumn: market_value_direction_after_transfer",model)
            for token in ("Tüm Sezonlar","Oyuncu secilmedi","Transfer & Piyasa Değeri"):
                self.assertNotIn(token,model[:model.index("\tcolumn transfer_key")])
            self.assertIn('"All seasons"',model)
            self.assertIn('"No player selected"',model)
            self.assertIn("Transfer & Market Value",model)


    def test_prediction_drillthrough_fallback_is_english(self):
        for edition in ("workspace","offline-demo"):
            model=(source(edition)/"Model"/"definition"/"tables"/"ml_player_market_value_current_predictions.tmdl").read_text(encoding="utf-8-sig")
            self.assertIn('"No player selected"',model)
            self.assertNotIn('"Oyuncu secilmedi"',model)


if __name__=="__main__":
    unittest.main()
