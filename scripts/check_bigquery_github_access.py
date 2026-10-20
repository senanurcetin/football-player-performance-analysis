"""Check GitHub BigQuery service-account access using metadata APIs ONLY.

No SQL/query jobs, dbt builds, snapshots, or model publication. Credentials
are loaded from GCP_SERVICE_ACCOUNT_JSON and never printed or persisted.
BigQuery metadata counts are not live SELECT COUNT(*) results.
"""
from __future__ import annotations
import argparse
import json
import os
from datetime import date,datetime
from pathlib import Path
from typing import Any

APPROVED_PROJECT="data-analiz-490513"
MART_DATASET="football_mart"
REQUIRED_TABLES=("fct_transfer_fixed_horizon_outcomes","fct_transfer_success_labels")

class MetadataPreflightError(RuntimeError):
    pass

def safe_date(x:Any)->str|None:
    return x.isoformat() if isinstance(x,(date,datetime)) else None

def inspect_metadata(client:Any,project:str)->dict:
    """Only get_dataset/get_table; never client.query()."""
    result={"scope":"metadata_only_no_sql","project":project,"status":"NOT_VERIFIED",
        "warehouse_query_jobs_started":0,"warehouse_tables_modified":0,
        "datasets":{},"required_tables":{},"optional_tables":{},
        "limitations":["Not a paid SQL test or BigQuery billing approval.",
                       "Metadata row counts may lag actual table rows.",
                       "Does not verify Power BI data, ML training, historical snapshots or CI."]}
    for ds in ("football_mart","football","football_ml"):
        try:
            d=client.get_dataset(f"{project}.{ds}")
            result["datasets"][ds]={"status":"FOUND","location":getattr(d,"location",None),
                                    "modified":safe_date(getattr(d,"modified",None))}
        except Exception as exc:
            result["datasets"][ds]={"status":"UNAVAILABLE","error_type":type(exc).__name__}
    if result["datasets"][MART_DATASET]["status"]!="FOUND":
        result["status"]="FAILED_REQUIRED_DATASET"
        return result
    for table in REQUIRED_TABLES:
        try:
            t=client.get_table(f"{project}.{MART_DATASET}.{table}")
            result["required_tables"][table]={
                "status":"FOUND","table_type":getattr(t,"table_type",None),
                "modified":safe_date(getattr(t,"modified",None)),
                "num_rows_metadata":getattr(t,"num_rows",None),
                "schema_columns":len(getattr(t,"schema",[]) or [])
            }
        except Exception as exc:
            result["required_tables"][table]={"status":"UNAVAILABLE","error_type":type(exc).__name__}
    if result["datasets"]["football_ml"]["status"]=="FOUND":
        tname="ml_player_market_value_current_predictions"
        try:
            t=client.get_table(f"{project}.football_ml.{tname}")
            result["optional_tables"][tname]={
                "status":"FOUND",
                "modified":safe_date(getattr(t,"modified",None)),
                "num_rows_metadata":getattr(t,"num_rows",None)
            }
        except Exception as exc:
            result["optional_tables"][tname]={"status":"UNAVAILABLE","error_type":type(exc).__name__}
    verified=all(t["status"]=="FOUND" for t in result["required_tables"].values())
    result["status"]="METADATA_PASS" if verified else "FAILED_REQUIRED_TABLES"
    return result

def credential_client(project:str):
    raw=os.environ.get("GCP_SERVICE_ACCOUNT_JSON","")
    if not raw.strip():
        raise MetadataPreflightError("GitHub secret GCP_SERVICE_ACCOUNT_JSON is missing or empty")
    try:
        info=json.loads(raw)
    except ValueError as exc:
        raise MetadataPreflightError("GitHub service account JSON is invalid") from exc
    if not isinstance(info,dict) or info.get("type")!="service_account":
        raise MetadataPreflightError("GitHub secret must contain service_account JSON")
    if not all(isinstance(info.get(x),str) and info[x].strip()
               for x in ("client_email","private_key","token_uri")):
        raise MetadataPreflightError("Service account JSON is incomplete")
    from google.oauth2.service_account import Credentials
    from google.cloud import bigquery
    creds=Credentials.from_service_account_info(
        info,scopes=["https://www.googleapis.com/auth/bigquery.readonly"]
    )
    return bigquery.Client(project=project,credentials=creds,location="EU")

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id",default=APPROVED_PROJECT)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.project_id!=APPROVED_PROJECT:
        print("FAIL: project ID does not match checked-in approved project")
        return 2
    report={"status":"NOT_RUN","project":args.project_id,"scope":"metadata_only_no_sql",
            "warehouse_query_jobs_started":0,"warehouse_tables_modified":0}
    try:
        client=credential_client(args.project_id)
        report=inspect_metadata(client,args.project_id)
    except MetadataPreflightError as exc:
        report["status"]="CREDENTIAL_PREFLIGHT_FAILED"
        print(f"FAIL: {exc}")
    except Exception as exc:
        report["status"]="METADATA_REQUEST_FAILED"
        report["error_type"]=type(exc).__name__
        print(f"FAIL: BigQuery metadata request failed ({type(exc).__name__})")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BigQuery metadata-only access:",report["status"])
    return 0 if report["status"]=="METADATA_PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
