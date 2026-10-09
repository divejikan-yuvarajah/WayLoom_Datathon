"""Frozen, model-agnostic raw forecast evaluation for Task 2A."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import pandas as pd


HORIZONS = tuple(range(1, 11))
SERIES = ("depot", "brand")


class ForecastMetricError(ValueError):
    """A prediction set cannot be evaluated under the frozen metric contract."""


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Use JSON-safe nulls so reordered inputs produce identical results."""
    object_frame = frame.astype(object)
    return object_frame.where(pd.notna(object_frame), None).to_dict(orient="records")


def _numeric(values: Any, label: str, *, allow_nonfinite: bool = False) -> np.ndarray:
    try:
        array = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as error:
        raise ForecastMetricError(f"{label} must be numeric.") from error
    if array.ndim != 1:
        raise ForecastMetricError(f"{label} must be one-dimensional.")
    if not allow_nonfinite and not np.isfinite(array).all():
        raise ForecastMetricError(f"{label} contains a nonfinite value.")
    return array


def forecast_prediction_diagnostics(total_pred: Any, chilled_pred: Any | None = None) -> dict[str, int]:
    """Count raw prediction problems without modifying their values."""
    total = _numeric(total_pred, "total prediction", allow_nonfinite=True)
    if chilled_pred is None:
        chilled = None
    else:
        chilled = _numeric(chilled_pred, "chilled prediction", allow_nonfinite=True)
        if len(total) != len(chilled):
            raise ForecastMetricError("Total and chilled predictions have different lengths.")
    invalid = ~np.isfinite(total)
    if chilled is not None:
        invalid |= ~np.isfinite(chilled)
    return {
        "n": int(len(total)),
        "nonfinite_prediction_count": int(invalid.sum()),
        "negative_prediction_count": int((np.isfinite(total) & (total < 0)).sum() + (
            (np.isfinite(chilled) & (chilled < 0)).sum() if chilled is not None else 0)),
        "chilled_gt_total_count": int((np.isfinite(total) & np.isfinite(chilled) & (chilled > total)).sum()) if chilled is not None else 0,
    }


def forecast_regression_metrics(y_true: Any, y_pred: Any) -> dict[str, float | int | None]:
    """MAE primary; RMSE, WAPE, bias and P90 absolute error are secondary."""
    truth = _numeric(y_true, "target")
    prediction = _numeric(y_pred, "prediction")
    if len(truth) != len(prediction) or len(truth) == 0:
        raise ForecastMetricError("Target and prediction lengths must match and be nonempty.")
    if (truth < 0).any():
        raise ForecastMetricError("Target volume must be nonnegative.")
    errors = prediction - truth
    absolute = np.abs(errors)
    denominator = float(truth.sum())
    return {
        "n": int(len(truth)),
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.mean(errors ** 2))),
        "wape": float(100 * absolute.sum() / denominator) if denominator > 0 else None,
        "mean_bias_m3": float(errors.mean()),
        "p90_absolute_error": float(np.percentile(absolute, 90)),
    }


def _validate_scored_rows(rows: pd.DataFrame, expected_backtest_ids: Iterable[str],
                          expected_series: Iterable[tuple[str, str]]) -> pd.DataFrame:
    required = ["backtest_id", *SERIES, "horizon_weeks", "target_total_volume_m3",
                "target_chilled_volume_m3", "pred_total_volume_m3", "pred_chilled_volume_m3"]
    missing = [name for name in required if name not in rows]
    if missing:
        raise ForecastMetricError("Scored rows missing columns: " + ", ".join(missing))
    if rows.empty or rows[required[:4]].isna().any().any():
        raise ForecastMetricError("Scored rows contain no data or missing identifiers.")
    required_backtests = tuple(expected_backtest_ids)
    required_series = tuple(tuple(series) for series in expected_series)
    if not required_backtests or len(set(required_backtests)) != len(required_backtests) or not required_series or len(set(required_series)) != len(required_series):
        raise ForecastMetricError("Frozen backtest IDs and required series must be nonempty and unique.")
    if set(rows.backtest_id) != set(required_backtests) or set(map(tuple, rows[list(SERIES)].drop_duplicates().itertuples(index=False, name=None))) != set(required_series):
        raise ForecastMetricError("Scored rows do not match the frozen backtest IDs and required series.")
    if rows.duplicated(["backtest_id", *SERIES, "horizon_weeks"]).any():
        raise ForecastMetricError("Scored rows contain duplicate backtest/series/horizon keys.")
    result = rows.sort_values(["backtest_id", *SERIES, "horizon_weeks"], kind="stable").reset_index(drop=True).copy()
    for _, group in result.groupby(["backtest_id", *SERIES], sort=False):
        if len(group) != 10 or sorted(group.horizon_weeks.tolist()) != list(HORIZONS):
            raise ForecastMetricError("Each backtest and series requires exact horizons 1..10.")
        if group.brand.iloc[0] != "Fresh" and not group.target_chilled_volume_m3.eq(0).all():
            raise ForecastMetricError("Style and Tech chilled targets must be exact structural zeros.")
    series_by_backtest = [
        set(map(tuple, group[list(SERIES)].drop_duplicates().itertuples(index=False, name=None)))
        for _, group in result.groupby("backtest_id", sort=False)
    ]
    if any(series != series_by_backtest[0] for series in series_by_backtest[1:]):
        raise ForecastMetricError("Required series differ across backtests.")
    for column in ("target_total_volume_m3", "target_chilled_volume_m3"):
        values = _numeric(result[column], column)
        if (values < 0).any():
            raise ForecastMetricError(f"{column} contains negative targets.")
    diagnostics = forecast_prediction_diagnostics(result.pred_total_volume_m3, result.pred_chilled_volume_m3)
    if diagnostics["nonfinite_prediction_count"]:
        raise ForecastMetricError("Raw predictions contain nonfinite values; diagnostics must be reviewed.")
    return result


