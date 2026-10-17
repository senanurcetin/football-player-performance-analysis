#!/usr/bin/env python3
"""Audit repository Markdown navigation and historical-document organization.

Checks local files and headings; network URLs are not fetched, so external-link
availability is not certified.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import html
import json
import re
import subprocess
import unicodedata
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
LINK=re.compile(r'!?\[[^\]\n]*\]\((<[^>]*>|[^)\n]+)\)|\b(?:href|src)="([^"]+)"')
HEAD=re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$",re.M)

def slug(raw:str)->str:
    raw=html.unescape(re.sub(r"<[^>]+>","",raw))
    raw=re.sub(r"[*_~]","",raw).lower().strip()
    raw=re.sub(r"[^\w\s-]","",raw,flags=re.UNICODE)
    return re.sub(r"\s+","-",raw)

def files()->list[Path]:
    listed=subprocess.run(["git","-C",str(ROOT),"ls-files","*.md"],capture_output=True,text=True,check=True,encoding="utf-8").stdout.splitlines()
    found={ROOT/n for n in listed if (ROOT/n).is_file()}
    found.update(ROOT.joinpath("docs").rglob("*.md"))
    return sorted(found)

def validate()->dict[str,int]:
    sources=files();heading_map={};missing=[];anchors=[];no_heading=[];bad_unicode=[];links=0
    for p in sources:
        content=p.read_text(encoding="utf-8-sig")
        rel=p.relative_to(ROOT).as_posix()
        if "\ufffd" in content:bad_unicode.append(rel)
        heads=[slug(m.group(1)) for m in HEAD.finditer(content)]
        if not heads:no_heading.append(rel)
        occurrences=Counter()
        all_ids=set()
        for s in heads:
            n=occurrences[s]
            all_ids.add(s if n==0 else f"{s}-{n}")
            occurrences[s]+=1
        all_ids.update(m.group(1) for m in re.finditer(r'<a\s+(?:id|name)="([^"]+)"',content))
        heading_map[p.resolve()]=all_ids
    for p in sources:
        rel=p.relative_to(ROOT).as_posix()
        for m in LINK.finditer(p.read_text(encoding="utf-8-sig")):
            url=(m.group(1) or m.group(2)).strip()
            if url.startswith("<") and url.endswith(">"):url=url[1:-1]
            url=url.split(' "',1)[0].split(" '",1)[0]
            if url.startswith(("http://","https://","mailto:","data:","javascript:","//")):continue
            path,_,fragment=url.partition("#")
            if not path and not fragment:continue
            if not path:dest=p.resolve()
            elif path.startswith("/"):dest=(ROOT/path.lstrip("/")).resolve()
            else:dest=(p.parent/unquote(path)).resolve()
            links+=1
            if not dest.is_relative_to(ROOT) or not dest.exists():
                missing.append(f"{rel}: {url}")
                continue
            if fragment and dest.suffix==".md" and dest in heading_map:
                token=unquote(fragment).lower()
                if token not in heading_map[dest] and not re.fullmatch(r"L\d+(?:-L\d+)?",fragment):
                    anchors.append(f"{rel}: {url}")
    archived=list((ROOT/"docs"/"archive"/"powerbi").glob("*.md"))
    totals={"markdown":len(sources),"local_links_checked":links,"archived_powerbi_documents":len(archived),"missing_targets":len(missing),"broken_anchors":len(anchors),"missing_headings":len(no_heading),"invalid_unicode_files":len(bad_unicode)}
    problems={"missing_targets":missing,"broken_anchors":anchors,"missing_headings":no_heading,"invalid_unicode_files":bad_unicode}
    if len(archived)<19:problems["archive"]=["Expected original 18 plans plus historical QA log"]
    if any(problems.values()):raise AssertionError(json.dumps({"summary":totals,"problems":problems},indent=2,ensure_ascii=False))
    return totals
if __name__=="__main__":
    print(json.dumps(validate(),indent=2))
