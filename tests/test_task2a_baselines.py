"""Synthetic-only tests for frozen Phase 15 Task 2A baseline formulas."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.task2a.baselines import (BaselineError, ForecastRequest, build_history_as_of_origin,
    load_baseline_config, predict_last_week, predict_recent_mean, predict_same_week_last_year,
    predict_seasonal_recent_weighted, validate_baseline_config)


ROOT = Path(__file__).resolve().parents[1]


def _panel(weeks: int = 110) -> pd.DataFrame:
    dates = pd.date_range("2020-10-05", periods=weeks, freq="7D")
    iso = dates.isocalendar()
    rows = []
    for depot, brand, offset in (("A", "Fresh", 0.0), ("A", "Tech", 100.0), ("B", "Style", 200.0)):
        total = np.arange(weeks, dtype=float) + offset
        rows.append(pd.DataFrame({"depot": depot, "brand": brand, "iso_year": iso.year.to_numpy(dtype=int),
            "iso_week": iso.week.to_numpy(dtype=int), "week_start_date": dates, "total_volume_m3": total,
            "chilled_volume_m3": total / 2 if brand == "Fresh" else 0.0, "panel_status": "OBSERVED_DEMAND"}))
    return pd.concat(rows, ignore_index=True)


def _request(panel: pd.DataFrame, origin_index: int = 70, horizon: int = 1) -> ForecastRequest:
    origin = panel.loc[panel.brand.eq("Fresh"), "week_start_date"].iloc[origin_index]
    target = origin + pd.Timedelta(weeks=horizon)
    iso = target.isocalendar()
    return ForecastRequest("A", "Fresh", origin, target, int(iso.year), int(iso.week), horizon)


def test_last_week_recent_mean_and_series_isolation_are_exact() -> None:
    panel = _panel()
    request = _request(panel)
    history = build_history_as_of_origin(panel, request.origin_week_start_date)
    assert predict_last_week(history, request, "total").value == 70.0
    assert predict_recent_mean(history, request, "total").value == pytest.approx((67 + 68 + 69 + 70) / 4)
    assert predict_last_week(history, request, "chilled").value == 35.0
    tech_request = ForecastRequest("A", "Tech", *request.__dict__.values()[2:]) if False else ForecastRequest(
        "A", "Tech", request.origin_week_start_date, request.target_week_start_date, request.target_iso_year,
        request.target_iso_week, request.forecast_horizon)
    assert predict_last_week(history, tech_request, "total").value == 170.0


def test_confirmed_zero_is_valid_and_short_recent_history_is_unavailable() -> None:
    panel = _panel()
    zero = (panel.depot.eq("A")) & panel.brand.eq("Fresh") & panel.week_start_date.eq(panel.week_start_date.unique()[70])
    panel.loc[zero, ["total_volume_m3", "chilled_volume_m3"]] = 0.0
    request = _request(panel)
    history = build_history_as_of_origin(panel, request.origin_week_start_date)
    assert predict_last_week(history, request, "total").value == 0.0
    early = _request(panel, origin_index=2)
    assert predict_recent_mean(build_history_as_of_origin(panel, early.origin_week_start_date), early, "total").value is None


def test_same_week_last_year_is_iso_based_and_weighted_is_exact() -> None:
    panel = _panel()
    request = _request(panel, horizon=4)
    history = build_history_as_of_origin(panel, request.origin_week_start_date)
    seasonal = predict_same_week_last_year(history, request, "total")
    expected = history.loc[(history.depot.eq("A")) & history.brand.eq("Fresh")
                           & history.iso_year.eq(request.target_iso_year - 1) & history.iso_week.eq(request.target_iso_week), "total_volume_m3"]
    assert len(expected) == 1 and seasonal.value == float(expected.iloc[0]) and seasonal.seasonal_exact_used
    recent = predict_recent_mean(history, request, "total")
    weighted = predict_seasonal_recent_weighted(history, request, "total")
    assert weighted.value == pytest.approx(0.5 * recent.value + 0.5 * seasonal.value)


def test_missing_week_53_and_missing_seasonal_use_recent_fallback() -> None:
    panel = _panel()
    request = _request(panel, origin_index=70)
    history = build_history_as_of_origin(panel, request.origin_week_start_date)
    impossible = ForecastRequest("A", "Fresh", request.origin_week_start_date, request.target_week_start_date, 2022, 53, 1)
    seasonal = predict_same_week_last_year(history, impossible, "total")
    recent = predict_recent_mean(history, impossible, "total")
    assert seasonal.value == recent.value and seasonal.seasonal_fallback_used
    weighted = predict_seasonal_recent_weighted(history, impossible, "total")
    assert weighted.value == recent.value and weighted.seasonal_fallback_used


def test_config_weights_are_frozen_and_negative_or_tuned_weights_fail() -> None:
    config = load_baseline_config(ROOT / "configs/task2a_baselines.yaml")
    config["baseline_families"]["seasonal_recent_weighted"]["recent_weight"] = -0.1
    with pytest.raises(BaselineError):
        validate_baseline_config(config)
    config = load_baseline_config(ROOT / "configs/task2a_baselines.yaml")
    config["baseline_families"]["seasonal_recent_weighted"]["recent_weight"] = 0.4
    config["baseline_families"]["seasonal_recent_weighted"]["seasonal_weight"] = 0.6
    with pytest.raises(BaselineError):
        validate_baseline_config(config)


def test_future_history_cannot_enter_as_of_origin_slice() -> None:
    panel = _panel()
    request = _request(panel)
    before = build_history_as_of_origin(panel, request.origin_week_start_date)
    changed = panel.copy()
    changed.loc[changed.week_start_date.gt(request.origin_week_start_date), "total_volume_m3"] = 99999.0
    after = build_history_as_of_origin(changed, request.origin_week_start_date)
    pd.testing.assert_frame_equal(before, after)
    assert predict_recent_mean(panel, request, "total").value == predict_recent_mean(before, request, "total").value
