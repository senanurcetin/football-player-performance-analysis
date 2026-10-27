#!/usr/bin/env python3
"""Promote the owner-accepted 34-source PBIP to the same user Documents path.

Requires Power BI Desktop closed. Never deletes an active model without a
complete reversible folder backup and verified replacement in the same NTFS
volume. Does not read credentials, query BigQuery, launch Power BI, or request
any screenshots. --check is non-mutating; --apply performs the swap.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,os,re,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

QA=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027\powerbi-full-dedup-qa-20261028\FootballPlayerAnalysis")
ACTIVE=Path(r"C:\Users\MONSTER\Documents\NEXUS-Football-PBI\FootballPlayerAnalysis")
REPORT_DIR=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027")
BACKUPS=ACTIVE.parent/"Backups"
def paths(base):
    return {x.relative_to(base).as_posix():x for x in base.rglob("*") if x.is_file()}
def sha(p):
    return hashlib.sha256(p.read_bytes()).digest()
def stats(p):
    tbl=p/"Model/definition/tables"
    tables=list(tbl.glob("*.tmdl"))
    bq=sum("GoogleBigQuery.Database(" in x.read_text("utf8") for x in tables)
    rel=(p/"Model/definition/relationships.tmdl").read_text("utf8")
    return {
      "model_files":len(tables),
      "bigquery_imports":bq,
      "relationships":len(re.findall(r"(?m)^relationship\s+",rel)),
      "visuals":len(list((p/"Report/definition/pages").rglob("visual.json"))),
      "pages":len(list((p/"Report/definition/pages").glob("*/page.json"))),
      "disk_bytes":sum(f.stat().st_size for f in paths(p).values()),
    }
def pbi_running():
    r=subprocess.run(["powershell","-NoProfile","-NonInteractive","-Command",
       "(Get-Process -Name PBIDesktop -ErrorAction SilentlyContinue | Measure-Object).Count"],
       capture_output=True,text=True,timeout=13,encoding="utf8",errors="replace")
    if r.returncode!=0 or not r.stdout.strip().isdigit():
        raise RuntimeError("Could not determine if Power BI Desktop is open")
    return int(r.stdout.strip())
def preflight():
    if not (QA/"FootballPlayerAnalysis.pbip").is_file() or not (ACTIVE/"FootballPlayerAnalysis.pbip").is_file():
        raise RuntimeError("Active or accepted QA PBIP descriptor is missing")
    qa,old=stats(QA),stats(ACTIVE)
    if (qa["bigquery_imports"],qa["relationships"],qa["pages"],qa["visuals"])!=(34,87,13,308):
        raise RuntimeError("Tested candidate fingerprint unexpectedly changed: "+repr(qa))
    if (old["bigquery_imports"],old["relationships"],old["pages"],old["visuals"])!=(65,158,13,308):
        raise RuntimeError("Active project was changed after acceptance: "+repr(old))
    aa,qq=paths(ACTIVE),paths(QA)
    extras=sorted(aa.keys()-qq.keys())
    expected_prefix="Model/definition/tables/"
    allowed=lambda x: (x.startswith(expected_prefix) and (x.endswith(" (2).tmdl") or x.split("/")[-1].startswith("LocalDateTable_"))) or x.startswith("Model/.pbi/") or x.startswith("Report/.pbi/")
    if not all(allowed(x) for x in extras):
        raise RuntimeError("Active contains unexpected non-QA files: "+repr([x for x in extras if not allowed(x)][:10]))
    if qq.keys()-aa.keys():
        raise RuntimeError("Accepted QA contains files absent from active; a broader change requires manual review")
    deltas=[key for key in qq if sha(qq[key])!=sha(aa[key])]
    expected_deltas={"Model/definition/model.tmdl","Model/definition/relationships.tmdl","Model/diagramLayout.json"}
    if set(deltas)!=expected_deltas:
        raise RuntimeError("Non-model content has changed relative to acceptance: "+repr(deltas))
    if pbi_running():
        raise RuntimeError("Power BI Desktop is running: do not replace active project")
    return {"qa":qa,"preexisting":old,"files_qa":len(qq),"files_old":len(aa),
            "removed_exclusive_files":len(extras),
            "changed_model_metadata":sorted(deltas),
            "cache_backed_up":any(x.startswith("Model/.pbi/") for x in extras)}
def promote():
    pre=preflight()
    stamp=datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    stage=ACTIVE.parent/(".NEXUS-Football-dedup-staging-"+stamp)
    backup=BACKUPS/("FootballPlayerAnalysis-pre-dedup-acceptance-"+stamp)
    BACKUPS.mkdir(parents=True,exist_ok=True)
    if stage.exists() or backup.exists():raise RuntimeError("Staging or backup already exists")
    # Stage and independently compare all bytes before moving the active dir.
    shutil.copytree(QA,stage)
    src_files=paths(QA)
    staged=paths(stage)
    if src_files.keys()!=staged.keys() or any(sha(x)!=sha(staged[n]) for n,x in src_files.items()):
        raise RuntimeError("Staged PBIP byte-for-byte verification failed; active untouched")
    if pbi_running():raise RuntimeError("Power BI opened during staging; active untouched")
    old_renamed=False
    try:
        os.replace(ACTIVE,backup)
        old_renamed=True
        os.replace(stage,ACTIVE)
    except Exception:
        if old_renamed and not ACTIVE.exists() and backup.exists():
            os.replace(backup,ACTIVE)
        raise
    try:
        active_files=paths(ACTIVE)
        if active_files.keys()!=src_files.keys() or any(sha(x)!=sha(active_files[n]) for n,x in src_files.items()):
            raise RuntimeError("Promoted project verification failed")
        if stats(ACTIVE)!=pre["qa"]:
            raise RuntimeError("Promoted project stats differ from QA")
        bstats=stats(backup)
        if bstats!=pre["preexisting"]:
            raise RuntimeError("Backup no longer matches former active project")
    except Exception:
        # Only attempt rollback if Desktop is not open, to avoid corrupting
        # an active Power BI session.
        if pbi_running()==0:
            broken=BACKUPS/("REJECTED-PBIP-"+stamp)
            os.replace(ACTIVE,broken)
            os.replace(backup,ACTIVE)
        raise
    return {
       "status":"OWNER_ACCEPTED_PBIP_PROMOTED_SOURCE_VERIFIED",
       "user_confirmed_tested":True,
       "new_active_pbip":str(ACTIVE/"FootballPlayerAnalysis.pbip"),
       "complete_original_rollback_folder":str(backup),
       "original_model_cache_in_rollback_only":pre["cache_backed_up"],
       "pre_upgrade":pre["preexisting"],
       "post_upgrade":stats(ACTIVE),
       "qa_files_byte_identical_to_active":True,
       "all_original_files_preserved_in_rollback":True,
       "promoted_metadata_files":pre["changed_model_metadata"],
       "report_pages_or_visuals_changed":False,
       "local_cache_reused":False,
       "bigquery_jobs":0,
       "additional_screenshots_requested":False,
       "external_powerbi_runtime_post_promotion_verified":False,
       "promoted_at_utc":datetime.now(timezone.utc).isoformat()
    }
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply",action="store_true")
    args=p.parse_args()
    try:
        if args.apply:
            result=promote()
            audit=REPORT_DIR/("workintech_pbip_production_promotion_20261028.json")
            audit.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
            print(json.dumps({"status":result["status"],"model":result["post_upgrade"],"rollback":result["complete_original_rollback_folder"],"audit":str(audit)},ensure_ascii=False))
        else:
            result=preflight()
            print(json.dumps({"status":"PROMOTION_PREFLIGHT_PASS_NOT_APPLIED",**result},ensure_ascii=False))
    except Exception as e:
        print("PBIP_PROMOTION_STOPPED:",type(e).__name__,str(e),file=sys.stderr)
        raise SystemExit(2)
if __name__=="__main__":main()
