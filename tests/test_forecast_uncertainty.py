import numpy as np
import pandas as pd
import pytest

from src.uncertainty.forecast_intervals import (ForecastIntervalError, build_forecast_intervals,
    calibrate_forecast_quantile, map_forecast_horizons)
from src.uncertainty.residual_sources import load_task2a_frozen_oos


def inputs():
    rows = []
    for brand in ("Fresh", "Style", "Tech"):
        for horizon, date in enumerate(pd.date_range("2027-01-04", periods=10, freq="7D"), 1):
            iso = date.isocalendar()
            rows.append({"row_id": f"{brand}-{horizon}", "depot": "D", "brand": brand,
                         "iso_year": iso.year, "iso_week": iso.week})
    return pd.DataFrame(rows)


def official():
    frame = inputs()
    return pd.DataFrame({"row_id": frame.row_id, "pred_total_volume_m3": [10.0] * len(frame),
                         "pred_chilled_volume_m3": [2.0 if b == "Fresh" else 0.0 for b in frame.brand]})


def residuals(target="total", n_per_horizon=2):
    rows = []
    for horizon in range(1, 11):
        for i in range(n_per_horizon):
            score = float(horizon + i)
            rows.append({"actual": 10 + score, "prediction": 10.0, "absolute_residual": score,
                "fold": i + 1, "source_type": "frozen_rolling_oos", "horizon_weeks": horizon,
                "origin_week_start_date": f"2025-{i + 1:02d}-01", "target": target})
    return pd.DataFrame(rows)


def test_horizon_mapping_uses_iso_sequence_not_row_position():
    shuffled = inputs().sample(frac=1, random_state=4)
    mapped = map_forecast_horizons(shuffled)
    assert set(mapped.forecast_horizon) == set(range(1, 11))
    assert mapped.groupby(["depot", "brand"]).forecast_horizon.agg(set).eq(set(range(1, 11))).all()


def test_horizon_specific_and_sparse_pooled_fallback():
    frame = residuals(n_per_horizon=3)
    local = calibrate_forecast_quantile(frame, 2, 0.8, minimum_per_horizon=3, minimum_pooled=20)
    assert local.source == "horizon_2" and local.sample_count == 3
    pooled = calibrate_forecast_quantile(frame, 2, 0.8, minimum_per_horizon=4, minimum_pooled=20)
    assert pooled.source == "pooled_target" and pooled.sample_count == 30


def test_missing_fallback_rejected():
    with pytest.raises(ForecastIntervalError):
        calibrate_forecast_quantile(residuals(n_per_horizon=1), 1, 0.8,
                                    minimum_per_horizon=20, minimum_pooled=20)


def test_forecast_intervals_physical_structural_and_unchanged():
    official_points = official()
    result, _, _ = build_forecast_intervals(official_points, inputs(), residuals(), residuals("chilled"),
        [0.8, 0.9], minimum_per_horizon=2, minimum_pooled=2)
    assert result.row_id.tolist() == official_points.row_id.tolist()
    assert result.pred_total_volume_m3.tolist() == official_points.pred_total_volume_m3.tolist()
    assert result.pred_chilled_volume_m3.tolist() == official_points.pred_chilled_volume_m3.tolist()
    assert (result.total_lower_80 >= 0).all()
    assert (result.total_lower_80 <= result.pred_total_volume_m3).all()
    assert (result.total_upper_80 >= result.pred_total_volume_m3).all()
    fresh = result.brand.eq("Fresh")
    assert (result.loc[fresh, "chilled_upper_80_raw"] > 0).all()
    zero = result.brand.isin(["Style", "Tech"])
    assert result.loc[zero, ["chilled_lower_80_raw", "chilled_upper_80_raw",
                             "chilled_lower_80", "chilled_upper_80"]].eq(0).all().all()
    assert (result.chilled_upper_80 <= result.total_upper_80).all()
    assert {"chilled_upper_80_raw", "chilled_upper_80", "coherence_adjusted_80"}.issubset(result)


def test_zero_total_point_can_have_positive_upper():
    points = official()
    points["pred_total_volume_m3"] = 0.0
    points["pred_chilled_volume_m3"] = 0.0
    result, _, _ = build_forecast_intervals(points, inputs(), residuals(), residuals("chilled"),
        [0.8], minimum_per_horizon=2, minimum_pooled=2)
    assert result.total_lower_80.eq(0).all()
    assert result.total_upper_80.gt(0).all()


def test_incomplete_horizon_sequence_rejected():
    with pytest.raises(ForecastIntervalError):
        map_forecast_horizons(inputs().iloc[:-1])


def test_frozen_oos_adapter_aligns_total_and_chilled_without_suffix_assumption():
    keys = {
        "backtest_id": 1,
        "depot": "D",
        "brand": "Fresh",
        "origin_week_start_date": "2025-01-06",
        "target_week_start_date": "2025-01-13",
        "horizon_weeks": 1,
        "phase14_backtest_signature": "sig",
    }
    rows = pd.DataFrame([
        {**keys, "target_name": "total", "candidate_id": "total_final", "y_true": 4.0, "y_pred": 3.0},
        {**keys, "target_name": "chilled", "candidate_id": "chilled_final", "y_true": 2.0, "y_pred": 5.0},
    ])
    config = {
        "validation": {"backtest_signature": "sig"},
        "total": {"candidate_id": "total_final"},
        "chilled_fresh": {"candidate_id": "chilled_final"},
    }
    result = load_task2a_frozen_oos(rows, config)
    assert result["total"].prediction.tolist() == [3.0]
    assert result["chilled"].prediction.tolist() == [3.0]
    assert result["chilled"].absolute_residual.tolist() == [1.0]
