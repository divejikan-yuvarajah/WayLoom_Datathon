"""Validate and register existing frozen model artifacts without retraining."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.artifact_registry import (
    load_artifact_registry,
    load_phase31_artifact_set,
    validate_legacy_inventory_alignment,
)
from src.task1.final_train import load_frozen_final_config
from src.task2a.model_selection import validate_final_model_config


EXPECTED_CONFIG = ROOT / "configs/model_artifacts.yaml"
EXPECTED_TASK1_CONFIG = ROOT / "configs/task1_final_models.yaml"
EXPECTED_TASK2A_CONFIG = ROOT / "configs/task2a_final_models.yaml"
EXPECTED_REGISTRY = ROOT / "models/artifact_registry.json"
EXPECTED_REPORT_DIR = ROOT / "reports/private/phase32_model_artifacts"


class ModelArtifactFinalizationError(ValueError):
    """The safe Phase 32 finalization preflight failed."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ModelArtifactFinalizationError("Artifact configuration must be a mapping.")
    return value


def _canonical(actual: Path, expected: Path, label: str) -> None:
    if actual.resolve() != expected.resolve():
        raise ModelArtifactFinalizationError(f"{label} must use its canonical repository path.")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _protected_paths(config: dict[str, Any], registry: dict[str, Any]) -> list[Path]:
    paths = [(ROOT / value).resolve() for value in config["protected_outputs"]]
    paths.extend(
        (ROOT / entry["relative_path"]).resolve()
        for entry in registry["artifacts"]
        if entry["task"] in {"task1_service", "task1_late"}
    )
    unique = list(dict.fromkeys(paths))
    if any(not path.is_file() for path in unique):
        raise ModelArtifactFinalizationError("A protected frozen artifact is missing.")
    return unique


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--task1-config", type=Path, required=True)
    parser.add_argument("--task2a-config", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _canonical(args.config, EXPECTED_CONFIG, "Artifact config")
    _canonical(args.task1_config, EXPECTED_TASK1_CONFIG, "Task 1 final config")
    _canonical(args.task2a_config, EXPECTED_TASK2A_CONFIG, "Task 2A final config")
    _canonical(args.registry, EXPECTED_REGISTRY, "Artifact registry")
    _canonical(args.report_dir, EXPECTED_REPORT_DIR, "Private report directory")

    config = _load_yaml(args.config)
    if config.get("state") != "READY_FOR_LOCAL_PARITY":
        raise ModelArtifactFinalizationError("Phase 32 safe finalization state is invalid.")
    task1 = load_frozen_final_config(args.task1_config)
    task2a = _load_yaml(args.task2a_config)
    validate_final_model_config(task2a)
    registry = load_artifact_registry(args.registry, ROOT)
    validate_legacy_inventory_alignment(registry, ROOT / "configs/final_artifacts.yaml", ROOT)
    if registry["task1_service"]["config_id"] != task1["service_model"]["config_id"]:
        raise ModelArtifactFinalizationError("Task 1 service registry/config mismatch.")
    if registry["task1_late"]["config_id"] != task1["lateness_model"]["config_id"]:
        raise ModelArtifactFinalizationError("Task 1 lateness registry/config mismatch.")
    if registry["task2a"]["total_strategy"] != task2a["total"]["candidate_id"]:
        raise ModelArtifactFinalizationError("Task 2A total registry/config mismatch.")
    if registry["task2a"]["chilled_strategy"] != task2a["chilled_fresh"]["candidate_id"]:
        raise ModelArtifactFinalizationError("Task 2A chilled registry/config mismatch.")

    protected = _protected_paths(config, registry)
    before = {path.relative_to(ROOT).as_posix(): _sha256(path) for path in protected}
    loaded = load_phase31_artifact_set(args.registry, ROOT)
    if set(loaded) != {"registry", "task1_service", "task1_late", "task2a"}:
        raise ModelArtifactFinalizationError("Fresh-loader bridge returned an incomplete artifact set.")
    after = {path.relative_to(ROOT).as_posix(): _sha256(path) for path in protected}
    if before != after:
        raise ModelArtifactFinalizationError("Safe finalization changed a protected artifact.")

    args.report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": 32,
        "status": "SAFE_FINALIZATION_PASS_PRIVATE_PARITY_PENDING",
        "tasks_ready": [f"DT-{number}" for number in range(412, 420)],
        "artifact_count": len(registry["artifacts"]),
        "task1_artifacts_unchanged": True,
        "official_outputs_unchanged": True,
        "fresh_process_load": "PENDING_SAFE_VALIDATOR",
        "private_parity": "PENDING_HUMAN_LOCAL",
    }
    (args.report_dir / "safe_finalization.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("WAYLOOM - PHASE 32 SAFE ARTIFACT FINALIZATION: PASS")
    print("DT-412-DT-418 READINESS: PASS")
    print("TASK 1 CANONICAL ARTIFACTS CHANGED: NO")
    print("OFFICIAL OUTPUTS CHANGED: NO")
    print("PRIVATE PARITY: PENDING HUMAN-LOCAL RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
