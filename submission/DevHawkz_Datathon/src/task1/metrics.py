"""Frozen, model-agnostic Task 1 validation metrics (Phase 07)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class Task1MetricError(ValueError):
    """Raised for invalid labels, predictions, or segment definitions."""


FORBIDDEN_SEGMENT_FIELDS = {
    "actual_depart_time", "actual_travel_duration_min", "arrival_time",
    "leave_outlet_time", "service_start_dt", "service_minutes", "late_flag",
}


def _numeric_pair(y_true: Any, y_pred: Any, *, probability: bool = False) -> tuple[np.ndarray, np.ndarray]:
    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    if true.ndim != 1 or pred.ndim != 1 or len(true) != len(pred):
        raise Task1MetricError("y_true and y_pred must be one-dimensional and equal length.")
    if len(true) == 0:
        raise Task1MetricError("Metric inputs must not be empty.")
    if not np.isfinite(true).all() or not np.isfinite(pred).all():
        raise Task1MetricError("Labels and predictions must be finite.")
    if probability:
        if not set(np.unique(true)).issubset({0.0, 1.0}):
            raise Task1MetricError("Probability metric labels must be binary 0/1.")
        if ((pred < 0) | (pred > 1)).any():
            raise Task1MetricError("Predicted probabilities must be in [0,1]; no clipping is applied.")
    return true, pred


def regression_metrics(y_true: Any, y_pred: Any) -> dict[str, float | int]:
    true, pred = _numeric_pair(y_true, y_pred)
    ae = np.abs(true - pred)
    return {
        "n": int(len(true)),
        "mae": float(np.mean(ae)),
        "rmse": float(np.sqrt(np.mean((true - pred) ** 2))),
        "median_absolute_error": float(np.median(ae)),
        "p90_absolute_error": float(np.percentile(ae, 90)),
        "negative_prediction_count": int(np.sum(pred < 0)),
        "nonfinite_prediction_count": 0,
    }


def _roc_auc(true: np.ndarray, score: np.ndarray) -> float | None:
    pos, neg = int(np.sum(true == 1)), int(np.sum(true == 0))
    if not pos or not neg:
        return None
    ranks = pd.Series(score).rank(method="average").to_numpy()
    return float((ranks[true == 1].sum() - pos * (pos + 1) / 2) / (pos * neg))


def _average_precision(true: np.ndarray, score: np.ndarray) -> float | None:
    positives = int(np.sum(true == 1))
    if not positives:
        return None
    order = np.argsort(-score, kind="stable")
    sorted_true = true[order]
    tp = np.cumsum(sorted_true)
    precision = tp / np.arange(1, len(true) + 1)
    return float(np.sum(precision[sorted_true == 1]) / positives)


def expected_calibration_error(y_true: Any, y_prob: Any, *, bins: int = 10) -> float:
    true, prob = _numeric_pair(y_true, y_prob, probability=True)
    bucket = np.minimum((prob * bins).astype(int), bins - 1)
    ece = 0.0
    for idx in range(bins):
        mask = bucket == idx
        if mask.any():
            ece += float(mask.mean() * abs(true[mask].mean() - prob[mask].mean()))
    return float(ece)


def lateness_probability_metrics(y_true: Any, y_prob: Any) -> dict[str, float | int | None]:
    true, prob = _numeric_pair(y_true, y_prob, probability=True)
    eps = np.finfo(float).eps
    stable = np.clip(prob, eps, 1 - eps)  # numerical log stability only
    return {
        "n": int(len(true)),
        "positive_count": int(np.sum(true == 1)),
        "negative_count": int(np.sum(true == 0)),
        "log_loss": float(-np.mean(true * np.log(stable) + (1 - true) * np.log(1 - stable))),
        "brier_score": float(np.mean((prob - true) ** 2)),
        "roc_auc": _roc_auc(true, prob),
        "average_precision": _average_precision(true, prob),
        "calibration_error": expected_calibration_error(true, prob),
    }


def regression_segment_metrics(
    frame: pd.DataFrame, y_true: Any, y_pred: Any, segment: str, *, minimum_n: int = 30
) -> list[dict[str, Any]]:
    if segment in FORBIDDEN_SEGMENT_FIELDS:
        raise Task1MetricError(f"Forbidden segment field: {segment}")
    if segment not in frame.columns:
        raise Task1MetricError(f"Segment field unavailable: {segment}")
    true, pred = _numeric_pair(y_true, y_pred)
    if len(frame) != len(true):
        raise Task1MetricError("Segment frame does not align with metrics arrays.")
    work = pd.DataFrame({"segment": frame[segment].fillna("MISSING"), "y": true, "p": pred})
    result: list[dict[str, Any]] = []
    for value, grp in work.groupby("segment", dropna=False):
        row = {"segment": segment, "value": str(value), **regression_metrics(grp["y"], grp["p"])}
        row["support_status"] = "LOW_SUPPORT" if row["n"] < minimum_n else "SUFFICIENT_SUPPORT"
        result.append(row)
    return result


def lateness_segment_metrics(
    frame: pd.DataFrame, y_true: Any, y_prob: Any, segment: str, *, minimum_n: int = 30,
    minimum_positive_for_auc: int = 5, minimum_negative_for_auc: int = 5,
) -> list[dict[str, Any]]:
    if segment in FORBIDDEN_SEGMENT_FIELDS:
        raise Task1MetricError(f"Forbidden segment field: {segment}")
    if segment not in frame.columns:
        raise Task1MetricError(f"Segment field unavailable: {segment}")
    true, prob = _numeric_pair(y_true, y_prob, probability=True)
    work = pd.DataFrame({"segment": frame[segment].fillna("MISSING"), "y": true, "p": prob})
    result: list[dict[str, Any]] = []
    for value, grp in work.groupby("segment", dropna=False):
        row = {"segment": segment, "value": str(value), **lateness_probability_metrics(grp["y"], grp["p"])}
        row["observed_late_rate"] = float(grp["y"].mean())
        enough_auc = row["positive_count"] >= minimum_positive_for_auc and row["negative_count"] >= minimum_negative_for_auc
        if not enough_auc:
            row["roc_auc"] = None
            row["average_precision"] = None
        row["support_status"] = "LOW_SUPPORT" if row["n"] < minimum_n else "SUFFICIENT_SUPPORT"
        result.append(row)
    return result
