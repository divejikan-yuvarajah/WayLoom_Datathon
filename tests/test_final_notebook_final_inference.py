from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "TeamName_FinalNotebook.ipynb"


def _source() -> str:
    return nbformat.read(NOTEBOOK, as_version=4).cells[-1].source


def test_final_cell_reloads_phase32_entrypoint_and_refuses_early_execution():
    source = _source()
    assert "importlib.import_module" in source
    assert 'phase32_config["loader_module"]' in source
    assert 'phase32_config["loader_callable"]' in source
    assert "PHASE32 SAVED ARTIFACT GATE: AWAITING_PHASE32" in source
    assert "artifact_registry.is_file()" in source


def test_final_cell_has_both_demos_and_parity_assertions():
    source = _source()
    for token in (
        "TASK 1 - INPUTS",
        "TASK 1 - PREDICTIONS",
        "TASK 2A - INPUTS",
        "TASK 2A - PREDICTIONS",
        "TASK 1 SAVED-MODEL PARITY: PASS",
        "TASK 2A SAVED-MODEL PARITY: PASS",
    ):
        assert token in source
    assert 'demo["saved_artifacts_loaded"] is not True' in source
    assert 'write_official_outputs=False' in source


def test_final_cell_does_not_train_or_write_official_outputs():
    source = _source().lower()
    for forbidden in (".fit(", "fit_predict", "to_csv(", "joblib.dump", "pickle.dump"):
        assert forbidden not in source
    assert "outputs/submission_task1.csv" not in source
    assert "outputs/submission_task2a.csv" not in source


def test_executor_records_complete_private_closure_evidence():
    source = (ROOT / "scripts" / "execute_final_notebook.py").read_text(encoding="utf-8")
    validator = (ROOT / "scripts" / "validate_final_notebook.py").read_text(encoding="utf-8")
    for filename in (
        "run_manifest.json",
        "execution_summary.json",
        "final_cell_only_summary.json",
        "final_inference_parity.json",
        "frozen_hash_audit.json",
    ):
        assert filename in source or filename in validator
    assert "before != after" in source
    assert "record.get(\"before\") != record.get(\"after\")" in validator
