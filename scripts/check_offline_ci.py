"""Offline-only CI preflight: YAML, dbt model syntax, and source layout.

This deliberately does not connect to BigQuery, query datasets, read
GCP_SERVICE_ACCOUNT_JSON, or claim that dbt cloud models executed.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from jinja2 import Environment, TemplateSyntaxError

ROOT = Path(__file__).resolve().parents[1]
YAML_ROOTS = ("models", "tests", "macros", "snapshots", "seeds", "analyses")
SQL_ROOTS = ("models", "analyses")


def main() -> None:
    project_path = ROOT / "dbt_project.yml"
    if not project_path.is_file():
        raise SystemExit("dbt_project.yml is missing")
    project = yaml.safe_load(project_path.read_text(encoding="utf-8"))
    if not isinstance(project, dict) or project.get("config-version") != 2:
        raise SystemExit("dbt_project.yml does not contain config-version: 2")
    if not project.get("name") or not project.get("profile"):
        raise SystemExit("dbt_project.yml requires a name and profile")

    yaml_files = [project_path]
    yaml_files.extend(ROOT.glob("*.yml"))
    for root_name in YAML_ROOTS:
        root = ROOT / root_name
        if root.exists():
            yaml_files.extend(root.rglob("*.yml"))
            yaml_files.extend(root.rglob("*.yaml"))
    for path in sorted(set(yaml_files)):
        try:
            list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except yaml.YAMLError as exc:
            raise SystemExit(f"Invalid YAML in {path.relative_to(ROOT)}: {exc}") from exc

    # Jinja source parsing catches malformed delimiters, not invalid dbt
    # references or database-specific SQL. Those require authenticated dbt CI.
    environment = Environment(extensions=["jinja2.ext.do"])
    sql_files = []
    for root_name in SQL_ROOTS:
        root = ROOT / root_name
        if root.exists():
            sql_files.extend(root.rglob("*.sql"))
    if not sql_files:
        raise SystemExit("No dbt SQL models found")
    for path in sql_files:
        try:
            environment.parse(path.read_text(encoding="utf-8"))
        except TemplateSyntaxError as exc:
            raise SystemExit(
                f"Invalid Jinja syntax in {path.relative_to(ROOT)}:{exc.lineno}: {exc}"
            ) from exc

    print(
        f"Offline preflight passed: {len(set(yaml_files))} YAML files, "
        f"{len(sql_files)} SQL/Jinja files. No BigQuery access attempted."
    )


if __name__ == "__main__":
    main()
