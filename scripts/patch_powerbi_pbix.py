import argparse
import io
import json
import pathlib
import re
import shutil
import tempfile
import zipfile


def patch_data_mashup(mashup_bytes: bytes) -> bytes:
    """Patch DataMashup ZIP to add UseStorageApi=false to all BigQuery connections."""
    buf = io.BytesIO(mashup_bytes)
    with zipfile.ZipFile(buf, "r") as mz:
        files = {name: mz.read(name) for name in mz.namelist()}

    replacements = 0
    for name in list(files):
        if name.endswith(".m"):
            text = files[name].decode("utf-8")
            patched, count = re.subn(
                r"GoogleBigQuery\.Database\(\s*\)",
                "GoogleBigQuery.Database([UseStorageApi=false])",
                text,
            )
            if count:
                files[name] = patched.encode("utf-8")
                replacements += count

    if replacements:
        print(f"  DataMashup: patched {replacements} BigQuery connection(s) → UseStorageApi=false")

    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as mz:
        for name, data in files.items():
            mz.writestr(name, data)
    return out.getvalue()


TARGET_PAGES = {
    "005_": 5,
    "006_": 6,
    "008_": 8,
    "009_": 9,
    "010_": 10,
    "011_": 11,
    "012_": 12,
}


def read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_visual_containers(page_path: pathlib.Path):
    containers = []
    visual_root = page_path / "visualContainers"

    for visual_path in sorted(path for path in visual_root.iterdir() if path.is_dir()):
        position = read_json(visual_path / "visualContainer.json")
        config = read_json(visual_path / "config.json")
        filters_path = visual_path / "filters.json"
        filters = read_json(filters_path) if filters_path.exists() else []

        containers.append(
            {
                "x": position["x"],
                "y": position["y"],
                "z": position["z"],
                "width": position["width"],
                "height": position["height"],
                "config": json.dumps(config, ensure_ascii=False, separators=(",", ":")),
                "filters": json.dumps(filters, ensure_ascii=False, separators=(",", ":")),
            }
        )

    return containers


def build_section(page_path: pathlib.Path):
    section = read_json(page_path / "section.json")
    config = read_json(page_path / "config.json")
    section["config"] = json.dumps(
        config,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    section["filters"] = json.dumps(
        read_json(page_path / "filters.json"),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    section["visualContainers"] = build_visual_containers(page_path)
    for property_name in ("visibility", "type", "filterSortOrder"):
        if property_name in config:
            section[property_name] = config[property_name]
    return section


def update_layout(layout, report_sections: pathlib.Path):
    for prefix, ordinal in TARGET_PAGES.items():
        page_path = next(path for path in report_sections.iterdir() if path.name.startswith(prefix))
        existing = next(
            (section for section in layout["sections"] if section["ordinal"] == ordinal),
            None,
        )

        if existing is None:
            layout["sections"].append(build_section(page_path))
            continue

        existing["visualContainers"] = build_visual_containers(page_path)
        if ordinal >= 8:
            source_section = build_section(page_path)
            existing["config"] = source_section["config"]
            existing["filters"] = source_section["filters"]
            existing["displayName"] = source_section["displayName"]
            existing["displayOption"] = source_section["displayOption"]
            existing["height"] = source_section["height"]
            existing["width"] = source_section["width"]
            for property_name in ("visibility", "type", "filterSortOrder"):
                if property_name in source_section:
                    existing[property_name] = source_section[property_name]

    layout["sections"].sort(key=lambda section: section["ordinal"])
    return layout


def patch_pbix(source: pathlib.Path, target: pathlib.Path, report_sections: pathlib.Path):
    with zipfile.ZipFile(source, "r") as input_zip:
        layout = json.loads(input_zip.read("Report/Layout").decode("utf-16-le"))
        updated_layout = update_layout(layout, report_sections)
        layout_bytes = json.dumps(
            updated_layout,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-16-le")

        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pbix", dir=target.parent) as temp_file:
            temp_path = pathlib.Path(temp_file.name)

        try:
            with zipfile.ZipFile(temp_path, "w") as output_zip:
                for item in input_zip.infolist():
                    if item.filename == "SecurityBindings":
                        output_zip.writestr(item, input_zip.read(item.filename))
                    elif item.filename == "Report/Layout":
                        continue
                    elif item.filename == "DataMashup":
                        output_zip.writestr(item, patch_data_mashup(input_zip.read(item.filename)))
                    else:
                        output_zip.writestr(item, input_zip.read(item.filename))

                output_zip.writestr("Report/Layout", layout_bytes)

            shutil.move(temp_path, target)
        finally:
            temp_path.unlink(missing_ok=True)


def verify_pbix(path: pathlib.Path):
    with zipfile.ZipFile(path, "r") as archive:
        layout = json.loads(archive.read("Report/Layout").decode("utf-16-le"))
        results = {}
        for _, ordinal in TARGET_PAGES.items():
            section = next(section for section in layout["sections"] if section["ordinal"] == ordinal)
            types = []
            for container in section["visualContainers"]:
                config = json.loads(container["config"])
                types.append(config["singleVisual"]["visualType"])
            section_config = json.loads(section["config"])
            results[section["displayName"]] = {
                "ordinal": section["ordinal"],
                "visual_types": types,
                "is_drillthrough": section.get("type", section_config.get("type")) == 2,
                "is_hidden": section.get("visibility", section_config.get("visibility")) == 1,
            }
        return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=pathlib.Path)
    parser.add_argument("--target", required=True, type=pathlib.Path)
    parser.add_argument("--report-sections", required=True, type=pathlib.Path)
    args = parser.parse_args()

    patch_pbix(args.source, args.target, args.report_sections)
    results = verify_pbix(args.target)
    print(f"Created: {args.target}")
    for page, result in results.items():
        flags = []
        if result["is_drillthrough"]:
            flags.append("drill-through")
        if result["is_hidden"]:
            flags.append("hidden")
        flag_text = f" [{' / '.join(flags)}]" if flags else ""
        print(
            f"{page}: {len(result['visual_types'])} visuals"
            f"{flag_text} ({', '.join(result['visual_types'])})"
        )


if __name__ == "__main__":
    main()
