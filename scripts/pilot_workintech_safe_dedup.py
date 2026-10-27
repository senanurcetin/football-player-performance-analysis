#!/usr/bin/env python3
"""Safe pilot: remove three provably unreferenced duplicate imports from a COPY.

This program NEVER mutates the owner's active PBIP or the repository source.
Its checks inspect the ENTIRE file-backed PBIP, require matching physical
BigQuery data source and schema, enforce absence of runtime references,
rewrite model table registration and diagram atomically in the sandbox,
and check all unrelated bytes are unchanged. It does NOT certify Power BI
Desktop rendering or fully consolidate remaining duplicate imports.
"""
from __future__ import annotations
import argparse,hashlib,json,re,shutil,sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
SOURCE=REPO/"powerbi/workintech-20261027/FootballPlayerAnalysis"
SANDBOX=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-dedup-pilot-20261027\FootballPlayerAnalysis")
TARGETS=(
 "fct_agent_portfolio (2)",
 "fct_data_coverage_bias (2)",
 "fct_transfer_cohort_performance (2)",
)
def digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def fields(text:str)->dict[str,str]:
 items={}
 matches=list(re.finditer(r"(?m)^\tcolumn (?:'([^']+)'|(\S+))(?: = [^\r\n]*)?\s*$",text))
 for i,m in enumerate(matches):
  name=m.group(1) or m.group(2)
  end=matches[i+1].start() if i+1<len(matches) else len(text)
  block=text[m.end():end]
  t=re.search(r"(?m)^\t\tdataType:\s*(\S+)",block)
  items[name]=t.group(1) if t else ""
 return items
def profile(root:Path):
 model=root/"Model/definition"
 folder=model/"tables"
 text=(model/"model.tmdl").read_text("utf-8-sig")
 rel=(model/"relationships.tmdl").read_text("utf-8-sig")
 diagram_path=root/"Model/diagramLayout.json"
 diagram=json.loads(diagram_path.read_text("utf-8-sig"))
 files={f.relative_to(root).as_posix():digest(f.read_bytes()) for f in root.rglob("*") if f.is_file() and ".pbi" not in f.relative_to(root).parts}
 coverage=[]
 for name in TARGETS:
  dup=folder/(name+".tmdl")
  canonical=folder/(name[:-4]+".tmdl")
  if not dup.is_file() or not canonical.is_file():raise ValueError("Missing matched duplicated/canonical TMDL: "+name)
  dp=dup.read_text("utf-8-sig");cp=canonical.read_text("utf-8-sig")
  expected=name[:-4]
  if 'GoogleBigQuery.Database(' not in dp or 'GoogleBigQuery.Database(' not in cp:raise ValueError(name+" is not a BigQuery copy")
  def src(content):
   a=re.findall(r'Name="([^"]+)"',content)
   if len(a)<3:raise ValueError("Unrecognized BigQuery source structure: "+name)
   return a[:3]
  if src(dp)!=src(cp) or src(dp)[0]!='workintech-working':
   raise ValueError("Different data source; cannot dedup: "+name)
  a,b=fields(dp),fields(cp)
  if not a or a!=b:
   raise ValueError("Column names or data types differ; manual review required: "+name)
  if re.search(r"(?m)^\s*measure\s+",dp):
   raise ValueError("Copied table contains a measure; never remove automatically: "+name)
  if name in rel:
   raise ValueError("Copied table participates in relationships: "+name)
  mentions=[]
  for relative in files:
   if relative in (f"Model/definition/tables/{name}.tmdl","Model/definition/model.tmdl","Model/diagramLayout.json"):continue
   file=root/relative
   if file.suffix.lower() not in (".json",".tmdl",".pbip",".pbir",".pbism",".m",".txt",".md"):continue
   try:t=file.read_text("utf-8-sig")
   except (UnicodeError,OSError):continue
   if name in t:mentions.append(relative)
  if mentions:raise ValueError("Non-metadata files reference "+name+": "+repr(mentions[:8]))
  ref=f"ref table '{name}'"
  if text.count(ref)!=1:raise ValueError("Expected exactly one model table registration for "+name)
  query=re.search(r"(?m)^annotation PBI_QueryOrder = (.+)\s*$",text)
  if not query:raise ValueError("Missing Power BI query order annotation")
  order=json.loads(query.group(1))
  if order.count(name)!=1:raise ValueError("Query order not one-to-one for "+name)
  matches=[]
  for i,entry in enumerate(diagram["diagrams"]):
   for j,node in enumerate(entry.get("nodes",[])):
    if node.get("nodeIndex")==name:matches.append((i,j))
  if len(matches)!=1:raise ValueError("Diagram node not one-to-one for "+name)
  coverage.append({"removed_name":name,"canonical_name":expected,"physical_source":".".join(src(dp)),"matching_column_count":len(a),"relationship_references":0,"other_file_references":0,"model_registration":1,"query_order":1,"diagram_nodes":len(matches)})
 return text,rel,diagram,files,coverage

