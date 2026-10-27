#!/usr/bin/env python3
"""NEXUS Football Workintech PBIP release-readiness assessment (offline).

Read-only: never signs in, refreshes, queries BigQuery, modifies PBIP/PNG,
removes duplicate tables, triggers CI, or requests new screenshots.

Usage:
  python scripts/audit_workintech_semantic_model.py
  python scripts/audit_workintech_semantic_model.py --report path/to/audit.json
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re

REPO=Path(__file__).resolve().parents[1]
DEFAULT_PBIP=REPO/"powerbi"/"workintech-20261027"/"FootballPlayerAnalysis"
BQ_RE=re.compile(r'GoogleBigQuery\.Database\(')
SRC_RE=re.compile(r'Name="([^"]+)"')
REL_RE=re.compile(r"(?m)^\s*(?:fromColumn|toColumn):\s*(?:'((?:[^']|'')+)'|([^.]+))\.([^ \r\n]+)")
MEASURE_RE=re.compile(r"(?m)^\s*measure\s+(?:'([^']+)'|(\S+))\s*=")
KEYS=("Report","Model")
EXPECTED_GOVERNED=31
EXPECTED_PAGES=13
EXPECTED_VISUALS=308


def model_tables(pbip: Path) -> dict[str, dict]:
    folder=pbip/"Model"/"definition"/"tables"
    if not folder.is_dir():
        raise ValueError("PBIP model tables directory is missing")
    result={}
    for f in folder.glob("*.tmdl"):
        raw=f.read_text(encoding="utf-8-sig")
        if not BQ_RE.search(raw):
            continue
        sources=SRC_RE.findall(raw)
        # TMDL identifiers quote project / dataset / physical table in order.
        if len(sources)<3:
            raise ValueError(f"Cannot identify physical BigQuery table: {f.name}")
        project,dataset,source=sources[:3]
        result[f.stem]={
            "table_name":f.stem,
            "project":project,
            "dataset":dataset,
            "physical_table":source,
            "source_id":".".join([project,dataset,source]),
            "billing_project_pinned":'BillingProject="workintech-working"' in raw,
            "measure_count":len(MEASURE_RE.findall(raw)),
            "declared_columns":len(re.findall(r'(?m)^\s*column\s+',raw)),
        }
    return result


def referenced_entities(pbip: Path) -> dict[str, Counter]:
    """Count only explicit model references; no speculative deletion inference."""
    relationship=(pbip/"Model"/"definition"/"relationships.tmdl")
    contents=relationship.read_text(encoding="utf-8-sig") if relationship.exists() else ""
    rels=Counter()
    for match in REL_RE.finditer(contents):
        rels[(match.group(1) or match.group(2)).replace("''","'").strip()]+=1

    visuals=Counter()
    queries=Counter()
    folder=pbip/"Report"/"definition"/"pages"
    # PBIR JSON embeds repeated query/formatting structures; exact key regex
    # is sufficient to collect *explicit* Entity/queryRef string identifiers.
    # It is far faster and less memory-intensive than recursively traversing
    # all object formatting nodes. JSON validity is checked separately.
    entity_re=re.compile(r'"Entity"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"')
    query_re=re.compile(r'"queryRef"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"')
    for path in folder.rglob("visual.json"):
        raw=path.read_text(encoding="utf-8-sig")
        for match in entity_re.finditer(raw):
            value=json.loads('"'+match.group(1)+'"')
            visuals[value]+=1
        for match in query_re.finditer(raw):
            value=json.loads('"'+match.group(1)+'"')
            if "." in value:queries[value.split(".",1)[0]]+=1
    return {"relationships":rels,"visual_entities":visuals,"visual_query_refs":queries}


def assess(pbip: Path) -> dict:
    pbip=pbip.resolve()
    if not (pbip/"FootballPlayerAnalysis.pbip").is_file():
        raise ValueError("PBIP project descriptor is missing")
    pages=pbip/"Report"/"definition"/"pages"
    page_files=list(pages.glob("*/page.json"))
    chart_files=list(pages.rglob("visual.json"))
    tables=model_tables(pbip)
    refs=referenced_entities(pbip)
    governing={n:t for n,t in tables.items() if t["billing_project_pinned"]}
    extra={n:t for n,t in tables.items() if not t["billing_project_pinned"]}
    base_by_source={t["source_id"] for t in governing.values()}
    duplicated={}
    unique_extra={}
    for name,t in extra.items():
        if t["source_id"] in base_by_source:
            duplicated[name]=t
        else:
            unique_extra[name]=t

    findings=[]
    structural=[]
    if len(page_files)!=EXPECTED_PAGES:
        structural.append(f"Unexpected report page count: {len(page_files)}")
    if len(chart_files)!=EXPECTED_VISUALS:
        structural.append(f"Unexpected PBIR visual count: {len(chart_files)}")
    if len(governing)!=EXPECTED_GOVERNED:
        structural.append(f"Expected {EXPECTED_GOVERNED} governed tables; found {len(governing)}")
    if any(t["project"]!="workintech-working" for t in tables.values()):
        structural.append("At least one imported source points to the wrong GCP project")
    if not tables:
        structural.append("No BigQuery source tables were discovered")
    if len(duplicated):
        findings.append({
            "severity":"high",
            "code":"DUPLICATED_BIGQUERY_IMPORTS",
            "count":len(duplicated),
            "description":"Separate Power BI model tables read the same physical BigQuery tables. They can multiply memory use, refresh workload and create ambiguous relationship paths.",
            "action":"Map measure, relationship, filter and navigation dependencies before consolidation. Do not mass-delete imported tables.",
        })
    if len(unique_extra):
        findings.append({
            "severity":"medium",
            "code":"ADDITIONAL_NON_GOVERNED_TABLES",
            "count":len(unique_extra),
            "description":"Imported tables exist outside the 31-table governed contract; they require their own grain, key and relationship tests.",
        })

    appendix=[]
    for name,t in sorted(extra.items()):
        evidence={
            "table":name,
            "source_id":t["source_id"],
            "duplicate_of_governed_physical_source":name in duplicated,
            "relationship_endpoints":refs["relationships"].get(name,0),
            "visual_entity_references":refs["visual_entities"].get(name,0),
            "visual_query_references":refs["visual_query_refs"].get(name,0),
            "measure_count":t["measure_count"],
            "safe_to_delete_automatically":False,
        }
        appendix.append(evidence)
    count_related=sum(x["relationship_endpoints"]>0 for x in appendix)
    if count_related:
        findings.append({
            "severity":"critical",
            "code":"EXTRA_IMPORTS_HAVE_RELATIONSHIPS",
            "count":count_related,
            "description":"The extra imports participate in active semantic-model relationships; deleting them blindly may break filter propagation, model cardinality and analytics.",
        })

    evidence={
        "audit_version":"1.0",
        "audit_generated_utc":datetime.now(timezone.utc).isoformat(),
        "scope":"workintech PBIP semantic-model structure only; no BigQuery or Power BI live refresh executed",
        "pbip":str(pbip),
        "pages":len(page_files),
        "visuals":len(chart_files),
        "governed_table_count":len(governing),
        "duplicate_physical_source_import_count":len(duplicated),
        "additional_unique_import_count":len(unique_extra),
        "all_bigquery_import_count":len(tables),
        "extra_imports_referenced_by_relationships":count_related,
        "structural_errors":structural,
        "findings":findings,
        "extra_tables":appendix,
        "evidence_limits":[
            "References in visual.json and relationships.tmdl are inspected; opaque bookmarks, DAX string expressions and Desktop internal caches can also depend on source names.",
            "The 31/31 published physical schema contract is separate from the extra imports and does not certify the whole 65-table semantic model.",
            "No screenshot or post-fix Desktop rendered view is required or claimed by this audit.",
            "The recovered Kaggle football source is historical, not a live 2026-10-27 feed.",
        ],
    }
    evidence["status"]="STRUCTURAL_INVALID" if structural else ("RELEASE_HOLD_SEMANTIC_CONSOLIDATION" if findings else "STRUCTURE_PASS")
    return evidence


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--pbip",type=Path,default=DEFAULT_PBIP)
    cli.add_argument("--report",type=Path,default=None)
    args=cli.parse_args()
    try:
        evidence=assess(args.pbip)
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"STRUCTURAL_INVALID","error":str(exc)},ensure_ascii=False,indent=2))
        raise SystemExit(2)
    print(json.dumps({
        key:evidence[key] for key in (
            "status","pages","visuals","governed_table_count",
            "duplicate_physical_source_import_count","additional_unique_import_count",
            "extra_imports_referenced_by_relationships","structural_errors",
        )
    },ensure_ascii=False,indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        print("READ_ONLY_SEMANTIC_AUDIT_SAVED:",args.report)
    if evidence["status"]=="STRUCTURAL_INVALID":raise SystemExit(2)

if __name__=="__main__":main()
