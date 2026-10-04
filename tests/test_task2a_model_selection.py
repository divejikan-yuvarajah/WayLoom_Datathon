"""Synthetic Phase 16 completeness, rejection, champion, and freeze tests."""

from __future__ import annotations

from copy import deepcopy
from argparse import Namespace
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.freeze_task2a_model_config import build_final_config
from scripts import freeze_task2a_model_config as freeze_script
from src.task2a.advanced_models import load_advanced_config
from src.task2a.baseline_evaluation import phase14_backtest_signature
from src.task2a.features import load_feature_config
from src.task2a.model_preprocessing import feature_profile
from src.task2a.model_selection import (ModelSelectionError, evaluate_candidate,
    expected_validation_rows, relative_improvement_pct, select_champion,
    validate_candidate_predictions, validate_final_model_config)
from src.task2a.validation import load_validation_config
from tests.test_task2a_advanced_models import _synthetic_plan


ROOT = Path(__file__).resolve().parents[1]


def _candidate(plan: dict, target: str, candidate_id: str, value: float = 5.0) -> pd.DataFrame:
    rows = expected_validation_rows(plan, target)
    rows["target_name"] = target
    rows["candidate_id"] = candidate_id
    rows["y_pred"] = value
    rows["phase14_backtest_signature"] = phase14_backtest_signature(plan)
    return rows


def test_exact_coverage_labels_and_signature_required() -> None:
    _, plan, _ = _synthetic_plan()
    rows = _candidate(plan, "total", "catboost_total_v1")
    counterpart = _candidate(plan, "chilled", "catboost_chilled_v1")
    assert len(validate_candidate_predictions(rows, plan, "total", "catboost_total_v1")) == len(rows)
    result = evaluate_candidate(pd.concat([rows, counterpart]), plan, "total", "catboost_total_v1",
                                "catboost_chilled_v1")
    assert result["backtest_count"] == 2 and len(result["per_horizon"]) == 10
    assert result["per_series"].target.eq("total").all()
    with pytest.raises(ModelSelectionError, match="missing"):
        evaluate_candidate(rows, plan, "total", "catboost_total_v1", "catboost_chilled_v1")
    with pytest.raises(ModelSelectionError, match="missing"):
        validate_candidate_predictions(rows.iloc[1:], plan, "total", "catboost_total_v1")
    changed = rows.copy()
    changed.loc[0, "y_true"] += 1
    with pytest.raises(ModelSelectionError, match="labels"):
        validate_candidate_predictions(changed, plan, "total", "catboost_total_v1")
    changed = rows.copy()
    changed.loc[0, "phase14_backtest_signature"] = "wrong"
    with pytest.raises(ModelSelectionError, match="signature"):
        validate_candidate_predictions(changed, plan, "total", "catboost_total_v1")
    changed = rows.copy()
    changed.loc[0, "y_pred"] = np.inf
    with pytest.raises(ModelSelectionError, match="NaN or infinite"):
        validate_candidate_predictions(changed, plan, "total", "catboost_total_v1")


def test_chilled_diagnostics_compare_real_raw_total_predictions() -> None:
    _, plan, _ = _synthetic_plan()
    total = _candidate(plan, "total", "catboost_total_v1", value=-1.0)
    chilled = _candidate(plan, "chilled", "catboost_chilled_v1", value=0.0)
    result = evaluate_candidate(pd.concat([total, chilled], ignore_index=True), plan, "chilled",
                                "catboost_chilled_v1", "catboost_total_v1")
    assert result["chilled_gt_total_count"] == len(chilled)
    assert result["per_series"].target.eq("chilled").all()
    assert result["per_series"].chilled_gt_total_count.sum() == len(chilled)
    assert result["per_horizon"].chilled_gt_total_count.sum() == len(chilled)
    assert result["backtests"].chilled_gt_total_count.sum() == len(chilled)


def _summaries(maes: list[float]) -> list[dict]:
    families = ["baseline", "catboost", "lightgbm", "catboost_lightgbm_ensemble",
                "advanced_reference_ensemble"]
    ids = ["total_last_week", "catboost_total_v1", "lightgbm_total_v1",
           "ensemble_cb_lgb_total_equal_v1", "ensemble_advanced_baseline_total_equal_v1"]
    return [{"candidate_id": name, "family": family, "overall_mae": mae,
             "overall_rmse": mae + 1, "p90_absolute_error": mae + 2,
             "std_backtest_mae": 1.0} for name, family, mae in zip(ids, families, maes, strict=True)]


