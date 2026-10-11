"""Horizon-aware Task 2A forecast uncertainty intervals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .quantiles import finite_sample_quantile, validate_coverage_levels
from .residual_sources import ResidualSourceError, validate_oos_residuals


class ForecastIntervalError(ValueError):
    """Task 2A interval calibration or output invariants were violated."""


@dataclass(frozen=True)
class CalibrationChoice:
    quantile: float
    source: str
    sample_count: int


def _suffix(level: float) -> str:
    return str(int(round(level * 100)))


def map_forecast_horizons(test_inputs: pd.DataFrame) -> pd.DataFrame:
    required = {"row_id", "depot", "brand", "iso_year", "iso_week"}
    if required.difference(test_inputs.columns) or test_inputs.empty:
        raise ForecastIntervalError("Task 2A test inputs are incomplete.")
    out = test_inputs.copy()
    if out.row_id.isna().any() or out.row_id.duplicated().any():
        raise ForecastIntervalError("Task 2A row_id must be unique and nonnull.")
    try:
        out["target_week_start_date"] = [
            pd.Timestamp.fromisocalendar(int(year), int(week), 1)
            for year, week in zip(out.iso_year, out.iso_week, strict=True)
        ]
    except (TypeError, ValueError) as exc:
        raise ForecastIntervalError("Task 2A ISO year/week values are invalid.") from exc
    weeks = sorted(out.target_week_start_date.unique())
    if len(weeks) != 10 or any(pd.Timestamp(b) - pd.Timestamp(a) != pd.Timedelta(days=7) for a, b in zip(weeks, weeks[1:])):
        raise ForecastIntervalError("Official Task 2A future weeks must be one consecutive 10-week sequence.")
    horizon = {pd.Timestamp(week): index for index, week in enumerate(weeks, 1)}
    out["forecast_horizon"] = out.target_week_start_date.map(horizon).astype(int)
    expected = set(range(1, 11))
    coverage = out.groupby(["depot", "brand"], sort=False).forecast_horizon.agg(set)
    if not coverage.map(lambda values: values == expected).all() or out.duplicated(["depot", "brand", "forecast_horizon"]).any():
        raise ForecastIntervalError("Every Task 2A series must map exactly once to horizons 1..10.")
    return out


def calibrate_forecast_quantile(
    residuals: pd.DataFrame,
    horizon: int,
    coverage: float,
    *,
    minimum_per_horizon: int,
    minimum_pooled: int,
) -> CalibrationChoice:
    try:
        clean = validate_oos_residuals(residuals, source_type="frozen_rolling_oos")
    except ResidualSourceError as exc:
        raise ForecastIntervalError(str(exc)) from exc
    if "horizon_weeks" not in clean or horizon not in range(1, 11):
        raise ForecastIntervalError("Forecast calibration requires a valid horizon 1..10.")
    local = clean.loc[pd.to_numeric(clean.horizon_weeks, errors="raise").eq(horizon)]
    if len(local) >= minimum_per_horizon:
        return CalibrationChoice(finite_sample_quantile(local.absolute_residual, coverage), f"horizon_{horizon}", len(local))
    if len(clean) >= minimum_pooled:
        return CalibrationChoice(finite_sample_quantile(clean.absolute_residual, coverage), "pooled_target", len(clean))
    raise ForecastIntervalError("Target has insufficient horizon residuals and no adequate pooled fallback.")


def build_forecast_intervals(
    official_submission: pd.DataFrame,
    test_inputs: pd.DataFrame,
    total_residuals: pd.DataFrame,
    chilled_residuals: pd.DataFrame,
    coverage_levels: list[float] | tuple[float, ...],
    *,
    minimum_per_horizon: int = 20,
    minimum_pooled: int = 20,
    chilled_zero_brands: tuple[str, ...] = ("Style", "Tech"),
) -> tuple[pd.DataFrame, dict[str, Any], list[dict[str, Any]]]:
    exact = ["row_id", "pred_total_volume_m3", "pred_chilled_volume_m3"]
    if list(official_submission.columns) != exact:
        raise ForecastIntervalError("Task 2A official schema is not exact.")
    levels = validate_coverage_levels(coverage_levels)
    mapped = map_forecast_horizons(test_inputs)
    base = official_submission.merge(
        mapped[["row_id", "depot", "brand", "iso_year", "iso_week", "forecast_horizon"]],
        on="row_id", how="left", validate="one_to_one", sort=False,
    )
    if len(base) != len(official_submission) or base.forecast_horizon.isna().any() or base.row_id.astype(str).tolist() != official_submission.row_id.astype(str).tolist():
        raise ForecastIntervalError("Task 2A private output lost official row coverage/order.")
    total_point = pd.to_numeric(base.pred_total_volume_m3, errors="raise").to_numpy(dtype=float)
    chilled_point = pd.to_numeric(base.pred_chilled_volume_m3, errors="raise").to_numpy(dtype=float)
    if not np.isfinite(np.column_stack([total_point, chilled_point])).all() or (total_point < 0).any() or (chilled_point < 0).any():
        raise ForecastIntervalError("Frozen Task 2A points must be finite and nonnegative.")
    if (chilled_point > total_point).any():
        raise ForecastIntervalError("Frozen chilled point exceeds total point.")
    fallback_rows: list[dict[str, Any]] = []
    choices: dict[tuple[str, int, float], CalibrationChoice] = {}
    for target, residuals in (("total", total_residuals), ("chilled", chilled_residuals)):
        for horizon in range(1, 11):
            for level in levels:
                choice = calibrate_forecast_quantile(
                    residuals, horizon, level,
                    minimum_per_horizon=minimum_per_horizon, minimum_pooled=minimum_pooled,
                )
                choices[target, horizon, level] = choice
                fallback_rows.append({"target": target, "horizon": horizon, "coverage": level,
                    "calibration_source": choice.source, "calibration_n": choice.sample_count})
    result = base.copy()
    for level in levels:
        suffix = _suffix(level)
        total_q = np.asarray([choices["total", int(h), level].quantile for h in base.forecast_horizon], dtype=float)
        total_lower = np.maximum(0.0, total_point - total_q)
        total_upper = np.maximum(total_lower, total_point + total_q)
        result[f"total_lower_{suffix}"] = total_lower
        result[f"total_upper_{suffix}"] = total_upper
        chilled_q = np.asarray([choices["chilled", int(h), level].quantile for h in base.forecast_horizon], dtype=float)
        raw_lower = np.maximum(0.0, chilled_point - chilled_q)
        raw_upper = np.maximum(raw_lower, chilled_point + chilled_q)
        structural = base.brand.isin(chilled_zero_brands).to_numpy()
        raw_lower[structural] = 0.0
        raw_upper[structural] = 0.0
        coherent_upper = np.minimum(raw_upper, total_upper)
        coherent_lower = np.minimum(raw_lower, coherent_upper)
        result[f"chilled_lower_{suffix}_raw"] = raw_lower
        result[f"chilled_upper_{suffix}_raw"] = raw_upper
        result[f"chilled_lower_{suffix}"] = coherent_lower
        result[f"chilled_upper_{suffix}"] = coherent_upper
        result[f"coherence_adjusted_{suffix}"] = (coherent_lower != raw_lower) | (coherent_upper != raw_upper)
    first = levels[0]
    result["total_calibration_source"] = [choices["total", int(h), first].source for h in base.forecast_horizon]
    result["total_calibration_n"] = [choices["total", int(h), first].sample_count for h in base.forecast_horizon]
    result["chilled_calibration_source"] = [
        "structural_zero" if brand in chilled_zero_brands else choices["chilled", int(h), first].source
        for brand, h in zip(base.brand, base.forecast_horizon, strict=True)
    ]
    result["chilled_calibration_n"] = [
        0 if brand in chilled_zero_brands else choices["chilled", int(h), first].sample_count
        for brand, h in zip(base.brand, base.forecast_horizon, strict=True)
    ]
    for level in levels:
        suffix = _suffix(level)
        if ((result[f"total_lower_{suffix}"] > total_point) | (result[f"total_upper_{suffix}"] < total_point)).any():
            raise ForecastIntervalError("Total interval does not contain its point prediction.")
        fresh = base.brand.eq("Fresh")
        if ((result.loc[fresh, f"chilled_lower_{suffix}"] > chilled_point[fresh]) |
                (result.loc[fresh, f"chilled_upper_{suffix}"] < chilled_point[fresh])).any():
            raise ForecastIntervalError("Fresh chilled interval does not contain its point prediction.")
        zeros = base.brand.isin(chilled_zero_brands)
        cols = [f"chilled_lower_{suffix}_raw", f"chilled_upper_{suffix}_raw", f"chilled_lower_{suffix}", f"chilled_upper_{suffix}"]
        if not result.loc[zeros, cols].eq(0.0).all().all():
            raise ForecastIntervalError("Structural-zero chilled intervals must be exactly [0,0].")
        if (result[f"chilled_upper_{suffix}"] > result[f"total_upper_{suffix}"]).any():
            raise ForecastIntervalError("Coherent chilled upper exceeds total upper.")
    if not np.array_equal(result.pred_total_volume_m3.to_numpy(), official_submission.pred_total_volume_m3.to_numpy()) or not np.array_equal(
        result.pred_chilled_volume_m3.to_numpy(), official_submission.pred_chilled_volume_m3.to_numpy()
    ):
        raise ForecastIntervalError("Phase 27 changed Task 2A point predictions.")
    summary = {
        "status": "PASS",
        "method": "horizon_specific_additive_absolute_residual_conformal_style",
        "coverage_levels": list(levels),
        "total_residual_count": int(len(total_residuals)),
        "chilled_fresh_residual_count": int(len(chilled_residuals)),
        "coherence_note": "Presentation-coherent chilled bounds are clipped to total upper bounds; raw marginal bounds are retained.",
        "future_coverage_guarantee": False,
    }
    return result, summary, fallback_rows
