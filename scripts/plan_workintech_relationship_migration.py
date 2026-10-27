#!/usr/bin/env python3
"""Read-only relationship migration matrix for a Workintech Power BI PBIP.

Classifies duplicate physical-source relations by endpoint and semantic property,
and separates 40 auto-date table links from 9 novel non-date links. Nothing is
deleted, renamed, pushed, refreshed, or rendered by this planner.
"""
from __future__ import annotations
import argparse,collections,json,re
from datetime import datetime,timezone
from pathlib import Path
DEFAULT=Path(__file__).resolve().parents[1]/"powerbi/workintech-20261027/FootballPlayerAnalysis"
OUTPUT=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027\workintech_relationship_migration_plan.json")
ATTRS=("isActive","crossFilteringBehavior","fromCardinality","toCardinality","joinOnDateBehavior","relyOnReferentialIntegrity","securityFilteringBehavior")
def unpack_endpoint(raw:str):
    raw=raw.strip()
    if raw.startswith("'"):
        tab,col=raw[1:].rsplit("'.",1)
        return tab.replace("''","'"),col
    parts=raw.split(".",1)
    if len(parts)!=2:raise ValueError("Invalid endpoint: "+raw)
    return parts[0],parts[1]
def canon(endpoint):
    tab,col=endpoint
    return (tab[:-4],col) if tab.endswith(" (2)") else endpoint
def parse(path:Path):
    text=path.read_text(encoding="utf-8-sig")
    sections=[x for x in re.split(r"(?=^relationship )",text,flags=re.M) if x.startswith("relationship ")]
    records=[]
    for chunk in sections:
        first=chunk.splitlines()[0]
        uid=first.partition(" ")[2].strip()
        props=dict(re.findall(r"(?m)^\s*(\w+):\s*(.*?)\s*$",chunk))
        if not {"fromColumn","toColumn"}<=props.keys():
            raise ValueError("Missing relation endpoint: "+uid)
        ep=(unpack_endpoint(props["fromColumn"]),unpack_endpoint(props["toColumn"]))
        records.append({"id":uid,"endpoints":ep,"properties":{k:v for k,v in props.items() if k not in ("fromColumn","toColumn")}})
    ids=[r["id"] for r in records]
    if len(ids)!=len(set(ids)):raise ValueError("Duplicate relationship identifiers")
    return records

def plan(pbip:Path):
    relpath=pbip/"Model/definition/relationships.tmdl"
    relations=parse(relpath)
    originals=collections.defaultdict(list)
    extras=[]
    for r in relations:
        ends=r["endpoints"]
        if any(tab.endswith(" (2)") for tab,col in ends):
            extras.append(r)
        else:
            originals[tuple(ends)].append(r)
    counts=collections.Counter()
    duplicate_exact=[]
    duplicate_different=[]
    auto_date=[]
    novel=[]
    for rel in extras:
        mapped=tuple(canon(end) for end in rel["endpoints"])
        source_match=originals.get(mapped,[])
        if source_match:
            if len(source_match)!=1:
                raise ValueError("Multiple canonical relationships for "+rel["id"])
            target=source_match[0]
            differences={
                attr:{"governed":target["properties"].get(attr), "duplicated":rel["properties"].get(attr)}
                for attr in set(target["properties"])|set(rel["properties"])
                if target["properties"].get(attr)!=rel["properties"].get(attr)
            }
            item={"original_relation_id":target["id"],"extra_relation_id":rel["id"],
                  "governed_endpoints":list(map(list,mapped)),
                  "extra_endpoints":list(map(list,rel["endpoints"])),
                  "attribute_differences":differences}
            if differences:duplicate_different.append(item)
            else:duplicate_exact.append(item)
        elif any(tab.startswith("LocalDateTable_") for tab,col in rel["endpoints"]):
            auto_date.append({"relation_id":rel["id"],"endpoints":list(map(list,rel["endpoints"])),
                              "reason":"local_date_hierarchy_reference_requires_companion_model_validation"})
        else:
            novel.append({"relation_id":rel["id"],"endpoints":list(map(list,rel["endpoints"])),
                          "mapped_endpoints":list(map(list,mapped)),
                          "reason":"not_present_in_existing_governed_relationship_graph"})
    affected=len(extras)
    counts.update({
      "all_relationships":len(relations),
      "duplicate_source_related_relationships":affected,
      "identical_pair_and_attributes":len(duplicate_exact),
      "same_pair_different_attributes":len(duplicate_different),
      "extra_local_date_relationships":len(auto_date),
      "novel_non_date_relationships":len(novel),
      "unaffected_relationships":len(relations)-affected,
    })
    if sum(counts[k] for k in ("identical_pair_and_attributes","same_pair_different_attributes","extra_local_date_relationships","novel_non_date_relationships"))!=affected:
        raise ValueError("Unclassified duplicate relationship")
    return {
       "audit_version":1,"as_of_utc":datetime.now(timezone.utc).isoformat(),
       "source_pbip":str(pbip),
       "status":"REQUIRES_SEMANTIC_REVIEW_BEFORE_ANY_BULK_DEDUP",
       "counts":dict(counts),
       "same_pair_different_attributes":duplicate_different,
       "novel_non_date_relationships":novel,
       "extra_local_date_relationships":auto_date,
       "identical_pair_details":duplicate_exact,
       "policy":{
          "bulk_delete_automated":False,
          "existing_governed_relationships_preserved":True,
          "never_discard_filter_direction_disagreement":True,
          "evaluate_local_date_variations_before_removing_related_table":True,
          "never_rewrite_active_owner_pbip_from_this_report":True,
          "require_actual_runtime_model_acceptance_before_production_promotion":True,
          "request_user_screenshots":False,
       },
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pbip",type=Path,default=DEFAULT)
    p.add_argument("--output",type=Path,default=OUTPUT)
    args=p.parse_args()
    result=plan(args.pbip)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"status":result["status"],"counts":result["counts"],"report":str(args.output)},ensure_ascii=False))
if __name__=="__main__":main()
