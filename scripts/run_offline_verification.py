#!/usr/bin/env python3
"""Offline verification of the NEXUS Football research repository.

Intentionally never accesses BigQuery, publishes artifacts or triggers CI.
Results are evidence for this commit only; a PASS is not production approval.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


def run(repo: Path, label: str, command: list[str], timeout: int) -> dict:
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=repo, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout, check=False,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        code, output = result.returncode, result.stdout
        status = "passed" if code == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        code, output, status = 124, str(exc), "timeout"
    except OSError as exc:
        code, output, status = 127, repr(exc), "unavailable"
    seconds = round(time.monotonic() - start, 3)
    print(f"[{status.upper()}] {label} ({seconds:.1f}s)", flush=True)
    if status != "passed":
        print(output[-1800:], flush=True)
    return {"name": label, "command": command, "status": status,
            "returncode": code, "duration_seconds": seconds,
            "output_tail": output[-6000:]}


def run_all(repo: Path, phases: list[str], timeout: int) -> dict:
    if not (repo / "dbt_project.yml").is_file():
        raise ValueError("Expected the GitHub repository root with dbt_project.yml")
    version = run(repo, "source_commit", ["git", "rev-parse", "HEAD"], 20)
    script_dir = str(repo / "scripts")
    test_dir = str(repo / "tests")
    py = sys.executable
    steps: list[tuple[str, list[str]]] = []
    if "source" in phases:
        steps.extend([
            ("python_syntax", [py, "-m", "compileall", "-q", "scripts", "tests"]),
            ("dbt_yaml_jinja_preflight", [py, f"{script_dir}/check_offline_ci.py"]),
            ("documentation_integrity", [py, f"{script_dir}/check_docs_integrity.py"]),
        ])
    if "ml" in phases:
        for pattern in (
            "test_ml_*.py", "test_evaluate_ml_artifacts.py",
            "test_walk_forward_research.py", "test_transfer_365d_source_contract.py",
        ):
            steps.append((f"ml_unit:{pattern}", [py, "-m", "unittest", "discover",
                                                  "-s", test_dir, "-p", pattern, "-v"]))
        steps.append(("ml_pipeline_synthetic_smoke", [py, f"{script_dir}/check_ml_pipeline.py"]))
    if "full" in phases:
        steps.append(("all_python_unit_tests", [py, "-m", "unittest", "discover", "-s",
                                                test_dir, "-p", "test_*.py", "-v"]))
    evidence = [run(repo, label, command, timeout) for label, command in steps]
    return {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "repository": "senanurcetin/football-player-performance-analysis",
            "commit_sha": version["output_tail"].strip() if version["status"] == "passed" else None,
            "python": platform.python_version(),
            "phases": phases,
            "source_type": "local_offline_checks_no_bigquery_no_ci",
            "results": evidence,
            "overall_status": "PASS" if evidence and all(x["status"] == "passed" for x in evidence) else "FAIL",
            "bigquery_verified": False,
            "model_real_data_verified": False,
            "powerbi_desktop_verified_by_this_runner": False,
            "hosted_ci_triggered_by_this_runner": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--phases", nargs="+", choices=["source", "ml", "full"],
                        default=["source", "ml", "full"])
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--report", type=Path, default=Path("verification_report.json"))
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be a positive number of seconds")
    if args.report.resolve().is_relative_to(args.repo.resolve()) and args.report.name in {
        "dbt_project.yml", "requirements.txt", "requirements-ml.txt"
    }:
        parser.error("Do not overwrite repository configuration")
    evidence = run_all(args.repo.resolve(), list(dict.fromkeys(args.phases)), args.timeout)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Report:", args.report.resolve(), "|", evidence["overall_status"])
    return 0 if evidence["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())