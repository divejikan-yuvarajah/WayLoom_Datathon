from __future__ import annotations

import hashlib
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from src.common.artifact_registry import (
    ArtifactRegistryError,
    load_artifact_registry,
    load_task1_late_bundle,
    load_task1_service_bundle,
)
from src.task1.inference import predict_late_from_bundle, predict_service_from_bundle


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "models/artifact_registry.json"


def _synthetic_frame(schema: dict, rows: int = 3) -> pd.DataFrame:
    categorical = set(schema["categorical_columns"])
    return pd.DataFrame(
        {
            column: (["__MISSING__"] * rows if column in categorical else np.arange(rows, dtype=float))
            for column in schema["feature_columns"]
        }
    )


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_task1_canonical_load_and_temporary_roundtrip_preserve_predictions(tmp_path: Path) -> None:
    registry = load_artifact_registry(REGISTRY, ROOT)
    service = load_task1_service_bundle(registry, ROOT)
    late = load_task1_late_bundle(registry, ROOT)
    frame = _synthetic_frame(service["schema"])
    service_expected = predict_service_from_bundle(service, frame)
    late_expected = predict_late_from_bundle(late, frame)

    service_copy = tmp_path / "service.joblib"
    late_copy = tmp_path / "late.joblib"
    joblib.dump(service["model"], service_copy)
    joblib.dump(late["model"], late_copy)
    service_roundtrip = {**service, "model": joblib.load(service_copy)}
    late_roundtrip = {**late, "model": joblib.load(late_copy)}

    np.testing.assert_allclose(predict_service_from_bundle(service_roundtrip, frame), service_expected)
    np.testing.assert_allclose(predict_late_from_bundle(late_roundtrip, frame), late_expected)
    assert np.isfinite(service_expected).all()
    assert ((late_expected >= 0) & (late_expected <= 1)).all()


def test_task1_class_calibration_schema_and_canonical_bytes_are_preserved() -> None:
    registry = load_artifact_registry(REGISTRY, ROOT)
    paths = [
        ROOT / entry["relative_path"]
        for entry in registry["artifacts"]
        if entry["task"] in {"task1_service", "task1_late"}
    ]
    before = [_hash(path) for path in paths]
    service = load_task1_service_bundle(registry, ROOT)
    late = load_task1_late_bundle(registry, ROOT)
    after = [_hash(path) for path in paths]
    assert before == after
    assert service["schema"]["feature_columns"] == late["schema"]["feature_columns"]
    assert late["metadata"]["positive_class_index"] == 1
    assert list(late["model"].classes_) == [0, 1]
    assert late["metadata"]["calibration_method"] == "raw"
    assert late["calibration"] is None


def test_task1_late_loaded_classes_must_match_registry() -> None:
    registry = load_artifact_registry(REGISTRY, ROOT)
    registry["task1_late"]["class_order"] = [1, 0]
    with pytest.raises(ArtifactRegistryError, match="class order"):
        load_task1_late_bundle(registry, ROOT)
