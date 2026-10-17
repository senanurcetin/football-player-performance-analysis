#!/usr/bin/env python3
"""Validate actual Power BI Desktop screenshot artifacts without claiming live data."""
from __future__ import annotations
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs"/"assets"/"screenshots"

def validate() -> dict[str,int]:
    info=json.loads((BASE/"capture_manifest.json").read_text(encoding="utf-8"))
    rows=info["captures"]
    if len(rows)!=13:raise AssertionError(f"Expected 13 captures, received {len(rows)}")
    for group,expected in (("Main",9),("Drillthrough",2),("Tooltip",2)):
        observed=sum(r["type"]==group for r in rows)
        if observed!=expected:raise AssertionError(f"{group}: {observed}!={expected}")
    for r in rows:
        file=ROOT/r["path"]
        data=file.read_bytes()
        if data[:8]!=b"\x89PNG\r\n\x1a\n":raise AssertionError(f"Invalid PNG {file}")
        dimensions=struct.unpack(">II",data[16:24])
        if dimensions!=(2177,1229) or list(dimensions)!=r["size"]:
            raise AssertionError(f"Invalid screenshot dimensions {file}")
        if hashlib.sha256(data).hexdigest()!=r["sha256"]:
            raise AssertionError(f"SHA-256 mismatch: {file}")
    frame_files=list((BASE/"portfolio").glob("*.png"))
    if len(frame_files)!=9:raise AssertionError(f"Expected nine framed PNGs, got {len(frame_files)}")
    if not (BASE/"NEXUS_Football_Page_Gallery.png").is_file():
        raise AssertionError("Gallery image missing")
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    screenshots_readme=(BASE/"README.md").read_text(encoding="utf-8")
    for p in set(re.findall(r"docs/assets/screenshots/[A-Za-z0-9_./-]+\.png",readme)):
        if not (ROOT/p).is_file():raise AssertionError(f"Broken README image: {p}")
    for p in set(re.findall(r"(?:production|portfolio|internal)/[A-Za-z0-9_.-]+\.png",screenshots_readme)):
        if not (BASE/p).is_file():raise AssertionError(f"Broken screenshot gallery link: {p}")
    return {"captures":len(rows),"presentation":9,"detail":2,"tooltips":2,"framed":len(frame_files)}

if __name__=="__main__":
    print(json.dumps(validate(),indent=2))
