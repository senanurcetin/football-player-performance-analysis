#!/usr/bin/env python3
"""CI-free, source-only product audit for NEXUS Football Power BI PBIR.

Does not open Power BI Desktop, execute DAX/Power Query, or verify BigQuery data.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EDITIONS = ("workspace", "offline-demo")
HOME = "5cb4db7e746975558322"
CLOSING = "c83db10673c28e3346ae"
DETAIL_PAGES = ("91edaa93bbbdbbc8e854", "MLPlayerDetail")
THEME = "NEXUSMidnight-20261012-v2.json"
LEGACY = {
    "#285D3D", "#2E6B45", "#119A91", "#F6FBF5", "#8BC99A",
    "#6FA56D", "#20323F", "#536A60", "#E6F2E8", "#0F4B3B",
    "#4E91CC", "#75B5EB", "#296393", "#C4E0FF",
}
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
EXPECTED_PAGES = 13
EXPECTED_DETAIL_VISUALS = {"workspace": 16, "offline-demo": 17}
DEMO_DETAIL_WATERMARKS = {
    "91edaa93bbbdbbc8e854": "de9a00000000000000006",
    "MLPlayerDetail": "de9a00000000000000008",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def detail_visuals(project: Path, page: str) -> dict[str, dict]:
    folder = project / "Report" / "definition" / "pages" / page / "visuals"
    return {path.parent.name: load(path) for path in sorted(folder.glob("*/visual.json"))}


def audit(root: Path) -> dict:
    issues: list[str] = []
    editions: dict[str, dict] = {}
    for edition in EDITIONS:
        project = root / "powerbi" / edition / "FootballPlayerAnalysis"
        definition = project / "Report" / "definition"
        try:
            order = load(definition / "pages" / "pages.json")["pageOrder"]
            report = load(definition / "report.json")
            home = load(definition / "pages" / HOME / "page.json")
            closing = load(definition / "pages" / CLOSING / "page.json")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            issues.append(f"{edition}: PBIR metadata unavailable: {exc}")
            continue
        if len(order) != EXPECTED_PAGES or len(set(order)) != EXPECTED_PAGES:
            issues.append(f"{edition}: expected {EXPECTED_PAGES} unique report pages")
        if not order or order[0] != HOME:
            issues.append(f"{edition}: Home is not the opening page")
        titles = ("Home", "Closing") if edition == "workspace" else ("[DEMO] Home", "[DEMO] Closing")
        if (home.get("displayName"), closing.get("displayName")) != titles:
            issues.append(f"{edition}: Home/Closing product tab titles do not match {titles}")
        custom = report.get("themeCollection", {}).get("customTheme", {}).get("name")
        if custom != THEME:
            issues.append(f"{edition}: NEXUS theme not registered (found {custom!r})")
        details: dict[str, dict] = {}
        for page in DETAIL_PAGES:
            try:
                visuals = detail_visuals(project, page)
            except (OSError, ValueError) as exc:
                issues.append(f"{edition}/{page}: unreadable native visuals: {exc}")
                continue
            if len(visuals) != EXPECTED_DETAIL_VISUALS[edition]:
                issues.append(f"{edition}/{page}: expected {EXPECTED_DETAIL_VISUALS[edition]} visuals, found {len(visuals)}")
            if edition == "offline-demo":
                watermark = DEMO_DETAIL_WATERMARKS[page]
                if watermark not in visuals or visuals[watermark].get("visual", {}).get("visualType") != "textbox":
                    issues.append(f"{edition}/{page}: synthetic provenance watermark missing")
            visual_types: dict[str, str] = {}
            bound = 0
            for visual_id, visual in visuals.items():
                if visual.get("name") != visual_id:
                    issues.append(f"{edition}/{page}/{visual_id}: PBIR identity mismatch")
                v = visual.get("visual") or {}
                visual_types[visual_id] = v.get("visualType", "")
                if (v.get("query") or {}).get("queryState"):
                    bound += 1
                colors = {c.upper() for c in HEX.findall(json.dumps(visual))}
                old = sorted(colors & LEGACY)
                if old:
                    issues.append(f"{edition}/{page}/{visual_id}: legacy brand literals {', '.join(old)}")
            if not bound:
                issues.append(f"{edition}/{page}: no data-bound detail visuals")
            details[page] = {"count": len(visuals), "data_bound": bound, "types": visual_types}
        editions[edition] = {"pages": len(order), "home": home.get("displayName"),
                             "closing": closing.get("displayName"), "details": details}
    if all(edition in editions for edition in EDITIONS):
        for page in DETAIL_PAGES:
            prod = editions["workspace"]["details"].get(page, {}).get("types")
            demo = editions["offline-demo"]["details"].get(page, {}).get("types")
            if prod is not None and demo is not None:
                demo_without_label = {visual_id: kind for visual_id, kind in demo.items()
                                      if visual_id != DEMO_DETAIL_WATERMARKS[page]}
                if prod != demo_without_label:
                    issues.append(f"{page}: production/demo shared visuals differ beyond demo watermark")
    for edition in editions.values():
        for page in edition["details"].values():
            page.pop("types", None)  # keep CLI output compact
    return {"status": "PASS" if not issues else "FAIL", "check_type": "PBIR source only",
            "editions": editions, "issues": issues,
            "release_note": "Power BI Desktop render and data-refresh acceptance remains REQUIRED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = audit(args.repository)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Cannot audit Power BI product source: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
