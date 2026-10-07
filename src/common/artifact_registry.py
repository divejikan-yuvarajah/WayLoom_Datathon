"""Validated registry and typed loaders for final WayLoom model artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from src.common.artifact_io import (
    ArtifactIOError,
    load_verified_joblib,
    load_verified_json,
    resolve_model_artifact,
    verify_registered_file,
)
from src.common.versioning import current_model_runtime_versions
from src.task2a.final_fit import FittedComponent


ARTIFACT_SCHEMA_VERSION = 1
REGISTRY_RELATIVE_PATH = "models/artifact_registry.json"
SUPPORTED_KINDS = {
    "trained_model",
    "feature_schema",
    "model_metadata",
    "ensemble_bundle",
    "ensemble_manifest",
    "preprocessor",
}
SUPPORTED_PREPROCESSOR_MODES = {
    "embedded",
    "external_serialized",
    "deterministic_code",
    "not_required",
}
REQUIRED_ENTRY_FIELDS = {
    "artifact_id",
    "task",
    "target",
    "artifact_kind",
    "model_family",
    "strategy_config_id",
    "serializer",
    "format",
    "relative_path",
    "sha256",
    "size_bytes",
    "feature_schema_ref",
    "preprocessor_mode",
    "postprocessing_ref",
    "required",
    "library_versions",
    "load_entrypoint",
    "inference_entrypoint",
}
PRIVATE_FIELD_NAMES = {
    "training_rows",
    "test_rows",
    "raw_data",
    "private_rows",
    "predictions",
    "delivery_ids",
    "row_ids",
}


class ArtifactRegistryError(ValueError):
    """The Phase 32 registry or one of its typed bundle contracts is invalid."""


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _artifact_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = registry.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ArtifactRegistryError("Artifact registry has no artifact entries.")
    result: dict[str, dict[str, Any]] = {}
    for entry in artifacts:
        if not isinstance(entry, dict) or REQUIRED_ENTRY_FIELDS.difference(entry):
            raise ArtifactRegistryError("Artifact entry is missing required metadata.")
        artifact_id = str(entry["artifact_id"])
        if not artifact_id or artifact_id in result:
            raise ArtifactRegistryError("Artifact IDs must be nonempty and unique.")
        result[artifact_id] = entry
    return result


def validate_registry_data(
    registry: dict[str, Any],
    project_root: Path,
    *,
    verify_files: bool = True,
) -> dict[str, Any]:
    """Validate schema, task contracts, paths, hashes, and runtime metadata."""
    if not isinstance(registry, dict) or registry.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION:
        raise ArtifactRegistryError("Unsupported artifact registry schema version.")
    if registry.get("phase") != 32 or registry.get("status") not in {"READY_FOR_LOCAL_PARITY", "PASS"}:
        raise ArtifactRegistryError("Artifact registry Phase 32 status is invalid.")
    leaked = sorted(PRIVATE_FIELD_NAMES & _walk_keys(registry))
    if leaked:
        raise ArtifactRegistryError("Artifact registry contains forbidden private-row fields.")
    runtime = registry.get("runtime_versions")
    if not isinstance(runtime, dict) or runtime != current_model_runtime_versions():
        raise ArtifactRegistryError("Artifact registry runtime versions do not match this environment.")

    entries = _artifact_map(registry)
    schema_paths = {
        entry["relative_path"]
        for entry in entries.values()
        if entry["artifact_kind"] == "feature_schema"
    }
    for entry in entries.values():
        if entry["artifact_kind"] not in SUPPORTED_KINDS:
            raise ArtifactRegistryError("Artifact registry contains an unsupported artifact kind.")
        if entry["preprocessor_mode"] not in SUPPORTED_PREPROCESSOR_MODES:
            raise ArtifactRegistryError("Artifact registry contains an invalid preprocessor mode.")
        if entry["serializer"] not in {"joblib", "json"} or entry["format"] != entry["serializer"]:
            raise ArtifactRegistryError("Artifact registry contains an unsupported serializer.")
        if entry["required"] is not True:
            raise ArtifactRegistryError("Every listed final artifact must be required.")
        if not isinstance(entry["library_versions"], dict) or not entry["library_versions"]:
            raise ArtifactRegistryError("Artifact entry lacks library-version metadata.")
        if entry["feature_schema_ref"] not in schema_paths:
            raise ArtifactRegistryError("Artifact entry does not reference a registered feature schema.")
        preprocessor_id = entry.get("preprocessor_artifact_id")
        if entry["preprocessor_mode"] == "external_serialized":
            if preprocessor_id not in entries or entries[preprocessor_id]["artifact_kind"] != "preprocessor":
                raise ArtifactRegistryError("External preprocessing state is not registered.")
        elif preprocessor_id is not None:
            raise ArtifactRegistryError("Non-external preprocessing must not reference a duplicate artifact.")
        try:
            resolve_model_artifact(project_root, entry["relative_path"], require_exists=verify_files)
            if verify_files:
                verify_registered_file(project_root, entry)
        except ArtifactIOError as exc:
            raise ArtifactRegistryError(str(exc)) from exc

    for task_key in ("task1_service", "task1_late", "task2a"):
        task = registry.get(task_key)
        if not isinstance(task, dict):
            raise ArtifactRegistryError(f"Registry is missing the {task_key} contract.")
        ids = task.get("artifact_ids")
        if not isinstance(ids, list) or not ids or any(value not in entries for value in ids):
            raise ArtifactRegistryError(f"Registry {task_key} artifact references are incomplete.")

    service = registry["task1_service"]
    late = registry["task1_late"]
    task2a = registry["task2a"]
    if service.get("config_id") != "catboost_regression_default" or service.get("model_family") != "catboost":
        raise ArtifactRegistryError("Task 1 service registry metadata differs from the frozen config.")
    if late.get("config_id") != "catboost_classifier_default" or late.get("model_family") != "catboost":
        raise ArtifactRegistryError("Task 1 lateness registry metadata differs from the frozen config.")
    if (
        late.get("positive_class") != 1
        or late.get("positive_class_index") != 1
        or late.get("calibration_mode") != "raw"
    ):
        raise ArtifactRegistryError("Task 1 lateness class/calibration metadata is invalid.")
    if task2a.get("artifact_kind") != "ensemble" or task2a.get("forecast_horizon_weeks") != 10:
        raise ArtifactRegistryError("Task 2A registry does not describe the frozen 10-week ensemble.")
    if task2a.get("component_weights") != [0.5, 0.5]:
        raise ArtifactRegistryError("Task 2A ensemble weights differ from the frozen strategy.")
    return registry


def _is_staging_registry(path: Path, root: Path) -> bool:
    staging_root = (root / "models/.staging/phase32").resolve()
    try:
        path.relative_to(staging_root)
        return path.name == "artifact_registry.json"
    except ValueError:
        return False


def load_artifact_registry(
    path: Path,
    project_root: Path,
    *,
    allow_staging: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    expected = (root / REGISTRY_RELATIVE_PATH).resolve()
    path = Path(path).resolve()
    allowed = path == expected or (allow_staging and _is_staging_registry(path, root))
    if not allowed or not path.is_file():
        raise ArtifactRegistryError("Artifact registry must use models/artifact_registry.json.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ArtifactRegistryError("Artifact registry is not valid JSON.") from exc
    return validate_registry_data(value, root, verify_files=True)


def artifact_entry(registry: dict[str, Any], artifact_id: str) -> dict[str, Any]:
    try:
        return _artifact_map(registry)[artifact_id]
    except KeyError as exc:
        raise ArtifactRegistryError("Requested artifact is not registered.") from exc


def _json_entry(registry: dict[str, Any], artifact_id: str, project_root: Path) -> dict[str, Any]:
    try:
        return load_verified_json(project_root, artifact_entry(registry, artifact_id))
    except ArtifactIOError as exc:
        raise ArtifactRegistryError(str(exc)) from exc


def _joblib_entry(registry: dict[str, Any], artifact_id: str, project_root: Path) -> Any:
    try:
        return load_verified_joblib(project_root, artifact_entry(registry, artifact_id))
    except ArtifactIOError as exc:
        raise ArtifactRegistryError(str(exc)) from exc


def load_task1_service_bundle(registry: dict[str, Any], project_root: Path) -> dict[str, Any]:
    contract = registry["task1_service"]
    model = _joblib_entry(registry, contract["model_artifact_id"], project_root)
    metadata = _json_entry(registry, contract["metadata_artifact_id"], project_root)
    schema = _json_entry(registry, contract["schema_artifact_id"], project_root)
    if metadata.get("task") != "task1_service" or metadata.get("config_id") != contract["config_id"]:
        raise ArtifactRegistryError("Task 1 service metadata does not match its registry contract.")
    if schema.get("feature_profile") != contract["feature_profile"]:
        raise ArtifactRegistryError("Task 1 service feature schema differs from the registry contract.")
    return {"model": model, "metadata": metadata, "schema": schema, "calibration": None}


def load_task1_late_bundle(registry: dict[str, Any], project_root: Path) -> dict[str, Any]:
    contract = registry["task1_late"]
    model = _joblib_entry(registry, contract["model_artifact_id"], project_root)
    metadata = _json_entry(registry, contract["metadata_artifact_id"], project_root)
    schema = _json_entry(registry, contract["schema_artifact_id"], project_root)
    if metadata.get("task") != "task1_late" or metadata.get("config_id") != contract["config_id"]:
        raise ArtifactRegistryError("Task 1 lateness metadata does not match its registry contract.")
    if metadata.get("positive_class_index") != contract["positive_class_index"]:
        raise ArtifactRegistryError("Task 1 lateness positive-class mapping changed.")
    model_classes = getattr(model, "classes_", None)
    if model_classes is None:
        raise ArtifactRegistryError("Task 1 lateness model has no class-order metadata.")
    normalized_classes = [int(float(value)) for value in list(model_classes)]
    if normalized_classes != contract.get("class_order"):
        raise ArtifactRegistryError("Task 1 lateness model class order differs from the registry.")
    positive_index = int(contract["positive_class_index"])
    if (
        contract.get("positive_class") != 1
        or positive_index >= len(normalized_classes)
        or normalized_classes[positive_index] != 1
    ):
        raise ArtifactRegistryError("Task 1 lateness positive-class contract is inconsistent.")
    if str(metadata.get("calibration_method", "raw")).lower() != contract["calibration_mode"]:
        raise ArtifactRegistryError("Task 1 lateness calibration metadata changed.")
    if schema.get("feature_profile") != contract["feature_profile"]:
        raise ArtifactRegistryError("Task 1 lateness feature schema differs from the registry contract.")
    return {"model": model, "metadata": metadata, "schema": schema, "calibration": None}


def load_task2a_bundle(registry: dict[str, Any], project_root: Path) -> dict[str, Any]:
    contract = registry["task2a"]
    manifest = _json_entry(registry, contract["manifest_artifact_id"], project_root)
    schema = _json_entry(registry, contract["schema_artifact_id"], project_root)
    total_metadata = _json_entry(registry, contract["total_metadata_artifact_id"], project_root)
    chilled_metadata = _json_entry(registry, contract["chilled_metadata_artifact_id"], project_root)
    total = _joblib_entry(registry, contract["total_artifact_id"], project_root)
    chilled = _joblib_entry(registry, contract["chilled_artifact_id"], project_root)
    if not isinstance(total, FittedComponent) or total.target != "total":
        raise ArtifactRegistryError("Registered Task 2A total artifact has an invalid type or target.")
    if not isinstance(chilled, FittedComponent) or chilled.target != "chilled":
        raise ArtifactRegistryError("Registered Task 2A chilled artifact has an invalid type or target.")
    for component, expected_id in (
        (total, contract["total_strategy"]),
        (chilled, contract["chilled_strategy"]),
    ):
        if component.spec.get("approach_type") != "ensemble":
            raise ArtifactRegistryError("Registered Task 2A component is not the frozen ensemble.")
        if component.spec.get("candidate_id") != expected_id or component.spec.get("component_weights") != [0.5, 0.5]:
            raise ArtifactRegistryError("Registered Task 2A ensemble identity or weights changed.")
        if component.components is None or len(component.components) != 2:
            raise ArtifactRegistryError("Registered Task 2A ensemble is incomplete.")
        families = [part.spec.get("family") for part in component.components]
        if families != ["catboost", "lightgbm"]:
            raise ArtifactRegistryError("Registered Task 2A ensemble families are incomplete or stale.")
        if component.components[1].preprocessor is None:
            raise ArtifactRegistryError("Registered Task 2A LightGBM preprocessing state is missing.")
    if manifest.get("final_strategy") != "fixed_equal_weight_catboost_lightgbm_ensemble":
        raise ArtifactRegistryError("Task 2A artifact manifest strategy is invalid.")
    if (
        manifest.get("forecast_horizon_weeks") != 10
        or (manifest.get("preprocessing") or {}).get("mode") != "embedded"
        or manifest.get("postprocessing")
        != {
            "clip_negative": True,
            "enforce_chilled_le_total": True,
            "rounding": "none",
            "style_chilled_zero": True,
            "tech_chilled_zero": True,
        }
    ):
        raise ArtifactRegistryError("Task 2A manifest preprocessing or postprocessing is invalid.")
    if (
        schema.get("feature_profile_id") != contract["feature_profile_id"]
        or total_metadata.get("feature_profile_id") != contract["feature_profile_id"]
        or chilled_metadata.get("feature_profile_id") != contract["feature_profile_id"]
    ):
        raise ArtifactRegistryError("Task 2A feature-profile metadata is inconsistent.")
    expected_metadata = (
        (total_metadata, "total", contract["total_strategy"]),
        (chilled_metadata, "chilled", contract["chilled_strategy"]),
    )
    if any(
        metadata.get("target") != target or metadata.get("candidate_id") != candidate_id
        for metadata, target, candidate_id in expected_metadata
    ):
        raise ArtifactRegistryError("Task 2A component metadata differs from the frozen strategy.")

    manifest_components = manifest.get("components")
    expected_components = (
        ("total", contract["total_artifact_id"], contract["total_strategy"]),
        ("chilled", contract["chilled_artifact_id"], contract["chilled_strategy"]),
    )
    if not isinstance(manifest_components, list) or len(manifest_components) != 2:
        raise ArtifactRegistryError("Task 2A artifact manifest is incomplete.")
    by_target = {
        component.get("target"): component
        for component in manifest_components
        if isinstance(component, dict)
    }
    entries = _artifact_map(registry)
    for target, artifact_id, candidate_id in expected_components:
        component = by_target.get(target)
        entry = entries[artifact_id]
        if (
            component is None
            or component.get("candidate_id") != candidate_id
            or component.get("relative_path") != entry["relative_path"]
            or component.get("sha256") != entry["sha256"]
            or component.get("component_weights") != contract["component_weights"]
            or component.get("component_families") != ["catboost", "lightgbm"]
        ):
            raise ArtifactRegistryError("Task 2A manifest component metadata is inconsistent.")
    return {
        "total": total,
        "chilled": chilled,
        "manifest": manifest,
        "schema": schema,
        "total_metadata": total_metadata,
        "chilled_metadata": chilled_metadata,
    }


def load_phase31_artifact_set(
    registry_path: Path,
    project_root: Path,
    *,
    allow_staging: bool = False,
) -> dict[str, Any]:
    """Fresh-process bridge used by the Phase 31 final inference layer."""
    registry = load_artifact_registry(registry_path, project_root, allow_staging=allow_staging)
    return {
        "registry": registry,
        "task1_service": load_task1_service_bundle(registry, project_root),
        "task1_late": load_task1_late_bundle(registry, project_root),
        "task2a": load_task2a_bundle(registry, project_root),
    }


def validate_legacy_inventory_alignment(
    registry: dict[str, Any],
    legacy_manifest_path: Path,
    project_root: Path,
) -> None:
    """Keep the deprecated Phase 31 manifest from silently diverging."""
    root = Path(project_root).resolve()
    path = Path(legacy_manifest_path).resolve()
    expected = (root / "configs/final_artifacts.yaml").resolve()
    if path != expected or not path.is_file():
        raise ArtifactRegistryError("Legacy artifact manifest path is not canonical.")
    try:
        legacy = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ArtifactRegistryError("Legacy artifact manifest is not valid YAML.") from exc
    validate_legacy_inventory_data(registry, legacy)


def validate_legacy_inventory_data(
    registry: dict[str, Any],
    legacy: Any,
) -> None:
    """Validate a parsed deprecated inventory against the canonical registry."""
    hashes = legacy.get("artifact_sha256") if isinstance(legacy, dict) else None
    if not isinstance(hashes, dict) or not hashes:
        raise ArtifactRegistryError("Legacy artifact inventory is incomplete.")
    registered = {
        entry["relative_path"]: entry["sha256"]
        for entry in registry["artifacts"]
    }
    if any(registered.get(str(relative)) != str(digest) for relative, digest in hashes.items()):
        raise ArtifactRegistryError("Legacy and canonical artifact inventories diverge.")
