#!/usr/bin/env python3
"""Opt in to a lean, genuine-data Power BI production model backed by BigQuery.

Run --apply only on a working Git branch. Source warehouse data is untouched.
The archival full schema remains retrievable from Git history.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = ("workspace", "offline-demo")
UNUSED = {
    "fct_player_match_performance",
    "fct_player_rolling_form",
}
LINKED_AUTODATE = {
    "LocalDateTable_8c7ab90b-e50b-4759-81b0-b489a1d97d36",
    "LocalDateTable_27442457-9c27-41f0-a2d1-637177c79376",
}
ALL_REMOVED = UNUSED | LINKED_AUTODATE
LEGACY = "GoogleBigQuery.Database([UseStorageApi=false])"
ADBC = 'GoogleBigQuery.Database([Implementation="2.0",UseStorageApi=false])'


def transform_project(project: Path, apply: bool = False) -> dict:
    definitions = project / "Model" / "definition"
    tables = definitions / "tables"
    if not tables.is_dir():
        raise ValueError(f"PBIP semantic model not found: {project}")
    existing = {name for name in ALL_REMOVED if (tables / (name + ".tmdl")).exists()}
    if existing and existing != ALL_REMOVED:
        raise ValueError(f"Partial optimization detected, aborting: {sorted(existing)}")

    model_path = definitions / "model.tmdl"
    model = model_path.read_text(encoding="utf-8-sig")
    match = re.search(r"(?m)^annotation PBI_QueryOrder = (\[.*\])$", model)
    if not match:
        raise ValueError("Missing Power BI model QueryOrder annotation")
    order = json.loads(match.group(1))
    order_new = [name for name in order if name not in UNUSED]
    for name in ALL_REMOVED:
        model = model.replace("ref table " + name + "\n", "")
    match_new = re.search(r"(?m)^annotation PBI_QueryOrder = (\[.*\])$", model)
    assert match_new
    model = (model[:match_new.start(1)]
             + json.dumps(order_new, ensure_ascii=False, separators=(",", ":"))
             + model[match_new.end(1):])

    relation_file = definitions / "relationships.tmdl"
    original_relations = relation_file.read_text(encoding="utf-8-sig")
    relation_blocks = re.split(r"(?m)(?=^relationship )", original_relations)
    remaining_relations = []
    removed_relations = 0
    for block in relation_blocks:
        dangling = any(re.search(r"\b" + re.escape(name) + r"\.", block)
                       for name in ALL_REMOVED)
        if block.startswith("relationship ") and dangling:
            removed_relations += 1
            continue
        remaining_relations.append(block)
    relationships = "".join(remaining_relations)

    replacements = {}
    for table_file in sorted(tables.glob("*.tmdl")):
        source = table_file.read_text(encoding="utf-8-sig")
        if LEGACY in source and table_file.stem not in ALL_REMOVED:
            replacements[table_file] = source.replace(LEGACY, ADBC)

    # Build an in-memory integrity check before changing any files.
    for name in ALL_REMOVED:
        if (re.search(r"\b" + re.escape(name) + r"\b", model)
                or re.search(r"\b" + re.escape(name) + r"\b", relationships)):
            raise ValueError(f"Orphaned model/relationship reference: {name}")
    if len(order_new) != len(order) - len(UNUSED) and existing:
        raise ValueError("Unexpected import query order")

    if apply:
        for name in existing:
            (tables / (name + ".tmdl")).unlink()
        if model_path.read_text(encoding="utf-8-sig") != model:
            model_path.write_text(model, encoding="utf-8", newline="\n")
        if original_relations != relationships:
            relation_file.write_text(relationships, encoding="utf-8", newline="\n")
        for file, source in replacements.items():
            file.write_text(source, encoding="utf-8", newline="\n")
        for file in (definitions / "tables").glob("*.tmdl"):
            data = file.read_text(encoding="utf-8-sig")
            if any(re.search(r"\b" + re.escape(n) + r"\b", data) for n in ALL_REMOVED):
                raise ValueError(f"Leftover model source reference in {file.name}")
        for file in (project / "Report" / "definition").rglob("*.json"):
            data = file.read_text(encoding="utf-8-sig")
            if any(re.search(r"\b" + re.escape(n) + r"\b", data) for n in ALL_REMOVED):
                raise ValueError(f"Unexpected visual dependency in {file.name}")

    return {
        "edition": project.parent.name,
        "mode": "APPLIED" if apply else "PREVIEW",
        "removed_large_unused_tables": sorted(existing & UNUSED),
        "removed_auto_dates": sorted(existing & LINKED_AUTODATE),
        "removed_unused_relationships": removed_relations,
        "adbc_v2_partitions_modified": len(replacements),
        "storage_api": "DISABLED",
        "portfolio_release": "HOLD",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Modify both edition source files; use only on Git branch")
    args = parser.parse_args()
    for edition in EDITIONS:
        project = ROOT / "powerbi" / edition / "FootballPlayerAnalysis"
        report = transform_project(project, apply=args.apply)
        print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