def test_advanced_gate_baseline_zero_and_exact_boundary() -> None:
    assert relative_improvement_pct(100, 99.5) == pytest.approx(0.5)
    assert relative_improvement_pct(0, 0) == 0
    champion, ranked = select_champion(_summaries([100, 99.5, 101, 102, 103]), "total_last_week")
    assert champion["candidate_id"] == "total_last_week"
    assert next(row for row in ranked if row["candidate_id"] == "catboost_total_v1")["selection_status"] == "REJECTED_NO_IMPROVEMENT"
    champion, _ = select_champion(_summaries([100, 98, 99, 97, 99]), "total_last_week")
    assert champion["candidate_id"] == "ensemble_cb_lgb_total_equal_v1"
    champion, _ = select_champion(_summaries([100, 99, 97, 98, 99]), "total_last_week")
    assert champion["candidate_id"] == "lightgbm_total_v1"
    champion, _ = select_champion(_summaries([100, 97, 99, 98, 99]), "total_last_week")
    assert champion["candidate_id"] == "catboost_total_v1"
    champion, _ = select_champion(_summaries([0, 1, 1, 1, 1]), "total_last_week")
    assert champion["candidate_id"] == "total_last_week"


def test_within_tolerance_uses_rmse_then_p90_then_stability() -> None:
    rows = _summaries([100, 90.0, 90.2, 95, 96])
    rows[1]["overall_rmse"] = 93
    rows[2]["overall_rmse"] = 92
    assert select_champion(rows, "total_last_week")[0]["candidate_id"] == "lightgbm_total_v1"
    rows[1]["overall_rmse"] = 92
    rows[1]["p90_absolute_error"] = 94
    rows[2]["p90_absolute_error"] = 93
    assert select_champion(rows, "total_last_week")[0]["candidate_id"] == "lightgbm_total_v1"
    rows[1]["p90_absolute_error"] = 93
    rows[1]["std_backtest_mae"] = 0.5
    assert select_champion(rows, "total_last_week")[0]["candidate_id"] == "catboost_total_v1"


def _selection(approach: str = "baseline") -> dict:
    profile = feature_profile(load_feature_config(ROOT / "configs/task2a_features.yaml"))
    def winner(target: str) -> dict:
        if approach == "baseline":
            return {"approach_type": "baseline", "candidate_id": f"{target}_last_week", "family": "last_week",
                    "parameters": {"enabled": True}, "final_iteration_policy": "NOT_APPLICABLE"}
        if approach == "model":
            return {"approach_type": "model", "candidate_id": f"catboost_{target}_v1", "family": "catboost",
                    "parameters": {"iterations": 2000, "random_seed": 42},
                    "final_iteration_policy": {"method": "median_best_iteration", "value": 37}}
        part = {"approach_type": "model", "candidate_id": f"catboost_{target}_v1", "family": "catboost",
                "parameters": {"iterations": 2000},
                "final_iteration_policy": {"method": "median_best_iteration", "value": 37}}
        return {"approach_type": "ensemble", "candidate_id": f"ensemble_{target}_v1",
                "family": "advanced_reference_ensemble", "component_candidates": [part, {
                    "approach_type": "baseline", "candidate_id": f"{target}_last_week", "parameters": {"enabled": True}}],
                "component_weights": [0.5, 0.5], "parameters": {"weight_left": 0.5, "weight_right": 0.5}}
    return {"total": winner("total"), "chilled_fresh": winner("chilled"),
            "phase14_backtest_signature": "test-signature", "feature_profile_id": profile["profile_id"],
            "feature_registry_hash": profile["registry_hash"], "selection_complete": True,
            "style_chilled_zero": True, "tech_chilled_zero": True}


