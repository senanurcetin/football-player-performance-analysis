#!/usr/bin/env python3
"""Offline PBIR layout audit; NOT a Power BI Desktop rendering test.

Detect data-visual overlap and out-of-page geometry in both editable report
projects. Decorative shapes, buttons and text are intentionally excluded from
overlap detection because many are designed as background layers.

Usage: python scripts/audit_powerbi_layout.py [--mode both] [--min-overlap 0.15]
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = ("workspace", "offline-demo")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rectangle(position: dict) -> tuple[float, float, float, float] | None:
    values = [position.get(key) for key in ("x", "y", "width", "height")]
    if not all(type(value) in (int, float) and math.isfinite(value) for value in values):
        return None
    x, y, width, height = map(float, values)
    if width <= 0 or height <= 0:
        return None
    return x, y, width, height


def overlap_fraction(a: tuple, b: tuple) -> float:
    """Intersecting area divided by the smaller visual's area."""
    x1, y1, w1, h1 = a
    x2, y2, w2, h2 = b
    dx = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    dy = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    return dx * dy / min(w1 * h1, w2 * h2)


def audit_page(page_path: Path, min_overlap: float) -> dict:
    page = read_json(page_path)
    page_id = page_path.parent.name
    width, height = page.get("width"), page.get("height")
    bounds_valid = (type(width) in (int, float) and type(height) in (int, float)
                    and math.isfinite(width) and math.isfinite(height)
                    and width > 0 and height > 0)
    warnings: list[dict] = []
    data_visuals: list[tuple[str, tuple]] = []
    visual_count = 0
    for path in sorted((page_path.parent / "visuals").glob("*/visual.json")):
        visual_count += 1
        try:
            visual = read_json(path)
        except (OSError, ValueError) as error:
            warnings.append({"type": "invalid_json", "visual": path.parent.name,
                             "detail": str(error)})
            continue
        visual_id = path.parent.name
        rect = rectangle(visual.get("position") or {})
        if rect is None:
            warnings.append({"type": "invalid_rectangle", "visual": visual_id})
            continue
        if bounds_valid:
            x, y, w, h = rect
            if x < -2 or y < -2 or x + w > width + 2 or y + h > height + 2:
                warnings.append({"type": "out_of_bounds", "visual": visual_id,
                                 "rectangle": [x, y, w, h]})
        state = visual.get("visual", {}).get("query", {}).get("queryState", {})
        if isinstance(state, dict) and state:
            data_visuals.append((visual_id, rect))
    if not bounds_valid:
        warnings.append({"type": "invalid_page_size"})
    for i, (left_id, left_box) in enumerate(data_visuals):
        for right_id, right_box in data_visuals[i + 1:]:
            fraction = overlap_fraction(left_box, right_box)
            if fraction >= min_overlap:
                warnings.append({"type": "data_visual_overlap", "visuals": [left_id, right_id],
                                 "fraction_of_smaller_visual": round(fraction, 4)})
    return {"page_id": page_id, "page": page.get("displayName", page_id),
            "visuals": visual_count, "data_visuals": len(data_visuals),
            "warnings": warnings}


def audit_report(root: Path, mode: str, min_overlap: float = 0.15) -> dict:
    page_root = (root / "powerbi" / mode / "FootballPlayerAnalysis" /
                 "Report" / "definition" / "pages")
    pages = sorted(page_root.glob("*/page.json"))
    if not pages:
        raise FileNotFoundError(f"No PBIR pages found: {page_root}")
    data = [audit_page(page, min_overlap) for page in pages]
    return {"mode": mode, "page_count": len(data),
            "data_visual_count": sum(p["data_visuals"] for p in data),
            "warning_count": sum(len(p["warnings"]) for p in data),
            "pages": data}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=ROOT)
    parser.add_argument("--mode", choices=("both", *MODES), default="both")
    parser.add_argument("--min-overlap", type=float, default=0.15)
    parser.add_argument("--fail-on-warning", action="store_true",
                        help="Opt-in gate after reviewing intentional visual layers")
    args = parser.parse_args()
    if not math.isfinite(args.min_overlap) or not 0 < args.min_overlap <= 1:
        parser.error("--min-overlap must be a finite fraction in (0, 1]")
    modes = MODES if args.mode == "both" else (args.mode,)
    try:
        reports = [audit_report(args.repository, mode, args.min_overlap) for mode in modes]
    except (OSError, ValueError) as error:
        parser.exit(2, f"PBIR layout scan failed: {error}\n")
    print(json.dumps(reports, indent=2, ensure_ascii=False))
    print("Source-level geometry only: does NOT verify Power BI Desktop rendering.")
    return int(args.fail_on_warning and any(r["warning_count"] for r in reports))


if __name__ == "__main__":
    raise SystemExit(main())
