from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

import src.common.artifact_io as artifact_io
import src.common.artifact_registry as artifact_registry
from src.common.artifact_registry import (
    ArtifactRegistryError,
    REQUIRED_ENTRY_FIELDS,
    load_artifact_registry,
    validate_legacy_inventory_data,
    validate_registry_data,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "models/artifact_registry.json"


def _temporary_registry(tmp_path: Path, value: dict) -> tuple[Path, Path]:
    project_root = tmp_path / "project"
    models = project_root / "models"
    models.mkdir(parents=True)
    registry_path = models / "artifact_registry.json"
    registry_path.write_text(json.dumps(value), encoding="utf-8")
    return project_root, registry_path


def _forbid_artifact_access(monkeypatch) -> dict[str, bool]:
    called = {"resolve": False, "verify": False, "deserialize": False}

    def forbidden_resolve(*_args, **_kwargs):
        called["resolve"] = True
        raise AssertionError("artifact paths must not be resolved before registry validation")

    def forbidden_verify(*_args, **_kwargs):
        called["verify"] = True
        raise AssertionError("artifact bytes must not be verified before registry validation")

    def forbidden_load(*_args, **_kwargs):
        called["deserialize"] = True
        raise AssertionError("joblib deserialization must not run")

    monkeypatch.setattr(artifact_registry, "resolve_model_artifact", forbidden_resolve)
    monkeypatch.setattr(artifact_registry, "verify_registered_file", forbidden_verify)
    monkeypatch.setattr(artifact_io.joblib, "load", forbidden_load)
    return called


def test_final_registry_has_complete_versioned_task_inventory() -> None:
    registry = load_artifact_registry(REGISTRY, ROOT)
    assert registry["artifact_schema_version"] == 1
    assert registry["phase"] == 32
    assert len(registry["artifacts"]) == 12
    assert {"task1_service", "task1_late", "task2a"} <= set(registry)
    for entry in registry["artifacts"]:
        assert not REQUIRED_ENTRY_FIELDS.difference(entry)
        assert not Path(entry["relative_path"]).is_absolute()
        assert entry["relative_path"].startswith("models/")


def test_registry_contains_no_private_row_payload_or_absolute_paths() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    assert "C:\\Users\\" not in text
    assert "/home/" not in text
    for forbidden in ("training_rows", "test_rows", "private_rows", "delivery_ids", "row_ids"):
        assert forbidden not in text


def test_registry_rejects_unknown_kind_and_duplicate_id() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    bad_kind = deepcopy(registry)
    bad_kind["artifacts"][0]["artifact_kind"] = "mystery_pickle"
    with pytest.raises(ArtifactRegistryError, match="unsupported artifact kind"):
        validate_registry_data(bad_kind, ROOT, verify_files=False)

    duplicate = deepcopy(registry)
    duplicate["artifacts"][1]["artifact_id"] = duplicate["artifacts"][0]["artifact_id"]
    with pytest.raises(ArtifactRegistryError, match="unique"):
        validate_registry_data(duplicate, ROOT, verify_files=False)


def test_secured_loader_rejects_unsupported_registry_schema_before_artifact_access(
    tmp_path: Path,
    monkeypatch,
) -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry["artifact_schema_version"] = 999
    project_root, registry_path = _temporary_registry(tmp_path, registry)
    called = _forbid_artifact_access(monkeypatch)

    with pytest.raises(ArtifactRegistryError, match="Unsupported artifact registry schema version"):
        load_artifact_registry(registry_path, project_root)
    assert called == {"resolve": False, "verify": False, "deserialize": False}


@pytest.mark.parametrize("mismatch", ["feature_schema", "preprocessor_reference"])
def test_secured_loader_rejects_schema_and_preprocessor_reference_mismatches_before_artifact_access(
    tmp_path: Path,
    monkeypatch,
    mismatch: str,
) -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    first = registry["artifacts"][0]
    if mismatch == "feature_schema":
        first["feature_schema_ref"] = "models/not_registered_feature_schema.json"
        expected = "does not reference a registered feature schema"
    else:
        first["preprocessor_mode"] = "external_serialized"
        first["preprocessor_artifact_id"] = first["artifact_id"]
        expected = "External preprocessing state is not registered"
    project_root, registry_path = _temporary_registry(tmp_path, registry)
    called = _forbid_artifact_access(monkeypatch)

    with pytest.raises(ArtifactRegistryError, match=expected):
        load_artifact_registry(registry_path, project_root)
    assert called == {"resolve": False, "verify": False, "deserialize": False}


def test_legacy_inventory_cannot_diverge_from_registry() -> None:
    registry = load_artifact_registry(REGISTRY, ROOT)
    legacy = {
        "artifact_sha256": {
            entry["relative_path"]: entry["sha256"]
            for entry in registry["artifacts"]
            if entry["artifact_id"] not in {"task2a_feature_schema", "task2a_manifest"}
        }
    }
    validate_legacy_inventory_data(registry, legacy)
    first = next(iter(legacy["artifact_sha256"]))
    legacy["artifact_sha256"][first] = "0" * 64
    with pytest.raises(ArtifactRegistryError, match="diverge"):
        validate_legacy_inventory_data(registry, legacy)
