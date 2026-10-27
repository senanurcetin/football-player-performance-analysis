#!/usr/bin/env python3
"""Static PBIR column/measure bind audit and relationship-graph risk report.

Works only against the full dedup QA copy. Never opens Desktop, refreshes data,
rewrites BI report, or asks user to capture images.
"""
from pathlib import Path
from collections import Counter,defaultdict,deque
import json,re,sys
from datetime import datetime,timezone

ROOT=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027")
QA=ROOT/"powerbi-full-dedup-qa-20261028/FootballPlayerAnalysis"
OUT=ROOT/"powerbi-full-dedup-qa-20261028/qa_field_and_filter_path_report.json"
REPO=Path(__file__).resolve().parents[1]
def table_fields(path):
    s=path.read_text("utf-8-sig")
    # Per field, extract the TMDL name declaration rather than a fragile text
    # search, so calculated columns and measures are both covered.
    fields=Counter()
    for m in re.finditer(r"(?m)^\tcolumn (?:'((?:[^']|'')+)'|([^=\r\n]+?))(?:\s*=.*)?$",s):
        fields["column:"+((m.group(1) or m.group(2)).strip().replace("''","'"))]+=1
    for m in re.finditer(r"(?m)^\tmeasure (?:'((?:[^']|'')+)'|([^=\r\n]+?))\s*=",s):
        fields["measure:"+((m.group(1) or m.group(2)).strip().replace("''","'"))]+=1
    return fields

def main():
    tables={p.stem:table_fields(p) for p in (QA/"Model/definition/tables").glob("*.tmdl")}
    all_refs=[]
    errors=[]
    unknown=[]
    def walk(node,file):
        if isinstance(node,dict):
            for key,v in node.items():
                if key in ("Column","Measure") and isinstance(v,dict):
                    src=v.get("Expression",{}).get("SourceRef",{})
                    if isinstance(src,dict):
                        table=src.get("Entity")
                        field=v.get("Property")
                        if table and field:
                            kind=key.lower()
                            all_refs.append((table,field,kind,file))
                            if table not in tables:
                                errors.append({"visual":file,"table":table,"field":field,"kind":kind,"problem":"missing-table"})
                            elif tables[table].get(f"{kind}:{field}",0)==0:
                                errors.append({"visual":file,"table":table,"field":field,"kind":kind,"problem":"missing-field"})
                walk(v,file)
        elif isinstance(node,list):
            for x in node:walk(x,file)
    page_dir=QA/"Report/definition/pages"
    for f in page_dir.rglob("visual.json"):
        j=json.loads(f.read_text("utf-8-sig"))
        rel=f.relative_to(QA).as_posix()
        walk(j.get("visual",{}).get("query",{}),rel)
    # Restrict graph to active, explicit bidirectional filters between business
    # tables. One-way relationship edge orientation needs engine metadata;
    # do not claim directed reachability equivalence using an approximation.
    rel=(QA/"Model/definition/relationships.tmdl").read_text("utf8")
    chunks=[x for x in re.split(r"(?=^relationship )",rel,flags=re.M) if x.startswith("relationship ")]
    undirected=defaultdict(set)
    both=defaultdict(set)
    for block in chunks:
        props=dict(re.findall(r"(?m)^\s*(\w+):\s*(.*?)\s*$",block))
        if props.get("isActive","true")=="false":continue
        ends=[]
        for col in ("fromColumn","toColumn"):
            raw=props[col]
            if raw.startswith("'"):
                tab,field=raw[1:].rsplit("'.",1)
            else:tab,field=raw.split(".",1)
            ends.append(tab)
        a,b=ends
        if a.startswith("LocalDateTable_") or b.startswith("LocalDateTable_"):continue
        undirected[a].add(b);undirected[b].add(a)
        if props.get("crossFilteringBehavior")=="bothDirections":
            both[a].add(b);both[b].add(a)
    components=[]
    remaining=set(both.keys())
    while remaining:
        root=sorted(remaining)[0]
        todo=[root];seen={root}
        while todo:
            node=todo.pop()
            for n in both[node]-seen:
                seen.add(n);todo.append(n)
        remaining-=seen
        components.append(sorted(seen))
    components.sort(key=lambda xs:(-len(xs),xs))
    # Detect simple cycles in undirected business relation graph (not proof of
    # active ambiguity because engine cardinality/filter direction matters).
    component_counter=0
    nodes=set(undirected)
    seen=set()
    for root in nodes:
        if root in seen:continue
        component_counter+=1
        queue=[root];seen.add(root)
        while queue:
            for n in undirected[queue.pop()]:
                if n not in seen:seen.add(n);queue.append(n)
    report={
        "status":"VISUAL_BINDINGS_PASS_FILTER_RUNTIME_STILL_REQUIRED" if not errors else "VISUAL_FIELD_BINDINGS_INVALID",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "validated_visual_column_measure_refs":len(all_refs),
        "distinct_bindings":len(set((t,f,k) for t,f,k,_ in all_refs)),
        "missing_table_or_field_references":errors,
        "model_tables":len(tables),
        "business_filter_graph_nodes":len(nodes),
        "business_filter_graph_components":component_counter,
        "bidirectional_business_components":[x for x in components if len(x)>1],
        "limitations":[
            "Does not run the Power BI semantic engine or evaluate DAX.",
            "Cross-filtering path results cannot be proven equivalent without TOM/runtime queries.",
            "Does not capture or require new screenshots.",
            "Does not mutate the production report or BigQuery data."
        ],
    }
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:report[k] for k in ("status","validated_visual_column_measure_refs","distinct_bindings","model_tables","business_filter_graph_nodes","business_filter_graph_components")},ensure_ascii=False))
    if errors:
        print("FIRST_INVALID_FIELDS",json.dumps(errors[:12],ensure_ascii=False))
        sys.exit(2)
if __name__=="__main__":main()
