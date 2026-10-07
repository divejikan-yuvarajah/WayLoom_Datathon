from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from src.common.artifact_registry import ArtifactRegistryError, validate_registry_data


ROOT = Path(__file__).resolve().parents[1]


def _registry() -> dict:
    return json.loads((ROOT / "models/artifact_registry.json").read_text(encoding="utf-8"))


def test_actual_preprocessing_modes_and_schema_references_are_explicit() -> None:
    registry = validate_registry_data(_registry(), ROOT, verify_files=False)
    assert registry["task1_service"]["preprocessor_mode"] == "deterministic_code"
    assert registry["task1_late"]["preprocessor_mode"] == "deterministic_code"
    assert registry["task2a"]["preprocessor_mode"] == "embedded"
    schema_paths = {
        entry["relative_path"]
        for entry in registry["artifacts"]
        if entry["artifact_kind"] == "feature_schema"
    }
    assert all(entry["feature_schema_ref"] in schema_paths for entry in registry["artifacts"])


def test_external_preprocessor_requires_registered_state() -> None:
    registry = _registry()
    registry["artifacts"][0]["preprocessor_mode"] = "external_serialized"
    with pytest.raises(ArtifactRegistryError, match="External preprocessing state"):
        validate_registry_data(registry, ROOT, verify_files=False)


def test_embedded_or_deterministic_preprocessing_rejects_duplicate_reference() -> None:
    registry = deepcopy(_registry())
    registry["artifacts"][0]["preprocessor_artifact_id"] = "task1_service_model"
    with pytest.raises(ArtifactRegistryError, match="must not reference"):
        validate_registry_data(registry, ROOT, verify_files=False)
