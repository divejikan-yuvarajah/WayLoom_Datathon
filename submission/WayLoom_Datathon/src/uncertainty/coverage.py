"""Honest empirical and sequential coverage diagnostics."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .quantiles import finite_sample_quantile, validate_coverage_levels


class CoverageError(ValueError):
    """Coverage diagnostics are invalid or temporally leaky."""


def interval_diagnostics(actual: pd.Series, lower: pd.Series, upper: pd.Series) -> dict[str, float]:
    values = np.column_stack([
        pd.to_numeric(actual, errors="raise"),
        pd.to_numeric(lower, errors="raise"),
        pd.to_numeric(upper, errors="raise"),
    ]).astype(float)
    if len(values) == 0 or not np.isfinite(values).all() or (values[:, 1] > values[:, 2]).any():
        raise CoverageError("Coverage inputs must be nonempty, finite, ordered intervals.")
    widths = values[:, 2] - values[:, 1]
    covered = (values[:, 0] >= values[:, 1]) & (values[:, 0] <= values[:, 2])
    return {"sample_count": int(len(values)), "empirical_coverage": float(covered.mean()),
            "average_interval_width": float(widths.mean()), "median_interval_width": float(np.median(widths))}


def coverage_by_horizon(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"horizon", "actual", "lower", "upper"}
    if required.difference(frame.columns):
        raise CoverageError("By-horizon coverage frame is incomplete.")
    rows = []
    for horizon, group in frame.groupby("horizon", sort=True):
        if int(horizon) not in range(1, 11):
            raise CoverageError("Coverage horizon must be 1..10.")
        rows.append({"horizon": int(horizon), **interval_diagnostics(group.actual, group.lower, group.upper)})
    return pd.DataFrame(rows)


def assert_no_future_fold_leakage(calibration_origins: pd.Series, evaluation_origin: Any) -> None:
    calibration = pd.to_datetime(calibration_origins, errors="raise")
    evaluation = pd.Timestamp(evaluation_origin)
    if calibration.empty or not calibration.lt(evaluation).all():
        raise CoverageError("Sequential coverage calibration includes the current or a future fold.")


def sequential_backtest_coverage(
    residuals: pd.DataFrame,
    coverage_levels: list[float] | tuple[float, ...],
    *,
    minimum_per_horizon: int,
    minimum_pooled: int,
    origin_column: str = "origin_week_start_date",
) -> pd.DataFrame:
    """Evaluate fold t using only residuals from strictly earlier origins."""
    needed = {origin_column, "horizon_weeks", "actual", "prediction", "absolute_residual", "source_type"}
    if needed.difference(residuals.columns) or residuals.empty:
        raise CoverageError("Sequential residual table is incomplete.")
    if not residuals.source_type.eq("frozen_rolling_oos").all():
        raise CoverageError("Sequential coverage requires frozen rolling OOS residuals.")
    levels = validate_coverage_levels(coverage_levels)
    work = residuals.copy()
    work[origin_column] = pd.to_datetime(work[origin_column], errors="raise")
    rows: list[dict[str, Any]] = []
    for origin in sorted(work[origin_column].unique()):
        current = work.loc[work[origin_column].eq(origin)]
        prior = work.loc[work[origin_column].lt(origin)]
        for horizon, evaluation in current.groupby("horizon_weeks", sort=True):
            local = prior.loc[prior.horizon_weeks.eq(horizon)]
            for level in levels:
                record = {"evaluation_origin": str(pd.Timestamp(origin).date()), "horizon": int(horizon),
                          "coverage_target": level, "evaluation_n": int(len(evaluation)),
                          "diagnostic_type": "sequential_historical_backtest"}
                if len(local) >= minimum_per_horizon:
                    calibration, source = local, f"earlier_horizon_{int(horizon)}"
                elif len(prior) >= minimum_pooled:
                    calibration, source = prior, "earlier_pooled_target"
                else:
                    rows.append({**record, "status": "UNAVAILABLE_INSUFFICIENT_EARLIER_FOLDS",
                                 "calibration_source": None, "calibration_n": int(len(prior)),
                                 "empirical_coverage": None, "average_interval_width": None,
                                 "median_interval_width": None})
                    continue
                assert_no_future_fold_leakage(calibration[origin_column], origin)
                quantile = finite_sample_quantile(calibration.absolute_residual, level)
                point = evaluation.prediction.to_numpy(dtype=float)
                lower = np.maximum(0.0, point - quantile)
                upper = np.maximum(lower, point + quantile)
                diag = interval_diagnostics(evaluation.actual, pd.Series(lower), pd.Series(upper))
                rows.append({**record, "status": "AVAILABLE", "calibration_source": source,
                             "calibration_n": int(len(calibration)), **{k: diag[k] for k in
                             ("empirical_coverage", "average_interval_width", "median_interval_width")}})
    return pd.DataFrame(rows)


def validate_coverage_language(text: str) -> None:
    forbidden = ("guaranteed 90% coverage", "guaranteed 80% coverage",
                 "95% confidence that the true value", "90% probability of being inside")
    lowered = text.lower()
    if any(phrase.lower() in lowered for phrase in forbidden):
        raise CoverageError("Reporting overstates the uncertainty guarantee.")
