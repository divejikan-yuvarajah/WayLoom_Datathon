from pathlib import Path

import yaml

from scripts.build_architecture_manifest import EXPECTED_OBJECTIVES, build_manifest


ROOT = Path(__file__).resolve().parents[1]


def _tracked_manifest():
    return yaml.safe_load((ROOT / "docs/architecture/architecture_manifest.yaml").read_text(encoding="utf-8"))


def test_manifest_resolves_frozen_model_and_output_contracts():
    manifest = _tracked_manifest()
    expected = build_manifest()
    assert manifest["task1"] == expected["task1"]
    assert manifest["task1"]["service_model_family"] == "catboost"
    assert manifest["task1"]["late_model_family"] == "catboost"
    assert manifest["task1"]["late_calibration"] == "raw"
    assert manifest["task1"]["service_postprocessing"] == "fail_on_negative_prediction"
    assert manifest["task1"]["output_columns"] == ["delivery_id", "pred_service_min", "pred_late_prob"]
    assert manifest["task2a"] == expected["task2a"]
    assert manifest["task2a"]["feature_strategy"] == "direct_global_table"
    assert manifest["task2a"]["total_model_family"] == "catboost_lightgbm_ensemble"
    assert manifest["task2a"]["chilled_model_family_or_strategy"] == "catboost_lightgbm_ensemble"
    assert manifest["task2a"]["forecast_horizon_weeks"] == 10
    assert manifest["task2a"]["output_columns"] == ["row_id", "pred_total_volume_m3", "pred_chilled_volume_m3"]


def test_manifest_resolves_solver_policy_and_deployment_contracts():
    manifest = _tracked_manifest()
    assert manifest["task2b"]["solver"] == "OR-Tools CP-SAT"
    assert manifest["task2b"]["max_trips_per_vehicle"] == 2
    assert manifest["task2b"]["fresh_minutes_limit"] == 270
    assert manifest["task2b"]["style_tech_minutes_limit"] == 480
    assert manifest["task2b"]["include_return_leg"] is False
    assert manifest["task2b"]["objective_levels"] == [
        f"{direction.upper()} {name}" for name, direction in EXPECTED_OBJECTIVES
    ]
    assert manifest["deployment"]["status"] == "proposed"
    assert manifest["deployment"]["hackathon_integration_required"] is False
    assert manifest["deployment"]["external_proprietary_modelling_api"] is False


def test_manifest_contains_safe_metadata_only():
    text = (ROOT / "docs/architecture/architecture_manifest.yaml").read_text(encoding="utf-8")
    assert "C:\\Users\\" not in text
    assert "/home/" not in text
    assert "reports/private" not in text
    assert _tracked_manifest()["contains_private_data"] is False
