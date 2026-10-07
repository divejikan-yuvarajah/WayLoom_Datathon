from pathlib import Path

import yaml

from scripts.build_preprocessing_manifest import (
    OBJECTIVE_LEVELS,
    TASK1_OUTPUT_COLUMNS,
    TASK2A_OUTPUT_COLUMNS,
    TASK2B_OUTPUT_COLUMNS,
    TASK_IDS,
    build_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "preprocessing_manifest.yaml"


def _manifest():
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_is_config_derived_and_has_all_required_sections():
    actual = _manifest()
    assert actual == build_manifest()
    required = {
        "official_requirement", "inputs", "joins", "task1_labels", "cleaning",
        "task1_features", "task1_leakage", "task1_validation", "task1_models",
        "task2a_history", "task2a_features", "task2a_validation", "task2a_models",
        "task2a_postprocessing", "task2b_inputs", "task2b_compatibility",
        "task2b_trip_time", "task2b_hard_rules", "task2b_priority",
        "task2b_validation", "outputs", "privacy", "task_completeness",
    }
    assert required.issubset(actual)


def test_manifest_maps_all_ten_phase30_tasks():
    mapping = _manifest()["task_completeness"]
    assert sorted(mapping) == TASK_IDS
    assert all(mapping[task] for task in TASK_IDS)


def test_manifest_resolves_models_policy_and_outputs_exactly():
    manifest = _manifest()
    assert manifest["task1_models"] == {
        "service_family": "catboost",
        "service_config_id": "catboost_regression_default",
        "service_postprocessing": "fail_on_negative_prediction",
        "lateness_family": "catboost",
        "lateness_config_id": "catboost_classifier_default",
        "calibration": "raw",
        "calibration_protocol": "chronological_oof",
    }
    assert manifest["task2a_models"]["final_strategy"] == "direct_global_table_separate_target_ensembles"
    assert manifest["task2a_models"]["total_family"] == "catboost_lightgbm_ensemble"
    assert manifest["task2a_models"]["chilled_family"] == "catboost_lightgbm_ensemble"
    assert manifest["task2b_priority"]["objective_levels"] == OBJECTIVE_LEVELS
    assert manifest["outputs"] == {
        "task1": TASK1_OUTPUT_COLUMNS,
        "task2a": TASK2A_OUTPUT_COLUMNS,
        "task2b": TASK2B_OUTPUT_COLUMNS,
    }


def test_manifest_contains_safe_metadata_only():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "C:\\Users\\" not in text
    assert "/home/" not in text
    assert "reports/private" not in text
    assert "TBD" not in text and "TODO" not in text and "FINAL_MODEL_HERE" not in text
    assert _manifest()["privacy"] == {
        "contains_private_rows": False,
        "contains_real_identifiers": False,
        "contains_absolute_user_paths": False,
        "reads_private_data": False,
    }
