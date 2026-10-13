"""Focused unit tests for the source-only NEXUS Power BI product guard."""
import tempfile
import unittest
from pathlib import Path
from scripts.check_powerbi_nexus_product import HEX, LEGACY, detail_visuals


class ProductSourceTests(unittest.TestCase):
    def test_legacy_palette_case_independent(self):
        colors = {c.upper() for c in HEX.findall('{"a":"#285d3d","b":"#4EA8FF"}')}
        self.assertEqual(colors & LEGACY, {"#285D3D"})

    def test_detail_visual_registry_uses_directory_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = (Path(temp) / "Report" / "definition" / "pages" /
                      "MLPlayerDetail" / "visuals" / "visual123")
            folder.mkdir(parents=True)
            (folder / "visual.json").write_text('{"name":"visual123","visual":{"visualType":"card"}}')
            result = detail_visuals(Path(temp), "MLPlayerDetail")
            self.assertEqual(list(result), ["visual123"])
            self.assertEqual(result["visual123"]["visual"]["visualType"], "card")


if __name__ == "__main__":
    unittest.main()
