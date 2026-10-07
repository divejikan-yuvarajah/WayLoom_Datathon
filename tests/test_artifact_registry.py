from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from src.common.artifact_registry import (
    ArtifactRegistryError,
    REQUIRED_ENTRY_FIELDS,
    load_artifact_registry,
    validate_legacy_inventory_data,
    validate_registry_data,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "models/artifact_registry.json"


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
