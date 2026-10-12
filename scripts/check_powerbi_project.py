#!/usr/bin/env python3
"""Offline structural preflight for the Football Player Analysis Power BI project.

Usage: python scripts/check_powerbi_project.py
Does not connect to BigQuery or require Power BI Desktop.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "powerbi" / "workspace" / "FootballPlayerAnalysis"
MODEL = PROJECT / "Model" / "definition"
REPORT = PROJECT / "Report"
DEFINITION = REPORT / "definition"


def check_project():
    errors = []

    def load_json(path):
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            errors.append(f"Invalid or missing JSON {path.relative_to(ROOT)}: {exc}")
            return None

    pbip = load_json(PROJECT / "FootballPlayerAnalysis.pbip")
    pbir = load_json(REPORT / "definition.pbir")
    load_json(PROJECT / "Model" / "definition.pbism")
    if isinstance(pbip, dict):
        for artifact in pbip.get("artifacts", []):
            path = artifact.get("report", {}).get("path")
            if path and not (PROJECT / path / "definition.pbir").is_file():
                errors.append(f"Missing report artifact: {path}")
    if isinstance(pbir, dict):
        dataset_path = pbir.get("datasetReference", {}).get("byPath", {})
        if dataset_path and not (REPORT / dataset_path["path"] / "definition.pbism").is_file():
            errors.append("Missing semantic model referenced by definition.pbir")

    model_path = MODEL / "model.tmdl"
    if not model_path.is_file():
        errors.append("Missing Model/definition/model.tmdl")
    else:
        model = model_path.read_text(encoding="utf-8-sig")
        names = {p.stem for p in (MODEL / "tables").glob("*.tmdl")}
        refs = re.findall(r"^ref table (.+?)\s*$", model, flags=re.MULTILINE)
        missing = sorted(set(refs) - names)
        unlisted = sorted(names - set(refs))
        for name in missing:
            errors.append(f"Orphan TMDL table reference: {name}")
        for name in unlisted:
            errors.append(f"Table file omitted from model.tmdl: {name}")
        query_order = re.search(r"^annotation PBI_QueryOrder = (\[.*\])$", model, flags=re.MULTILINE)
        if query_order:
            for name in json.loads(query_order.group(1)):
                if name not in names:
                    errors.append(f"Stale PBI_QueryOrder table: {name}")

    if (REPORT / "report.json").exists():
        errors.append("Legacy Report/report.json conflicts with Report/definition/ (PBIR)")

    report = load_json(DEFINITION / "report.json")
    pages = load_json(DEFINITION / "pages" / "pages.json")
    if isinstance(pages, dict):
        available = {p.parent.name for p in (DEFINITION / "pages").glob("*/page.json")}
        for name in pages.get("pageOrder", []):
            if name not in available:
                errors.append(f"Missing PBIR page: {name}")
        active = pages.get("activePageName")
        if active and active not in available:
            errors.append(f"Missing active PBIR page: {active}")
    if isinstance(report, dict):
        for package in report.get("resourcePackages", []):
            for item in package.get("items", []):
                resource = REPORT / "StaticResources" / package["name"] / item["path"]
                if not resource.is_file():
                    errors.append(f"Missing report resource: {resource.relative_to(ROOT)}")

    for path in DEFINITION.rglob("*.json"):
        if path not in {DEFINITION / "report.json", DEFINITION / "pages" / "pages.json"}:
            definition = load_json(path)
            if path.name == "visual.json" and isinstance(definition, dict):
                if "visualContainerObjects" in definition:
                    errors.append(
                        f"Invalid root-level visualContainerObjects in {path.relative_to(ROOT)}: "
                        "must be nested under visual"
                    )

    return errors


if __name__ == "__main__":
    issues = check_project()
    if issues:
        print("Power BI project preflight FAILED:")
        for issue in issues:
            print(f" - {issue}")
        sys.exit(1)
    print("Power BI project preflight OK (files and references; not a Desktop load test).")
