"""Chronology-safe probability calibration utilities for Phase 09."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from src.task1.metrics import expected_calibration_error, lateness_probability_metrics


class Task1CalibrationError(ValueError):
    """Raised when calibration protocol violates frozen constraints."""


@dataclass(frozen=True)
class ChronologicalCalibrationSplit:
    fit_index: pd.Index
    eval_index: pd.Index
    fit_dates: tuple[pd.Timestamp, ...]
    eval_dates: tuple[pd.Timestamp, ...]


def reliability_table(y_true: Any, y_prob: Any, *, bins: int = 10) -> pd.DataFrame:
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(y_prob, dtype=float)
    if len(y) == 0 or len(y) != len(p):
        raise Task1CalibrationError("Calibration arrays must be same non-empty length.")
    if ((p < 0) | (p > 1)).any():
        raise Task1CalibrationError("Probabilities must be in [0,1].")
    work = pd.DataFrame({"y": y, "p": p})
    n_unique = int(work["p"].nunique())
    q = max(1, min(int(bins), n_unique))
    bucket = pd.qcut(work["p"], q=q, labels=False, duplicates="drop")
    if bucket.isna().any():
        bucket = bucket.fillna(0)
    work["bin"] = bucket.astype(int)
    rows = []
    for b, grp in work.groupby("bin", sort=True):
        rows.append(
            {
                "bin": int(b),
                "n": int(len(grp)),
                "mean_predicted_probability": float(grp["p"].mean()),
                "observed_late_rate": float(grp["y"].mean()),
                "absolute_gap": float(abs(grp["p"].mean() - grp["y"].mean())),
            }
        )
    return pd.DataFrame(rows)


def chronological_calibration_split(
    frame: pd.DataFrame,
    *,
    date_col: str = "validation_date",
    fit_fraction: float = 0.70,
) -> ChronologicalCalibrationSplit:
    if date_col not in frame.columns:
        raise Task1CalibrationError(f"Missing date column: {date_col}")
    if not 0.0 < fit_fraction < 1.0:
        raise Task1CalibrationError("fit_fraction must be between 0 and 1.")
    dates = pd.to_datetime(frame[date_col], errors="raise").dt.normalize()
    unique_dates = sorted(dates.unique())
    if len(unique_dates) < 2:
        raise Task1CalibrationError("Need at least two unique dates for chronological calibration split.")
    cut = max(1, min(len(unique_dates) - 1, int(np.floor(len(unique_dates) * fit_fraction))))
    fit_dates = tuple(pd.Timestamp(d) for d in unique_dates[:cut])
    eval_dates = tuple(pd.Timestamp(d) for d in unique_dates[cut:])
    fit_idx = frame.index[dates.isin(fit_dates)]
    eval_idx = frame.index[dates.isin(eval_dates)]
    if set(fit_dates) & set(eval_dates):
        raise Task1CalibrationError("Same-date calibration atomicity violated.")
    return ChronologicalCalibrationSplit(fit_idx, eval_idx, fit_dates, eval_dates)


def calibrate_sigmoid(train_prob: Any, train_y: Any, eval_prob: Any) -> np.ndarray:
    p_train = np.asarray(train_prob, dtype=float)
    y_train = np.asarray(train_y, dtype=float)
    p_eval = np.asarray(eval_prob, dtype=float)
    eps = np.finfo(float).eps
    logit_train = np.log(np.clip(p_train, eps, 1 - eps) / np.clip(1 - p_train, eps, 1 - eps))
    logit_eval = np.log(np.clip(p_eval, eps, 1 - eps) / np.clip(1 - p_eval, eps, 1 - eps))
    model = LogisticRegression(solver="lbfgs", max_iter=2000, C=1.0, class_weight=None, random_state=42)
    model.fit(logit_train.reshape(-1, 1), y_train)
    out = model.predict_proba(logit_eval.reshape(-1, 1))[:, 1]
    return np.asarray(out, dtype=float)


def calibrate_isotonic(train_prob: Any, train_y: Any, eval_prob: Any, *, minimum_rows: int = 20) -> np.ndarray | None:
    p_train = np.asarray(train_prob, dtype=float)
    y_train = np.asarray(train_y, dtype=float)
    if len(p_train) < minimum_rows or len(np.unique(y_train)) < 2:
        return None
    model = IsotonicRegression(out_of_bounds="clip")
    model.fit(p_train, y_train)
    out = model.predict(np.asarray(eval_prob, dtype=float))
    return np.asarray(out, dtype=float)


def compare_probability_variants(y_true: Any, variants: dict[str, np.ndarray]) -> pd.DataFrame:
    """Compare raw/sigmoid/isotonic on the exact same eval population."""
    y = np.asarray(y_true, dtype=float)
    rows = []
    for name, prob in variants.items():
        p = np.asarray(prob, dtype=float)
        metrics = lateness_probability_metrics(y, p)
        rows.append(
            {
                "variant": name,
                "log_loss": float(metrics["log_loss"]),
                "brier_score": float(metrics["brier_score"]),
                "calibration_error": float(metrics["calibration_error"]),
                "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
                "average_precision": float(average_precision_score(y, p)) if len(np.unique(y)) == 2 else None,
            }
        )
    return pd.DataFrame(rows).sort_values(["log_loss", "brier_score", "variant"], kind="stable").reset_index(drop=True)

