from pathlib import Path

import nbformat
import yaml

from scripts.validate_final_notebook import validate_source_notebook


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "TeamName_FinalNotebook.ipynb"
CONFIG = ROOT / "configs" / "final_notebook.yaml"


def _text() -> str:
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    return "\n".join(cell.source for cell in notebook.cells)


def test_canonical_source_notebook_passes_static_contract():
    result = validate_source_notebook(NOTEBOOK, CONFIG)
    assert result["task_count"] == 23
    assert result["code_cell_count"] > 0
    assert result["phase32_status"] in {"AWAITING_PHASE32", "PASS"}


def test_notebook_uses_frozen_task1_and_task2a_choices():
    text = _text()
    for token in (
        "safe_core_plus_history",
        "catboost_regression_default",
        "catboost_classifier_default",
        "ensemble_cb_lgb_total_equal_v1",
        "ensemble_cb_lgb_chilled_equal_v1",
        "four deterministic rolling origins",
    ):
        assert token in text


def test_task_specific_calendar_representations_are_not_cross_wired():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    preprocessing = next(
        cell.source
        for cell in notebook.cells
        if "dt-395" in cell.get("metadata", {}).get("tags", []) and cell.cell_type == "code"
    )
    assert "calendar=calendar," in preprocessing
    assert "calendar=calendar_validated," not in preprocessing
    assert "calendar_validated," in preprocessing  # Task 2A canonical validated calendar


def test_task2b_is_summary_only_and_preserves_official_rule_boundary():
    text = _text()
    assert "does not rerun the optimizer" in text
    assert "No return leg" in text
    assert "Fresh <= 270" in text
    assert "Style+Tech <= 480" in text
    assert "feasibility only" in text


def test_phase32_handoff_has_a_strict_controlled_state():
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["phase32"]["status"] in {"AWAITING_PHASE32", "PASS"}
    assert config["phase32"]["artifact_registry"] == "models/artifact_registry.json"
    assert config["phase32"]["loader_callable"] == "run_saved_artifact_inference_demo"
    if config["phase32"]["status"] == "PASS":
        assert (ROOT / config["phase32"]["artifact_registry"]).is_file()