@pytest.mark.parametrize("approach", ["baseline", "model", "ensemble"])
def test_final_config_freezes_each_champion_type_without_scores(approach: str) -> None:
    config = build_final_config(_selection(approach),
        load_advanced_config(ROOT / "configs/task2a_advanced_models.yaml"),
        load_feature_config(ROOT / "configs/task2a_features.yaml"),
        load_validation_config(ROOT / "configs/task2a_validation.yaml"),
        feature_path="configs/task2a_features.yaml", validation_path="configs/task2a_validation.yaml")
    validate_final_model_config(config)
    assert config["state"] == "FROZEN" and "overall_mae" not in str(config)
    broken = deepcopy(config)
    broken["state"] = "PENDING"
    with pytest.raises(ModelSelectionError, match="FROZEN"):
        validate_final_model_config(broken)
    broken = deepcopy(config)
    broken["chilled_fresh"] = None
    with pytest.raises(ModelSelectionError, match="champion"):
        validate_final_model_config(broken)
    broken = deepcopy(config)
    broken["structural_output_rules"]["style_chilled_zero"] = False
    with pytest.raises(ModelSelectionError, match="zero"):
        validate_final_model_config(broken)
    if approach == "ensemble":
        broken = deepcopy(config)
        broken["total"]["component_weights"] = [0.6, 0.4]
        with pytest.raises(ModelSelectionError, match="50/50"):
            validate_final_model_config(broken)
    if approach == "model":
        broken = deepcopy(config)
        broken["total"]["final_iteration_policy"] = {}
        with pytest.raises(ModelSelectionError, match="iteration"):
            validate_final_model_config(broken)


def test_freeze_command_explains_missing_local_run_without_changing_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path
    output = root / "configs/task2a_final_models.yaml"
    output.parent.mkdir(parents=True)
    output.write_text("version: 1\nstate: PENDING_LOCAL_PHASE16_RUN\n", encoding="utf-8")
    selection = root / "reports/private/phase16_task2a_advanced/selection_decisions.json"
    monkeypatch.setattr(freeze_script, "PROJECT_ROOT", root)
    monkeypatch.setattr(freeze_script, "parse_args", lambda: Namespace(output=output, selection=selection))
    assert freeze_script.main() == 2
    assert "selection_decisions.json" in capsys.readouterr().err
    assert "PENDING_LOCAL_PHASE16_RUN" in output.read_text(encoding="utf-8")


@pytest.mark.parametrize(("existing_approach", "new_approach", "expected_code"), [
    ("baseline", "baseline", 0), ("baseline", "model", 2)])
def test_freeze_rerun_preserves_existing_frozen_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    existing_approach: str, new_approach: str, expected_code: int,
) -> None:
    output = tmp_path / "configs/task2a_final_models.yaml"
    output.parent.mkdir(parents=True)
    selection_path = tmp_path / "reports/private/phase16_task2a_advanced/selection_decisions.json"
    selection_path.parent.mkdir(parents=True)
    plan_path = tmp_path / "phase14_plan.json"
    plan_path.write_text("{}", encoding="utf-8")
    selection = _selection(new_approach)
    selection_path.write_text(json.dumps(selection), encoding="utf-8")
    (selection_path.parent / "run_manifest.json").write_text(json.dumps({
        "phase14_backtest_signature": "test-signature", "phase15_references_verified": True,
        "forbidden_feature_count": 0, "feature_registry_hash": selection["feature_registry_hash"]}),
        encoding="utf-8")
    advanced = load_advanced_config(ROOT / "configs/task2a_advanced_models.yaml")
    features = load_feature_config(ROOT / "configs/task2a_features.yaml")
    validation = load_validation_config(ROOT / "configs/task2a_validation.yaml")
    frozen = build_final_config(_selection(existing_approach), advanced, features, validation,
        feature_path="configs/task2a_features.yaml", validation_path="configs/task2a_validation.yaml")
    output.write_bytes(yaml.safe_dump(frozen, sort_keys=False).encode("utf-8"))
    original = output.read_bytes()
    monkeypatch.setattr(freeze_script, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(freeze_script, "parse_args", lambda: Namespace(
        output=output, selection=selection_path, phase14_plan=plan_path,
        advanced_config=ROOT / "configs/task2a_advanced_models.yaml",
        feature_config=ROOT / "configs/task2a_features.yaml",
        validation_config=ROOT / "configs/task2a_validation.yaml"))
    monkeypatch.setattr(freeze_script, "phase14_backtest_signature_from_metadata", lambda _: "test-signature")
    assert freeze_script.main() == expected_code
    assert output.read_bytes() == original
    report = capsys.readouterr()
    if expected_code == 0:
        assert "FROZEN (UNCHANGED)" in report.out
    else:
        assert "refusing to replace" in report.err
