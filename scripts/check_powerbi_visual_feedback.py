#!/usr/bin/env python3
"""Verify screenshot-driven NEXUS Football PBIR source fixes without CI or Desktop.

Source checks only: do NOT certify render, refresh, color contrast or DAX results.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "d2bc1e6a078c5c5b125c": ("d8d9c792b1d0787a492e", "dc86a3b8089569065768"),
    "24c53960ddc19662d824": ("90e95677c958b7987ea7", "02bd36bd0844b7569d73"),
    "25f58efd2bb140e62be9": ("a3a77965b7e55a40ee82", "440c187d69a21a50015c"),
    "4c63ad904b1db6e0d156": ("7b333c65907240a1d5c3", "7c00d835949e831b0215"),
    "292e3d92e92693c05047": ("5263aba2cae1d9605ac0", "f531f6e3675221356cb2"),
    "1f4c5c8000149b2e2be8": ("8f4e836b8670592e2788", "25e9b528c82342d1d729"),
}
NAV_TARGETS = {
    "5cb4db7e746975558322": "H",
    "d2bc1e6a078c5c5b125c": "P",
    "24c53960ddc19662d824": "S",
    "25f58efd2bb140e62be9": "C",
    "4c63ad904b1db6e0d156": "T",
    "292e3d92e92693c05047": "V",
    "1f4c5c8000149b2e2be8": "M",
}


def literal(obj):
    return obj["expr"]["Literal"]["Value"].strip("'")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def inspect(root=ROOT):
    errors = []
    for edition in ("workspace", "offline-demo"):
        base = root / "powerbi" / edition / "FootballPlayerAnalysis" / "Report" / "definition" / "pages"
        for page, (rail, header) in PAGES.items():
            directory = base / page / "visuals"
            try:
                for visual_id, expected in ((rail, "#091E33"), (header, "#102B47")):
                    visual = load(directory / visual_id / "visual.json")
                    value = visual["visual"]["objects"]["fill"][0]["properties"]["fillColor"]["solid"]["color"]
                    if literal(value) != expected:
                        errors.append(f"{edition}/{page}/{visual_id}: expected {expected} sidebar/header")
                links = {}
                for path in directory.glob("*/visual.json"):
                    visual = load(path).get("visual", {})
                    if visual.get("visualType") != "actionButton":
                        continue
                    vco = visual.get("visualContainerObjects", {})
                    if "visualLink" not in vco:
                        continue
                    link = vco["visualLink"][0]["properties"]
                    if literal(link["type"]) != "PageNavigation":
                        continue
                    target = literal(link["navigationSection"])
                    texts = visual["objects"].get("text", [])
                    defaults = [x for x in texts if x.get("selector", {}).get("id") == "default"
                                and "text" in x.get("properties", {})]
                    label = literal(defaults[0]["properties"]["text"]) if defaults else None
                    if label != NAV_TARGETS.get(target):
                        errors.append(f"{edition}/{page}: navigation {target} label {label!r}")
                    links[target] = label
                if set(links) != set(NAV_TARGETS):
                    errors.append(f"{edition}/{page}: expected seven native sidebar links")
            except (OSError, KeyError, IndexError, ValueError) as exc:
                errors.append(f"{edition}/{page}: invalid PBIR source: {exc}")
        for page, ids in (
            ("5cb4db7e746975558322", [f"be10000000000000000{i}" for i in range(1, 8)]),
            ("c83db10673c28e3346ae", ["be100000000000000008", "be100000000000000009", "be10000000000000000a"]),
        ):
            for vid in ids:
                try:
                    node = load(base / page / "visuals" / vid / "visual.json")
                    state = node["visual"]["visualContainerObjects"]["background"][0]["properties"]["show"]
                    if literal(state) != "false":
                        errors.append(f"{edition}/{page}/{vid}: white textbox background not disabled")
                except (OSError, ValueError, KeyError, IndexError) as exc:
                    errors.append(f"{edition}/{page}/{vid}: missing transparent textbox: {exc}")
        seg = base / "24c53960ddc19662d824" / "visuals"
        market = load(seg / "a7e10000000000000004" / "visual.json")
        if market["visual"]["visualType"] != "clusteredBarChart":
            errors.append(f"{edition}: market value category comparison is not a bar chart")
    fixture = (root / "powerbi" / "offline-demo" / "FootballPlayerAnalysis" /
               "Model" / "definition" / "tables" / "fct_club_risk_profile.tmdl")
    try:
        content = fixture.read_text(encoding="utf-8-sig")
        records = re.findall(r'^\s*\{\d+, "Demo [^"]+".*\},?\s*$', content, flags=re.M)
        if len(records) != 6:
            errors.append(f"Risk fixture: expected six rows, found {len(records)}")
        for index, record in enumerate(records, 1):
            if re.search(r',\s*"\d+\.\d+"', record):
                errors.append(f"Risk fixture row {index}: quoted number in typed numeric field")
            if not re.search(r',\s*false,\s*"insufficient_data"\}', record):
                errors.append(f"Risk fixture row {index}: small sample category or flag inconsistent")
    except OSError as exc:
        errors.append(f"Risk fixture: {exc}")
    return errors


def main():
    issues = inspect()
    for issue in issues:
        print("FAIL:", issue)
    if issues:
        raise SystemExit(1)
    print("Source-only visual feedback guard PASS (Desktop refresh/render remains unverified).")


if __name__ == "__main__":
    main()
