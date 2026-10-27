#!/usr/bin/env python3
"""Isolated full migration of redundant Workintech Power BI imports.

Never modifies the owner Desktop report or the canonical Git source. Reads
from the three-table sandbox pilot; creates a NEW isolated PBIP copy. Redundant
source imports, their own date hierarchies, duplicate relationships, query
order/model registrations and diagram positions are removed; novel business
relationships are remapped to existing governed physical tables.

This is STATIC verification, NOT Desktop/TOM runtime certification.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict
import argparse,copy,hashlib,json,re,shutil
from datetime import datetime,timezone

RECOVERY=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027")
SOURCE=RECOVERY/"powerbi-dedup-pilot-20261027/FootballPlayerAnalysis"
DEST=RECOVERY/"powerbi-full-dedup-qa-20261028/FootballPlayerAnalysis"
OUT=DEST.parent/"full_dedup_static_audit.json"
REL_RE=re.compile(r"(?m)^relationship [^\r\n]+(?:\r?\n(?!relationship )[^\r\n]*)*")
PROJ="workintech-working"
DEF="Model/definition"

def sha(p:Path):return hashlib.sha256(p.read_bytes()).hexdigest()
def cols(t:str):
    pat=re.compile(r"(?m)^\tcolumn (?:'([^']+)'|([^\s=]+))(?:\s*=([^\r\n]*))?$")
    matches=list(pat.finditer(t))
    d={}
    for i,m in enumerate(matches):
        name=m.group(1) or m.group(2)
        body=t[m.end():matches[i+1].start() if i+1<len(matches) else len(t)]
        type_match=re.search(r"(?m)^\t\tdataType:\s*(\S+)",body)
        d[name]=type_match.group(1) if type_match else None
    return d
def physical_source(s:str):
    a=re.findall(r'Name="([^"]+)"',s)
    if len(a)<3:raise ValueError("Malformed BigQuery source")
    return a[:3]
def pair(s:str):
    opts=dict(re.findall(r"(?m)^\s*(\w+):\s*(.*?)\s*$",s))
    def ep(v):
        if v.startswith("'"):
            t,col=v[1:].rsplit("'.",1)
            return t.replace("''","'"),col
        return tuple(v.split(".",1))
    return ep(opts["fromColumn"]),ep(opts["toColumn"]),opts
def canon(name:str):
    return name[:-4] if name.endswith(" (2)") else name
def format_ep(t,c):
    if " " in t or "(" in t or ")" in t:
        return "'"+t.replace("'","''")+"'."+c
    return t+"."+c
def collect(root:Path):
    return {p.relative_to(root).as_posix():sha(p) for p in root.rglob("*") if p.is_file() and ".pbi" not in p.relative_to(root).parts}
def run(source:Path,dest:Path):
    source=source.resolve()
    dest=dest.resolve()
    if dest.exists():raise ValueError("Output already exists: "+str(dest))
    if source==dest or source in dest.parents:raise ValueError("Output cannot overlap input")
    if not (source/"FootballPlayerAnalysis.pbip").is_file():raise ValueError("Source missing PBIP descriptor")
    src_hashes=collect(source)
    tables=source/DEF/"tables"
    to_remove=sorted(p.stem for p in tables.glob("*.tmdl") if p.stem.endswith(" (2)"))
    if len(to_remove)!=28:raise ValueError("Expected exactly 28 remaining duplicate imports after isolated pilot; got "+str(len(to_remove)))
    candidates=set(to_remove)
    date_removal=set()
    for name in to_remove:
        dupe=(tables/(name+".tmdl")).read_text("utf-8-sig")
        canonical_file=tables/(name[:-4]+".tmdl")
        if not canonical_file.is_file():raise ValueError("Missing governed table: "+name)
        governing=canonical_file.read_text("utf-8-sig")
        if "GoogleBigQuery.Database(" not in dupe or "GoogleBigQuery.Database(" not in governing:
            raise ValueError("Non-BigQuery input "+name)
        if physical_source(dupe)!=physical_source(governing) or physical_source(dupe)[0]!=PROJ:
            raise ValueError("Physical source mismatch "+name)
        c1,c2=cols(dupe),cols(governing)
        if not c1 or any(col not in c2 or c2[col]!=typ for col,typ in c1.items()):
            raise ValueError("Schema incompatible "+name)
        if re.search(r"(?m)^\s*measure\s+",dupe):
            raise ValueError("Duplicate defines extra measures "+name)
        dates=re.findall(r"defaultHierarchy:\s*(LocalDateTable_[0-9a-f-]+)\.",dupe)
        date_removal.update(dates)
    if len(date_removal)!=40:raise ValueError("Expected exactly 40 exclusive auto-date variations: "+str(len(date_removal)))
    if any(not (tables/(d+".tmdl")).is_file() for d in date_removal):
        raise ValueError("Auto date table definition not present")
    model_src=(source/DEF/"model.tmdl").read_text("utf8")
    old_order=re.search(r"(?m)^annotation PBI_QueryOrder = (.+)$",model_src)
    if not old_order:raise ValueError("Missing query order")
    q=json.loads(old_order.group(1))
    if len(set(q))!=len(q):raise ValueError("Duplicate query order names")
    if set(to_remove)-set(q):raise ValueError("Some duplicated import not registered in PBI_QueryOrder")
    model_deltas=set(to_remove)|date_removal
    if sum(int(("ref table '"+x+"'") in model_src or ("ref table "+x) in model_src) for x in model_deltas)!=len(model_deltas):
        raise ValueError("Missing some model table registrations")
    rel_text=(source/DEF/"relationships.tmdl").read_text("utf8")
    rels=REL_RE.findall(rel_text)
    if len(rels)!=158:raise ValueError("Expected 158 original relationships; got "+str(len(rels)))
    kept,novel=[],[]
    removed_dupes,removed_dates=[],[]
    firstseen={}
    canonical_pairs=set()
    for b in rels:
        left,right,_=pair(b)
        if not (left[0] in candidates or right[0] in candidates or left[0] in date_removal or right[0] in date_removal):
            canonical_pairs.add((left,right))
    for b in rels:
        a,c,info=pair(b)
        if any(t in date_removal for t,col in (a,c)):
            if not any(t in candidates for t,col in (a,c)):
                raise ValueError("Date table referenced by non-removal source")
            removed_dates.append(b)
            continue
        if not any(t in candidates for t,col in (a,c)):
            kept.append(b)
            continue
        mapped=((canon(a[0]),a[1]),(canon(c[0]),c[1]))
        if mapped in canonical_pairs:
            removed_dupes.append(b)
            continue
        # Preserve additional business links. Changing the participating
        # table identifier must not alter original relationship attributes.
        modified=b
        for field,ep in (("fromColumn",a),("toColumn",c)):
            old_raw=info[field]
            replacement=format_ep(canon(ep[0]),ep[1])
            if ep[0] in candidates:
                pattern=r"(?m)^(\t"+re.escape(field)+r":\s*)"+re.escape(old_raw)+r"(\s*)$"
                modified,count=re.subn(pattern,lambda m:m.group(1)+replacement+m.group(2),modified,count=1)
                if count!=1:raise ValueError("Failed to map relationship endpoint")
        new_a,new_c,new_info=pair(modified)
        if (new_a,new_c)!=mapped:raise ValueError("Invalid remapped relationship")
        if any(new_info.get(k)!=info.get(k) for k in set(info)|set(new_info) if k not in ("fromColumn","toColumn")):
            raise ValueError("Remapping changed cardinality/filter attributes")
        if mapped in canonical_pairs:raise ValueError("Conflicting novel relationship with canonical graph")
        if mapped in firstseen:raise ValueError("Two novel relationships map to same relation")
        firstseen[mapped]=b
        kept.append(modified)
        novel.append({"from":list(new_a),"to":list(new_c),"id":b.splitlines()[0].split()[1]})
    if (len(removed_dates),len(removed_dupes),len(novel),len(kept))!=(40,31,9,87):
        raise ValueError("Migration relationship counts differ: "+str(tuple(map(len,(removed_dates,removed_dupes,novel,kept)))))
    # Only allowed residual references to removed names occur in
    # removed source TMDLs, exclusive date TMDLs, model registry,
    # relationship graph and diagram layout. Refuse any other use,
    # including bookmarks, report JSON, calculated table DAX or caches.
    allowed={f"{DEF}/tables/{n}.tmdl" for n in model_deltas}
    allowed|={f"{DEF}/model.tmdl",f"{DEF}/relationships.tmdl","Model/diagramLayout.json"}
    tokens=sorted(model_deltas,key=len,reverse=True)
    for rel in sorted(src_hashes):
        if rel in allowed:continue
        f=source/rel
        if f.suffix.lower() not in (".json",".tmdl",".pbip",".pbir",".pbism",".md",".txt",".m"):
            continue
        raw=f.read_text("utf8",errors="replace")
        for name in tokens:
            if name in raw:
                raise ValueError(f"Outside reference {name} found in {rel}; cannot safely dedup")
    # All date tables removed are exclusively tied to copies (no reliance
    # on another retained source definition).
    for n in date_removal:
        d=(tables/(n+".tmdl")).read_text("utf8")
        found=set(re.findall(r"(?m)^\s*sourceColumn:.*$",d))
        if re.search(r"(?m)^\tmeasure\s+",d):
            raise ValueError("Unexpected measure on date table "+n)
        if any(x in d for x in ("GoogleBigQuery.Database(","fromColumn:","toColumn:")):
            raise ValueError("Unknown date table source "+n)
    shutil.copytree(source,dest,ignore=shutil.ignore_patterns(".pbi"))
    dst_model=dest/DEF
    for name in model_deltas:
        (dst_model/"tables"/(name+".tmdl")).unlink()
    mod=model_src
    for name in model_deltas:
        entry=("ref table '"+name+"'" if name.endswith(" (2)") else "ref table "+name)
        mod,n=re.subn(r"(?m)^"+re.escape(entry)+r"\s*\n","",mod,count=1)
        if n!=1:raise ValueError("Could not remove unique table registration "+name)
    new_order=[x for x in q if x not in candidates]
    mod=mod.replace(old_order.group(0),"annotation PBI_QueryOrder = "+json.dumps(new_order,separators=(",",":"),ensure_ascii=False),1)
    (dst_model/"model.tmdl").write_text(mod,encoding="utf8")
    (dst_model/"relationships.tmdl").write_text("\n\n".join(x.rstrip() for x in kept)+"\n",encoding="utf8")
    diagram_path=dest/"Model/diagramLayout.json"
    original_diagram=json.loads(diagram_path.read_text("utf8"))
    original_nodes=sum(len(x.get("nodes",[])) for x in original_diagram.get("diagrams",[]))
    for d in original_diagram.get("diagrams",[]):
        d["nodes"]=[node for node in d.get("nodes",[]) if node.get("nodeIndex") not in model_deltas]
    removed_nodes=original_nodes-sum(len(x.get("nodes",[])) for x in original_diagram.get("diagrams",[]))
    if removed_nodes!=28:raise ValueError("Unexpected diagram node removal count "+str(removed_nodes))
    diagram_path.write_text(json.dumps(original_diagram,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    # Verify all remaining table refs and relationship endpoints point to
    # current TMDL tables; all unrelated source hashes are identical.
    dst_table_names={p.stem for p in (dst_model/"tables").glob("*.tmdl")}
    if dst_table_names.intersection(model_deltas):raise ValueError("Removed table remains in output")
    refs=re.findall(r"(?m)^ref table (?:'([^']+)'|(\S+))\s*$",mod)
    refnames=[x or y for x,y in refs]
    if set(refnames)!=dst_table_names:
        raise ValueError("Ref table registrations differ from actual remaining tables: "+str(len(set(refnames)^dst_table_names)))
    if any(t not in dst_table_names for t in new_order):
        raise ValueError("Dangling QueryOrder table")
    for b in kept:
        left,right,info=pair(b)
        if any(t not in dst_table_names for t,c in (left,right)):
            raise ValueError("Dangling relation endpoint")
    post_hashes=collect(dest)
    expected_paths=set(src_hashes)-{f"{DEF}/tables/{x}.tmdl" for x in model_deltas}
    if set(post_hashes)!=expected_paths:
        raise ValueError("Unexpected removed/new files: "+str((set(post_hashes)^expected_paths)))
    actual_changed={rel for rel in expected_paths if src_hashes[rel]!=post_hashes[rel]}
    if actual_changed!={f"{DEF}/model.tmdl",f"{DEF}/relationships.tmdl","Model/diagramLayout.json"}:
        raise ValueError("Other files unexpectedly changed: "+str(actual_changed))
    pages=len(list((dest/"Report/definition/pages").glob("*/page.json")))
    visuals=list((dest/"Report/definition/pages").rglob("visual.json"))
    if pages!=13 or len(visuals)!=308:raise ValueError("PBIR pages or visuals changed")
    for v in visuals:json.loads(v.read_text("utf8"))
    return {
        "status":"FULL_DEDUP_STATIC_QA_PASS_RUNTIME_UNVERIFIED",
        "owner_active_pbip_changed":False,"canonical_repo_pbip_changed":False,
        "source":str(source),"test_copy":str(dest),
        "original_bigquery_duplicate_definitions":31,
        "removed_in_earlier_sandbox":3,"removed_in_this_sandbox":len(candidates),
        "exclusive_autodate_tables_removed":len(date_removal),
        "total_source_tables_removed":len(model_deltas),
        "relations_before":len(rels),"relations_after":len(kept),
        "redundant_relations_removed":len(removed_dupes),
        "exclusive_autodate_relations_removed":len(removed_dates),
        "novel_business_relations_preserved_and_remapped":len(novel),
        "novel_business_relations":novel,
        "changed_model_metadata_files":sorted(actual_changed),
        "other_file_hashes_identical":True,
        "remaining_physical_import_duplicates":0,
        "pages_preserved":pages,"visuals_preserved":len(visuals),
        "all_remaining_relations_reference_existing_tables":True,
        "existing_dax_measure_definitions_changed":False,
        "known_cross_filter_discrepancies_between_prior_copies":2,
        "migrated_filter_policy":"keep original governed filter settings; must validate player filtering in Power BI runtime",
        "powerbi_desktop_runtime_tested":False,
        "screenshot_requests":0,
        "reason_not_promoted":"No loaded-model/TOM runtime semantic equivalence has been demonstrated.",
        "generated_at_utc":datetime.now(timezone.utc).isoformat()
    }
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=SOURCE)
    parser.add_argument("--out",type=Path,default=DEST)
    parser.add_argument("--audit",type=Path,default=OUT)
    a=parser.parse_args()
    try:
        data=run(a.source,a.out)
    except (ValueError,OSError,AssertionError,json.JSONDecodeError) as e:
        raise SystemExit("FULL_DEDUP_QA_STOPPED: "+repr(e))
    a.audit.parent.mkdir(parents=True,exist_ok=True)
    a.audit.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:data[k] for k in ("status","removed_in_this_sandbox","exclusive_autodate_tables_removed","relations_after","novel_business_relations_preserved_and_remapped","pages_preserved","visuals_preserved","test_copy")},ensure_ascii=False))
if __name__=="__main__":main()
