#!/usr/bin/env python3
"""CI-free Power BI handoff preflight. Not a Desktop or BigQuery verification."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ("pbip_structure", ("scripts/check_powerbi_project.py",)),
    ("demo_source", ("scripts/check_powerbi_offline_demo.py",)),
    ("visual_bindings", ("scripts/audit_powerbi_visuals.py",)),
    ("visual_layout", ("scripts/audit_powerbi_layout.py",)),
    ("nexus_product", ("scripts/check_powerbi_nexus_product.py",)),
    ("unit_tests", ("-m", "unittest", "discover", "-s", "tests", "-p", "test_powerbi_*.py")),
)


def layout_warnings(output: str) -> int | None:
    """Parse the layout audit's JSON array before its human-readable footer."""
    try:
        reports, _ = json.JSONDecoder().raw_decode(output.lstrip())
        if not isinstance(reports, list):
            return None
        return sum(int(report["warning_count"]) for report in reports)
    except (ValueError, TypeError, KeyError):
        return None


def decision(checks: list[dict]) -> str:
    """An unknown, missing, or failing source check cannot pass the gate."""
    if not checks or any(c.get("status") == "FAIL" for c in checks):
        return "FAIL"
    if any(c.get("status") not in ("PASS", "WARN") for c in checks):
        return "FAIL"
    return "WARN" if any(c["status"] == "WARN" for c in checks) else "PASS"


def run_check(root: Path, name: str, args: tuple[str, ...], timeout: int) -> dict:
    command = [sys.executable, *args]
    started = time.monotonic()
    result = {"name": name, "command": command, "status": "FAIL"}
    try:
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True,
                                   timeout=timeout, check=False)
        result["returncode"] = completed.returncode
        result["stdout_tail"] = completed.stdout[-4000:]
        result["stderr_tail"] = completed.stderr[-2000:]
        result["status"] = "PASS" if completed.returncode == 0 else "FAIL"
        if name == "visual_layout" and completed.returncode == 0:
            count = layout_warnings(completed.stdout)
            result["warning_count"] = count
            if count is None:
                result["status"] = "FAIL"  # Do not hide malformed layout output.
            elif count:
                result["status"] = "WARN"  # Requires review; not proof of overlap.
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["error"] = str(exc)
    result["seconds"] = round(time.monotonic() - started, 2)
    return result


def git_sha(root: Path) -> str | None:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True,
                              capture_output=True, timeout=10, check=False)
        return proc.stdout.strip() if proc.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=None,
                        help="Write a JSON evidence summary at this path")
    parser.add_argument("--timeout", type=int, default=180,
                        help="Timeout per source check in seconds (default: 180)")
    opts = parser.parse_args()
    if opts.timeout < 1:
        parser.error("--timeout must be at least one second")
    root = opts.repository.resolve()
    checks = [run_check(root, name, args, opts.timeout) for name, args in CHECKS]
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repository": str(root),
        "git_sha": git_sha(root),
        "edition_to_open": "powerbi/workspace/FootballPlayerAnalysis/FootballPlayerAnalysis.pbip",
        "source_checks": decision(checks),
        "powerbi_desktop_refresh": "NOT_VERIFIED",
        "bigquery_production_reconciliation": "NOT_VERIFIED",
        "portfolio_release": "HOLD",
        "checks": checks,
    }
    rendered = json.dumps(record, indent=2, ensure_ascii=False)
    print(rendered)
    if opts.output:
        opts.output.parent.mkdir(parents=True, exist_ok=True)
        opts.output.write_text(rendered + "\n", encoding="utf-8")
    return 1 if record["source_checks"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
