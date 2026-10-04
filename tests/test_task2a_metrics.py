"""Synthetic-only tests for frozen Phase 14 forecast metrics and evaluators."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from src.task2a.metrics import (
    ForecastMetricError,
    evaluate_forecast_by_horizon,
    evaluate_forecast_overall,
    evaluate_forecast_per_series,
    equal_weight_series_metrics,
    forecast_prediction_diagnostics,
    forecast_regression_metrics,
    summarize_backtest_stability,
)


def _scored_rows() -> pd.DataFrame:
    records = []
    for backtest, multiplier in (("BT01", 1.0), ("BT02", 2.0)):
        for depot, brand, total_error in (("A", "Fresh", 1.0), ("A", "Tech", 2.0), ("B", "Style", 3.0)):
            for horizon in range(1, 11):
                records.append({
                    "backtest_id": backtest, "depot": depot, "brand": brand, "horizon_weeks": horizon,
                    "target_total_volume_m3": 10.0,
                    "target_chilled_volume_m3": 4.0 if brand == "Fresh" else 0.0,
                    "pred_total_volume_m3": 10 + total_error * multiplier,
                    "pred_chilled_volume_m3": 4 + multiplier if brand == "Fresh" else 0.0,
                })
    return pd.DataFrame(records)


BACKTEST_IDS = ("BT01", "BT02")
REQUIRED_SERIES = (("A", "Fresh"), ("A", "Tech"), ("B", "Style"))


def _per_series(rows: pd.DataFrame) -> pd.DataFrame:
    return evaluate_forecast_per_series(rows, expected_backtest_ids=BACKTEST_IDS, expected_series=REQUIRED_SERIES)


def _by_horizon(rows: pd.DataFrame) -> pd.DataFrame:
    return evaluate_forecast_by_horizon(rows, expected_backtest_ids=BACKTEST_IDS, expected_series=REQUIRED_SERIES)


def _overall(rows: pd.DataFrame) -> dict:
    return evaluate_forecast_overall(rows, expected_backtest_ids=BACKTEST_IDS, expected_series=REQUIRED_SERIES)


def test_hand_calculated_primary_and_secondary_metrics() -> None:
    perfect = forecast_regression_metrics([0, 2], [0, 2])
    assert perfect["mae"] == 0 and perfect["rmse"] == 0
    result = forecast_regression_metrics([1, 3], [2, 1])
    assert result["mae"] == 1.5
    assert result["rmse"] == pytest.approx(math.sqrt(2.5))
    assert result["wape"] == 75.0
    assert result["mean_bias_m3"] == -0.5
    assert result["p90_absolute_error"] == pytest.approx(1.9)
    assert forecast_regression_metrics([0, 0], [1, -1])["wape"] is None
    assert forecast_regression_metrics([1], [2])["mean_bias_m3"] == 1
    assert forecast_regression_metrics([2], [1])["mean_bias_m3"] == -1


def test_prediction_diagnostics_are_raw_and_nonfinite_metrics_fail() -> None:
    diagnostics = forecast_prediction_diagnostics([-1.0, 2.0, np.nan], [0.0, 3.0, np.inf])
    assert diagnostics == {"n": 3, "nonfinite_prediction_count": 1,
                           "negative_prediction_count": 1, "chilled_gt_total_count": 2}
    assert forecast_regression_metrics([0], [-1])["mae"] == 1  # no Phase 17 clipping
    for truth, prediction in (([1], [np.nan]), ([1], [np.inf]), ([np.nan], [1]), ([1, 2], [1])):
        with pytest.raises(ForecastMetricError):
            forecast_regression_metrics(truth, prediction)


def test_per_series_scores_and_structural_chilled_are_separate() -> None:
    rows = _scored_rows()
    results = _per_series(rows)
    assert len(results) == 12
    assert results.n.eq(10).all()
    fresh = results.loc[results.brand.eq("Fresh") & results.target.eq("chilled")]
    assert fresh.mae.tolist() == [1.0, 2.0]
    zeros = results.loc[results.target.eq("chilled") & ~results.brand.eq("Fresh")]
    assert zeros.chilled_status.eq("STRUCTURAL_ZERO").all() and zeros.mae.isna().all()
    assert set(results.loc[results.target.eq("total"), "depot"]) == {"A", "B"}
    assert set(results.loc[results.target.eq("total"), "brand"]) == {"Fresh", "Style", "Tech"}
    stability = summarize_backtest_stability(results)
    row = stability.loc[stability.depot.eq("A") & stability.brand.eq("Fresh") & stability.target.eq("total")].iloc[0]
    assert row.backtest_count == 2 and row.mean_mae == 1.5 and row.worst_backtest_mae == 2


def test_overall_micro_macro_backtest_and_horizon_outputs_are_deterministic() -> None:
    rows = _scored_rows()
    result = _overall(rows)
    shuffled = _overall(rows.sample(frac=1, random_state=11))
    assert result == shuffled
    assert result["total_micro"]["n"] == 60
    assert result["total_micro"]["mae"] == 3.0
    assert result["total_macro_series"]["mae"] == 3.0  # balanced frozen coverage
    assert result["fresh_chilled_micro"]["n"] == 20
    assert result["fresh_chilled_micro"]["mae"] == 1.5
    assert result["overall_backtest_stability"]["total"]["backtest_count"] == 2
    assert result["overall_backtest_stability"]["total"]["best_backtest_id"] == "BT01"
    assert result["overall_backtest_stability"]["total"]["worst_backtest_id"] == "BT02"
    assert len(result["by_horizon"]) == 20
    horizon = _by_horizon(rows)
    assert sorted(horizon.horizon_weeks.unique()) == list(range(1, 11))


def test_equal_series_macro_differs_from_micro_when_support_is_unbalanced() -> None:
    pooled = pd.DataFrame({"depot": ["A", "B"], "brand": ["Fresh", "Fresh"],
                           "target": ["total", "total"], "mae": [1.0, 9.0], "rmse": [1.0, 9.0]})
    macro = equal_weight_series_metrics(pooled, "total")
    micro = (1 * 100 + 9 * 10) / 110
    assert macro["mae"] == 5.0 and micro != macro["mae"]


def test_missing_horizon_missing_series_and_bad_structural_actual_fail() -> None:
    rows = _scored_rows()
    with pytest.raises(ForecastMetricError, match="exact horizons"):
        _per_series(rows.drop(index=rows.index[0]))
    with pytest.raises(ForecastMetricError, match="Required series"):
        _overall(rows.loc[~(rows.backtest_id.eq("BT02") & rows.brand.eq("Tech"))])
    wrong = rows.copy()
    wrong.loc[wrong.brand.eq("Style"), "target_chilled_volume_m3"] = 1
    with pytest.raises(ForecastMetricError, match="structural zeros"):
        _overall(wrong)


def test_raw_negative_and_chilled_above_total_are_reported_without_correction() -> None:
    rows = _scored_rows()
    rows.loc[rows.index[0], "pred_total_volume_m3"] = -2
    rows.loc[rows.index[0], "pred_chilled_volume_m3"] = 8
    result = _overall(rows)
    assert result["total_micro"]["negative_prediction_count"] == 1
    assert result["total_micro"]["chilled_gt_total_count"] == 1
    assert result["total_micro"]["mae"] > 3.0
    rows.loc[rows.index[0], "pred_total_volume_m3"] = np.inf
    with pytest.raises(ForecastMetricError, match="nonfinite"):
        _overall(rows)


def test_whole_missing_backtest_or_series_fails_frozen_plan_check() -> None:
    rows = _scored_rows()
    with pytest.raises(ForecastMetricError, match="frozen backtest IDs"):
        _overall(rows.loc[rows.backtest_id.eq("BT01")])
    with pytest.raises(ForecastMetricError, match="frozen backtest IDs"):
        _overall(rows.loc[rows.brand.ne("Style")])
