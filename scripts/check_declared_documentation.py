"""Offline validation of SQL model and declared YAML column descriptions.

This is not physical BigQuery catalog verification. The separate
check_documentation_coverage.py validates physical columns after dbt docs generate.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def audit(root: Path) -> tuple[dict[str, int], list[str]]:
    model_root = root / "models"
    errors: list[str] = []
    sql_files = sorted(model_root.rglob("*.sql"))
    sql_names: dict[str, list[Path]] = {}
    for file in sql_files:
        sql_names.setdefault(file.stem, []).append(file)
    for name, paths in sql_names.items():
        if len(paths) != 1:
            errors.append(f"Duplicate SQL model name: {name}")
    declared: dict[str, Path] = {}
    total_columns = 0
    yaml_files = sorted([*model_root.rglob("*.yml"), *model_root.rglob("*.yaml")])
    for file in yaml_files:
        try:
            item = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, UnicodeError) as exc:
            errors.append(f"Invalid YAML {file}: {exc}")
            continue
        if not isinstance(item, dict):
            errors.append(f"Non-mapping YAML: {file}")
            continue
        models = item.get("models") or []
        if not isinstance(models, list):
            errors.append(f"Non-list models entry: {file}")
            continue
        for model in models:
            if not isinstance(model, dict) or not isinstance(model.get("name"), str):
                errors.append(f"Invalid model declaration: {file}")
                continue
            name = model["name"]
            if name in declared:
                errors.append(f"Duplicate model declaration: {name}")
            declared[name] = file
            if not str(model.get("description") or "").strip():
                errors.append(f"Missing model description: {name}")
            columns = model.get("columns")
            if not isinstance(columns, list) or not columns:
                errors.append(f"Missing column declarations: {name}")
                continue
            seen: set[str] = set()
            for col in columns:
                if not isinstance(col, dict) or not isinstance(col.get("name"), str):
                    errors.append(f"Invalid column: {name}")
                    continue
                column_name = col["name"].lower()
                total_columns += 1
                if column_name in seen:
                    errors.append(f"Duplicate declared column: {name}.{column_name}")
                seen.add(column_name)
                if not str(col.get("description") or "").strip():
                    errors.append(f"Missing declared column description: {name}.{column_name}")
    for name in sorted(sql_names.keys() - declared.keys()):
        errors.append(f"Undocumented SQL model: {name}")
    for name in sorted(declared.keys() - sql_names.keys()):
        errors.append(f"Orphan YAML model declaration: {name}")
    if not sql_files:
        errors.append("No SQL models found")
    return {"sql_models": len(sql_files), "yaml_models": len(declared),
            "declared_columns": total_columns}, errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=ROOT)
    args = parser.parse_args()
    results, errors = audit(args.repo.resolve())
    if errors:
        print("\n".join(errors))
        print(f"FAIL: {len(errors)} declaration issue(s)")
        return 1
    print(f"PASS: {results['sql_models']} SQL models, "
          f"{results['yaml_models']} declared models, "
          f"{results['declared_columns']} described declared columns")
    print("Physical BigQuery catalog columns have NOT been checked.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