def pilot(src:Path,dst:Path):
 src=src.resolve()
 if not (src/"FootballPlayerAnalysis.pbip").is_file():raise ValueError("Source PBIP missing")
 if dst.resolve()==src or src in dst.resolve().parents:raise ValueError("Destination cannot replace or be nested inside source")
 if dst.exists():raise ValueError("Pilot directory already exists; refusing overwrite")
 before,relationships,diagram,hashes,coverage=profile(src)
 shutil.copytree(src,dst,ignore=shutil.ignore_patterns(".pbi"))
 model=dst/"Model/definition"
 registration=model/"model.tmdl"
 order_pattern=r"(?m)^(annotation PBI_QueryOrder = )(.+)$"
 def replace_order(match):
  entries=json.loads(match.group(2))
  entries=[x for x in entries if x not in TARGETS]
  return match.group(1)+json.dumps(entries,ensure_ascii=False,separators=(",",":"))
 current=before
 for name in TARGETS:
  current=current.replace(f"ref table '{name}'\n","",1)
 current,n=re.subn(order_pattern,replace_order,current,count=1)
 if n!=1:raise ValueError("Missing unique query-order metadata")
 registration.write_text(current,encoding="utf8")
 for d in diagram["diagrams"]:
  d["nodes"]=[node for node in d.get("nodes",[]) if node.get("nodeIndex") not in TARGETS]
 diagram_file=dst/"Model/diagramLayout.json"
 diagram_file.write_text(json.dumps(diagram,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 for name in TARGETS:
  (model/"tables"/(name+".tmdl")).unlink()
 # Post-apply strictly verify model, static references, unrelated bytes, and
 # all page/visual/report boundaries. No missing TMDL references are allowed.
 _,after_rel,after_diag,after_hashes,_=profile_remaining(dst)
 if after_rel!=relationships:raise ValueError("Relationships changed unexpectedly")
 expected=set(hashes)-{f"Model/definition/tables/{name}.tmdl" for name in TARGETS}
 if set(after_hashes)!=expected:raise ValueError("Unexpected output files")
 changed={relative for relative in expected if hashes[relative]!=after_hashes[relative]}
 if changed!={"Model/definition/model.tmdl","Model/diagramLayout.json"}:
  raise ValueError("Unexpected modified files: "+str(changed))
 page_count=len(list((dst/"Report/definition/pages").glob("*/page.json")))
 visual_count=len(list((dst/"Report/definition/pages").rglob("visual.json")))
 assert page_count==13 and visual_count==308
 assert len(list((dst/"Model/definition/tables").glob("*.tmdl")))==len(list((src/"Model/definition/tables").glob("*.tmdl")))-3
 for p in (dst/"Report/definition/pages").rglob("visual.json"):json.loads(p.read_text("utf8"))
 return {"result":"ISOLATED_DEDUP_PILOT_STATIC_PASS","source":str(src),"test_copy":str(dst),
         "removed_duplicates":[d["removed_name"] for d in coverage],
         "metadata_updates":sorted(changed),"checks":coverage,
         "pages_preserved":page_count,"visuals_preserved":visual_count,
         "other_file_hashes_identical":True,"relationships_untouched":True,
         "powerbi_runtime_render_tested":False,
         "production_owner_pbip_modified":False,
         "commercial_release_ready":False}

def profile_remaining(root:Path):
 model=root/"Model/definition"
 text=(model/"model.tmdl").read_text("utf-8-sig")
 rel=(model/"relationships.tmdl").read_text("utf-8-sig")
 layout=json.loads((root/"Model/diagramLayout.json").read_text("utf-8-sig"))
 query=re.search(r"(?m)^annotation PBI_QueryOrder = (.+)$",text)
 if not query:raise ValueError("Missing query order in migrated copy")
 entries=json.loads(query.group(1))
 names={p.stem for p in (model/"tables").glob("*.tmdl")}
 for t in TARGETS:
  if t in names or t in entries or f"ref table '{t}'" in text or t in rel:
   raise ValueError("Residual metadata dependency after removal: "+t)
  if any(n.get("nodeIndex")==t for diagram in layout["diagrams"] for n in diagram.get("nodes",[])):
   raise ValueError("Residual diagram node: "+t)
 if len(entries)!=len(set(entries)):raise ValueError("Duplicate query order entries")
 if any(ref not in names for ref in entries):raise ValueError("Missing query order table")
 if any(m.group(1).replace("''","'") not in names for m in re.finditer(r"(?m)^ref table '([^']+)'$",text)):
  raise ValueError("Dangling model ref table entry")
 hashes={f.relative_to(root).as_posix():digest(f.read_bytes()) for f in root.rglob("*") if f.is_file() and ".pbi" not in f.relative_to(root).parts}
 return text,rel,layout,hashes,None

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--source",type=Path,default=SOURCE)
 parser.add_argument("--output",type=Path,default=SANDBOX)
 parser.add_argument("--audit",type=Path,default=SANDBOX.parent/"safe_three_table_dedup_pilot.json")
 parser.add_argument("--dry-run",action="store_true")
 opts=parser.parse_args()
 if opts.dry_run:
  _,_,_,_,coverage=profile(opts.source)
  print(json.dumps({"status":"SAFE_THREE_TABLE_DEDUP_PLAN","candidates":coverage,"files_modified":0},ensure_ascii=False))
  return
 try:
  result=pilot(opts.source,opts.output)
 except (OSError,ValueError,AssertionError,json.JSONDecodeError) as error:
  raise SystemExit("DEDUP_SANDBOX_STOPPED: "+str(error))
 opts.audit.parent.mkdir(parents=True,exist_ok=True)
 opts.audit.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps({"status":result["result"],"removed_duplicates":result["removed_duplicates"],
                   "report_pages":result["pages_preserved"],"visuals":result["visuals_preserved"],
                   "audit":str(opts.audit)},ensure_ascii=False))
if __name__=="__main__":main()
