"""Synthetic-only tests for Phase 15 frozen-plan reuse and comparison."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pandas as pd
import pytest

from scripts import run_task2a_baselines as baseline_script
from src.task2a.baseline_evaluation import (BaselineEvaluationError, evaluate_baseline_predictions,
    generate_backtest_baseline_predictions, load_and_verify_phase14_plan, phase14_backtest_signature, phase14_plan_metadata, rank_reference_baselines,
    validate_baseline_predictions)
from src.task2a.baselines import load_baseline_config
from src.task2a.multihorizon import build_direct_multihorizon_table
from src.task2a.validation import build_rolling_origin_plan, load_validation_config
from tests.test_task2a_validation import _calendar, _panel


ROOT = Path(__file__).resolve().parents[1]


def _inputs() -> tuple[pd.DataFrame, dict]:
    panel = _panel(76)
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    config = load_validation_config(ROOT / "configs/task2a_validation.yaml")
    config["backtesting"]["n_backtests"] = 2
    config["backtesting"]["minimum_training_weeks"] = 20
    return panel, build_rolling_origin_plan(panel, table, None, config)


def test_predictions_reuse_exact_phase14_rows_and_structural_chilled_zeros() -> None:
    panel, plan = _inputs()
    predicted = generate_backtest_baseline_predictions(panel, plan, load_baseline_config(ROOT / "configs/task2a_baselines.yaml"))
    validate_baseline_predictions(predicted, plan)
    assert predicted.phase14_backtest_signature.nunique() == 1 == len({phase14_backtest_signature(plan)})
    assert len(predicted) == len(plan["splits"]) * len(plan["required_series"]) * 10 * 8
    zeros = predicted.loc[predicted.target_name.eq("chilled") & predicted.brand.isin(["Style", "Tech"])]
    assert zeros.y_pred.eq(0).all()


def test_persisted_phase14_signature_must_match_exactly(tmp_path: Path) -> None:
    _, plan = _inputs()
    stored = phase14_plan_metadata(plan)
    path = tmp_path / "validation_plan.json"
    path.write_text(__import__("json").dumps(stored), encoding="utf-8")
    assert load_and_verify_phase14_plan(path, plan) == phase14_backtest_signature(plan)
    stored["backtests"][0]["validation_target_end_date"] = "2030-01-01"
    path.write_text(__import__("json").dumps(stored), encoding="utf-8")
    with pytest.raises(BaselineEvaluationError, match="signature mismatch"):
        load_and_verify_phase14_plan(path, plan)


def test_future_and_validation_target_mutation_cannot_change_predictions() -> None:
    panel, plan = _inputs()
    config = load_baseline_config(ROOT / "configs/task2a_baselines.yaml")
    before = generate_backtest_baseline_predictions(panel, plan, config)
    origin = plan["splits"][-1].origin_week_start_date
    changed = panel.copy()
    future = changed.week_start_date.gt(origin)
    changed.loc[future, "total_volume_m3"] = 7777.0
    changed.loc[future & changed.brand.eq("Fresh"), "chilled_volume_m3"] = 3333.0
    table = build_direct_multihorizon_table(changed, _calendar(changed))
    mutated_plan = build_rolling_origin_plan(changed, table, None, {**load_validation_config(ROOT / "configs/task2a_validation.yaml"), "backtesting": {**load_validation_config(ROOT / "configs/task2a_validation.yaml")["backtesting"], "n_backtests": 2, "minimum_training_weeks": 20}})
    after = generate_backtest_baseline_predictions(changed, mutated_plan, config)
    keys = ["target_name", "baseline_name", "backtest_id", "depot", "brand", "horizon_weeks"]
    pd.testing.assert_frame_equal(before.sort_values(keys)[keys + ["y_pred"]].reset_index(drop=True), after.sort_values(keys)[keys + ["y_pred"]].reset_index(drop=True))


def test_evaluator_reuses_phase14_metrics_and_rejects_missing_candidate_rows() -> None:
    panel, plan = _inputs()
    predicted = generate_backtest_baseline_predictions(panel, plan, load_baseline_config(ROOT / "configs/task2a_baselines.yaml"))
    evaluated = evaluate_baseline_predictions(predicted, plan)
    assert len(evaluated) == 8
    summary, references = rank_reference_baselines(evaluated)
    assert set(summary.target_name) == {"total", "chilled"} and set(references) == {"total", "chilled"}
    with pytest.raises(BaselineEvaluationError, match="frozen Phase 14 validation row"):
        evaluate_baseline_predictions(predicted.iloc[1:], plan)


def test_rank_tie_breaks_through_simplicity_deterministically() -> None:
    def result(target: str, name: str, mae: float = 1.0, rmse: float = 2.0, p90: float = 3.0,
               backtests: list[float] | None = None) -> dict:
        return {"target_name": target, "baseline_name": name,
                "overall": {"mae": mae, "rmse": rmse, "wape": 1.0, "mean_bias_m3": 0.0,
                            "p90_absolute_error": p90, "negative_prediction_count": 0, "chilled_gt_total_count": 0},
                "backtests": pd.DataFrame({"mae": backtests or [1.0, 1.0]}), "seasonal_fallback_count": 0,
                "unavailable_prediction_count": 0}
    def candidates(**overrides: dict) -> dict:
        values = {}
        for prefix, target in (("total", "total"), ("chilled", "chilled")):
            for family in ("last_week", "recent_mean_4", "same_week_last_year", "seasonal_recent_weighted"):
                values[f"{prefix}:{family}"] = result(target, f"{prefix}_{family}", **overrides.get(family, {}))
        return values
    assert rank_reference_baselines(candidates())[1] == {"chilled": "chilled_last_week", "total": "total_last_week"}
    assert rank_reference_baselines(candidates(recent_mean_4={"rmse": 1.0}))[1]["total"] == "total_recent_mean_4"
    assert rank_reference_baselines(candidates(same_week_last_year={"p90": 1.0}))[1]["total"] == "total_same_week_last_year"
    assert rank_reference_baselines(candidates(last_week={"backtests": [0.0, 2.0]}))[1]["total"] == "total_recent_mean_4"


def test_private_cli_writes_only_private_artifacts_and_sanitized_console(tmp_path: Path, monkeypatch, capsys) -> None:
    panel, _ = _inputs()
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    panel_path, table_path = tmp_path / "panel.csv", tmp_path / "table.csv"
    panel.to_csv(panel_path, index=False)
    table.to_csv(table_path, index=False)
    output = tmp_path / "reports" / "private" / "phase15_task2a_baselines"
    phase14_plan_path = tmp_path / "reports" / "private" / "phase14_task2a_validation" / "validation_plan.json"
    phase14_plan_path.parent.mkdir(parents=True)
    config = load_validation_config(ROOT / "configs/task2a_validation.yaml")
    config["backtesting"]["n_backtests"] = 2
    config["backtesting"]["minimum_training_weeks"] = 20
    _, frozen_plan = _inputs()
    phase14_plan_path.write_text(__import__("json").dumps(phase14_plan_metadata(frozen_plan)), encoding="utf-8")
    monkeypatch.setattr(baseline_script, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(baseline_script, "load_validation_config", lambda _: config)
    monkeypatch.setattr(baseline_script, "parse_args", lambda: Namespace(weekly_panel=panel_path, multihorizon_table=table_path,
        validation_config=ROOT / "configs/task2a_validation.yaml", baseline_config=ROOT / "configs/task2a_baselines.yaml",
        feature_config=ROOT / "configs/task2a_features.yaml", output_dir=output, phase14_plan=phase14_plan_path))
    assert baseline_script.main() == 0
    console = capsys.readouterr().out
    assert "LOCAL PHASE 15 BASELINE RUN: PASS" in console
    assert "target_total_volume_m3" not in console and "delivery_id" not in console
    assert (output / "baseline_reference.json").exists() and (output / "run_manifest.json").exists()
