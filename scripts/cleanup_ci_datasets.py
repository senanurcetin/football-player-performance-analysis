import os

from google.cloud import bigquery


project_id = os.environ["DBT_PROJECT_ID"]
base_dataset = os.environ["DBT_DATASET"]

if not base_dataset.startswith("football_ci_pr_"):
    raise RuntimeError(f"Refusing to delete non-CI dataset prefix: {base_dataset}")

client = bigquery.Client(project=project_id)

for suffix in ("staging", "intermediate", "mart", "ml", "snapshots"):
    dataset_id = f"{project_id}.{base_dataset}_{suffix}"
    client.delete_dataset(dataset_id, delete_contents=True, not_found_ok=True)
    print(f"Deleted temporary dataset: {dataset_id}")
