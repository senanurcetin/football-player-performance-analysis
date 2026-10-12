#!/usr/bin/env python3
"""Targeted offline probes to localize the synthetic Power BI demo CI failure."""
from __future__ import annotations

import argparse

import check_powerbi_offline_demo as checker


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scope", choices=("transfer", "relationships", "joins", "keys", "rates"))
    args = parser.parse_args()

    tables = checker.DEMO / "Model" / "definition" / "tables"
    if args.scope == "transfer":
        fixtures = {
            path.stem: checker.load_inline_fixture(path)
            for path in tables.glob("*.tmdl")
            if not path.name.startswith(("LocalDateTable_", "DateTableTemplate_"))
        }
        checker.check_365_day_transfer_contract(fixtures)
        label = f"{len(fixtures)} fixture tables and 365d transfer arithmetic"
    else:
        count, relations = checker.check_demo_relationships(tables)
        label = f"{count} fixture tables and {relations} relationships"
        if args.scope == "joins":
            checker.errors[:] = [
                e for e in checker.errors
                if any(k in e for k in (
                    "relationship", "reference field", "reference target",
                    "one-side key",
                ))
            ]
            label += " (join constraints)"
        elif args.scope == "keys":
            checker.errors[:] = [
                e for e in checker.errors
                if any(k in e for k in (
                    "Missing fixture rows", "NULL/missing", "Duplicate key",
                ))
            ]
            label += " (unique keys)"
        elif args.scope == "rates":
            checker.errors[:] = [
                e for e in checker.errors
                if any(k in e for k in (
                    "player", "Club", "Competition", "Malformed",
                    "Zero", "goals", "assists",
                )) and "relationship" not in e
            ]
            label += " (metric arithmetic)"

    if checker.errors:
        print(f"{label} FAILED:")
        for issue in checker.errors:
            print(" - " + issue)
        return 1
    print(f"{label} OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
