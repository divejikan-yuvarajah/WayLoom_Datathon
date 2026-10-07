from pathlib import Path

import joblib
import pandas as pd
import pytest
import yaml

import src.artifacts.final_inference as artifacts
from src.artifacts.final_inference import (
    FinalArtifactError,
    assert_prediction_parity,
    load_artifact_manifest,
    load_task2a_component,
    run_saved_artifact_inference_demo,
    sha256_file,
)
from src.task2a.final_fit import FittedComponent


def _manifest(root: Path, artifact: Path, versions: dict[str, str]) -> Path:
    relative = artifact.relative_to(root).as_posix()
    value = {
        "version": 1,
        "phase": 32,
        "status": "PASS",
        "artifact_paths": [relative],
        "artifact_sha256": {relative: sha256_file(artifact)},
        "interfaces": {
            "task1_service_dir": "models/service",
            "task1_late_dir": "models/late",
            "task2a_total_bundle": relative,
            "task2a_chilled_bundle": relative,
        },
        "library_versions": versions,
    }
    path = root / "manifest.yaml"
    path.write_text(yaml.safe_dump(value), encoding="utf-8")
    return path


def test_manifest_hash_and_environment_validation(tmp_path: Path, monkeypatch) -> None:
    artifact = tmp_path / "component.bin"
    artifact.write_bytes(b"validated")
    versions = {"python": "test"}
    monkeypatch.setattr(artifacts, "current_library_versions", lambda: versions)
    manifest_path = _manifest(tmp_path, artifact, versions)
    assert load_artifact_manifest(manifest_path, tmp_path)["status"] == "PASS"
    artifact.write_bytes(b"changed")
    with pytest.raises(FinalArtifactError, match="hash mismatch"):
        load_artifact_manifest(manifest_path, tmp_path)


def test_task2a_component_roundtrip_is_typed_and_target_bound(tmp_path: Path) -> None:
    path = tmp_path / "component.joblib"
    joblib.dump(FittedComponent({"approach_type": "model"}, "total", model="synthetic"), path)
    assert load_task2a_component(path, expected_target="total").target == "total"
    with pytest.raises(FinalArtifactError, match="invalid type or target"):
        load_task2a_component(path, expected_target="chilled")


def test_prediction_parity_is_key_aligned_and_tolerance_bounded() -> None:
    expected = pd.DataFrame({"row_id": ["b", "a"], "prediction": [2.0, 1.0]})
    actual = pd.DataFrame({"row_id": ["a", "b"], "prediction": [1.0, 2.0 + 1e-10]})
    assert_prediction_parity(
        actual,
        expected,
        key="row_id",
        prediction_columns=("prediction",),
        tolerance=1e-9,
    )
    actual.loc[0, "prediction"] = 1.1
    with pytest.raises(FinalArtifactError, match="parity failed"):
        assert_prediction_parity(
            actual,
            expected,
            key="row_id",
            prediction_columns=("prediction",),
            tolerance=1e-9,
        )


def test_final_demo_refuses_official_output_writes(tmp_path: Path) -> None:
    with pytest.raises(FinalArtifactError, match="must not write"):
        run_saved_artifact_inference_demo(
            project_root=tmp_path,
            artifact_registry=tmp_path / "models/artifact_registry.json",
            max_demo_rows=1,
            numeric_tolerance=1e-9,
            write_official_outputs=True,
        )
