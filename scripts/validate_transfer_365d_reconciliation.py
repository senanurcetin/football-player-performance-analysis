"""Validate transfer-level BigQuery discrepancy export; never query BigQuery here.

Input: CSV from analyses/audit_transfer_365d_row_level_20261020.sql.
This checks internal row/set consistency only. Source freshness and historical
screenshot matching require separate provider evidence and dashboard filters.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

REASONS = {
    "null_transfer_key",
    "duplicate_horizon_key",
    "duplicate_label_key",
    "label_without_horizon_key",
    "label_before_maturity_cutoff",
    "label_without_matured_observation",
    "matured_observation_without_label",
    "unexpected_inconsistency",
}
REQUIRED = {
    "transfer_key", "capture_date", "effective_cutoff_date",
    "horizon_rows", "label_rows", "dax_observed", "in_success_labels",
    "discrepancy_reason",
}

def parse_bool(value: str) -> bool:
    value = (value or '').strip().lower()
    if value in ("true", "1"): return True
    if value in ("false", "0"): return False
    raise ValueError(f"Invalid boolean: {value!r}")

def audit_export(path: Path, expected_capture_date: str) -> dict:
    try:
        capture = date.fromisoformat(expected_capture_date)
    except ValueError as exc:
        raise ValueError('Invalid requested capture date') from exc
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        counts: Counter[str] = Counter()
        keys: set[str] = set()
        total = 0
        cutoff_dates: set[str] = set()
        for row in reader:
            total += 1
            key = (row["transfer_key"] or "").strip()
            if key in keys:
                raise ValueError(f"Duplicate transfer_key in export: {key!r}")
            keys.add(key)
            if row["capture_date"] != expected_capture_date:
                raise ValueError(f"Unexpected capture_date for {key!r}")
            cutoff_value = row["effective_cutoff_date"] or ""
            try:
                cutoff = date.fromisoformat(cutoff_value)
            except ValueError as exc:
                raise ValueError(f'Invalid source cutoff for {key!r}') from exc
            if cutoff > capture:
                raise ValueError(f'Source cutoff after capture date for {key!r}')
            cutoff_dates.add(cutoff_value)
            reason = row["discrepancy_reason"]
            if reason not in REASONS:
                raise ValueError(f"Unknown discrepancy reason for {key!r}: {reason!r}")
            horizon = int(row["horizon_rows"])
            labels = int(row["label_rows"])
            if horizon < 0 or labels < 0: raise ValueError("Negative row count")
            dax = parse_bool(row["dax_observed"])
            in_labels = parse_bool(row["in_success_labels"])
            if in_labels != (labels > 0):
                raise ValueError(f"Invalid label flag for {key!r}")
            if dax and horizon == 0:
                raise ValueError(f"Observed DAX row absent from horizon: {key!r}")
            if reason == "label_before_maturity_cutoff" and (not in_labels or dax):
                raise ValueError(f"Incorrect maturity classification for {key!r}")
            if reason == "label_without_matured_observation" and (not in_labels or dax):
                raise ValueError(f"Incorrect label-only classification for {key!r}")
            if reason == "matured_observation_without_label" and (not dax or in_labels):
                raise ValueError(f"Incorrect observed-only classification for {key!r}")
            if reason == "label_without_horizon_key" and (horizon != 0 or labels == 0):
                raise ValueError(f"Incorrect missing-horizon classification for {key!r}")
            if reason == "duplicate_horizon_key" and horizon <= 1:
                raise ValueError(f"Incorrect duplicate horizon classification: {key!r}")
            if reason == "duplicate_label_key" and labels <= 1:
                raise ValueError(f"Incorrect duplicate label classification: {key!r}")
            if reason == "null_transfer_key" and key:
                raise ValueError("Non-null key marked null")
            if dax == in_labels and horizon == 1 and labels <= 1 and key:
                raise ValueError(f"Spurious discrepancy row: {key!r}")
            counts[reason] += 1
    if total == 0:
        raise ValueError("Empty export cannot substantiate the historical discrepancy")
    if not cutoff_dates or any(not d for d in cutoff_dates) or len(cutoff_dates) != 1:
        raise ValueError("Missing/inconsistent source cutoff")
    return {
        "status": "validated_export_only",
        "capture_date": expected_capture_date,
        "effective_cutoff_date": next(iter(cutoff_dates)),
        "discordant_or_duplicate_keys": total,
        "classification_counts": dict(sorted(counts.items())),
        "note": "Not BigQuery source freshness, dashboard-filter parity, or historical 3-key confirmation",
    }

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--capture-date", required=True)
    parser.add_argument("--output", type=Path)
    args=parser.parse_args()
    try: result=audit_export(args.input,args.capture_date)
    except (ValueError,OSError) as exc:
        print(f"FAIL: {exc}")
        return 1
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
