"""Synthetic fixed-fold CatBoost and LightGBM candidate checks."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import src.task2a.advanced_models as advanced_models
from src.task2a.advanced_models import (AdvancedModelError, load_advanced_config,
    run_advanced_backtests, validate_advanced_config, verify_frozen_phase14_plan)
from src.task2a.advanced_models import _fit_fold
from src.task2a.baseline_evaluation import phase14_plan_metadata
from src.task2a.baseline_evaluation import (build_baseline_run_manifest,
    evaluate_baseline_predictions, generate_backtest_baseline_predictions, rank_reference_baselines)
from src.task2a.baselines import load_baseline_config
from src.task2a.features import load_feature_config
from src.task2a.model_preprocessing import feature_profile, select_predictors
from src.task2a.multihorizon import build_direct_multihorizon_table
from src.task2a.validation import build_rolling_origin_plan, load_validation_config
from scripts.run_task2a_advanced_models import private_output_dir, run_experiment
from scripts.freeze_task2a_model_config import build_final_config
from tests.test_task2a_validation import _calendar, _panel


ROOT = Path(__file__).resolve().parents[1]


def _synthetic_plan() -> tuple[pd.DataFrame, dict, dict]:
    panel = _panel(76)
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    validation = load_validation_config(ROOT / "configs/task2a_validation.yaml")
    validation["backtesting"]["n_backtests"] = 2
    validation["backtesting"]["minimum_training_weeks"] = 20
    return panel, build_rolling_origin_plan(panel, table, None, validation), validation


def _small_config() -> dict:
    config = load_advanced_config(ROOT / "configs/task2a_advanced_models.yaml")
    for family in ("catboost", "lightgbm"):
        for target in ("total", "chilled"):
            settings = config[family][target]
            settings["iterations" if family == "catboost" else "n_estimators"] = 25
            settings["early_stopping_rounds"] = 5
    return config


def test_models_fit_both_targets_on_exact_frozen_folds(tmp_path: Path) -> None:
    _, plan, _ = _synthetic_plan()
    path = tmp_path / "validation_plan.json"
    stored = phase14_plan_metadata(plan)
    for record, split in zip(stored["backtests"], plan["splits"], strict=True):
        record["train_indices"] = split.train_indices.tolist()
        record["validation_indices"] = split.validation_indices.tolist()
    path.write_text(json.dumps(stored), encoding="utf-8")
    signature = verify_frozen_phase14_plan(path, plan)
    predictions, folds, profile = run_advanced_backtests(plan, None, _small_config())
    assert set(predictions.candidate_id) == {"catboost_total_v1", "catboost_chilled_v1",
                                              "lightgbm_total_v1", "lightgbm_chilled_v1"}
    assert len(folds) == 8 and folds.best_iteration.ge(1).all()
    assert folds.configured_max_iterations.eq(25).all()
    assert folds.trained_iterations.le(25).all()
    assert folds.best_validation_metric.map(np.isfinite).all()
    assert predictions.phase14_backtest_signature.eq(signature).all()
    assert np.isfinite(predictions.y_pred).all()
    assert predictions.loc[predictions.target_name.eq("chilled"), "brand"].eq("Fresh").all()
    assert folds.loc[folds.target_name.eq("chilled"), "training_row_count"].lt(
        folds.loc[folds.target_name.eq("total"), "training_row_count"].to_numpy()).all()
    assert profile["columns"] == feature_profile()["columns"]


def test_signature_and_exact_indices_mismatch_are_rejected(tmp_path: Path) -> None:
    _, plan, _ = _synthetic_plan()
    path = tmp_path / "validation_plan.json"
    stored = phase14_plan_metadata(plan)
    stored["backtests"][0]["train_indices"] = [999]
    path.write_text(json.dumps(stored), encoding="utf-8")
    with pytest.raises(AdvancedModelError, match="training indices"):
        verify_frozen_phase14_plan(path, plan)
    stored["backtests"][0]["origin_week_start_date"] = "2030-01-01"
    path.write_text(json.dumps(stored), encoding="utf-8")
    with pytest.raises(ValueError, match="signature mismatch"):
        verify_frozen_phase14_plan(path, plan)


def test_local_models_are_deterministic_with_frozen_seed() -> None:
    _, plan, _ = _synthetic_plan()
    split = plan["splits"][0]
    train = plan["table"].iloc[split.train_indices]
    valid = plan["table"].iloc[split.validation_indices]
    profile = feature_profile()
    config = _small_config()
    for family in ("catboost", "lightgbm"):
        first, first_metadata = _fit_fold(family, "total", train, valid, profile, config[family]["total"])
        second, second_metadata = _fit_fold(family, "total", train, valid, profile, config[family]["total"])
        np.testing.assert_allclose(first, second, rtol=1e-10, atol=1e-10)
        assert first_metadata["best_iteration"] == second_metadata["best_iteration"]


def test_catboost_early_stop_uses_evaluated_not_retained_iterations(monkeypatch: pytest.MonkeyPatch) -> None:
    class BestModelTruncatedCatBoost:
        tree_count_ = 1

        def __init__(self, **params: object) -> None:
            pass

        def fit(self, *args: object, **kwargs: object) -> None:
            pass

        def predict(self, validation: pd.DataFrame) -> np.ndarray:
            return np.zeros(len(validation))

        def get_best_iteration(self) -> int:
            return 0

        def get_best_score(self) -> dict:
            return {"validation": {"MAE": 1.0}}

        def get_evals_result(self) -> dict:
            return {"validation": {"MAE": [1.0] * 25}}

    monkeypatch.setattr(advanced_models, "CatBoostRegressor", BestModelTruncatedCatBoost)
    _, plan, _ = _synthetic_plan()
    split = plan["splits"][0]
    settings = _small_config()["catboost"]["total"]
    settings["early_stopping_rounds"] = 100
    _, metadata = _fit_fold("catboost", "total", plan["table"].iloc[split.train_indices],
                            plan["table"].iloc[split.validation_indices], feature_profile(), settings)
    assert metadata["trained_iterations"] == 25
    assert metadata["configured_max_iterations"] == 25
    assert metadata["stopped_early"] is False


def test_future_and_validation_y_mutation_cannot_enter_validation_x() -> None:
    panel, plan, _ = _synthetic_plan()
    split = plan["splits"][0]
    profile = feature_profile()
    before = select_predictors(plan["table"].iloc[split.validation_indices], profile)
    changed = plan["table"].copy()
    changed.loc[split.validation_indices, "target_total_volume_m3"] = 999999.0
    changed.loc[split.validation_indices, "target_chilled_volume_m3"] = 999999.0
    after = select_predictors(changed.iloc[split.validation_indices], profile)
    pd.testing.assert_frame_equal(before, after)
    demand = [name for name in profile["columns"] if name.startswith(("total_", "chilled_"))]
    for _, block in before.groupby(["depot", "brand"], sort=False):
        assert all(block[name].nunique(dropna=False) == 1 for name in demand)
    assert plan["leakage_audit"]["training_target_availability_pass"]


def test_intermediate_future_demand_mutation_cannot_change_horizon_ten_features() -> None:
    panel, plan, _ = _synthetic_plan()
    split = plan["splits"][0]
    profile = feature_profile()
    original = plan["table"].iloc[split.validation_indices]
    original = original.loc[original.horizon_weeks.eq(10)].sort_values(["depot", "brand"])
    changed = panel.copy()
    intermediate = changed.week_start_date.gt(split.origin_week_start_date) & changed.week_start_date.lt(
        split.origin_week_start_date + pd.Timedelta(weeks=10))
    changed.loc[intermediate, "total_volume_m3"] += 1000.0
    changed.loc[intermediate & changed.brand.eq("Fresh"), "chilled_volume_m3"] += 500.0
    rebuilt = build_direct_multihorizon_table(changed, _calendar(changed))
    rebuilt = rebuilt.loc[rebuilt.origin_week_start_date.eq(split.origin_week_start_date) &
                          rebuilt.horizon_weeks.eq(10)].sort_values(["depot", "brand"])
    pd.testing.assert_frame_equal(select_predictors(original, profile).reset_index(drop=True),
                                  select_predictors(rebuilt, profile).reset_index(drop=True))


def test_frozen_config_rejects_disabled_lightgbm_and_tuned_weights() -> None:
    config = _small_config()
    config["lightgbm"]["enabled"] = False
    with pytest.raises(AdvancedModelError, match="enabled"):
        validate_advanced_config(config)
    config = _small_config()
    config["ensembles"]["advanced_reference_equal_weight"]["weight_advanced"] = 0.6
    with pytest.raises(AdvancedModelError, match="50/50"):
        validate_advanced_config(config)


def test_phase16_output_is_restricted_to_private_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Phase 16 outputs"):
        private_output_dir(tmp_path)


def test_complete_local_experiment_with_synthetic_frozen_references(tmp_path: Path) -> None:
    panel, plan, validation = _synthetic_plan()
    baseline_config = load_baseline_config(ROOT / "configs/task2a_baselines.yaml")
    baseline_predictions = generate_backtest_baseline_predictions(panel, plan, baseline_config)
    _, references = rank_reference_baselines(evaluate_baseline_predictions(baseline_predictions, plan))
    baseline_dir = tmp_path / "phase15"
    baseline_dir.mkdir()
    baseline_predictions.to_csv(baseline_dir / "backtest_predictions.csv", index=False)
    manifest = build_baseline_run_manifest(baseline_config, validation, plan)
    (baseline_dir / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (baseline_dir / "baseline_reference.json").write_text(json.dumps({
        "phase": 15, "best_total_baseline": references["total"],
        "best_chilled_baseline": references["chilled"],
        "baseline_config_hash": manifest["baseline_config_hash"]}), encoding="utf-8")
    phase14 = tmp_path / "phase14.json"
    stored = phase14_plan_metadata(plan)
    for record, split in zip(stored["backtests"], plan["splits"], strict=True):
        record["train_indices"] = split.train_indices.tolist()
        record["validation_indices"] = split.validation_indices.tolist()
    phase14.write_text(json.dumps(stored), encoding="utf-8")
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    features = load_feature_config(ROOT / "configs/task2a_features.yaml")
    result = run_experiment(panel, table, features, validation, _small_config(), baseline_dir,
                            phase14, baseline_config)
    assert result["selection"]["selection_complete"] is True
    assert set(result["selection"]) >= {"total", "chilled_fresh", "phase14_backtest_signature"}
    assert len(result["summaries"]) == 10
    assert result["summaries"].groupby("target_name").selection_status.apply(
        lambda status: status.eq("SELECTED").sum()).eq(1).all()
    assert result["chilled_gt_total_count"] >= 0
    for candidate_id, tables in result["diagnostics"].items():
        target = "chilled" if "chilled" in candidate_id else "total"
        assert tables["per_series"].target.eq(target).all()
        assert tables["per_horizon"].target.eq(target).all()
        assert tables["backtests"].target.eq(target).all()
        if target == "chilled":
            assert tables["per_series"].brand.eq("Fresh").all()
            summary = result["summaries"].set_index("candidate_id").loc[candidate_id]
            assert tables["backtests"].chilled_gt_total_count.sum() == summary.chilled_gt_total_count
    frozen = build_final_config(result["selection"], _small_config(), features, validation,
        feature_path="configs/task2a_features.yaml", validation_path="configs/task2a_validation.yaml")
    assert frozen["state"] == "FROZEN"
