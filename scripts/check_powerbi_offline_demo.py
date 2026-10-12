#!/usr/bin/env python3
"""Offline PBIP static checks. This does not run Desktop or certify report visuals."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "powerbi" / "offline-demo" / "FootballPlayerAnalysis"
PROD = ROOT / "powerbi" / "workspace" / "FootballPlayerAnalysis"
errors = []

def check(condition, description):
    if not condition:
        errors.append(description)

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        errors.append(f"Missing/bad JSON: {path.relative_to(ROOT)} ({exc})")
        return {}

def main():
    check((DEMO / "FootballPlayerAnalysis.pbip").is_file(), "Missing offline PBIP entry")
    check((DEMO / "Model" / "definition.pbism").is_file(), "Missing offline semantic model")
    check((DEMO / "Report" / "definition.pbir").is_file(), "Missing offline report")
    demo_tables = DEMO / "Model" / "definition" / "tables"
    originals = PROD / "Model" / "definition" / "tables"
    physical = [p for p in originals.glob("*.tmdl") if not
                p.name.startswith(("LocalDateTable_", "DateTableTemplate_"))]
    check(len(physical) == 33, f"Expected 33 source tables; found {len(physical)}")
    for file in physical:
        copy = demo_tables / file.name
        check(copy.exists(), f"Missing demo table {file.name}")
        if not copy.exists():
            continue
        original_text = file.read_text(encoding="utf-8-sig")
        text = copy.read_text(encoding="utf-8-sig")
        check("GoogleBigQuery.Database(" in original_text,
              f"Production query modified or absent in {file.name}")
        check("GoogleBigQuery.Database(" not in text,
              f"Unconverted cloud data source in demo {file.name}")
        check(re.search(r"^\s*#table\(", text, re.MULTILINE) is not None,
              f"Missing inline sample table in {file.name}")
        source_columns = re.findall(r"^\s+sourceColumn: (.+)$", original_text, re.MULTILINE)
        for col in source_columns:
            if col.startswith("[") or col.endswith("]"):
                continue  # auto date / calculated field
            name = '#"' + col.replace('"', '""') + '"'
            check(name in text, f"Missing physical source column {col} in {file.name}")
    page_root = DEMO / "Report" / "definition" / "pages"
    pages = load_json(page_root / "pages.json")
    for page_id in pages.get("pageOrder", []):
        page = load_json(page_root / page_id / "page.json")
        check(page.get("displayName", "").startswith("[DEMO]"),
              f"Demo label missing on page {page_id}")
    for vpath in page_root.glob("*/visuals/*/visual.json"):
        v = load_json(vpath)
        check("visualContainerObjects" not in v,
              f"Invalid root-level visualContainerObjects: {vpath.relative_to(ROOT)}")
    check((DEMO / "Report" / "StaticResources").is_dir(), "Missing report resources")
    theme = load_json(DEMO / "Report" / "StaticResources" / "SharedResources" /
                      "BuiltInThemes" / "AccessibleTidal.json")
    check(theme.get("dataColors", [None])[0] == "#4EA8FF",
          "Demo theme differs from NEXUS blue palette")
    if errors:
        print("Offline PBIP checks FAILED:")
        for issue in errors:
            print(" - " + issue)
        return 1
    print(f"Offline PBIP static preflight OK: {len(physical)} inline tables, "
          f"{len(pages.get('pageOrder', []))} labeled pages.")
    print("NOT a Power BI Desktop load, refresh, or chart-rendering test.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
