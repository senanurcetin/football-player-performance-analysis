"""Targeted regression for clipped text and truncated KPI in real Power BI Desktop.

Source checks only: final pixel-level acceptance requires opening refreshed PBIP.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE="FootballPlayerAnalysis"
CASES={
 ("5cb4db7e746975558322","be100000000000000001"):{"height":42,"min_gutter":30},
 ("5cb4db7e746975558322","8d1dcd7736f6bd9649c7"):{"height":30,"min_gutter":25},
 ("292e3d92e92693c05047","e7c73867bb304fc4319a"):{"height":24,"min_gutter":15},
 ("292e3d92e92693c05047","a0b7c05588a1b12ea7ee"):{"height":34,"min_gutter":22},
}

class VisibleTextSafeBounds(unittest.TestCase):
    def test_headline_and_secondary_label_have_room_to_render(self):
        for edition in ("workspace","offline-demo"):
            base=ROOT/"powerbi"/edition/BASE
            for (page,ident),info in CASES.items():
                path=base/"Report"/"definition"/"pages"/page/"visuals"/ident/"visual.json"
                obj=json.loads(path.read_text(encoding="utf-8-sig"))
                with self.subTest(edition=edition,visual=ident):
                    self.assertEqual(obj["visual"]["visualType"],"textbox")
                    self.assertGreaterEqual(obj["position"]["height"],info["height"])
                    self.assertGreater(obj["position"]["height"],info["min_gutter"])
                    self.assertLess(obj["position"]["y"]+obj["position"]["height"],136)
            head=json.loads((base/"Report"/"definition"/"pages"/"5cb4db7e746975558322"/"visuals"/"be100000000000000001"/"visual.json").read_text(encoding="utf-8-sig"))
            subtitle=json.loads((base/"Report"/"definition"/"pages"/"5cb4db7e746975558322"/"visuals"/"8d1dcd7736f6bd9649c7"/"visual.json").read_text(encoding="utf-8-sig"))
            self.assertLess(head["position"]["y"]+head["position"]["height"],subtitle["position"]["y"])

    def test_transfer_count_card_keeps_compact_numeric_format(self):
        for edition in ("workspace","offline-demo"):
            path=ROOT/"powerbi"/edition/BASE/"Model"/"definition"/"tables"/"fct_transfer_market_value_analysis.tmdl"
            text=path.read_text(encoding="utf-8-sig")
            marker="measure 'Transfer Count' = DISTINCTCOUNT(fct_transfer_market_value_analysis[transfer_key])"
            self.assertIn(marker,text)
            self.assertIn('formatString: #,0\n',text[text.index(marker):text.index(marker)+120])
            self.assertNotIn('formatString: #,0 "transfers"',text[text.index(marker):text.index(marker)+120])

if __name__ == "__main__":
    unittest.main()
