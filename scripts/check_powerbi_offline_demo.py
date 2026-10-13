#!/usr/bin/env python3
"""Offline PBIP static checks. This does not run Desktop or certify report visuals."""
import json
import re
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "powerbi" / "offline-demo" / "FootballPlayerAnalysis"
PROD = ROOT / "powerbi" / "workspace" / "FootballPlayerAnalysis"
errors = []

def check(condition, description):
    if not condition:
        errors.append(description)

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        errors.append(f"Missing/bad JSON: {path.relative_to(ROOT)} ({exc})")
        return {}



def split_m_csv(row):
    """Split a simple #table row without splitting #date/#datetime arguments."""
    values, current, in_string, depth = [], [], False, 0
    i = 0
    while i < len(row):
        char = row[i]
        if char == '"':
            current.append(char)
            if in_string and i + 1 < len(row) and row[i + 1] == '"':
                current.append('"')
                i += 2
                continue
            in_string = not in_string
        elif not in_string and char == "(":
            depth += 1
            current.append(char)
        elif not in_string and char == ")":
            depth -= 1
            current.append(char)
        elif not in_string and char == "," and depth == 0:
            values.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        i += 1
    values.append("".join(current).strip())
    if in_string or depth:
        raise ValueError("Unbalanced M literal in sample row")
    return values


def decode_literal(value):
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('""', '"')
    if value in ("true", "false"):
        return value == "true"
    if value == "null":
        return None
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value  # e.g. #datetime(2025, 5, 1, 0, 0, 0)


def load_inline_fixture(table_file):
    text = table_file.read_text(encoding="utf-8-sig")
    match = re.search(r"type table \[([^\]]+)\],", text)
    if not match:
        errors.append(f"Missing typed #table schema in {table_file.name}")
        return []
    fields = re.findall(r'#"((?:[^"]|"")*)"\s*=', match.group(1))
    fields = [field.replace('""', '"') for field in fields]
    if not fields:
        errors.append(f"No named columns in fixture {table_file.name}")
        return []
    source = text[match.end():]
    records = re.findall(r"^[\t ]+\{(.+)\},?$", source, re.MULTILINE)
    if not records:
        errors.append(f"No inline rows in fixture {table_file.name}")
        return []
    output = []
    for lineno, record in enumerate(records, 1):
        try:
            values = split_m_csv(record)
        except ValueError as exc:
            errors.append(f"{table_file.name} row {lineno}: {exc}")
            continue
        if len(values) != len(fields):
            errors.append(
                f"{table_file.name} row {lineno}: {len(values)} cells "
                f"but {len(fields)} schema fields"
            )
            continue
        output.append(dict(zip(fields, (decode_literal(v) for v in values))))
    return output




def parse_fixture_date(value):
    """Read an inline Power Query #datetime literal without evaluating M."""
    match = re.fullmatch(r"#datetime\((\d+),\s*(\d+),\s*(\d+),\s*\d+,\s*\d+,\s*\d+\)", str(value))
    if not match:
        raise ValueError(f"Unexpected fixture datetime: {value}")
    return date(*(int(v) for v in match.groups()))



def check_club_risk_demo_contract(fixtures):
    """Catch incorrectly typed #table cells, fraction/percent and sample-size drift."""
    rows = fixtures.get("fct_club_risk_profile", [])
    check(len(rows) == 6, "Expected six deterministic club-risk demo rows")
    for row in rows:
        key = row.get("club_id")
        count = row.get("total_incoming_transfers")
        known = row.get("transfers_with_known_fee")
        observed = row.get("observed_365d_transfers")
        successes = row.get("successful_transfers")
        failures = row.get("unsuccessful_transfers")
        numeric_rates = all(isinstance(row.get(name), (int, float)) and
                            not isinstance(row.get(name), bool) for name in
                            ("known_fee_coverage_pct", "outcome_365d_coverage_pct",
                             "avg_overpay_pct", "transfer_success_rate_pct"))
        for field in ("known_fee_coverage_pct", "outcome_365d_coverage_pct",
                      "avg_overpay_pct", "transfer_success_rate_pct"):
            check(isinstance(row.get(field), (int, float)) and not isinstance(row.get(field), bool),
                  f"Club-risk {key}: {field} is a text literal, not a number")
        if numeric_rates and all(isinstance(v, (int, float)) for v in (count, known, observed, successes, failures)) and count > 0:
            check(abs(row["known_fee_coverage_pct"] - 100 * known / count) < 0.02,
                  f"Club-risk {key}: known-fee coverage must be percentage points")
            check(abs(row["outcome_365d_coverage_pct"] - 100 * observed / count) < 0.02,
                  f"Club-risk {key}: 365d coverage must be percentage points")
            if successes + failures:
                check(abs(row["transfer_success_rate_pct"] -
                          100 * successes / (successes + failures)) < 0.02,
                      f"Club-risk {key}: success rate must be percentage points")
            check(row.get("meets_minimum_sample_size") is (observed >= 30),
                  f"Club-risk {key}: minimum sample-size flag differs from SQL")
            if observed < 30:
                check(row.get("transfer_risk_category") == "insufficient_data",
                      f"Club-risk {key}: small cohort must be classified insufficient_data")

