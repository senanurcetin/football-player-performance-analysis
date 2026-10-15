"""Read-only portfolio release preflight for the PRODUCTION Power BI report.

No Power BI Desktop launch, token access, warehouse queries or hosted CI.
This is source integrity, NOT proof that Desktop refresh finished successfully.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "powerbi" / "workspace" / "FootballPlayerAnalysis"
PAGES = PROD / "Report" / "definition" / "pages"
TABLES = PROD / "Model" / "definition" / "tables"
FORBIDDEN = re.compile(r"\\b(?:synthetic(?:\\s+data|\\s+demo)?|demo(?:nstration)?(?:\\s+data)?|fake\\s+data|not\\s+real\\s+data|sahte\\s+veri)\\b", re.I)
NON_ENGLISH = re.compile("[ğüşöçıİĞÜŞÖÇ]")


def check() -> dict:
    errors=[]
    pages=list(PAGES.glob("*/page.json"))
    if len(pages)!=13:errors.append(f"Expected 13 production pages, found {len(pages)}")
    for page in pages:
        meta=json.loads(page.read_text(encoding="utf-8-sig"))
        title=meta.get("displayName","")
        if FORBIDDEN.search(title) or NON_ENGLISH.search(title):errors.append(f"Page title: {page}: {title}")
    visuals=list(PAGES.glob("*/visuals/*/visual.json"))
    for path in visuals:
        data=json.loads(path.read_text(encoding="utf-8-sig"))
        visual=data["visual"]
        for obj in visual.get("visualContainerObjects",{}).get("title",[]):
            t=obj.get("properties",{}).get("text",{}).get("expr",{}).get("Literal",{}).get("Value","")
            if FORBIDDEN.search(t) or NON_ENGLISH.search(t):errors.append(f"Visual heading: {path}: {t}")
        for obj in visual.get("objects",{}).get("general",[]):
            for para in obj.get("properties",{}).get("paragraphs",[]):
                for run in para.get("textRuns",[]):
                    text=run.get("value","")
                    if FORBIDDEN.search(text) or NON_ENGLISH.search(text):errors.append(f"Visible copy: {path}: {text[:90]}")
    tables=list(TABLES.glob("*.tmdl"))
    bigquery=[p for p in tables if "GoogleBigQuery.Database" in p.read_text(encoding="utf-8-sig")]
    if len(bigquery)<25:errors.append(f"Production BigQuery sources unexpectedly reduced: {len(bigquery)}")
    report=json.loads((PROD/"Report"/"definition"/"report.json").read_text(encoding="utf-8-sig"))
    items=[x.get("name") for pack in report.get("resourcePackages",[]) for x in pack.get("items",[])]
    if "NEXUS_Official_Transparent_Logo.png" not in items:errors.append("Official transparent NEXUS 2.0 branding absent")
    if not (PROD/"Report"/"StaticResources"/"RegisteredResources"/"NEXUS_Official_Transparent_Logo.png").exists():
        errors.append("Registered official transparent NEXUS 2.0 logo file absent")
    return {"status":"PASS" if not errors else "FAIL", "pages":len(pages), "visuals":len(visuals),
            "bigquery_source_tables":len(bigquery),"errors":errors,
            "scope":"production PBIP only; static source review, not a Desktop refresh or live warehouse proof"}

if __name__=="__main__":
    result=check()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    raise SystemExit(0 if result["status"]=="PASS" else 1)
