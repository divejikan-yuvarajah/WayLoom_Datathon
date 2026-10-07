"""Validate Phase 32 artifacts and loaded-model parity on authorized local data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.artifacts.final_inference import (  # noqa: E402
    load_artifact_manifest,
    run_saved_artifact_inference_demo,
    sha256_file,
)


EXPECTED_CONFIG = ROOT / "configs/artifact_management.yaml"


class ArtifactValidationError(ValueError):
    """Phase 32 validation evidence is incomplete or inconsistent."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ArtifactValidationError(f"Configuration is not a mapping: {path.name}")
    return value


def _path(config: dict[str, Any], section: str, key: str) -> Path:
    return (ROOT / str(config[section][key])).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=EXPECTED_CONFIG)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.config.resolve() != EXPECTED_CONFIG.resolve():
        raise ArtifactValidationError("Phase 32 must use configs/artifact_management.yaml.")
    config = _load_yaml(args.config)
    if config.get("state") != "PASS":
        raise ArtifactValidationError("Phase 32 artifact-management config is not PASS.")
    phase31 = _load_yaml(_path(config, "configs", "final_notebook"))
    if phase31.get("phase32", {}).get("status") != "PASS":
        raise ArtifactValidationError("Phase 31 has not accepted the Phase 32 artifact handoff.")

    manifest_path = _path(config, "paths", "manifest")
    manifest = load_artifact_manifest(manifest_path, ROOT)
    expected_tasks = {f"DT-{number}": "PASS" for number in range(412, 420)}
    if manifest.get("tasks") != expected_tasks:
        raise ArtifactValidationError("Phase 32 task evidence is incomplete.")
    if manifest.get("roundtrip_parity") != {"task1": "PASS", "task2a": "PASS"}:
        raise ArtifactValidationError("Phase 32 roundtrip parity evidence is incomplete.")

    demo = run_saved_artifact_inference_demo(
        project_root=ROOT,
        artifact_registry=ROOT / "models/artifact_registry.json",
        max_demo_rows=1,
        numeric_tolerance=float(config["serialization"]["numeric_tolerance"]),
        write_official_outputs=False,
    )
    if not all(demo[key] is True for key in ("saved_artifacts_loaded", "task1_parity_pass", "task2a_parity_pass")):
        raise ArtifactValidationError("Loaded-model integration parity failed.")

    report_dir = _path(config, "paths", "private_report_dir")
    report_path = report_dir / "run_manifest.json"
    hash_path = report_dir / "frozen_hash_audit.json"
    if not report_path.is_file() or not hash_path.is_file():
        raise ArtifactValidationError("Phase 32 private build evidence is missing.")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    audit = json.loads(hash_path.read_text(encoding="utf-8"))
    if report.get("status") != "PASS" or report.get("tasks_passed") != 8:
        raise ArtifactValidationError("Phase 32 private run manifest is not PASS.")
    if audit.get("status") != "PASS" or audit.get("before") != audit.get("after"):
        raise ArtifactValidationError("Phase 32 frozen-artifact audit did not pass.")
    current = {
        relative: sha256_file(ROOT / relative)
        for relative in manifest["artifact_paths"]
    }
    if current != manifest["artifact_sha256"]:
        raise ArtifactValidationError("A saved artifact changed after Phase 32 freeze.")

    print("LOCAL PHASE 32 ARTIFACT VALIDATION: PASS")
    print("TASKS DT-412-DT-419: PASS (8 / 8)")
    print("SERIALIZATION: PASS")
    print("DESERIALIZATION: PASS")
    print("TASK 1 SAVED-MODEL PARITY: PASS")
    print("TASK 2A SAVED-MODEL PARITY: PASS")
    print("FROZEN ARTIFACTS CHANGED: NO")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