def check_365_day_transfer_contract(fixtures):
    """Check synthetic outcome arithmetic against the production 365d SQL contract."""
    sql_path = ROOT / "models" / "marts" / "fct_transfer_success_labels.sql"
    sql = sql_path.read_text(encoding="utf-8-sig")
    check("365 as label_horizon_days" in sql and "20 as success_threshold_pct" in sql,
          "Source SQL contract changed; review the 365-day Power BI model")
    check("where outcomes.has_365d_outcome" in sql,
          "Transfer labels are no longer restricted to observed outcomes")
    for mode in ("offline-demo", "workspace"):
        label_model = ROOT / "powerbi" / mode / "FootballPlayerAnalysis" / "Model" / "definition" / "tables" / "fct_transfer_success_labels.tmdl"
        content = label_model.read_text(encoding="utf-8-sig")
        check(content.count("label_horizon_days] = 365") == 3,
              f"{mode} transfer measures must all use the SQL 365-day horizon")
        check("label_horizon_days] = 90" not in content,
              f"{mode} contains stale 90-day transfer measures")

    labels = fixtures.get("fct_transfer_success_labels", [])
    horizons = fixtures.get("fct_transfer_fixed_horizon_outcomes", [])
    transfers = fixtures.get("fct_transfers", [])
    check(len(labels) == 24 and len(horizons) == 24 and len(transfers) == 24,
          "Expected 24 deterministic transfer-demo rows per fact table")
    by_horizon = {v["transfer_key"]: v for v in horizons}
    by_transfer = {v["player_id"]: v for v in transfers}
    check(len(by_horizon) == len(horizons), "Duplicate horizon transfer_key")
    check(len(by_transfer) == len(transfers), "Duplicate demo transfer player_id")
    flags = set()
    for row in labels:
        key = row["transfer_key"]
        other = by_horizon.get(key)
        tx = by_transfer.get(row["player_id"])
        if not other or not tx:
            errors.append(f"Missing transfer/fixed horizon row for {key}")
            continue
        base = row["market_value_baseline"]
        fee = row["transfer_fee"]
        result = row["outcome_market_value"]
        if not isinstance(base, (int, float)) or base <= 0:
            errors.append(f"{key}: invalid market value baseline")
            continue
        fee_pct = (fee / base - 1) * 100
        outcome_pct = (result / base - 1) * 100
        check(row["label_horizon_days"] == 365, f"{key}: wrong label horizon")
        check(row["success_threshold_pct"] == 20, f"{key}: wrong success threshold")
        check(row["label_status"] == "observed", f"{key}: wrong observed label")
        check(row["from_club_id"] != row["to_club_id"], f"{key}: same-club transfer")
        check((parse_fixture_date(row["outcome_valuation_date"]) -
               parse_fixture_date(row["transfer_date"])).days == 365,
              f"{key}: outcome date does not match 365 days")
        check(abs(row["market_value_change_at_horizon_pct"] - outcome_pct) <= 0.02,
              f"{key}: expected percentage points, not fractional returns")
        check(abs(row["fee_market_value_difference_pct"] - fee_pct) <= 0.02,
              f"{key}: fee premium uses wrong percent unit")
        expected = int(outcome_pct >= 20)
        flags.add(row["is_successful_transfer"])
        check(row["is_successful_transfer"] == expected,
              f"{key}: incorrect binary success label")
        check(other["has_365d_outcome"] is True and other["outcome_365d_status"] == "observed",
              f"{key}: inconsistent horizon status")
        check(other["market_value_365d"] == result, f"{key}: outcome market-value mismatch")
        check(abs(other["market_value_change_365d_pct"] - outcome_pct) <= 0.02,
              f"{key}: fixed horizon percent mismatch")
        check(abs(tx["fee_market_value_difference_pct"] - fee_pct) <= 0.02,
              f"{key}: fact transfer fee percentage mismatch")
        check(abs(tx["fee_market_value_difference"] - (fee - base)) <= 0.02,
              f"{key}: fact transfer fee difference mismatch")
        check((parse_fixture_date(other["source_latest_valuation_date"]) -
               parse_fixture_date(other["target_365d_date"])).days >= 30,
              f"{key}: demo outcome cannot yet be observed")
    check(flags == {0, 1}, "Demo must exercise both successful and unsuccessful outcomes")

