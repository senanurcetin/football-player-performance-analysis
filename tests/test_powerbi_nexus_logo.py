"""Source-only acceptance for the canonical NEXUS logo in editable PBIR reports.

This verifies bytes, registry, PBIR image URLs and basic geometry.
Power BI Desktop render and visual contrast still require manual acceptance.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "nexus-brand-original-20261013.png"
CROPPED = "nexus-wordmark-crop.svg"
ORIGINAL_BLOB = "e8a72df6f117ef1cbcc0002e28395b50cc752c74"
PAGES = (
    "5cb4db7e746975558322",  # Home
    "d2bc1e6a078c5c5b125c",  # Performance
    "24c53960ddc19662d824",  # Segmentation
    "25f58efd2bb140e62be9",  # Clubs
    "4c63ad904b1db6e0d156",  # 365d transfer outcomes
    "292e3d92e92693c05047",  # Transfer and value
    "1f4c5c8000149b2e2be8",  # Valuation
    "MLModelPerformance",      # ML reliability
    "c83db10673c28e3346ae",  # Closing
    "91edaa93bbbdbbc8e854",  # Transfer drillthrough
    "MLPlayerDetail",          # Prediction drillthrough
)
DARK_HEADER_LOGOS = {PAGES[i] for i in (1, 2, 3, 4, 5, 6, 7)}
ANALYTIC_TITLES = {
    PAGES[2]: "a7e10000000000000005",
    PAGES[3]: "a7e20000000000000005",
    PAGES[4]: "a7e30000000000000005",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git_blob_sha(blob: bytes) -> str:
    return hashlib.sha1(f"blob {len(blob)}\0".encode() + blob).hexdigest()


class NexusLogoSourceContract(unittest.TestCase):
    def test_exact_canonical_brand_asset_in_both_source_editions(self):
        payloads = []
        for edition in ("workspace", "offline-demo"):
            report = ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Report"
            payload = (report / "StaticResources" / "RegisteredResources" / IMAGE).read_bytes()
            self.assertEqual(git_blob_sha(payload), ORIGINAL_BLOB)
            self.assertGreater(len(payload), 50_000)
            payloads.append(payload)
            manifest = read_json(report / "definition" / "report.json")
            registered = next(x for x in manifest["resourcePackages"] if x["name"] == "RegisteredResources")
            entries = [x for x in registered["items"] if x["name"] == IMAGE]
            self.assertEqual(entries, [{"name": IMAGE, "path": IMAGE, "type": "Image"}])
        self.assertEqual(payloads[0], payloads[1])
        for edition in ("workspace", "offline-demo"):
            report = ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Report"
            svg = (report / "StaticResources" / "RegisteredResources" / CROPPED).read_text(encoding="utf-8")
            self.assertIn('viewBox="245 385 535 255"', svg)
            self.assertIn("data:image/png;base64,", svg)
            import base64
            embedded = svg.split("data:image/png;base64,", 1)[1].split('"', 1)[0]
            self.assertEqual(base64.b64decode(embedded), payloads[0])
            registry = read_json(report / "definition" / "report.json")
            items = next(r["items"] for r in registry["resourcePackages"]
                         if r["name"] == "RegisteredResources")
            self.assertIn({"name": CROPPED, "path": CROPPED, "type": "Image"}, items)

    def test_each_full_size_page_contains_native_registered_logo(self):
        for edition in ("workspace", "offline-demo"):
            root = ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Report" / "definition" / "pages"
            for i, page in enumerate(PAGES, 1):
                visual_id = "b6a" + str(i).zfill(17)
                with self.subTest(edition=edition, page=page):
                    path = root / page / "visuals" / visual_id / "visual.json"
                    node = read_json(path)
                    self.assertEqual(node["name"], visual_id)
                    self.assertEqual(node["visual"]["visualType"], "image")
                    self.assertNotIn("query", node["visual"])
                    package = node["visual"]["objects"]["general"][0]["properties"]["imageUrl"]["expr"]["ResourcePackageItem"]
                    expected = CROPPED
                    self.assertEqual(package, {
                        "PackageName": "RegisteredResources",
                        "PackageType": 1,
                        "ItemName": expected,
                    })
                    vco = node["visual"]["visualContainerObjects"]
                    self.assertEqual(vco["title"][0]["properties"]["show"]["expr"]["Literal"]["Value"], "false")
                    self.assertEqual(vco["background"][0]["properties"]["show"]["expr"]["Literal"]["Value"], "false")
                    self.assertTrue(vco["general"][0]["properties"]["altText"]["expr"]["Literal"]["Value"])
                    p = node["position"]
                    self.assertGreaterEqual(p["x"], 0)
                    self.assertGreaterEqual(p["y"], 0)
                    self.assertGreater(p["width"], 0)
                    self.assertGreater(p["height"], 0)
                    self.assertLessEqual(p["x"] + p["width"], 1280)
                    self.assertLessEqual(p["y"] + p["height"], 720)
                    if page in DARK_HEADER_LOGOS:
                        self.assertLessEqual(p["y"] + p["height"], 72)
                    if page in ANALYTIC_TITLES:
                        heading = read_json(root / page / "visuals" / ANALYTIC_TITLES[page] / "visual.json")
                        self.assertLessEqual(p["x"] + p["width"], heading["position"]["x"])

    def test_home_hero_copy_does_not_overlap_logo_surface(self):
        for edition in ("workspace", "offline-demo"):
            page = ROOT / "powerbi" / edition / "FootballPlayerAnalysis" / "Report" / "definition" / "pages" / PAGES[0]
            logo = read_json(page / "visuals" / "b6a00000000000000001" / "visual.json")
            left = logo["position"]["x"]
            for i in (1, 2, 3):
                node = read_json(page / "visuals" / f"be10000000000000000{i}" / "visual.json")
                a, b = node["position"], logo["position"]
                intersects = (
                    max(a["x"], b["x"]) < min(a["x"] + a["width"], b["x"] + b["width"])
                    and max(a["y"], b["y"]) < min(a["y"] + a["height"], b["y"] + b["height"])
                )
                self.assertFalse(intersects, "Signature logo must clear cover typography")


if __name__ == "__main__":
    unittest.main()
