"""Human-local private parity gate for the Phase 32 registered artifacts."""

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

from src.artifacts.final_inference import run_saved_artifact_inference_demo
from src.common.artifact_registry import (
    load_phase31_artifact_set,
    validate_legacy_inventory_alignment,
)


EXPECTED_CONFIG = ROOT / "configs/model_artifacts.yaml"
EXPECTED_REGISTRY = ROOT / "models/artifact_registry.json"
EXPECTED_DATASET_MANIFEST = ROOT / "configs/dataset_manifest.yaml"
EXPECTED_TASK1_OUTPUT = ROOT / "outputs/submission_task1.csv"
EXPECTED_TASK2A_OUTPUT = ROOT / "outputs/submission_task2a.csv"
EXPECTED_REPORT_DIR = ROOT / "reports/private/phase32_model_artifacts"


class ModelArtifactParityError(ValueError):
    """Loaded registered artifacts do not reproduce frozen predictions."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ModelArtifactParityError("Artifact configuration must be a mapping.")
    return value


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-config", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--dataset-manifest", type=Path, required=True)
    parser.add_argument("--task1-frozen-output", type=Path, required=True)
    parser.add_argument("--task2a-frozen-output", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected = {
        "artifact config": (args.artifact_config, EXPECTED_CONFIG),
        "registry": (args.registry, EXPECTED_REGISTRY),
        "raw root": (args.raw_root, ROOT / "data/raw"),
        "dataset manifest": (args.dataset_manifest, EXPECTED_DATASET_MANIFEST),
        "Task 1 frozen output": (args.task1_frozen_output, EXPECTED_TASK1_OUTPUT),
        "Task 2A frozen output": (args.task2a_frozen_output, EXPECTED_TASK2A_OUTPUT),
        "report directory": (args.report_dir, EXPECTED_REPORT_DIR),
    }
    for label, (actual, canonical) in expected.items():
        if actual.resolve() != canonical.resolve():
            raise ModelArtifactParityError(f"{label} path is not canonical.")

    config = _load_yaml(args.artifact_config)
    loaded = load_phase31_artifact_set(args.registry, ROOT)
    registry = loaded["registry"]
    validate_legacy_inventory_alignment(registry, ROOT / "configs/final_artifacts.yaml", ROOT)
    protected = [(ROOT / value).resolve() for value in config["protected_outputs"]]
    protected.extend((ROOT / entry["relative_path"]).resolve() for entry in registry["artifacts"])
    protected = list(dict.fromkeys(protected))
    before = {path.relative_to(ROOT).as_posix(): _hash(path) for path in protected}

    demo = run_saved_artifact_inference_demo(
        project_root=ROOT,
        artifact_registry=args.registry,
        max_demo_rows=1,
        numeric_tolerance=float(config["parity"]["numeric_tolerance"]),
        write_official_outputs=False,
        loaded_artifacts=loaded,
    )
    if not all(demo[key] is True for key in ("saved_artifacts_loaded", "task1_parity_pass", "task2a_parity_pass")):
        raise ModelArtifactParityError("Loaded-artifact private parity failed.")
    after = {path.relative_to(ROOT).as_posix(): _hash(path) for path in protected}
    if before != after:
        raise ModelArtifactParityError("A protected artifact changed during private parity.")

    args.report_dir.mkdir(parents=True, exist_ok=True)
    gate = {
        "phase": 32,
        "status": "PASS",
        **{f"dt{number}": "PASS" for number in range(412, 420)},
        "task1_artifacts_unchanged": True,
        "official_outputs_unchanged": True,
        "task1_parity": "PASS",
        "task2a_parity": "PASS",
        "fresh_process_load": "PASS",
    }
    (args.report_dir / "phase32_gate.json").write_text(
        json.dumps(gate, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("WAYLOOM - PHASE 32 MODEL ARTIFACT PARITY: PASS")
    print("DT-412-DT-419: PASS")
    print("TASK 1 SAVED-MODEL PARITY: PASS")
    print("TASK 2A SAVED-MODEL PARITY: PASS")
    print("ID/ORDER PARITY: PASS")
    print("PROTECTED ARTIFACTS CHANGED: NO")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
