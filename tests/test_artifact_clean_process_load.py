import json
from pathlib import Path
import shutil

import pytest

from scripts.validate_model_artifacts import ModelArtifactValidationError, run_clean_process_load


ROOT = Path(__file__).resolve().parents[1]


def test_all_final_artifacts_load_in_a_fresh_python_process() -> None:
    result = run_clean_process_load(ROOT, ROOT / "models/artifact_registry.json")
    assert result == {
        "registry": "PASS",
        "checksums": "PASS",
        "task1_service_inference": "PASS",
        "task1_late_inference": "PASS",
        "task2a_total_inference": "PASS",
        "task2a_chilled_inference": "PASS",
    }


def test_fresh_process_checksum_failure_stops_before_inference(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "models", tmp_path / "models")
    registry_path = tmp_path / "models/artifact_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    target = tmp_path / registry["artifacts"][0]["relative_path"]
    target.write_bytes(target.read_bytes() + b"corrupt")
    with pytest.raises(ModelArtifactValidationError, match="inference failed"):
        run_clean_process_load(tmp_path, registry_path, source_root=ROOT)


def test_clean_process_loader_source_has_no_training_call() -> None:
    source = (ROOT / "src/common/artifact_registry.py").read_text(encoding="utf-8")
    for forbidden in ("train_final_models(", "fit_frozen_component(", ".fit("):
        assert forbidden not in source
