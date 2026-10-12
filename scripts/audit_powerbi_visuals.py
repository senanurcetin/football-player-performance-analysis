#!/usr/bin/env python3
"""Offline PBIR structural audit; does not replace Power BI Desktop rendering."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

DECORATION = {"actionButton", "shape", "textbox", "image", "slicer"}
FORBIDDEN = {"#B7D9D8", "#476A7A", "#F6FBF5"}
SCHEMA_ROOT = "visualContainerObjects"
TABLE_COL = re.compile(r"^\s+column\s+(?:'([^']+)'|([^\s=]+))", re.M)
TABLE_MEA = re.compile(r"^\s+measure\s+'([^']+)'\s*=", re.M)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def model_fields(model: Path):
    fields = {}
    for path in (model / "definition" / "tables").glob("*.tmdl"):
        content = path.read_text(encoding="utf-8-sig")
        cols = {a or b for a, b in TABLE_COL.findall(content)}
        measures = set(TABLE_MEA.findall(content))
        fields[path.stem] = cols | measures
    return fields


def references(value):
    if isinstance(value, dict):
        for kind in ("Column", "Measure"):
            node = value.get(kind)
            if isinstance(node, dict):
                entity = node.get("Expression", {}).get("SourceRef", {}).get("Entity")
                property_name = node.get("Property")
                if entity and property_name:
                    yield entity, property_name
        for child in value.values():
            yield from references(child)
    elif isinstance(value, list):
        for child in value:
            yield from references(child)


def audit(root: Path, mode: str):
    base = root / "powerbi" / mode / "FootballPlayerAnalysis"
    report = base / "Report" / "definition"
    tables = model_fields(base / "Model")
    errors, warnings = [], []
    metadata = read_json(report / "pages" / "pages.json")
    ordered = metadata.get("pageOrder", [])
    if len(ordered) != len(set(ordered)):
        errors.append("Duplicate page identifiers in pageOrder")
    if metadata.get("activePageName") != ordered[0]:
        warnings.append("Report does not open on first page (Home)")
    summary = []
    all_pages = set()
    for page_path in sorted((report / "pages").glob("*/page.json")):
        page = read_json(page_path)
        page_id = page_path.parent.name
        all_pages.add(page_id)
        if page.get("name") != page_id:
            errors.append(f"{page_id}: page.name and directory differ")
        pwidth, pheight = page.get("width", 1280), page.get("height", 720)
        charts, count, watermark = 0, 0, False
        for vp in sorted((page_path.parent / "visuals").glob("*/visual.json")):
            count += 1
            try:
                visual = read_json(vp)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{vp}: invalid JSON: {exc}")
                continue
            if visual.get("name") != vp.parent.name:
                errors.append(f"{vp}: visual.name and directory differ")
            if SCHEMA_ROOT in visual:
                errors.append(f"{vp}: visualContainerObjects must not be root")
            kind = visual.get("visual", {}).get("visualType")
            state = visual.get("visual", {}).get("query", {}).get("queryState", {})
            if kind not in DECORATION and kind:
                charts += 1
                if not state:
                    errors.append(f"{vp}: data visual has no queryState")
            for entity, prop in set(references(state)):
                if entity not in tables:
                    errors.append(f"{vp}: unknown model table {entity}")
                elif prop not in tables[entity]:
                    errors.append(f"{vp}: unknown field {entity}.{prop}")
            box = visual.get("position", {})
            if pwidth and pheight and all(k in box for k in ("x", "y", "width", "height")):
                x, y, w, h = (box[k] for k in ("x", "y", "width", "height"))
                if min(w, h) <= 0 or x < -2 or y < -2 or x + w > pwidth + 2 or y + h > pheight + 2:
                    warnings.append(f"{vp}: outside page bounds")
            raw = json.dumps(visual, ensure_ascii=False)
            watermark |= "SYNTHETIC DEMO" in raw
            for color in FORBIDDEN:
                if color.lower() in raw.lower():
                    warnings.append(f"{vp}: legacy green/teal color {color}")
        display = page.get("displayName", page_id)
        is_main = pwidth >= 1200 and pheight >= 700
        exempt = any(x in display.lower() for x in ("home", "closing", "tooltip"))
        if is_main and not exempt and page.get("visibility") != "HiddenInViewMode" and charts == 0:
            errors.append(f"{display}: analytics page has ZERO data visuals")
        if mode == "offline-demo" and is_main and not watermark:
            errors.append(f"{display}: missing on-page synthetic demo watermark")
        summary.append({"page": display, "visuals": count, "data_visuals": charts,
                        "watermark": watermark})
    for page_id in ordered:
        if page_id not in all_pages:
            errors.append(f"pageOrder references absent page {page_id}")
    if set(ordered) != all_pages:
        warnings.append("pageOrder does not exactly match page directories")
    return {"mode": mode, "pages": len(summary), "visuals": sum(s["visuals"] for s in summary),
            "data_visuals": sum(s["data_visuals"] for s in summary),
            "model_tables": len(tables), "page_details": summary,
            "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--mode", choices=("both", "offline-demo", "workspace"), default="both")
    args = parser.parse_args()
    modes = ("offline-demo", "workspace") if args.mode == "both" else (args.mode,)
    reports = [audit(args.repository, mode) for mode in modes]
    print(json.dumps(reports, indent=2, ensure_ascii=False))
    return 1 if any(r["errors"] for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