def _scored_metrics(group: pd.DataFrame, target: str) -> dict[str, Any]:
    label = f"target_{target}_volume_m3"
    prediction = f"pred_{target}_volume_m3"
    metrics = forecast_regression_metrics(group[label], group[prediction])
    diagnostics = forecast_prediction_diagnostics(group.pred_total_volume_m3, group.pred_chilled_volume_m3)
    metrics.update({
        "negative_prediction_count": int((group[prediction] < 0).sum()),
        "nonfinite_prediction_count": diagnostics["nonfinite_prediction_count"],
        "chilled_gt_total_count": diagnostics["chilled_gt_total_count"],
    })
    return metrics


def evaluate_forecast_per_series(rows: pd.DataFrame, *, expected_backtest_ids: Iterable[str],
                                 expected_series: Iterable[tuple[str, str]]) -> pd.DataFrame:
    frame = _validate_scored_rows(rows, expected_backtest_ids, expected_series)
    records: list[dict[str, Any]] = []
    for (backtest_id, depot, brand), group in frame.groupby(["backtest_id", *SERIES], sort=True):
        records.append({"backtest_id": backtest_id, "depot": depot, "brand": brand,
                        "target": "total", "coverage_status": "COMPLETE_10_WEEK", "chilled_status": None,
                        **_scored_metrics(group, "total")})
        if brand == "Fresh":
            records.append({"backtest_id": backtest_id, "depot": depot, "brand": brand,
                            "target": "chilled", "coverage_status": "COMPLETE_10_WEEK", "chilled_status": "EVALUATED_FRESH",
                            **_scored_metrics(group, "chilled")})
        else:
            records.append({"backtest_id": backtest_id, "depot": depot, "brand": brand,
                            "target": "chilled", "coverage_status": "COMPLETE_10_WEEK", "chilled_status": "STRUCTURAL_ZERO",
                            "n": int(len(group)), "mae": None, "rmse": None, "wape": None,
                            "mean_bias_m3": None, "p90_absolute_error": None,
                            "negative_prediction_count": int((group.pred_chilled_volume_m3 < 0).sum()),
                            "nonfinite_prediction_count": 0,
                            "chilled_gt_total_count": int((group.pred_chilled_volume_m3 > group.pred_total_volume_m3).sum())})
    return pd.DataFrame(records)


def summarize_backtest_stability(per_series: pd.DataFrame) -> pd.DataFrame:
    """Summarize completed per-series scores across every frozen backtest."""
    frame = per_series.loc[per_series.chilled_status.ne("STRUCTURAL_ZERO")].copy()
    records = []
    for (depot, brand, target), group in frame.groupby([*SERIES, "target"], sort=True):
        wape = group.wape.dropna()
        records.append({"depot": depot, "brand": brand, "target": target,
                        "backtest_count": int(len(group)), "mean_mae": float(group.mae.mean()),
                        "std_mae": float(group.mae.std(ddof=0)), "median_mae": float(group.mae.median()),
                        "worst_backtest_mae": float(group.mae.max()),
                        "mean_rmse": float(group.rmse.mean()),
                        "mean_wape": float(wape.mean()) if len(wape) else None,
                        "mean_bias_m3": float(group.mean_bias_m3.mean())})
    return pd.DataFrame(records)


