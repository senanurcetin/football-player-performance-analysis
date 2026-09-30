"""Verify the governed player market value model artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib

from train_player_market_value import feature_contract_hash, file_sha256


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/player_market_value")
    return parser.parse_args()


def main() -> None:
    output_dir = Path(parse_args().output_dir)
    model_path = output_dir / "model.joblib"
    manifest_path = output_dir / "artifact_manifest.json"
    metrics_path = output_dir / "metrics.json"

    for path in [model_path, manifest_path, metrics_path]:
        if not path.exists():
            raise FileNotFoundError(f"Required ML artifact is missing: {path}.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    model_bundle = joblib.load(model_path)

    if file_sha256(model_path) != manifest["model_artifact_sha256"]:
        raise ValueError("Model artifact checksum does not match the manifest.")
    if manifest["feature_contract_hash"] != feature_contract_hash():
        raise ValueError("Manifest feature contract does not match the current code.")
    if model_bundle["feature_contract_hash"] != manifest["feature_contract_hash"]:
        raise ValueError("Model bundle feature contract does not match the manifest.")
    if model_bundle["model_version"] != manifest["model_version"]:
        raise ValueError("Model bundle version does not match the manifest.")
    if metrics["model_version"] != manifest["model_version"]:
        raise ValueError("Metrics version does not match the manifest.")
    if manifest["release_status"] == "rejected":
        raise ValueError("Rejected model artifact cannot be promoted.")
    if not metrics["blocking_quality_gates_passed"]:
        raise ValueError("Model artifact has failed blocking quality gates.")

    required_bundle_keys = {
        "pipeline",
        "selected_ml_blend_weight",
        "selected_ml_blend_weights_by_quality_status",
        "baseline_fill_value_eur",
        "numeric_features",
        "categorical_features",
        "feature_contract",
        "runtime_versions",
    }
    missing_keys = sorted(required_bundle_keys.difference(model_bundle))
    if missing_keys:
        raise ValueError(f"Model bundle is missing required keys: {missing_keys}.")

    blend_weights = model_bundle["selected_ml_blend_weights_by_quality_status"]
    if blend_weights.get("limited") != 0:
        raise ValueError("Limited-quality predictions must use the baseline fallback.")
    if any(not 0 <= weight <= 1 for weight in blend_weights.values()):
        raise ValueError("Model artifact contains an invalid blend weight.")

    print(
        f"ML artifact verified: {manifest['model_version']} "
        f"({manifest['release_status']})."
    )


if __name__ == "__main__":
    main()
