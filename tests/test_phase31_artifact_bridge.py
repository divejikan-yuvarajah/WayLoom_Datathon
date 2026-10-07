from __future__ import annotations

from pathlib import Path

import inspect
import yaml

from src.artifacts.final_inference import run_saved_artifact_inference_demo
from src.common.artifact_registry import load_phase31_artifact_set
from scripts.validate_model_artifacts import run_clean_process_load


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "models/artifact_registry.json"


def test_phase31_bridge_loads_every_final_task_without_notebook_state() -> None:
    loaded = load_phase31_artifact_set(REGISTRY, ROOT)
    assert loaded["task1_service"]["metadata"]["task"] == "task1_service"
    assert loaded["task1_late"]["metadata"]["task"] == "task1_late"
    assert loaded["task2a"]["total"].target == "total"
    assert loaded["task2a"]["chilled"].target == "chilled"


def test_phase31_bridge_is_package_relative_and_fresh_process_importable() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    assert "C:\\Users\\" not in text and "/home/" not in text
    run_clean_process_load(ROOT, REGISTRY)


def test_phase31_final_notebook_uses_secured_registry_loader() -> None:
    config = yaml.safe_load((ROOT / "configs/final_notebook.yaml").read_text(encoding="utf-8"))
    phase32 = config["phase32"]
    assert phase32["artifact_registry"] == "models/artifact_registry.json"
    assert "artifact_manifest" not in phase32
    source = inspect.getsource(run_saved_artifact_inference_demo)
    assert "load_phase31_artifact_set" in source
    assert "joblib.load" not in source
    assert "load_artifact_manifest" not in source


def test_private_parity_passes_exact_registry_bundles_to_inference() -> None:
    source = (ROOT / "scripts/run_model_artifact_parity.py").read_text(encoding="utf-8")
    assert "loaded = load_phase31_artifact_set" in source
    assert "loaded_artifacts=loaded" in source
    assert "artifact_manifest=" not in source
