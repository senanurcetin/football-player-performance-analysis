"""Fail when dbt model or physical column descriptions are incomplete."""

import json
from pathlib import Path


LAYERS = ("staging", "intermediate", "marts", "ml")
TARGET = Path("target")


def load_json(name: str) -> dict:
    path = TARGET / name
    if not path.exists():
        raise SystemExit(f"Missing {path}; run `dbt docs generate` first.")
    return json.loads(path.read_text(encoding="utf-8"))


manifest = load_json("manifest.json")
catalog = load_json("catalog.json")
project_name = manifest["metadata"]["project_name"]
models = [
    node
    for node in manifest["nodes"].values()
    if node["resource_type"] == "model" and node["package_name"] == project_name
]

failures: list[str] = []
missing_model_descriptions = [
    model["name"] for model in models if not model.get("description", "").strip()
]
failures.extend(
    f"Missing model description: {name}" for name in missing_model_descriptions
)

total_documented = 0
total_columns = 0

for layer in LAYERS:
    layer_models = [
        model
        for model in models
        if f"models/{layer}/" in model["original_file_path"].replace("\\", "/")
    ]
    layer_documented = 0
    layer_columns = 0

    for model in layer_models:
        catalog_columns = catalog["nodes"][model["unique_id"]]["columns"].values()
        physical_columns = {column["name"].lower() for column in catalog_columns}
        documented_columns = {
            name.lower(): bool(metadata.get("description", "").strip())
            for name, metadata in model.get("columns", {}).items()
        }

        for column_name in sorted(physical_columns):
            layer_columns += 1
            if documented_columns.get(column_name):
                layer_documented += 1
            else:
                failures.append(
                    f"Missing column description: {model['name']}.{column_name}"
                )

        for column_name in sorted(documented_columns.keys() - physical_columns):
            failures.append(
                f"Documented column does not exist: {model['name']}.{column_name}"
            )

    print(f"{layer}: {layer_documented}/{layer_columns} columns documented")
    total_documented += layer_documented
    total_columns += layer_columns

print(
    f"models: {len(models) - len(missing_model_descriptions)}/{len(models)} documented"
)
print(f"total: {total_documented}/{total_columns} columns documented")

if failures:
    raise SystemExit("\n".join(failures))
