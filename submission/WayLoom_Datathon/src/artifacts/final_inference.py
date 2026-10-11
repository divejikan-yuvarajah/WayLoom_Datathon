"""Load Phase 32 artifacts and reproduce frozen Task 1/Task 2A predictions."""

from __future__ import annotations

import hashlib
import importlib.metadata
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import yaml

from src.common.data_inventory import discover_dataset_files, load_manifest
from src.common.artifact_registry import load_phase31_artifact_set
from src.task1.inference import (
    predict_late_from_bundle,
    predict_service_from_bundle,
    run_task1_inference_from_loaded_bundles,
)
from src.task2a.features import load_feature_config
from src.task2a.final_fit import FittedComponent, predict_frozen_component
from src.task2a.final_inference import OFFICIAL_ROW_ORDER, build_final_test_features, postprocess_predictions
from src.task2a.model_preprocessing import feature_profile
from src.task2a.model_selection import validate_final_model_config


class FinalArtifactError(ValueError):
    """A saved artifact or its prediction-parity contract is invalid."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def current_library_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("python", "numpy", "pandas", "scikit-learn", "catboost", "lightgbm", "joblib"):
        if name == "python":
            import platform

            versions[name] = platform.python_version()
            continue
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT_INSTALLED"
    return versions


def load_artifact_manifest(path: Path, project_root: Path) -> dict[str, Any]:
    path = Path(path).resolve()
    project_root = Path(project_root).resolve()
    if not _inside(path, project_root) or not path.is_file():
        raise FinalArtifactError("Phase 32 artifact manifest is missing or outside the repository.")
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("version") != 1 or manifest.get("status") != "PASS":
        raise FinalArtifactError("Phase 32 artifact manifest is not PASS.")
    paths = manifest.get("artifact_paths")
    hashes = manifest.get("artifact_sha256")
    if not isinstance(paths, list) or not paths or not isinstance(hashes, dict):
        raise FinalArtifactError("Phase 32 artifact inventory is incomplete.")
    if len(paths) != len(set(paths)) or set(paths) != set(hashes):
        raise FinalArtifactError("Phase 32 artifact path/hash inventory is inconsistent.")
    for relative in paths:
        artifact = (project_root / str(relative)).resolve()
        if not _inside(artifact, project_root) or not artifact.is_file():
            raise FinalArtifactError("A Phase 32 artifact is missing or escapes the repository.")
        if sha256_file(artifact) != hashes[relative]:
            raise FinalArtifactError(f"Phase 32 artifact hash mismatch: {relative}")
    required = {"task1_service_dir", "task1_late_dir", "task2a_total_bundle", "task2a_chilled_bundle"}
    if required.difference(manifest.get("interfaces") or {}):
        raise FinalArtifactError("Phase 32 inference interfaces are incomplete.")
    if manifest.get("library_versions") != current_library_versions():
        raise FinalArtifactError("Current library versions differ from the validated artifact environment.")
    return manifest


def load_task2a_component(path: Path, *, expected_target: str) -> FittedComponent:
    value = joblib.load(path)
    if not isinstance(value, FittedComponent) or value.target != expected_target:
        raise FinalArtifactError(f"Saved Task 2A {expected_target} component has an invalid type or target.")
    if value.spec.get("approach_type") == "ensemble" and value.components is None:
        raise FinalArtifactError(f"Saved Task 2A {expected_target} ensemble has no components.")
    return value


def predict_task2a_from_loaded_components(
    *,
    panel: pd.DataFrame,
    calendar: pd.DataFrame,
    test_inputs: pd.DataFrame,
    final_config: dict[str, Any],
    feature_config: dict[str, Any],
    total_component: FittedComponent,
    chilled_component: FittedComponent,
) -> dict[str, Any]:
    validate_final_model_config(final_config)
    profile = feature_profile(feature_config)
    if profile["registry_hash"] != final_config["feature_profile"]["registry_hash"]:
        raise FinalArtifactError("Task 2A feature profile differs from the frozen final configuration.")
    features, origin = build_final_test_features(panel, calendar, test_inputs, feature_config)
    total_raw = predict_frozen_component(total_component, features, panel, origin, profile)
    chilled_raw = np.zeros(len(features), dtype=float)
    fresh = features["brand"].eq("Fresh")
    chilled_raw[fresh.to_numpy()] = predict_frozen_component(
        chilled_component,
        features.loc[fresh].reset_index(drop=True),
        panel,
        origin,
        profile,
    )
    raw = features[[OFFICIAL_ROW_ORDER, "row_id", "brand"]].copy()
    raw["raw_pred_total_volume_m3"] = total_raw
    raw["raw_pred_chilled_volume_m3"] = chilled_raw
    predictions, corrections = postprocess_predictions(raw)
    return {"predictions": predictions, "features": features, "origin": origin, "corrections": corrections}


def run_loaded_artifact_synthetic_smoke(loaded: dict[str, Any]) -> dict[str, str]:
    """Run deterministic inference through every loaded final artifact."""
    service_bundle = loaded["task1_service"]
    late_bundle = loaded["task1_late"]
    task1_schema = service_bundle["schema"]
    task1_categorical = set(task1_schema["categorical_columns"])
    task1_frame = pd.DataFrame(
        {
            column: (
                ["__MISSING__"] * 3
                if column in task1_categorical
                else np.arange(3, dtype=float)
            )
            for column in task1_schema["feature_columns"]
        }
    )
    service = predict_service_from_bundle(service_bundle, task1_frame)
    late = predict_late_from_bundle(late_bundle, task1_frame)
    if service.shape != (3,) or not np.isfinite(service).all() or np.any(service < 0):
        raise FinalArtifactError("Synthetic Task 1 service inference failed validation.")
    if late.shape != (3,) or not np.isfinite(late).all() or np.any((late < 0) | (late > 1)):
        raise FinalArtifactError("Synthetic Task 1 lateness inference failed validation.")

    task2a = loaded["task2a"]
    schema = task2a["schema"]
    categorical = set(schema["categorical_columns"])
    brands = ["Fresh", "Style", "Tech"]
    features = pd.DataFrame(
        {
            column: (
                brands
                if column == "brand"
                else ["synthetic"] * 3
                if column in categorical
                else np.arange(3, dtype=float)
            )
            for column in schema["feature_columns"]
        }
    )
    features.insert(0, "row_id", [f"synthetic-{index}" for index in range(3)])
    profile = {
        "profile_id": schema["feature_profile_id"],
        "columns": schema["feature_columns"],
        "categorical": schema["categorical_columns"],
        "numeric": [column for column in schema["feature_columns"] if column not in categorical],
    }
    history = pd.DataFrame()
    origin = pd.Timestamp("2026-01-01")
    total_raw = predict_frozen_component(task2a["total"], features, history, origin, profile)
    chilled_raw = np.zeros(3, dtype=float)
    fresh = features["brand"].eq("Fresh")
    chilled_raw[fresh.to_numpy()] = predict_frozen_component(
        task2a["chilled"],
        features.loc[fresh].reset_index(drop=True),
        history,
        origin,
        profile,
    )
    raw = features[["row_id", "brand"]].copy()
    raw.insert(0, OFFICIAL_ROW_ORDER, np.arange(3))
    raw["raw_pred_total_volume_m3"] = total_raw
    raw["raw_pred_chilled_volume_m3"] = chilled_raw
    predictions, _ = postprocess_predictions(raw)
    values = predictions[["pred_total_volume_m3", "pred_chilled_volume_m3"]].to_numpy(dtype=float)
    if values.shape != (3, 2) or not np.isfinite(values).all() or np.any(values < 0):
        raise FinalArtifactError("Synthetic Task 2A inference failed validation.")
    if np.any(values[:, 1] > values[:, 0]):
        raise FinalArtifactError("Synthetic Task 2A chilled predictions exceed total predictions.")
    if not predictions.loc[features["brand"].isin(["Style", "Tech"]), "pred_chilled_volume_m3"].eq(0).all():
        raise FinalArtifactError("Synthetic Task 2A structural chilled-zero validation failed.")
    return {
        "registry": "PASS",
        "checksums": "PASS",
        "task1_service_inference": "PASS",
        "task1_late_inference": "PASS",
        "task2a_total_inference": "PASS",
        "task2a_chilled_inference": "PASS",
    }


def assert_prediction_parity(
    actual: pd.DataFrame,
    expected: pd.DataFrame,
    *,
    key: str,
    prediction_columns: tuple[str, ...],
    tolerance: float,
    require_order: bool = False,
) -> None:
    required = {key, *prediction_columns}
    if required.difference(actual.columns) or required.difference(expected.columns):
        raise FinalArtifactError("Prediction parity input is missing required columns.")
    if actual[key].duplicated().any() or expected[key].duplicated().any():
        raise FinalArtifactError("Prediction parity keys must be unique.")
    if require_order and actual[key].astype("string").tolist() != expected[key].astype("string").tolist():
        raise FinalArtifactError("Prediction parity key order differs from the frozen output.")
    left = expected[[key, *prediction_columns]].copy()
    right = actual[[key, *prediction_columns]].copy()
    joined = left.merge(right, on=key, how="outer", suffixes=("_expected", "_actual"), indicator=True)
    if len(joined) != len(left) or len(joined) != len(right) or not joined["_merge"].eq("both").all():
        raise FinalArtifactError("Prediction parity keys differ from the frozen output.")
    for column in prediction_columns:
        expected_values = pd.to_numeric(joined[f"{column}_expected"], errors="raise").to_numpy(dtype=float)
        actual_values = pd.to_numeric(joined[f"{column}_actual"], errors="raise").to_numpy(dtype=float)
        if not np.isfinite(expected_values).all() or not np.isfinite(actual_values).all():
            raise FinalArtifactError("Prediction parity values contain NaN/Inf.")
        if not np.allclose(actual_values, expected_values, rtol=0.0, atol=float(tolerance)):
            raise FinalArtifactError(f"Loaded-artifact parity failed for {column}.")


def _official_paths(project_root: Path, raw_root: Path) -> dict[str, Path]:
    manifest = load_manifest(project_root / "configs/dataset_manifest.yaml")
    found = discover_dataset_files(raw_root, manifest).get("found_artifacts") or {}
    required = ("task1_test_inputs.csv", "calendar.csv", "task2a_test_inputs.csv")
    result: dict[str, Path] = {}
    for filename in required:
        value = found.get(filename, {}).get("path")
        if not value:
            raise FinalArtifactError(f"Required official artifact is unavailable: {filename}")
        result[filename] = Path(value)
    return result


def _relative_path(project_root: Path, value: str) -> Path:
    path = (project_root / value).resolve()
    if not _inside(path, project_root):
        raise FinalArtifactError("Artifact interface path escapes the repository.")
    return path


def run_saved_artifact_inference_demo(
    *,
    project_root: Path,
    artifact_registry: Path,
    max_demo_rows: int,
    numeric_tolerance: float,
    write_official_outputs: bool,
    loaded_artifacts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reload all artifacts, infer without training, and compare with frozen outputs."""
    project_root = Path(project_root).resolve()
    if write_official_outputs:
        raise FinalArtifactError("Final notebook inference must not write official outputs.")
    if int(max_demo_rows) not in {1, 2, 3} or float(numeric_tolerance) < 0:
        raise FinalArtifactError("Final inference demo limits are invalid.")
    loaded = (
        load_phase31_artifact_set(artifact_registry, project_root)
        if loaded_artifacts is None
        else loaded_artifacts
    )
    if set(loaded) != {"registry", "task1_service", "task1_late", "task2a"}:
        raise FinalArtifactError("Secured Phase 32 artifact set is incomplete.")
    raw_root = project_root / "data/raw"
    official = _official_paths(project_root, raw_root)

    labels_path = project_root / "data/interim/task1_training_labels.csv"
    if not labels_path.is_file():
        raise FinalArtifactError("Task 1 historical training labels are unavailable.")
    task1 = run_task1_inference_from_loaded_bundles(
        raw_root=raw_root,
        feature_registry_path=project_root / "configs/task1_features.yaml",
        final_config_path=project_root / "configs/task1_final_models.yaml",
        service_bundle=loaded["task1_service"],
        late_bundle=loaded["task1_late"],
        inference_config_path=project_root / "configs/task1_inference.yaml",
        historical_train_labels=pd.read_csv(labels_path, low_memory=False),
    )
    frozen_task1 = pd.read_csv(project_root / "outputs/submission_task1.csv")
    assert_prediction_parity(
        task1["predictions"],
        frozen_task1,
        key="delivery_id",
        prediction_columns=("pred_service_min", "pred_late_prob"),
        tolerance=numeric_tolerance,
        require_order=True,
    )

    feature_config = load_feature_config(project_root / "configs/task2a_features.yaml")
    final_config = yaml.safe_load((project_root / "configs/task2a_final_models.yaml").read_text(encoding="utf-8"))
    panel = pd.read_csv(project_root / "data/interim/task2a_weekly_panel.csv", low_memory=False)
    calendar = pd.read_csv(official["calendar.csv"], low_memory=False)
    task2a_inputs = pd.read_csv(official["task2a_test_inputs.csv"], low_memory=False)
    task2a = predict_task2a_from_loaded_components(
        panel=panel,
        calendar=calendar,
        test_inputs=task2a_inputs,
        final_config=final_config,
        feature_config=feature_config,
        total_component=loaded["task2a"]["total"],
        chilled_component=loaded["task2a"]["chilled"],
    )
    frozen_task2a = pd.read_csv(project_root / "outputs/submission_task2a.csv")
    assert_prediction_parity(
        task2a["predictions"],
        frozen_task2a,
        key="row_id",
        prediction_columns=("pred_total_volume_m3", "pred_chilled_volume_m3"),
        tolerance=numeric_tolerance,
        require_order=True,
    )

    task1_inputs = pd.read_csv(official["task1_test_inputs.csv"], low_memory=False)
    task1_safe = [
        name
        for name in (
            "delivery_id",
            "route_id",
            "seq_in_route",
            "outlet_id",
            "brand",
            "district",
            "depot",
            "order_units",
            "order_weight_kg",
            "order_volume_m3",
        )
        if name in task1_inputs.columns
    ]
    task2a_safe = [name for name in ("row_id", "depot", "brand", "iso_year", "iso_week") if name in task2a_inputs]
    task1_predictions = task1["predictions"][["delivery_id", "pred_service_min", "pred_late_prob"]]
    task2a_predictions = task2a["predictions"][["row_id", "pred_total_volume_m3", "pred_chilled_volume_m3"]]
    return {
        "task1_inputs": task1_inputs[task1_safe].head(max_demo_rows).reset_index(drop=True),
        "task1_predictions": task1_predictions.head(max_demo_rows).reset_index(drop=True),
        "task1_parity_pass": True,
        "task2a_inputs": task2a_inputs[task2a_safe].head(max_demo_rows).reset_index(drop=True),
        "task2a_predictions": task2a_predictions.head(max_demo_rows).reset_index(drop=True),
        "task2a_parity_pass": True,
        "saved_artifacts_loaded": True,
    }
