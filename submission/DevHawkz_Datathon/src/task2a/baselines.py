"""Leakage-safe, frozen simple Task 2A forecast baselines for Phase 15."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.task2a.eda import EDAValidationError, validate_task2a_eda_input


SERIES = ("depot", "brand")
TOTAL_BASELINES = ("total_last_week", "total_recent_mean_4", "total_same_week_last_year", "total_seasonal_recent_weighted")
CHILLED_BASELINES = ("chilled_last_week", "chilled_recent_mean_4", "chilled_same_week_last_year", "chilled_seasonal_recent_weighted")


class BaselineError(ValueError):
    """A fixed Phase 15 baseline rule or information boundary was violated."""


@dataclass(frozen=True)
class ForecastRequest:
    depot: str
    brand: str
    origin_week_start_date: pd.Timestamp
    target_week_start_date: pd.Timestamp
    target_iso_year: int
    target_iso_week: int
    forecast_horizon: int


@dataclass(frozen=True)
class BaselinePrediction:
    value: float | None
    fallback_status: str
    seasonal_exact_used: bool = False
    seasonal_fallback_used: bool = False


def load_baseline_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    validate_baseline_config(config)
    return config


def validate_baseline_config(config: dict[str, Any]) -> None:
    if not isinstance(config, dict) or config.get("version") != 1:
        raise BaselineError("Baseline configuration version must be 1.")
    if config.get("series_keys") != list(SERIES):
        raise BaselineError("Baseline series key must be depot and brand.")
    if config.get("validation") != {"reuse_phase14_plan": True, "require_exact_10_week_windows": True}:
        raise BaselineError("Phase 14 plan reuse and exact ten-week windows must remain enabled.")
    families = config.get("baseline_families", {})
    if not all(families.get(name, {}).get("enabled") is True for name in ("last_week", "recent_mean", "same_week_last_year", "seasonal_recent_weighted")):
        raise BaselineError("All four frozen baseline families must be enabled.")
    recent = families["recent_mean"]
    if recent.get("window_weeks") != 4 or recent.get("minimum_history_weeks") != 4:
        raise BaselineError("Recent mean must use exactly four trailing weeks.")
    seasonal = families["same_week_last_year"]
    if seasonal.get("lookup") != "exact_prior_iso_year_same_iso_week" or seasonal.get("unavailable_fallback") != "recent_mean":
        raise BaselineError("Seasonal lookup and fallback are frozen.")
    weights = families["seasonal_recent_weighted"]
    recent_weight, seasonal_weight = weights.get("recent_weight"), weights.get("seasonal_weight")
    if not all(isinstance(value, (int, float)) and value >= 0 for value in (recent_weight, seasonal_weight)) or not np.isclose(recent_weight + seasonal_weight, 1.0):
        raise BaselineError("Frozen blend weights must be nonnegative and sum to one.")
    if not np.isclose(recent_weight, 0.5) or not np.isclose(seasonal_weight, 0.5):
        raise BaselineError("Phase 15 blend weights must remain 0.50 / 0.50.")
    chilled = config.get("chilled_target", {})
    if chilled.get("column") != "chilled_volume_m3" or chilled.get("fresh_brand") != "Fresh" or set(chilled.get("structural_zero_brands", [])) != {"Style", "Tech"}:
        raise BaselineError("Frozen chilled target policy is Fresh with Style/Tech structural zeros.")
    if config.get("postprocessing") != {"clip_negative": False, "enforce_chilled_le_total": False}:
        raise BaselineError("Phase 15 may not clip or cap raw baseline predictions.")
    selection = config.get("selection", {})
    if selection.get("total_primary_metric") != "mae" or selection.get("chilled_primary_metric") != "mae" or selection.get("tie_break_order") != ["rmse", "p90_absolute_error", "backtest_mae_std", "simplicity"]:
        raise BaselineError("Frozen reference-baseline ranking rule was changed.")


def build_history_as_of_origin(panel: pd.DataFrame, origin: pd.Timestamp) -> pd.DataFrame:
    """Return only canonical history that was available at the forecast origin."""
    try:
        history = validate_task2a_eda_input(panel)
    except EDAValidationError as error:
        raise BaselineError(str(error)) from error
    origin = pd.Timestamp(origin).normalize()
    result = history.loc[history.week_start_date.le(origin)].copy()
    if result.empty:
        raise BaselineError("No weekly history is available at the forecast origin.")
    return result.sort_values([*SERIES, "week_start_date"], kind="stable").reset_index(drop=True)


def _series_history(history: pd.DataFrame, request: ForecastRequest) -> pd.DataFrame:
    # Keep the boundary here as well as in build_history_as_of_origin so a
    # direct caller cannot accidentally provide a full-history look-ahead.
    rows = history.loc[history.depot.eq(request.depot) & history.brand.eq(request.brand)
                       & history.week_start_date.le(request.origin_week_start_date)].copy()
    if rows.empty or rows.week_start_date.max() != request.origin_week_start_date:
        raise BaselineError("Required origin-week history value is unavailable for the requested series.")
    return rows.sort_values("week_start_date", kind="stable")


def _target_column(target_name: str) -> str:
    if target_name == "total":
        return "total_volume_m3"
    if target_name == "chilled":
        return "chilled_volume_m3"
    raise BaselineError("Baseline target must be total or chilled.")


def predict_last_week(history: pd.DataFrame, request: ForecastRequest, target_name: str) -> BaselinePrediction:
    series = _series_history(history, request)
    return BaselinePrediction(float(series.iloc[-1][_target_column(target_name)]), "LAST_WEEK")


def predict_recent_mean(history: pd.DataFrame, request: ForecastRequest, target_name: str, *, window_weeks: int = 4) -> BaselinePrediction:
    series = _series_history(history, request)
    if window_weeks != 4:
        raise BaselineError("Phase 15 recent mean window is frozen at four weeks.")
    trailing = series.tail(window_weeks)
    if len(trailing) != window_weeks or not trailing.week_start_date.diff().dropna().eq(pd.Timedelta(weeks=1)).all():
        return BaselinePrediction(None, "BASELINE_UNAVAILABLE")
    return BaselinePrediction(float(trailing[_target_column(target_name)].mean()), "RECENT_MEAN_4")


def predict_same_week_last_year(history: pd.DataFrame, request: ForecastRequest, target_name: str) -> BaselinePrediction:
    seasonal = history.loc[
        history.depot.eq(request.depot) & history.brand.eq(request.brand)
        & history.iso_year.eq(request.target_iso_year - 1) & history.iso_week.eq(request.target_iso_week)
    ]
    if len(seasonal) == 1 and seasonal.week_start_date.iloc[0] <= request.origin_week_start_date:
        return BaselinePrediction(float(seasonal.iloc[0][_target_column(target_name)]), "SEASONAL_EXACT", True, False)
    fallback = predict_recent_mean(history, request, target_name)
    if fallback.value is None:
        return fallback
    return BaselinePrediction(fallback.value, "SEASONAL_FALLBACK_RECENT_MEAN_4", False, True)


def predict_seasonal_recent_weighted(history: pd.DataFrame, request: ForecastRequest, target_name: str,
                                     *, recent_weight: float = 0.5, seasonal_weight: float = 0.5) -> BaselinePrediction:
    if recent_weight < 0 or seasonal_weight < 0 or not np.isclose(recent_weight + seasonal_weight, 1.0):
        raise BaselineError("Baseline weights must be nonnegative and sum to one.")
    if not np.isclose(recent_weight, 0.5) or not np.isclose(seasonal_weight, 0.5):
        raise BaselineError("Phase 15 weighted baseline is fixed at 0.50 / 0.50.")
    recent = predict_recent_mean(history, request, target_name)
    if recent.value is None:
        return recent
    seasonal = predict_same_week_last_year(history, request, target_name)
    if seasonal.seasonal_fallback_used:
        return BaselinePrediction(recent.value, "WEIGHTED_SEASONAL_FALLBACK_RECENT_MEAN_4", False, True)
    if seasonal.value is None:  # defensive; the seasonal function normally falls back itself
        return recent
    return BaselinePrediction(recent_weight * recent.value + seasonal_weight * seasonal.value,
                              "WEIGHTED_EXACT", True, False)


def predict_baseline(history: pd.DataFrame, request: ForecastRequest, target_name: str, family: str) -> BaselinePrediction:
    if family == "last_week":
        return predict_last_week(history, request, target_name)
    if family == "recent_mean_4":
        return predict_recent_mean(history, request, target_name)
    if family == "same_week_last_year":
        return predict_same_week_last_year(history, request, target_name)
    if family == "seasonal_recent_weighted":
        return predict_seasonal_recent_weighted(history, request, target_name)
    raise BaselineError(f"Unknown frozen baseline family: {family}")
