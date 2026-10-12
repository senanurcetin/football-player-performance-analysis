"""Pure, offline checks for Power BI PBIR page and query-order registries."""
import json


def validate_pages(pages: object, available: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(pages, dict):
        return ["Invalid PBIR pages metadata: expected a JSON object"]
    order = pages.get("pageOrder")
    if not isinstance(order, list) or not all(
        isinstance(name, str) and bool(name.strip()) for name in order
    ):
        return ["Invalid PBIR pageOrder: expected a list of nonempty page identifiers"]
    if not order:
        errors.append("Empty PBIR pageOrder")
    seen: set[str] = set()
    for name in order:
        if name in seen:
            errors.append(f"Duplicate PBIR pageOrder entry: {name}")
        seen.add(name)
        if name not in available:
            errors.append(f"Missing PBIR page: {name}")
    for name in sorted(available - seen):
        errors.append(f"Unlisted PBIR page file: {name}")
    active = pages.get("activePageName")
    if active is not None:
        if not isinstance(active, str) or active not in seen:
            errors.append(f"Invalid active PBIR page: {active}")
        elif active not in available:
            errors.append(f"Missing active PBIR page: {active}")
    return errors


def validate_query_order(annotation: str, table_names: set[str]) -> list[str]:
    try:
        names = json.loads(annotation)
    except (TypeError, ValueError) as exc:
        return [f"Invalid PBI_QueryOrder JSON annotation: {exc}"]
    if not isinstance(names, list) or not all(
        isinstance(name, str) and bool(name.strip()) for name in names
    ):
        return ["Invalid PBI_QueryOrder: expected an array of nonempty table names"]
    errors: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name in seen:
            errors.append(f"Duplicate PBI_QueryOrder table: {name}")
        seen.add(name)
        if name not in table_names:
            errors.append(f"Stale PBI_QueryOrder table: {name}")
    return errors


def validate_relationships(source: str, table_names: set[str]) -> list[str]:
    """Validate static TMDL relationship endpoints against table files.

    This checks presence/shape and table references, not column existence or
    whether Power BI can successfully load the semantic model.
    """
    import re

    errors: list[str] = []
    blocks = re.split(r"(?=^relationship\s+)", source, flags=re.MULTILINE)
    seen: set[str] = set()
    count = 0
    for block in blocks:
        header = re.search(r"^relationship[ \t]+(\S+)[ \t]*$", block, re.MULTILINE)
        if not header:
            continue
        count += 1
        name = header.group(1)
        if name in seen:
            errors.append(f"Duplicate relationship ID: {name}")
        seen.add(name)
        for direction in ("fromColumn", "toColumn"):
            occurrences = re.findall(
                rf"^\s*{direction}:\s*(.*?)\s*$", block, flags=re.MULTILINE
            )
            if len(occurrences) != 1:
                errors.append(f"Relationship {name}: expected exactly one {direction}")
                continue
            endpoint = occurrences[0]
            if "." not in endpoint:
                errors.append(f"Relationship {name}: invalid {direction}: {endpoint}")
                continue
            table, column = endpoint.rsplit(".", 1)
            if not table.strip() or not column.strip():
                errors.append(f"Relationship {name}: invalid {direction}: {endpoint}")
            elif table not in table_names:
                errors.append(f"Relationship {name}: missing table {table} ({direction})")
    if not count:
        errors.append("No relationships found in relationships.tmdl")
    return errors
