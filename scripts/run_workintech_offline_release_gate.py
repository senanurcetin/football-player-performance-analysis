#!/usr/bin/env python3
"""One-command, CI-free, zero-screenshot Workintech offline release gate.

Never modifies Power BI, snapshots, BigQuery or source files, and never
asks the owner for screenshot uploads. Output is an inspectable JSON report.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RECOVERY=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027")

def load(relative):
    path=ROOT/relative
    spec=importlib.util.spec_from_file_location(path.stem,path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load offline gate module "+str(path))
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def image_evidence():
    manifest=ROOT/"docs"/"assets"/"screenshots"/"capture_manifest.json"
    info=json.loads(manifest.read_text(encoding="utf-8"))
    captures=info.get("captures",[])
    bad=[]
    for item in captures:
        rel=item.get("path")
        if not isinstance(rel,str) or not rel.startswith("docs/assets/screenshots/"):
            bad.append({"name":str(rel),"reason":"invalid-relative-source-path"})
            continue
        dest=(ROOT/rel).resolve()
        if not dest.is_relative_to((ROOT/"docs/assets/screenshots").resolve()) or not dest.is_file():
            bad.append({"name":rel,"reason":"missing-or-outside-gallery"})
            continue
        raw=dest.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item.get("sha256"):
            bad.append({"name":rel,"reason":"source-image-hash-mismatch"})
    return {
        "capture_count":len(captures),
        "capture_date":info.get("captured"),
        "hashes_verified":len(captures)-len(bad),
        "errors":bad,
        "status":"PASS_HISTORICAL_IMAGES_PRESERVED" if len(captures)==13 and not bad else "FAILED_SCREENSHOT_ARCHIVE_INTEGRITY",
        "live_render_verified":False,
        "new_screenshots_requested":False,
    }

def run(pbip:Path, archive:Path, manifest:Path):
    semantic=load("scripts/audit_workintech_semantic_model.py").assess(pbip)
    relationships=load("scripts/plan_workintech_relationship_migration.py").plan(pbip)
    quality=load("scripts/profile_workintech_source_quality.py").build_profile(archive,manifest)
    images=image_evidence()
    findings=[]
    for entry in semantic["findings"]:
        findings.append({"source":"semantic_model",**entry})
    for entry in quality["issues"]:
        findings.append({"source":"historical_source",**entry})
    if semantic["structural_errors"]:
        for error in semantic["structural_errors"]:
            findings.append({"source":"semantic_model","severity":"critical","code":"STRUCTURAL_INVALID","description":error})
    if images["status"]!="PASS_HISTORICAL_IMAGES_PRESERVED":
        findings.append({"source":"images","severity":"high","code":"SCREENSHOT_INTEGRITY","description":"Archived screenshot checksum mismatch."})
    # This is intentionally stricter than passing a local unit test.
    status="RELEASE_HOLD" if findings else "OFFLINE_CHECKS_PASS_RUNTIME_ACCEPTANCE_UNVERIFIED"
    return {
        "audit_created_utc":datetime.now(timezone.utc).isoformat(),
        "environment":"workintech-working / EU / historical Kaggle source",
        "status":status,
        "assessment_type":"offline source and semantic model only; NOT a live Power BI screenshot or production certification",
        "bigquery_jobs_started":0,
        "powerbi_refresh_started":False,
        "user_screenshot_requests":0,
        "semantic_model":{
            "status":semantic["status"],
            "governed_tables":semantic["governed_table_count"],
            "extra_duplicate_imports":semantic["duplicate_physical_source_import_count"],
            "additional_unique_imports":semantic["additional_unique_import_count"],
            "extra_imports_with_relationships":semantic["extra_imports_referenced_by_relationships"],
            "pages":semantic["pages"],
            "visuals":semantic["visuals"],
            "structure_errors":semantic["structural_errors"],
        },
        "historical_source":{
            "status":quality["status"],
            "archive_max_game_date":quality["matches"]["max_date"],
            "source_row_counts_all_match":all(r["match"] for r in quality["rows"].values()),
            "games_unique":quality["matches"]["rows"]==quality["matches"]["unique_game_ids"],
            "same_day_conflicting_valuations":quality["valuations"]["groups_with_conflicting_positive_values"],
            "missing_appearance_player_refs":quality["appearance_orphans"]["missing_players"],
            "planned_or_future_dated_transfers":quality["transfers"]["future_dated_as_of_2026_10_27"],
            "future_transfer_outcome_exclusion_sql_verified":(
                "where not is_future_transfer" in (ROOT/"models/marts/fct_transfer_fixed_horizon_outcomes.sql").read_text("utf8").lower()
            ),
            "source_competition_games_without_dictionary_description":sum(x["games"] for x in quality["source_competitions_without_dictionary_entry"]),
            "nonpositive_valuation_rows":quality["valuations"]["nonpositive_values"],
        },
        "existing_images":images,
        "relationship_migration":{
            "status":relationships["status"],
            "counts":relationships["counts"],
            "filter_direction_disagreements":relationships["same_pair_different_attributes"],
            "novel_non_date_relationships":relationships["novel_non_date_relationships"],
            "automatic_bulk_dedup_authorized":False,
        },
        "findings":findings,
        "next_release_gates":[
            "Preserve the 29 exact duplicate relation pairs but resolve 2 differing ML cross-filter directions before consolidating model imports.",
            "Preserve 40 auto-date variations and 9 novel relationships during any safe semantic migration.",
            "Consolidate 31 duplicate sources only after preserving relationships, fields, measures, and page bindings.",
            "Validate 3 additional imported tables against governed grain and refresh costs.",
            "Document and test orphan-appearance handling; never fabricate player identity.",
            "Confirm that future transfer dates never inflate realized outcomes.",
            "Independently validate important KPIs and temporal ML on holdout cohorts before business release.",
            "Verify Power BI interaction and service scheduled refresh when authorized, without asking for additional screenshots.",
        ],
    }

def main():
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--pbip",type=Path,default=ROOT/"powerbi/workintech-20261027/FootballPlayerAnalysis")
    arg.add_argument("--archive",type=Path,default=RECOVERY/"kaggle_archive_typed_parquet")
    arg.add_argument("--manifest",type=Path,default=RECOVERY/"kaggle_archive_typed_manifest.json")
    arg.add_argument("--report",type=Path,default=RECOVERY/"workintech_offline_release_gate.json")
    args=arg.parse_args()
    try:
        report=run(args.pbip,args.archive,args.manifest)
    except (OSError,ValueError,RuntimeError,KeyError,ImportError,json.JSONDecodeError) as error:
        print(json.dumps({"status":"AUDIT_FAILED","error":type(error).__name__+": "+str(error)},ensure_ascii=False))
        raise SystemExit(2)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({
       "status":report["status"],
       "governed_tables":report["semantic_model"]["governed_tables"],
       "duplicate_imports":report["semantic_model"]["extra_duplicate_imports"],
       "source_max_game_date":report["historical_source"]["archive_max_game_date"],
       "archive_screenshots_verified":report["existing_images"]["hashes_verified"],
       "issues":len(report["findings"]),
       "report":str(args.report),
    },ensure_ascii=False))
if __name__=="__main__":main()
