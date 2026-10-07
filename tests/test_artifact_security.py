from __future__ import annotations

import hashlib
from pathlib import Path

import joblib
import pytest

import src.common.artifact_io as artifact_io
from src.common.artifact_io import ArtifactIOError, load_verified_joblib, resolve_model_artifact


@pytest.mark.parametrize(
    "unsafe",
    [
        "C:/Users/person/model.joblib",
        "/home/person/model.joblib",
        "models/../outside.joblib",
        "../models/model.joblib",
        "https://example.invalid/model.joblib",
        "s3://bucket/model.joblib",
    ],
)
def test_unsafe_artifact_paths_are_rejected(tmp_path: Path, unsafe: str) -> None:
    (tmp_path / "models").mkdir()
    with pytest.raises(ArtifactIOError):
        resolve_model_artifact(tmp_path, unsafe, require_exists=False)


def test_checksum_mismatch_fails_before_joblib_deserialization(tmp_path: Path, monkeypatch) -> None:
    models = tmp_path / "models"
    models.mkdir()
    path = models / "model.joblib"
    path.write_bytes(b"corrupt")
    called = False

    def forbidden_load(_path):
        nonlocal called
        called = True
        raise AssertionError("deserializer must not run")

    monkeypatch.setattr(artifact_io.joblib, "load", forbidden_load)
    entry = {
        "relative_path": "models/model.joblib",
        "sha256": "0" * 64,
        "size_bytes": path.stat().st_size,
        "serializer": "joblib",
        "format": "joblib",
    }
    with pytest.raises(ArtifactIOError, match="checksum"):
        load_verified_joblib(tmp_path, entry)
    assert called is False


def test_registered_joblib_loads_only_after_valid_checksum(tmp_path: Path) -> None:
    models = tmp_path / "models"
    models.mkdir()
    path = models / "model.joblib"
    joblib.dump({"safe": True}, path)
    entry = {
        "relative_path": "models/model.joblib",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
        "serializer": "joblib",
        "format": "joblib",
    }
    assert load_verified_joblib(tmp_path, entry) == {"safe": True}


def test_unknown_serializer_and_corrupt_registered_file_fail_safely(tmp_path: Path) -> None:
    models = tmp_path / "models"
    models.mkdir()
    path = models / "model.joblib"
    path.write_bytes(b"not-a-joblib")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    entry = {
        "relative_path": "models/model.joblib",
        "sha256": digest,
        "size_bytes": path.stat().st_size,
        "serializer": "pickle",
        "format": "pickle",
    }
    with pytest.raises(ArtifactIOError, match="supported joblib"):
        load_verified_joblib(tmp_path, entry)
    entry.update(serializer="joblib", format="joblib")
    with pytest.raises(ArtifactIOError, match="could not be loaded safely") as caught:
        load_verified_joblib(tmp_path, entry)
    assert str(path) not in str(caught.value)
