"""Enforce portfolio-only production provenance without altering the offline fixture.

This is a static source contract, not proof of a successful Desktop refresh.
"""
from pathlib import Path
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "powerbi" / "workspace" / "FootballPlayerAnalysis"
FIXTURE = ROOT / "powerbi" / "offline-demo" / "FootballPlayerAnalysis"
LOGO = "NEXUS_Official_Transparent_Logo.png"
LOGO_SHA = "6faaa1ec7fd4a849c3cffe3fa424f3aba9fe9ab6"
PALETTE = (
    "#4EA8FF", "#8F9BFF", "#00E0FF", "#6E55C6",
    "#76B8FF", "#B9C5CE", "#376DBE", "#B3A4F6",
)
REAL_TABLES = (
    "fct_player_performance", "fct_club_performance",
    "fct_transfer_market_value_analysis", "fct_club_risk_profile",
)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git_blob_sha(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


class ProductionPortfolioSourceContract(unittest.TestCase):
    def test_registered_official_brand_is_pixel_asset_from_approved_pack(self):
        for edition in (PROD, FIXTURE):
            report = edition / "Report"
            logo = (report / "StaticResources" / "RegisteredResources" / LOGO).read_bytes()
            self.assertEqual(git_blob_sha(logo), LOGO_SHA)
            self.assertTrue(logo.startswith(b"\x89PNG\r\n\x1a\n"))
            manifest = read(report / "definition" / "report.json")
            resources = next(p["items"] for p in manifest["resourcePackages"]
                             if p["name"] == "RegisteredResources")
            self.assertIn({"name": LOGO, "path": LOGO, "type": "Image"}, resources)
            theme = read(report / "StaticResources" / "RegisteredResources" /
                         "NEXUSMidnight-20261016-v3.json")
            self.assertEqual(theme["dataColors"], list(PALETTE))

    def test_portfolio_pages_are_real_edition_without_development_badges(self):
        prod_pages = PROD / "Report" / "definition" / "pages"
        fixture_pages = FIXTURE / "Report" / "definition" / "pages"
        ids = [p.name for p in prod_pages.iterdir() if (p / "page.json").exists()]
        self.assertEqual(len(ids), 13)
        self.assertEqual(set(ids), {p.name for p in fixture_pages.iterdir()
                                   if (p / "page.json").exists()})
        for pid in ids:
            page = read(prod_pages / pid / "page.json")
            self.assertFalse(page["displayName"].upper().startswith("[DEMO]"))
            for p in (prod_pages / pid / "visuals").glob("*/visual.json"):
                visual = read(p)["visual"]
                if visual["visualType"] != "textbox":
                    continue
                for paragraph in visual.get("objects", {}).get("general", [{}])[0].get(
                        "properties", {}).get("paragraphs", []):
                    for item in paragraph.get("textRuns", []):
                        displayed = item.get("value", "").upper()
                        self.assertNotIn("SYNTHETIC", displayed, str(p))
                        self.assertNotIn("NOT REAL DATA", displayed, str(p))
                        self.assertNotIn("DEMO", displayed, str(p))

    def test_real_data_import_connections_are_unchanged_bigquery_marts(self):
        for table in REAL_TABLES:
            p = PROD / "Model" / "definition" / "tables" / f"{table}.tmdl"
            source = p.read_text(encoding="utf-8-sig")
            with self.subTest(table=table):
                self.assertIn('GoogleBigQuery.Database([Implementation="2.0",UseStorageApi=false])', source)
                self.assertIn('Name="data-analiz-490513"', source)
                self.assertIn('Name="football_mart",Kind="Schema"', source)
                self.assertIn(f'Name="{table}",Kind="Table"', source)
        risk = (PROD / "Model" / "definition" / "tables" /
                "fct_club_risk_profile.tmdl").read_text(encoding="utf-8-sig")
        self.assertIn('"avg_overpay_pct", each if _ = null then null else Number.From(_)', risk)
        rates = (PROD / "Model" / "definition" / "tables" /
                 "fct_club_performance.tmdl").read_text(encoding="utf-8-sig")
        self.assertIn('"win_rate", each if _ = null then null else Number.From(_) / 100', rates)


if __name__ == "__main__":
    unittest.main()
