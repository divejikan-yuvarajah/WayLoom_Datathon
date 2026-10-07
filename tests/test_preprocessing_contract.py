from pathlib import Path

import yaml

from scripts.build_preprocessing_manifest import OBJECTIVE_LEVELS, build_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs" / "preprocessing_manifest.yaml"
DOCUMENT_PATH = ROOT / "docs" / "preprocessing.md"


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_manifest_matches_final_tracked_configs():
    manifest = _load(MANIFEST_PATH)
    assert manifest == build_manifest()
    assert manifest["outputs"]["task1"] == ["delivery_id", "pred_service_min", "pred_late_prob"]
    assert manifest["outputs"]["task2a"] == ["row_id", "pred_total_volume_m3", "pred_chilled_volume_m3"]
    assert manifest["outputs"]["task2b"] == ["scenario", "order_ref", "outlet_id", "decision", "vehicle_id", "trip_id"]
    assert manifest["task1_models"]["service_family"] == "catboost"
    assert manifest["task1_models"]["lateness_family"] == "catboost"
    assert manifest["task1_models"]["calibration"] == "raw"
    assert manifest["task2a_models"]["state"] == "FROZEN"
    assert manifest["task2b_validation"]["solver"] == "OR-Tools CP-SAT"
    assert manifest["task2b_priority"]["objective_levels"] == OBJECTIVE_LEVELS


def test_document_preserves_leakage_and_task2b_nonrule_boundaries():
    text = DOCUMENT_PATH.read_text(encoding="utf-8").lower()
    assert "prohibited as direct current-row predictors" in text
    for field in ("actual_depart_time", "actual_travel_duration_min", "arrival_time", "leave_outlet_time"):
        assert field in text
    assert "task 1 lateness predictions and task 2a forecasts are also not imported as hard rules" in text
    assert "fuel quota and delivery window are not task 2b hard constraints" in text
    assert "feasibility only; it does not prove optimality" in text


def test_document_matches_frozen_task2a_and_task2b_contracts():
    manifest = _load(MANIFEST_PATH)
    text = DOCUMENT_PATH.read_text(encoding="utf-8")
    assert manifest["task2a_history"]["retained_statuses"] == ["attempted", "deferred", "not_run"]
    assert manifest["task2a_features"]["lags"] == [1, 2, 4, 13, 52]
    assert manifest["task2a_features"]["rolling_windows"] == [4, 8, 13]
    assert manifest["task2b_trip_time"]["include_return_leg"] is False
    assert manifest["task2b_trip_time"]["fresh_budget_min"] == 270
    assert manifest["task2b_trip_time"]["style_tech_budget_min"] == 480
    assert len(manifest["task2b_hard_rules"]) == 7
    assert "not organizer priority" in text
