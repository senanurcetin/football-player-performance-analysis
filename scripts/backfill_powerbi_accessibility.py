#!/usr/bin/env python3
"""Audit or fill missing native Power BI data-visual accessibility descriptions.

Source-only. Derives labels from existing visual type, title and query
projections; never changes queries, coordinates, model partitions or data.
Existing editorial alt text is left intact.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = ("workspace", "offline-demo")
FILTERS = {"slicer", "advancedSlicerVisual"}
TABLES = {"tableEx", "pivotTable"}
CARDS = {"card", "multiRowCard"}
CHARTS = {
    "clusteredBarChart", "clusteredColumnChart", "scatterChart",
    "donutChart", "treemap", "lineStackedColumnComboChart",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def plain(text: str) -> str:
    """Sanitize extracted Power BI literals for TMDL quote-safe UI prose."""
    value = text.strip().strip("'")
    value = re.sub(r"([a-z])([A-Z])", r"\1 \2", value)
    value = re.sub(r"[_\s]+", " ", value).replace("'", "")
    return value.strip(" .:\n\t")


def query_fields(node: dict) -> list[str]:
    fields: list[str] = []

    def visit(item: object) -> None:
        if isinstance(item, dict):
            for key, value in item.items():
                if key in {"Measure", "Column"} and isinstance(value, dict):
                    name = value.get("Property")
                    if isinstance(name, str):
                        cleaned = plain(name)
                        if cleaned and cleaned not in fields:
                            fields.append(cleaned)
                visit(value)
        elif isinstance(item, list):
            for value in item:
                visit(value)

    visit(node.get("visual", {}).get("query", {}).get("queryState", {}))
    return fields


def visual_title(node: dict) -> str:
    title = node.get("visual", {}).get("visualContainerObjects", {}).get("title", [])
    if not title:
        return ""
    text = title[0].get("properties", {}).get("text", {})
    return plain(text.get("expr", {}).get("Literal", {}).get("Value", ""))


def accessible_description(node: dict) -> str:
    kind = node["visual"]["visualType"]
    fields = query_fields(node)
    title = visual_title(node)
    headline = title or ", ".join(fields[:2]) or "Report data"
    if kind in FILTERS:
        content = f"Interactive filter for {', '.join(fields[:3]) or headline}. Selection changes connected report visuals."
    elif kind in CARDS:
        content = f"Key performance indicator: {headline}. Calculated from the current report filter context."
    elif kind in TABLES:
        content = f"Data table: {headline}. Displays {', '.join(fields[:3]) or 'model fields'} for the current filters."
    elif kind in CHARTS:
        content = f"{kind.replace('Chart', ' chart')}: {headline}. Uses {', '.join(fields[:3]) or 'bound model values'} under the current filters."
    else:
        content = f"Data visual: {headline}. Responds to the current report filters."
    content = plain(content)
    if len(content) > 245:
        content = content[:245].rsplit(" ", 1)[0].rstrip(" .")
    return content + ("." if not content.endswith(".") else "")


def has_description(node: dict) -> bool:
    visual = node.get("visual", {})
    general = visual.get("visualContainerObjects", {}).get("general", [])
    if not general:
        return False
    props = general[0].get("properties", {})
    text = props.get("altText", {}).get("expr", {}).get("Literal", {}).get("Value", "")
    return bool(plain(text))


def update_visual(node: dict) -> bool:
    if not node.get("visual", {}).get("query", {}).get("queryState"):
        return False
    if has_description(node):
        return False
    visual = node["visual"]
    container = visual.setdefault("visualContainerObjects", {})
    general = container.setdefault("general", [])
    if not general:
        general.append({"properties": {}})
    props = general[0].setdefault("properties", {})
    props["altText"] = {
        "expr": {"Literal": {"Value": "'" + accessible_description(node) + "'"}}
    }
    return True


def audit(root: Path, apply: bool = False) -> dict:
    results = {}
    for edition in EDITIONS:
        pages = (root / "powerbi" / edition / "FootballPlayerAnalysis" /
                 "Report" / "definition" / "pages")
        total = 0
        changed = 0
        missing = []
        for path in sorted(pages.glob("*/visuals/*/visual.json")):
            node = load(path)
            if not node.get("visual", {}).get("query", {}).get("queryState"):
                continue
            total += 1
            if update_visual(node):
                changed += 1
                missing.append(str(path.relative_to(root)).replace("\\", "/"))
                if apply:
                    path.write_text(json.dumps(node, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")
        results[edition] = {
            "data_visuals": total,
            "missing_before": changed,
            "modified": changed if apply else 0,
            "remaining_after": 0 if apply else changed,
            "paths": missing,
        }
    return results


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true",
                   help="Edit only missing altText in source PBIR data visuals")
    p.add_argument("--repository", type=Path, default=ROOT)
    p.add_argument("--compact", action="store_true")
    args = p.parse_args()
    results = audit(args.repository, apply=args.apply)
    if args.compact:
        for edition, stat in results.items():
            print(f"{edition}: data={stat['data_visuals']} missing_before="
                  f"{stat['missing_before']} modified={stat['modified']}")
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
