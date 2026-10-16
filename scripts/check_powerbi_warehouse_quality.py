#!/usr/bin/env python3
"""Read-only, budget-capped BigQuery quality gate for NEXUS Football PBIP.

Explicitly invoked by the owner. Never changes warehouse data, refreshes
Power BI Desktop, or asserts that any visual rendered successfully.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "data-analiz-490513"
DATASET = "football_mart"
LOCATION = "EU"
MAX_BYTES_BILLED = 10_485_760
TICK = chr(96)


def table(name: str) -> str:
    return f"{TICK}{PROJECT}.{DATASET}.{name}{TICK}"


QUERIES = {
    "club_performance": f"""
SELECT COUNT(*) AS n, COUNT(DISTINCT club_id) AS unique_clubs,
  COUNTIF(matches_played <= 0 OR matches_played IS NULL) AS invalid_matches,
  COUNTIF(win_rate IS NOT NULL AND
    ABS(win_rate - ROUND(SAFE_DIVIDE(wins, matches_played) * 100, 2)) > 0.11
  ) AS win_rate_mismatch,
  COUNTIF(win_rate < 0 OR win_rate > 100) AS invalid_win_rate,
  MIN(win_rate) AS min_win_rate, MAX(win_rate) AS max_win_rate
FROM {table("fct_club_performance")}
""".strip(),
    "club_risk": f"""
SELECT COUNT(*) AS n, COUNT(DISTINCT club_id) AS unique_clubs,
  COUNTIF(total_incoming_transfers < 0) AS negative_transfers,
  COUNTIF(known_fee_coverage_pct < 0 OR known_fee_coverage_pct > 100)
    AS fee_coverage_outside_pct,
  COUNTIF(outcome_365d_coverage_pct < 0 OR outcome_365d_coverage_pct > 100)
    AS outcome_coverage_outside_pct,
  COUNTIF(transfer_success_rate_pct < 0 OR transfer_success_rate_pct > 100)
    AS success_outside_pct,
  COUNTIF(observed_365d_transfers > total_incoming_transfers)
    AS outcome_exceeds_population
FROM {table("fct_club_risk_profile")}
""".strip(),
    "quality_audit": f"""
SELECT COUNT(*) AS audit_rows,
  CAST(MAX(audit_generated_at_utc) AS STRING) AS latest_audit_utc
FROM {table("fct_analytics_refresh_audit")}
""".strip(),
}

BLOCKER_KEYS = {
    "club_performance": ("invalid_matches", "win_rate_mismatch", "invalid_win_rate"),
    "club_risk": (
        "negative_transfers", "fee_coverage_outside_pct",
        "outcome_coverage_outside_pct", "success_outside_pct",
        "outcome_exceeds_population",
    ),
}


def run_query(sql: str, executable: str, *, timeout_seconds: int = 120) -> dict:
    """Execute a fixed SQL SELECT with the explicit 10 MiB/query billing ceiling."""
    # Windows .CMD wrappers split embedded newlines in positional SQL arguments.
    # Flatten immutable SELECT statements before passing them to the bq wrapper.
    command = [
        executable, f"--location={LOCATION}", "query",
        "--use_legacy_sql=false", f"--maximum_bytes_billed={MAX_BYTES_BILLED}",
        "--format=json", " ".join(sql.split()),
    ]
    process = subprocess.run(
        command, capture_output=True, text=True,
        timeout=timeout_seconds, check=False,
    )
    if process.returncode:
        # Never expose CLI stderr: it may include account and profile details.
        raise RuntimeError(
            f"BigQuery exit code {process.returncode}; inspect local credentials, "
            "permissions, EU dataset and 10 MiB billed-byte ceiling"
        )
    try:
        rows = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("BigQuery CLI did not return JSON") from exc
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise RuntimeError("Expected exactly one aggregate BigQuery row")
    return rows[0]


def assess(results: dict[str, dict], now: datetime, *, max_audit_age_days: int = 90) -> dict:
    """Evaluate warehouse invariants without treating missing values as zeros."""
    if now.tzinfo is None:
        raise ValueError("Provide timezone-aware UTC now")
    blockers: list[str] = []
    warnings: list[str] = []
    for name in ("club_performance", "club_risk"):
        row = results[name]
        count = int(row["n"])
        unique = int(row["unique_clubs"])
        if count < 1:
            blockers.append(f"{name}: warehouse has no rows")
        if unique != count:
            blockers.append(f"{name}: duplicate or missing club keys: {count} rows vs {unique} distinct")
        for key in BLOCKER_KEYS[name]:
            if int(row[key]) != 0:
                blockers.append(f"{name}: {key}={int(row[key])}")
    p = results["club_performance"]
    if p.get("min_win_rate") is None or p.get("max_win_rate") is None:
        blockers.append("club_performance: missing win-rate domain")
    audit = results["quality_audit"]
    audit_age_days = None
    if int(audit["audit_rows"]) < 1 or not audit["latest_audit_utc"]:
        warnings.append("No warehouse quality-audit timestamp is available")
    else:
        stamp = str(audit["latest_audit_utc"]).replace(" UTC", "+00:00")
        if stamp.endswith("+00"):
            stamp += ":00"
        try:
            parsed = datetime.fromisoformat(stamp)
        except ValueError as exc:
            raise ValueError("Invalid quality-audit timestamp") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        audit_age_days = (now - parsed.astimezone(timezone.utc)).total_seconds() / 86400
        if audit_age_days < 0:
            blockers.append("Quality-audit timestamp lies in the future")
        elif audit_age_days > max_audit_age_days:
            warnings.append(
                f"Quality-audit evidence is {audit_age_days:.0f} days old; "
                "label as historical, not live or current-season"
            )
    return {
        "status": "FAIL" if blockers else "WARN" if warnings else "PASS",
        "warehouse": f"{PROJECT}.{DATASET}",
        "read_only": True,
        "max_bytes_billed_per_query": MAX_BYTES_BILLED,
        "checks": results,
        "latest_audit_age_days": round(audit_age_days, 2) if audit_age_days is not None else None,
        "blocking_findings": blockers,
        "warnings": warnings,
        "desktop_refresh": "NOT_VERIFIED",
        "desktop_kpi_reconciliation": "NOT_VERIFIED",
        "portfolio_release": "HOLD",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="Explicitly run three fixed read-only SQL queries; max 10 MiB billed per query")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-audit-age-days", type=int, default=90)
    args = parser.parse_args(argv)
    if not args.execute:
        parser.error("Pass --execute to authorize the three bounded read-only queries")
    if args.max_audit_age_days < 1:
        parser.error("--max-audit-age-days must be positive")
    exe = shutil.which("bq")
    if not exe:
        parser.error("Google Cloud bq CLI is not available on PATH")
    try:
        results = {name: run_query(sql, exe) for name, sql in QUERIES.items()}
        output = assess(results, datetime.now(timezone.utc),
                        max_audit_age_days=args.max_audit_age_days)
    except (RuntimeError, ValueError, OSError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f"WAREHOUSE QUALITY CHECK BLOCKED: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if output["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
