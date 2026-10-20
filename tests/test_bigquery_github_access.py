"""Synthetic contract tests for manual GitHub BigQuery metadata preflight."""
from __future__ import annotations
import ast
import importlib.util
import os
import unittest
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"scripts/check_bigquery_github_access.py"
SPEC=importlib.util.spec_from_file_location("bigquery_gh_meta",SOURCE)
module=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class FakeClient:
    def __init__(self,missing=()):
        self.missing=set(missing)
        self.calls=[]
    def get_dataset(self,d):
        self.calls.append(("get_dataset",d))
        if d in self.missing: raise PermissionError("masked")
        return SimpleNamespace(location="EU",modified=datetime(2026,10,18,tzinfo=timezone.utc))
    def get_table(self,t):
        self.calls.append(("get_table",t))
        if t in self.missing:raise PermissionError("masked")
        return SimpleNamespace(modified=datetime(2026,10,19,tzinfo=timezone.utc),
                               num_rows=8584,table_type="TABLE",schema=[1,2,3])

class BigQueryGitHubMetadataContract(unittest.TestCase):
    def test_marts_verified_without_query_jobs(self):
        client=FakeClient()
        report=module.inspect_metadata(client,"data-analiz-490513")
        self.assertEqual(report["status"],"METADATA_PASS")
        self.assertEqual(report["warehouse_query_jobs_started"],0)
        self.assertEqual(report["warehouse_tables_modified"],0)
        self.assertEqual(report["required_tables"]["fct_transfer_success_labels"]["status"],"FOUND")
        self.assertTrue(all(method in ("get_dataset","get_table") for method,_ in client.calls))

    def test_mart_unavailable_fails_closed(self):
        p="data-analiz-490513.football_mart"
        client=FakeClient(missing=(p,))
        report=module.inspect_metadata(client,"data-analiz-490513")
        self.assertEqual(report["status"],"FAILED_REQUIRED_DATASET")
        self.assertEqual(client.calls[-1][0],"get_dataset")

    def test_missing_mart_table_fails(self):
        t="data-analiz-490513.football_mart.fct_transfer_success_labels"
        result=module.inspect_metadata(FakeClient(missing=(t,)),"data-analiz-490513")
        self.assertEqual(result["status"],"FAILED_REQUIRED_TABLES")
        self.assertEqual(result["required_tables"]["fct_transfer_success_labels"]["error_type"],"PermissionError")

    def test_optional_ml_table_absence_does_not_overstate_mart_status(self):
        client=FakeClient(missing=("data-analiz-490513.football_ml.ml_player_market_value_current_predictions",))
        result=module.inspect_metadata(client,"data-analiz-490513")
        self.assertEqual(result["status"],"METADATA_PASS")
        self.assertEqual(result["optional_tables"]["ml_player_market_value_current_predictions"]["status"],"UNAVAILABLE")

    def test_missing_github_secret_rejected_without_echoing(self):
        with mock.patch.dict(os.environ,{"GCP_SERVICE_ACCOUNT_JSON":""}):
            with self.assertRaisesRegex(module.MetadataPreflightError,"missing or empty"):
                module.credential_client("data-analiz-490513")

    def test_invalid_secret_rejected(self):
        with mock.patch.dict(os.environ,{"GCP_SERVICE_ACCOUNT_JSON":"not json"}):
            with self.assertRaisesRegex(module.MetadataPreflightError,"invalid"):
                module.credential_client("data-analiz-490513")

    def test_source_never_invokes_bigquery_sql_or_mutations(self):
        source=SOURCE.read_text("utf8")
        tree=ast.parse(source)
        methods={node.func.attr for node in ast.walk(tree)
                 if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute)}
        self.assertFalse(methods & {"query","query_and_wait","insert_rows",
            "create_table","delete_table","update_table","create_dataset","delete_dataset"})
        self.assertIn("get_dataset",methods)
        self.assertIn("get_table",methods)

    def test_workflow_is_manual_and_credential_scoped(self):
        workflow=(ROOT/".github/workflows/bigquery-readonly-preflight.yml").read_text("utf8")
        self.assertIn("workflow_dispatch:",workflow)
        self.assertIn("confirm_metadata_only",workflow)
        self.assertIn("secrets.GCP_SERVICE_ACCOUNT_JSON",workflow)
        self.assertNotIn("  push:",workflow)
        self.assertNotIn("  schedule:",workflow)
        self.assertNotIn("train_player_market_value.py",workflow)
        self.assertNotIn("run: dbt build",workflow)
        self.assertIn("persist-credentials: false",workflow)

if __name__=="__main__":
    unittest.main()