def evaluate_forecast_by_horizon(rows: pd.DataFrame, *, expected_backtest_ids: Iterable[str],
                                 expected_series: Iterable[tuple[str, str]]) -> pd.DataFrame:
    frame = _validate_scored_rows(rows, expected_backtest_ids, expected_series)
    records = []
    for horizon, group in frame.groupby("horizon_weeks", sort=True):
        records.append({"target": "total", "horizon_weeks": int(horizon), **_scored_metrics(group, "total")})
        fresh = group.loc[group.brand.eq("Fresh")]
        if not fresh.empty:
            records.append({"target": "chilled", "horizon_weeks": int(horizon), **_scored_metrics(fresh, "chilled")})
    return pd.DataFrame(records)


def equal_weight_series_metrics(per_series_pooled: pd.DataFrame, target: str) -> dict[str, float | int]:
    """Average one pooled score per series with equal series weight."""
    subset = per_series_pooled.loc[per_series_pooled.target.eq(target)]
    if subset.empty or subset.duplicated(list(SERIES)).any():
        raise ForecastMetricError("Macro aggregation requires one score per eligible series.")
    return {"series_count": int(len(subset)), "mae": float(subset.mae.mean()),
            "rmse": float(subset.rmse.mean())}


def evaluate_forecast_overall(rows: pd.DataFrame, *, expected_backtest_ids: Iterable[str],
                              expected_series: Iterable[tuple[str, str]]) -> dict[str, Any]:
    """Return pooled and equal-series-weight scores with full backtest diagnostics."""
    frozen_backtests = tuple(expected_backtest_ids)
    frozen_series = tuple(tuple(series) for series in expected_series)
    frame = _validate_scored_rows(rows, frozen_backtests, frozen_series)
    per_series = evaluate_forecast_per_series(frame, expected_backtest_ids=frozen_backtests,
                                              expected_series=frozen_series)
    fresh = frame.loc[frame.brand.eq("Fresh")]
    per_series_pooled = []
    for (depot, brand), group in frame.groupby(list(SERIES), sort=True):
        per_series_pooled.append({"depot": depot, "brand": brand, "target": "total", **_scored_metrics(group, "total")})
        if brand == "Fresh":
            per_series_pooled.append({"depot": depot, "brand": brand, "target": "chilled", **_scored_metrics(group, "chilled")})
    pooled_series = pd.DataFrame(per_series_pooled)
    macro_chilled = pooled_series.loc[pooled_series.target.eq("chilled")]
    backtests = []
    for backtest_id, group in frame.groupby("backtest_id", sort=True):
        backtests.append({"backtest_id": backtest_id, "target": "total", **_scored_metrics(group, "total")})
        chilled_group = group.loc[group.brand.eq("Fresh")]
        if not chilled_group.empty:
            backtests.append({"backtest_id": backtest_id, "target": "chilled", **_scored_metrics(chilled_group, "chilled")})
    backtest_frame = pd.DataFrame(backtests)
    def _overall_stability(target: str) -> dict[str, Any] | None:
        subset = backtest_frame.loc[backtest_frame.target.eq(target)].sort_values("backtest_id")
        if subset.empty:
            return None
        best = subset.sort_values(["mae", "backtest_id"], kind="stable").iloc[0]
        worst = subset.sort_values(["mae", "backtest_id"], ascending=[False, True], kind="stable").iloc[0]
        return {"backtest_count": int(len(subset)), "mean_backtest_mae": float(subset.mae.mean()),
                "std_backtest_mae": float(subset.mae.std(ddof=0)),
                "best_backtest_id": best.backtest_id, "worst_backtest_id": worst.backtest_id}
    return {
        "metric_contract": {"total_primary": "mae", "chilled_primary": "mae", "chilled_primary_population": "Fresh",
                            "wape_zero_denominator": None, "raw_predictions": True},
        "total_micro": _scored_metrics(frame, "total"),
        "total_macro_series": equal_weight_series_metrics(pooled_series, "total"),
        "fresh_chilled_micro": _scored_metrics(fresh, "chilled") if not fresh.empty else None,
        "fresh_chilled_macro_series": equal_weight_series_metrics(pooled_series, "chilled") if not macro_chilled.empty else None,
        "per_series": _records(per_series),
        "per_series_stability": _records(summarize_backtest_stability(per_series)),
        "by_backtest": _records(backtest_frame),
        "overall_backtest_stability": {"total": _overall_stability("total"), "chilled": _overall_stability("chilled")},
        "by_horizon": _records(evaluate_forecast_by_horizon(frame, expected_backtest_ids=frozen_backtests,
                                                              expected_series=frozen_series)),
    }