def check_demo_relationships(demo_tables):
    """Check fixture values and their keys; this is NOT a Power BI engine test."""
    fixtures = {
        p.stem: load_inline_fixture(p)
        for p in demo_tables.glob("*.tmdl")
        if not p.name.startswith(("LocalDateTable_", "DateTableTemplate_"))
    }

    unique_keys = {
        "dim_players": "player_id",
        "dim_clubs": "club_id",
        "dim_competitions": "competition_id",
        "fct_player_performance": "player_id",
        "fct_club_performance": "club_id",
        "fct_club_risk_profile": "club_id",
        "fct_competition_performance": "competition_id",
        "ml_player_market_value_model_registry": "model_version",
        "ml_player_market_value_feature_drift": "feature",
    }
    for table, col in unique_keys.items():
        rows = fixtures.get(table, [])
        keys = [r.get(col) for r in rows]
        check(bool(rows), f"Missing fixture rows for {table}")
        check(None not in keys, f"NULL/missing {table}.{col}")
        check(len(keys) == len(set(keys)), f"Duplicate key {table}.{col}")

    relations_path = DEMO / "Model" / "definition" / "relationships.tmdl"
    relations = relations_path.read_text(encoding="utf-8-sig")
    count = 0
    for block in re.split(r"(?=^relationship )", relations, flags=re.MULTILINE):
        from_match = re.search(r"^\s*fromColumn: ([^\s]+)$", block, re.MULTILINE)
        to_match = re.search(r"^\s*toColumn: ([^\s]+)$", block, re.MULTILINE)
        if not from_match or not to_match:
            continue
        a = from_match.group(1).split(".", 1)
        b = to_match.group(1).split(".", 1)
        if len(a) != 2 or len(b) != 2 or a[0] not in fixtures or b[0] not in fixtures:
            continue  # Power BI's calculated LocalDateTables are not inline fixtures
        src_rows, dst_rows = fixtures[a[0]], fixtures[b[0]]
        src = [r.get(a[1]) for r in src_rows]
        dst = [r.get(b[1]) for r in dst_rows]
        check(None not in src, f"NULL / missing reference field {from_match.group(1)}")
        check(None not in dst, f"NULL / missing reference target {to_match.group(1)}")
        target = set(dst)
        missing = {key for key in src if key not in target and key is not None}
        check(not missing, f"Unmatched relationship {from_match.group(1)} -> "
              f"{to_match.group(1)}: {list(missing)[:3]}")
        if re.search(r"^\s*fromCardinality: one$", block, re.MULTILINE):
            check(len(src) == len(set(src)), f"Declared one-side key not unique: "
                  f"{from_match.group(1)}")
        if re.search(r"^\s*toCardinality: one$", block, re.MULTILINE):
            check(len(dst) == len(set(dst)), f"Declared one-side key not unique: "
                  f"{to_match.group(1)}")
        count += 1

    players = fixtures.get("fct_player_performance", [])
    for row in players:
        games, minutes = row.get("matches_played"), row.get("total_minutes_played")
        if not isinstance(games, (float, int)) or not isinstance(minutes, (float, int)):
            errors.append("Malformed player performance fixture")
            break
        if games <= 0 or minutes <= 0:
            errors.append("Zero player minutes/matches in fixture")
            break
        for part in ("goals", "assists"):
            raw = row.get("total_" + part)
            rate = row.get(part + "_per_90")
            if not isinstance(raw, (float, int)) or not isinstance(rate, (float, int)):
                errors.append("Malformed per-90 player statistic")
                continue
            check(abs(rate - raw * 90 / minutes) < 0.00002,
                  f"Incorrect synthetic {part}_per_90 for player {row.get('player_id')}")

    for row in fixtures.get("fct_club_performance", []):
        check(row["wins"] + row["draws"] + row["losses"] == row["matches_played"],
              f"Club {row['club_id']} results do not sum to matches")
        check(row["goals_scored"] - row["goals_conceded"] == row["goal_difference"],
              f"Club {row['club_id']} goal difference mismatch")
        games = row.get("matches_played")
        for column, numerator in (
            ("win_rate", row["wins"]),
            ("avg_goals_scored", row["goals_scored"]),
            ("avg_goals_conceded", row["goals_conceded"]),
        ):
            value = row.get(column)
            if not isinstance(value, (int, float)) or not isinstance(games, (int, float)) or games <= 0:
                errors.append(f"Club {row['club_id']} invalid numeric {column}")
            else:
                check(abs(value - numerator / games) < 0.00002,
                      f"Club {row['club_id']} {column} arithmetic mismatch")

    for row in fixtures.get("fct_competition_performance", []):
        if row.get("matches_played"):
            average = row.get("avg_goals_per_match")
            if not isinstance(average, (int, float)):
                errors.append(f"Competition {row['competition_id']} goal average must be numeric")
            else:
                check(abs(average - row["total_goals"] / row["matches_played"]) < 0.00002,
                      f"Competition {row['competition_id']} goal average mismatch")

    check_365_day_transfer_contract(fixtures)
    check_club_risk_demo_contract(fixtures)

    return len(fixtures), count

