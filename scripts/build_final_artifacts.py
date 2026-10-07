"""Build and validate Phase 32 saved artifacts on the authorized local dataset."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.artifacts.final_inference import (  # noqa: E402
    assert_prediction_parity,
    current_library_versions,
    load_artifact_manifest,
    load_task2a_component,
    predict_task2a_from_loaded_components,
    run_saved_artifact_inference_demo,
    run_loaded_artifact_synthetic_smoke,
    sha256_file,
)
from src.common.data_inventory import discover_dataset_files, load_manifest  # noqa: E402
from src.common.artifact_registry import load_phase31_artifact_set  # noqa: E402
from src.task1.final_train import load_model_bundle  # noqa: E402
from src.task1.inference import run_task1_inference  # noqa: E402
from src.task2a.features import load_feature_config  # noqa: E402
from src.task2a.final_fit import fit_frozen_component  # noqa: E402
from src.task2a.final_inference import build_final_test_features  # noqa: E402
from src.task2a.model_preprocessing import feature_profile  # noqa: E402
from src.task2a.model_selection import validate_final_model_config  # noqa: E402


EXPECTED_CONFIG = ROOT / "configs/artifact_management.yaml"


class ArtifactBuildError(ValueError):
    """Phase 32 artifacts could not be built without violating a frozen contract."""


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ArtifactBuildError(f"Configuration is not a mapping: {path.name}")
    return value


def _path(config: dict[str, Any], section: str, key: str) -> Path:
    value = (ROOT / str(config[section][key])).resolve()
    if not _inside(value, ROOT):
        raise ArtifactBuildError(f"Configured path escapes repository: {section}.{key}")
    return value


def _official(raw_root: Path, manifest_path: Path, filename: str) -> Path:
    found = discover_dataset_files(raw_root, load_manifest(manifest_path)).get("found_artifacts") or {}
    value = found.get(filename, {}).get("path")
    if not value:
        raise ArtifactBuildError(f"Required official artifact is unavailable: {filename}")
    return Path(value)


def _atomic_joblib(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    joblib.dump(value, temporary)
    os.replace(temporary, path)


def _atomic_json(value: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


def _atomic_yaml(value: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    os.replace(temporary, path)


def _promote_validated_candidate(
    files: list[tuple[Path, Path]],
    *,
    registry_payload: dict[str, Any],
    registry_path: Path,
    candidate_validated: bool,
) -> None:
    """Publish a complete validated set, rolling back every partial move."""
    if not candidate_validated:
        raise ArtifactBuildError("Candidate validation must pass before promotion.")
    if not files or any(not source.is_file() for source, _ in files):
        raise ArtifactBuildError("Validated candidate file set is incomplete.")
    existing = [destination for _, destination in files if destination.exists()]
    if existing:
        if len(existing) != len(files) or any(
            sha256_file(source) != sha256_file(destination)
            for source, destination in files
        ):
            raise ArtifactBuildError(
                "Canonical Task 2A artifacts already exist; explicit controlled refinalization is required."
            )
        return

    registry_before = registry_path.read_bytes() if registry_path.is_file() else None
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_temp = registry_path.with_suffix(registry_path.suffix + ".promotion.tmp")
    registry_temp.write_text(
        json.dumps(registry_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    moved: list[Path] = []
    try:
        for source, destination in files:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)
            moved.append(destination)
        os.replace(registry_temp, registry_path)
    except Exception:
        for destination in reversed(moved):
            destination.unlink(missing_ok=True)
        registry_temp.unlink(missing_ok=True)
        if registry_before is not None:
            restore = registry_path.with_suffix(registry_path.suffix + ".restore.tmp")
            restore.write_bytes(registry_before)
            os.replace(restore, registry_path)
        else:
            registry_path.unlink(missing_ok=True)
        raise


def _candidate_registry(
    *,
    staging_root: Path,
    staged_paths: dict[str, Path],
    manifest_path: Path,
) -> tuple[Path, dict[str, Any]]:
    registry_path = ROOT / "models/artifact_registry.json"
    if not registry_path.is_file():
        raise ArtifactBuildError("Canonical registry template is missing.")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    entries = {entry["artifact_id"]: entry for entry in registry["artifacts"]}
    artifact_ids = {
        "total_bundle": "task2a_total_bundle",
        "total_metadata": "task2a_total_metadata",
        "chilled_bundle": "task2a_chilled_bundle",
        "chilled_metadata": "task2a_chilled_metadata",
        "manifest": "task2a_manifest",
    }
    candidate_paths = {**staged_paths, "manifest": manifest_path}
    for key, artifact_id in artifact_ids.items():
        path = candidate_paths[key]
        entry = entries[artifact_id]
        entry["relative_path"] = path.relative_to(ROOT).as_posix()
        entry["sha256"] = sha256_file(path)
        entry["size_bytes"] = path.stat().st_size
    candidate_registry = staging_root / "artifact_registry.json"
    _atomic_json(registry, candidate_registry)
    return candidate_registry, registry


def _stage_task2a_candidate(
    *,
    staging_root: Path,
    total: Any,
    chilled: Any,
    total_metadata: dict[str, Any],
    chilled_metadata: dict[str, Any],
) -> tuple[dict[str, Path], Path]:
    paths = {
        "total_bundle": staging_root / "task2a_total/component.joblib",
        "total_metadata": staging_root / "task2a_total/metadata.json",
        "chilled_bundle": staging_root / "task2a_chilled/component.joblib",
        "chilled_metadata": staging_root / "task2a_chilled/metadata.json",
    }
    _atomic_joblib(total, paths["total_bundle"])
    _atomic_joblib(chilled, paths["chilled_bundle"])
    _atomic_json(total_metadata, paths["total_metadata"])
    _atomic_json(chilled_metadata, paths["chilled_metadata"])

    template_path = ROOT / "models/task2a/artifact_manifest.json"
    if not template_path.is_file():
        raise ArtifactBuildError("Task 2A manifest template is missing.")
    manifest = json.loads(template_path.read_text(encoding="utf-8"))
    by_target = {component["target"]: component for component in manifest["components"]}
    for target, key in (("total", "total_bundle"), ("chilled", "chilled_bundle")):
        by_target[target]["relative_path"] = paths[key].relative_to(ROOT).as_posix()
        by_target[target]["sha256"] = sha256_file(paths[key])
    manifest_path = staging_root / "task2a/artifact_manifest.json"
    _atomic_json(manifest, manifest_path)
    return paths, manifest_path


def _frozen_paths(config: dict[str, Any]) -> list[Path]:
    paths = [_path(config, "frozen_outputs", key) for key in ("task1", "task2a")]
    for key in ("task1_service_dir", "task1_late_dir"):
        directory = _path(config, "paths", key)
        if not directory.is_dir():
            raise ArtifactBuildError(f"Frozen Task 1 artifact directory is missing: {directory.name}")
        paths.extend(sorted(item for item in directory.iterdir() if item.is_file()))
    if any(not path.is_file() for path in paths):
        raise ArtifactBuildError("A frozen output or Task 1 artifact is missing.")
    return paths


def _hashes(paths: list[Path]) -> dict[str, str]:
    return {path.relative_to(ROOT).as_posix(): sha256_file(path) for path in paths}


def _artifact_inventory(config: dict[str, Any]) -> list[Path]:
    files: list[Path] = []
    for key in ("task1_service_dir", "task1_late_dir"):
        files.extend(sorted(item for item in _path(config, "paths", key).iterdir() if item.is_file()))
    for key in (
        "task2a_total_bundle",
        "task2a_total_metadata",
        "task2a_chilled_bundle",
        "task2a_chilled_metadata",
    ):
        files.append(_path(config, "paths", key))
    if any(not path.is_file() for path in files):
        raise ArtifactBuildError("Serialized artifact inventory is incomplete.")
    return files


def _update_gate_configs(config: dict[str, Any]) -> None:
    phase31_path = _path(config, "configs", "final_notebook")
    phase31 = _load_yaml(phase31_path)
    phase31["phase32"]["status"] = "PASS"
    manager = dict(config)
    manager["state"] = "PASS"
    _atomic_yaml(manager, EXPECTED_CONFIG)
    _atomic_yaml(phase31, phase31_path)


def _recover_completed_build(config: dict[str, Any], manifest_path: Path) -> int:
    """Finish only the gate flip after a previously verified atomic build."""
    load_artifact_manifest(manifest_path, ROOT)
    report_dir = _path(config, "paths", "private_report_dir")
    report_path = report_dir / "run_manifest.json"
    audit_path = report_dir / "frozen_hash_audit.json"
    if not report_path.is_file() or not audit_path.is_file():
        raise ArtifactBuildError("Existing artifact manifest lacks completed private build evidence.")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if report.get("status") != "PASS" or audit.get("status") != "PASS" or audit.get("before") != audit.get("after"):
        raise ArtifactBuildError("Existing Phase 32 build evidence is not PASS.")
    demo = run_saved_artifact_inference_demo(
        project_root=ROOT,
        artifact_registry=ROOT / "models/artifact_registry.json",
        max_demo_rows=1,
        numeric_tolerance=float(config["serialization"]["numeric_tolerance"]),
        write_official_outputs=False,
    )
    if not all(demo[key] is True for key in ("saved_artifacts_loaded", "task1_parity_pass", "task2a_parity_pass")):
        raise ArtifactBuildError("Existing Phase 32 artifacts no longer reproduce frozen predictions.")
    _update_gate_configs(config)
    print("LOCAL PHASE 32 ARTIFACT MANAGEMENT: PASS")
    print("RECOVERED COMPLETED ATOMIC BUILD: YES")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=EXPECTED_CONFIG)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.config.resolve() != EXPECTED_CONFIG.resolve():
        raise ArtifactBuildError("Phase 32 must use configs/artifact_management.yaml.")
    config = _load_yaml(args.config)
    if config.get("version") != 1 or config.get("state") not in {"AWAITING_LOCAL_BUILD", "PASS"}:
        raise ArtifactBuildError("Artifact-management state is invalid.")
    manifest_path = _path(config, "paths", "manifest")
    if config["state"] == "PASS":
        raise ArtifactBuildError("Phase 32 artifacts are already frozen; use the validator instead of overwriting them.")
    if manifest_path.is_file():
        return _recover_completed_build(config, manifest_path)

    frozen_paths = _frozen_paths(config)
    frozen_before = _hashes(frozen_paths)
    tolerance = float(config["serialization"]["numeric_tolerance"])

    print("PHASE 32 STEP 1/4: validating frozen Task 1 saved models and parity")
    service_dir = _path(config, "paths", "task1_service_dir")
    late_dir = _path(config, "paths", "task1_late_dir")
    load_model_bundle(service_dir)
    load_model_bundle(late_dir)
    task1 = run_task1_inference(
        raw_root=args.raw_root,
        feature_registry_path=_path(config, "configs", "task1_features"),
        final_config_path=_path(config, "configs", "task1_final_models"),
        service_model_dir=service_dir,
        late_model_dir=late_dir,
        inference_config_path=_path(config, "configs", "task1_inference"),
        historical_train_labels=pd.read_csv(_path(config, "paths", "task1_labels"), low_memory=False),
    )
    assert_prediction_parity(
        task1["predictions"],
        pd.read_csv(_path(config, "frozen_outputs", "task1")),
        key="delivery_id",
        prediction_columns=("pred_service_min", "pred_late_prob"),
        tolerance=tolerance,
    )

    print("PHASE 32 STEP 2/4: fitting frozen Task 2A components (no model search)")
    final_config = _load_yaml(_path(config, "configs", "task2a_final_models"))
    validate_final_model_config(final_config)
    feature_config = load_feature_config(_path(config, "configs", "task2a_features"))
    profile = feature_profile(feature_config)
    panel = pd.read_csv(_path(config, "paths", "task2a_weekly_panel"), low_memory=False)
    table = pd.read_csv(_path(config, "paths", "task2a_multihorizon_table"), low_memory=False)
    calendar = pd.read_csv(_official(args.raw_root, _path(config, "configs", "dataset_manifest"), "calendar.csv"), low_memory=False)
    test_inputs = pd.read_csv(
        _official(args.raw_root, _path(config, "configs", "dataset_manifest"), "task2a_test_inputs.csv"),
        low_memory=False,
    )
    features, origin = build_final_test_features(panel, calendar, test_inputs, feature_config)
    total = fit_frozen_component(final_config["total"], "total", table, origin, profile)
    chilled = fit_frozen_component(final_config["chilled_fresh"], "chilled", table, origin, profile)
    in_memory = predict_task2a_from_loaded_components(
        panel=panel,
        calendar=calendar,
        test_inputs=test_inputs,
        final_config=final_config,
        feature_config=feature_config,
        total_component=total,
        chilled_component=chilled,
    )
    assert_prediction_parity(
        in_memory["predictions"],
        pd.read_csv(_path(config, "frozen_outputs", "task2a")),
        key="row_id",
        prediction_columns=("pred_total_volume_m3", "pred_chilled_volume_m3"),
        tolerance=tolerance,
    )

    print("PHASE 32 STEP 3/4: serializing and reloading Task 2A artifacts")
    total_path = _path(config, "paths", "task2a_total_bundle")
    chilled_path = _path(config, "paths", "task2a_chilled_bundle")
    versions = current_library_versions()
    common_metadata = {
        "phase": 32,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_profile_id": profile["profile_id"],
        "feature_registry_hash": profile["registry_hash"],
        "training_origin": pd.Timestamp(origin).date().isoformat(),
        "library_versions": versions,
        "serialization_format": "joblib",
    }
    total_metadata = {
        **common_metadata,
        "target": "total",
        "candidate_id": final_config["total"]["candidate_id"],
    }
    chilled_metadata = {
        **common_metadata,
        "target": "chilled",
        "candidate_id": final_config["chilled_fresh"]["candidate_id"],
    }
    staging_parent = ROOT / "models/.staging/phase32"
    staging_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="candidate-", dir=staging_parent) as temporary:
        staging_root = Path(temporary)
        staged_paths, staged_manifest = _stage_task2a_candidate(
            staging_root=staging_root,
            total=total,
            chilled=chilled,
            total_metadata=total_metadata,
            chilled_metadata=chilled_metadata,
        )
        candidate_registry_path, candidate_registry = _candidate_registry(
            staging_root=staging_root,
            staged_paths=staged_paths,
            manifest_path=staged_manifest,
        )
        loaded_candidate = load_phase31_artifact_set(
            candidate_registry_path,
            ROOT,
            allow_staging=True,
        )
        run_loaded_artifact_synthetic_smoke(loaded_candidate)
        reloaded = predict_task2a_from_loaded_components(
            panel=panel,
            calendar=calendar,
            test_inputs=test_inputs,
            final_config=final_config,
            feature_config=feature_config,
            total_component=loaded_candidate["task2a"]["total"],
            chilled_component=loaded_candidate["task2a"]["chilled"],
        )
        assert_prediction_parity(
            reloaded["predictions"],
            in_memory["predictions"],
            key="row_id",
            prediction_columns=("pred_total_volume_m3", "pred_chilled_volume_m3"),
            tolerance=tolerance,
            require_order=True,
        )

        canonical_paths = {
            "total_bundle": total_path,
            "total_metadata": _path(config, "paths", "task2a_total_metadata"),
            "chilled_bundle": chilled_path,
            "chilled_metadata": _path(config, "paths", "task2a_chilled_metadata"),
        }
        canonical_manifest_value = json.loads(staged_manifest.read_text(encoding="utf-8"))
        components = {item["target"]: item for item in canonical_manifest_value["components"]}
        for target, key in (("total", "total_bundle"), ("chilled", "chilled_bundle")):
            components[target]["relative_path"] = canonical_paths[key].relative_to(ROOT).as_posix()
            components[target]["sha256"] = sha256_file(staged_paths[key])
        canonical_manifest_candidate = staging_root / "canonical_artifact_manifest.json"
        _atomic_json(canonical_manifest_value, canonical_manifest_candidate)
        canonical_manifest_path = ROOT / "models/task2a/artifact_manifest.json"

        registry_entries = {
            entry["artifact_id"]: entry for entry in candidate_registry["artifacts"]
        }
        for key, artifact_id in {
            "total_bundle": "task2a_total_bundle",
            "total_metadata": "task2a_total_metadata",
            "chilled_bundle": "task2a_chilled_bundle",
            "chilled_metadata": "task2a_chilled_metadata",
        }.items():
            entry = registry_entries[artifact_id]
            entry["relative_path"] = canonical_paths[key].relative_to(ROOT).as_posix()
            entry["sha256"] = sha256_file(staged_paths[key])
            entry["size_bytes"] = staged_paths[key].stat().st_size
        manifest_entry = registry_entries["task2a_manifest"]
        manifest_entry["relative_path"] = canonical_manifest_path.relative_to(ROOT).as_posix()
        manifest_entry["sha256"] = sha256_file(canonical_manifest_candidate)
        manifest_entry["size_bytes"] = canonical_manifest_candidate.stat().st_size

        promotion_files = [
            (staged_paths[key], canonical_paths[key]) for key in canonical_paths
        ]
        promotion_files.append((canonical_manifest_candidate, canonical_manifest_path))
        _promote_validated_candidate(
            promotion_files,
            registry_payload=candidate_registry,
            registry_path=ROOT / "models/artifact_registry.json",
            candidate_validated=True,
        )

    print("PHASE 32 STEP 4/4: validating end-to-end loaded-artifact parity")
    artifacts = _artifact_inventory(config)
    relative = [path.relative_to(ROOT).as_posix() for path in artifacts]
    manifest = {
        "version": 1,
        "phase": 32,
        "status": "PASS",
        "tasks": {f"DT-{number}": "PASS" for number in range(412, 420)},
        "artifact_paths": relative,
        "artifact_sha256": _hashes(artifacts),
        "interfaces": {
            "task1_service_dir": service_dir.relative_to(ROOT).as_posix(),
            "task1_late_dir": late_dir.relative_to(ROOT).as_posix(),
            "task2a_total_bundle": total_path.relative_to(ROOT).as_posix(),
            "task2a_chilled_bundle": chilled_path.relative_to(ROOT).as_posix(),
        },
        "library_versions": versions,
        "roundtrip_parity": {"task1": "PASS", "task2a": "PASS"},
        "preprocessing": {"task1": "BUNDLED_SCHEMA", "task2a": "BUNDLED_WITH_COMPONENTS"},
    }
    pending_manifest = manifest_path.with_suffix(".pending.yaml")
    _atomic_yaml(manifest, pending_manifest)
    demo = run_saved_artifact_inference_demo(
        project_root=ROOT,
        artifact_registry=ROOT / "models/artifact_registry.json",
        max_demo_rows=1,
        numeric_tolerance=tolerance,
        write_official_outputs=False,
    )
    if not demo["saved_artifacts_loaded"] or not demo["task1_parity_pass"] or not demo["task2a_parity_pass"]:
        raise ArtifactBuildError("Final saved-artifact integration parity did not pass.")
    frozen_after = _hashes(frozen_paths)
    if frozen_before != frozen_after:
        raise ArtifactBuildError("A frozen model or official output changed during Phase 32.")
    report_dir = _path(config, "paths", "private_report_dir")
    report = {
        "phase": 32,
        "status": "PASS",
        "tasks_passed": 8,
        "task1_roundtrip_parity": "PASS",
        "task2a_roundtrip_parity": "PASS",
        "artifact_count": len(artifacts),
        "frozen_artifacts": "UNCHANGED",
    }
    _atomic_json(report, report_dir / "run_manifest.json")
    _atomic_json({"status": "PASS", "before": frozen_before, "after": frozen_after}, report_dir / "frozen_hash_audit.json")
    os.replace(pending_manifest, manifest_path)
    _update_gate_configs(config)

    print("LOCAL PHASE 32 ARTIFACT MANAGEMENT: PASS")
    print("TASKS DT-412-DT-419: PASS (8 / 8)")
    print("TASK 1 SAVED-MODEL PARITY: PASS")
    print("TASK 2A SERIALIZATION ROUNDTRIP: PASS")
    print("TASK 2A FROZEN-OUTPUT PARITY: PASS")
    print("FROZEN ARTIFACTS CHANGED: NO")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
