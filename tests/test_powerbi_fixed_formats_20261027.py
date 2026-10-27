"""Offline regression guard for 27 October Power BI formatting fixes.

Checks PBIR source only. It does NOT assert that Desktop has rerendered the
report; old PNGs remain faithful records of the previous format defects.
"""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PBIP=ROOT/"powerbi"/"workintech-20261027"/"FootballPlayerAnalysis"
VISUALS=PBIP/"Report"/"definition"/"pages"

class TestPowerBIFixedFormats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.visual_files=list(VISUALS.rglob("visual.json"))

    def test_full_report_preserved(self):
        self.assertEqual(len(self.visual_files),308)
        self.assertEqual(sum(p.is_dir() for p in VISUALS.iterdir()),13)
        self.assertTrue((PBIP/"FootballPlayerAnalysis.pbip").is_file())

    def test_fee_premium_percent_must_not_use_million_display_units(self):
        p=VISUALS/"292e3d92e92693c05047"/"visuals"/"0839d8ed3d7479a01f32"/"visual.json"
        d=json.loads(p.read_text("utf8"))
        obj=d["visual"]["objects"]
        for axis in ("valueAxis","labels"):
            with self.subTest(axis=axis):
                self.assertEqual(
                    obj[axis][0]["properties"]["labelDisplayUnits"]["expr"]["Literal"]["Value"],
                    "1D")
        projection=d["visual"]["query"]["queryState"]["Y"]["projections"][0]
        self.assertIn("Average Fee Premium Discount %",projection["queryRef"])

    def test_tooltip_money_formats_scale_instead_of_adding_literal_m(self):
        for page,visual in (
            ("tooltip_transfer_p011","tt011_stats_0001"),
            ("tooltip_pred_p012","tt012_stats_0001"),
        ):
            with self.subTest(page=page):
                p=VISUALS/page/"visuals"/visual/"visual.json"
                d=json.loads(p.read_text("utf8"))
                projections=d["visual"]["query"]["queryState"]["Values"]["projections"]
                self.assertEqual(projections[0]["format"],'€0.0,,"M"')
                self.assertIn("Average ",projections[0]["queryRef"])
                self.assertNotEqual(projections[0]["format"],"€0.0M")

    def test_donut_category_name_is_kept_in_legend(self):
        p=VISUALS/"1f4c5c8000149b2e2be8"/"visuals"/"3ccd5a45594119af9bb7"/"visual.json"
        d=json.loads(p.read_text("utf8"))
        obj=d["visual"]["objects"]
        self.assertEqual(
            obj["labels"][0]["properties"]["labelStyle"]["expr"]["Literal"]["Value"],
            "'Percent of total'")
        self.assertEqual(
            obj["legend"][0]["properties"]["show"]["expr"]["Literal"]["Value"],
            "true")

    def test_no_replacement_pngs_claiming_fresh_desktop_render(self):
        manifest=json.loads((ROOT/"docs/assets/screenshots/capture_manifest.json").read_text("utf8"))
        self.assertEqual(manifest["captured"],"2026-10-27")
        self.assertEqual(len(manifest["captures"]),13)
        self.assertTrue(all(r["sha256"] for r in manifest["captures"]))

if __name__=="__main__":
    unittest.main()
