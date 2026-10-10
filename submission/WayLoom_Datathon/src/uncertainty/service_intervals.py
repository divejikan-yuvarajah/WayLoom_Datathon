"""Task 1 service-time conformal-style residual intervals."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .quantiles import finite_sample_quantile, validate_coverage_levels
from .residual_sources import ResidualSourceError, validate_oos_residuals


class ServiceIntervalError(ValueError):
    """Task 1 service uncertainty invariants were violated."""


def _suffix(level: float) -> str:
    return str(int(round(level * 100)))


def calibrate_service_quantiles(
    residuals: pd.DataFrame,
    coverage_levels: list[float] | tuple[float, ...],
    *,
    minimum_count: int = 1,
) -> dict[float, float]:
    try:
        clean = validate_oos_residuals(residuals, source_type="frozen_oos_validation")
    except ResidualSourceError as exc:
        raise ServiceIntervalError(str(exc)) from exc
    if type(minimum_count) is not int or minimum_count < 1 or len(clean) < minimum_count:
        raise ServiceIntervalError("Insufficient global Task 1 OOS residuals.")
    levels = validate_coverage_levels(coverage_levels)
    scores = clean.absolute_residual.to_numpy(dtype=float)
    return {level: finite_sample_quantile(scores, level) for level in levels}


def calibrate_service_segment(
    residuals: pd.DataFrame,
    coverage: float,
    *,
    segment_column: str,
    segment_value: Any,
    minimum_segment_count: int = 30,
    minimum_global_count: int = 1,
) -> tuple[float, str, int]:
    """Use a predeclared segment only when adequate; otherwise fall back globally."""
    clean = validate_oos_residuals(residuals, source_type="frozen_oos_validation")
    if segment_column not in clean:
        raise ServiceIntervalError("Predeclared service segment is absent from OOS residuals.")
    segment = clean.loc[clean[segment_column].eq(segment_value)]
    if len(segment) >= minimum_segment_count:
        return finite_sample_quantile(segment.absolute_residual, coverage), f"segment:{segment_column}", len(segment)
    if len(clean) < minimum_global_count:
        raise ServiceIntervalError("Insufficient global Task 1 OOS residuals for segment fallback.")
    return finite_sample_quantile(clean.absolute_residual, coverage), "global_fallback", len(clean)


def build_service_intervals(
    official_submission: pd.DataFrame,
    residuals: pd.DataFrame,
    coverage_levels: list[float] | tuple[float, ...],
    *,
    minimum_count: int = 1,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    required = ["delivery_id", "pred_service_min", "pred_late_prob"]
    if list(official_submission.columns) != required:
        raise ServiceIntervalError("Task 1 official schema is not exact.")
    if official_submission.delivery_id.isna().any() or official_submission.delivery_id.duplicated().any():
        raise ServiceIntervalError("Task 1 identifiers must be unique and nonnull.")
    point = pd.to_numeric(official_submission.pred_service_min, errors="raise").to_numpy(dtype=float)
    if not np.isfinite(point).all() or (point < 0).any():
        raise ServiceIntervalError("Frozen service point predictions must be finite and nonnegative.")
    quantiles = calibrate_service_quantiles(residuals, coverage_levels, minimum_count=minimum_count)
    result = official_submission[["delivery_id", "pred_service_min"]].copy()
    clipped: dict[float, int] = {}
    for level, quantile in quantiles.items():
        suffix = _suffix(level)
        raw_lower = point - quantile
        lower = np.maximum(0.0, raw_lower)
        upper = np.maximum(lower, point + quantile)
        result[f"service_lower_{suffix}"] = lower
        result[f"service_upper_{suffix}"] = upper
        result[f"service_width_{suffix}"] = upper - lower
        clipped[level] = int((raw_lower < 0).sum())
    result["calibration_method"] = "finite_sample_higher_absolute_oos_residual"
    result["calibration_sample_count"] = int(len(residuals))
    if not np.array_equal(result.pred_service_min.to_numpy(), official_submission.pred_service_min.to_numpy()):
        raise ServiceIntervalError("Phase 27 changed Task 1 point predictions.")
    for level in quantiles:
        suffix = _suffix(level)
        if ((result[f"service_lower_{suffix}"] > point) | (result[f"service_upper_{suffix}"] < point)).any():
            raise ServiceIntervalError("A service interval does not contain its frozen point prediction.")
    widths = [result[f"service_width_{_suffix(level)}"].to_numpy() for level in quantiles]
    if any((later + 1e-12 < earlier).any() for earlier, later in zip(widths, widths[1:])):
        raise ServiceIntervalError("Higher target coverage produced a narrower service interval.")
    scores = residuals.absolute_residual.to_numpy(dtype=float)
    summary = {
        "status": "PASS",
        "calibration_method": "finite_sample_higher_absolute_oos_residual",
        "calibration_residual_count": int(len(scores)),
        "residual_mae": float(np.mean(scores)),
        "residual_median_absolute_error": float(np.median(scores)),
        "quantiles": {str(level): quantiles[level] for level in quantiles},
        "interval_widths": {
            str(level): {
                "mean": float(result[f"service_width_{_suffix(level)}"].mean()),
                "median": float(result[f"service_width_{_suffix(level)}"].median()),
                "min": float(result[f"service_width_{_suffix(level)}"].min()),
                "max": float(result[f"service_width_{_suffix(level)}"].max()),
                "fraction_lower_clipped_zero": clipped[level] / len(result),
            }
            for level in quantiles
        },
        "independent_coverage_evaluation": "NOT_AVAILABLE",
    }
    return result, summary
