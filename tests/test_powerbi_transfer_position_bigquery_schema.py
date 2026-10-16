"""Ensure market-value visuals reference the real BigQuery position column.

Based on a Power BI Desktop native visual error captured 16 Oct 2026:
missing fct_transfer_market_value_analysis.position_tr.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class TransferPositionBinding(unittest.TestCase):
    def test_position_property_is_backed_by_real_mart_column(self):
        for edition in ('workspace','offline-demo'):
            base=ROOT/'powerbi'/edition/'FootballPlayerAnalysis'
            model=(base/'Model'/'definition'/'tables'/'fct_transfer_market_value_analysis.tmdl').read_text(encoding='utf-8-sig')
            self.assertIn('\tcolumn position\n',model)
            self.assertNotIn('\tcolumn position_tr\n',model)
            self.assertNotIn('fct_transfer_market_value_analysis[position_tr]',model)
            for ident in ('0839d8ed3d7479a01f32','13ccac612fab8060cf67','fe3412c355304a9a3162'):
                path=base/'Report'/'definition'/'pages'/'292e3d92e92693c05047'/'visuals'/ident/'visual.json'
                node=json.loads(path.read_text(encoding='utf-8-sig'))
                source=json.dumps(node,ensure_ascii=False)
                with self.subTest(edition=edition,visual=ident):
                    self.assertNotIn('position_tr',source)
                    self.assertIn('fct_transfer_market_value_analysis.position',source)
                    self.assertEqual(node['name'],ident)

if __name__=='__main__':
    unittest.main()
