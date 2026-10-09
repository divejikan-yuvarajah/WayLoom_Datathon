"""Run safe registry, integrity, and fresh-process artifact validation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.artifact_registry import (
    load_artifact_registry,
    load_phase31_artifact_set,
    validate_legacy_inventory_alignment,
)


EXPECTED_CONFIG = ROOT / "configs/model_artifacts.yaml"
EXPECTED_REGISTRY = ROOT / "models/artifact_registry.json"
EXPECTED_REPORT_DIR = ROOT / "reports/private/phase32_model_artifacts"


class ModelArtifactValidationError(ValueError):
    """Safe model-artifact validation did not pass."""


def run_clean_process_load(
    project_root: Path,
    registry: Path,
    *,
    source_root: Path | None = None,
    allow_staging: bool = False,
) -> dict[str, str]:
    code = (
        "import json; "
        "from pathlib import Path; "
        "from src.common.artifact_registry import load_phase31_artifact_set; "
        "from src.artifacts.final_inference import run_loaded_artifact_synthetic_smoke; "
        f"root=Path({str(project_root)!r}); "
        f"bundle=load_phase31_artifact_set(Path({str(registry)!r}), root, allow_staging={allow_staging!r}); "
        "assert set(bundle)=={'registry','task1_service','task1_late','task2a'}; "
        "print(json.dumps(run_loaded_artifact_synthetic_smoke(bundle), sort_keys=True))"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(source_root or project_root)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode != 0:
        raise ModelArtifactValidationError("Fresh-process artifact inference failed.")
    try:
        status = json.loads(result.stdout.strip().splitlines()[-1])
    except Exception as exc:
        raise ModelArtifactValidationError("Fresh-process artifact status was invalid.") from exc
    expected = {
        "registry",
        "checksums",
        "task1_service_inference",
        "task1_late_inference",
        "task2a_total_inference",
        "task2a_chilled_inference",
    }
    if set(status) != expected or any(value != "PASS" for value in status.values()):
        raise ModelArtifactValidationError("Fresh-process artifact inference was incomplete.")
    return status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--mode", choices=("all-safe",), required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.config.resolve() != EXPECTED_CONFIG.resolve():
        raise ModelArtifactValidationError("Artifact config path is not canonical.")
    if args.registry.resolve() != EXPECTED_REGISTRY.resolve():
        raise ModelArtifactValidationError("Artifact registry path is not canonical.")
    if args.report_dir.resolve() != EXPECTED_REPORT_DIR.resolve():
        raise ModelArtifactValidationError("Private report directory is not canonical.")
    registry = load_artifact_registry(args.registry, ROOT)
    validate_legacy_inventory_alignment(registry, ROOT / "configs/final_artifacts.yaml", ROOT)
    loaded = load_phase31_artifact_set(args.registry, ROOT)
    if loaded["task1_late"]["metadata"].get("positive_class_index") != 1:
        raise ModelArtifactValidationError("Task 1 positive-class mapping is invalid.")
    smoke = run_clean_process_load(ROOT, args.registry.resolve())
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": 32,
        "status": "SAFE_VALIDATION_PASS",
        "artifact_count": len(registry["artifacts"]),
        "checksums": "PASS",
        "feature_schemas": "PASS",
        "fresh_process_load": "PASS",
        "fresh_process_inference": smoke,
        "private_parity": "PENDING_HUMAN_LOCAL",
    }
    (args.report_dir / "safe_validation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("WAYLOOM - PHASE 32 SAFE ARTIFACT VALIDATION: PASS")
    print("ARTIFACT CHECKSUMS: PASS")
    print("FEATURE SCHEMAS: PASS")
    print("FRESH-PROCESS LOAD: PASS")
    print("FRESH-PROCESS SYNTHETIC INFERENCE: PASS")
    print("PRIVATE PARITY: PENDING HUMAN-LOCAL RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