def main():
    check((DEMO / "FootballPlayerAnalysis.pbip").is_file(), "Missing offline PBIP entry")
    check((DEMO / "Model" / "definition.pbism").is_file(), "Missing offline semantic model")
    check((DEMO / "Report" / "definition.pbir").is_file(), "Missing offline report")
    demo_tables = DEMO / "Model" / "definition" / "tables"
    originals = PROD / "Model" / "definition" / "tables"
    physical = [p for p in originals.glob("*.tmdl") if not
                p.name.startswith(("LocalDateTable_", "DateTableTemplate_"))]
    check(len(physical) == 33, f"Expected 33 source tables; found {len(physical)}")
    for file in physical:
        copy = demo_tables / file.name
        check(copy.exists(), f"Missing demo table {file.name}")
        if not copy.exists():
            continue
        original_text = file.read_text(encoding="utf-8-sig")
        text = copy.read_text(encoding="utf-8-sig")
        check("GoogleBigQuery.Database(" in original_text,
              f"Production query modified or absent in {file.name}")
        check("GoogleBigQuery.Database(" not in text,
              f"Unconverted cloud data source in demo {file.name}")
        check(re.search(r"^\s*#table\(", text, re.MULTILINE) is not None,
              f"Missing inline sample table in {file.name}")
        source_columns = re.findall(r"^\s+sourceColumn: (.+)$", original_text, re.MULTILINE)
        for col in source_columns:
            if col.startswith("[") or col.endswith("]"):
                continue  # auto date / calculated field
            name = '#"' + col.replace('"', '""') + '"'
            check(name in text, f"Missing physical source column {col} in {file.name}")
    page_root = DEMO / "Report" / "definition" / "pages"
    pages = load_json(page_root / "pages.json")
    for page_id in pages.get("pageOrder", []):
        page = load_json(page_root / page_id / "page.json")
        check(not page.get("displayName", "").startswith("[DEMO]"),
              f"Decorative [DEMO] tab prefix retained on {page_id}")
        if page.get("width", 0) >= 1200:
            markers = list((page_root / page_id / "visuals").glob(
                "de9a*/visual.json"))
            check(len(markers) == 1 and
                  "SYNTHETIC DATA  /  NOT REAL" in markers[0].read_text(encoding="utf-8"),
                  f"Explicit provenance disclaimer missing on {page_id}")
    for vpath in page_root.glob("*/visuals/*/visual.json"):
        v = load_json(vpath)
        check("visualContainerObjects" not in v,
              f"Invalid root-level visualContainerObjects: {vpath.relative_to(ROOT)}")
    check((DEMO / "Report" / "StaticResources").is_dir(), "Missing report resources")
    theme = load_json(DEMO / "Report" / "StaticResources" / "SharedResources" /
                      "BuiltInThemes" / "AccessibleTidal.json")
    check(theme.get("dataColors", [None])[0] == "#4EA8FF",
          "Demo theme differs from NEXUS blue palette")
    table_count, relation_count = check_demo_relationships(demo_tables)
    if errors:
        print("Offline PBIP checks FAILED:")
        for issue in errors:
            print(" - " + issue)
        return 1
    print(f"Fixture integrity OK: {table_count} tables; {relation_count} cross-table relationships checked.")
    print(f"Offline PBIP static preflight OK: {len(physical)} inline tables, "
          f"{len(pages.get('pageOrder', []))} labeled pages.")
    print("NOT a Power BI Desktop load, refresh, or chart-rendering test.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
