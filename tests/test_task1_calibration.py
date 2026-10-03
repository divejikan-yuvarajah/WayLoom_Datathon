from __future__ import annotations

import numpy as np
import pandas as pd

from src.task1.calibration import (
    calibrate_isotonic,
    calibrate_sigmoid,
    chronological_calibration_split,
    compare_probability_variants,
    reliability_table,
)


def test_reliability_table_and_split_are_deterministic() -> None:
    frame = pd.DataFrame(
        {
            "validation_date": pd.to_datetime(
                ["2025-01-01", "2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]
            ),
            "late_flag": [0, 1, 0, 1, 0, 1],
            "pred_late_prob": [0.1, 0.2, 0.2, 0.8, 0.9, 0.7],
        }
    )
    rel = reliability_table(frame["late_flag"], frame["pred_late_prob"], bins=10)
    assert rel["n"].sum() == len(frame)
    split = chronological_calibration_split(frame, date_col="validation_date", fit_fraction=0.7)
    fit_dates = set(frame.loc[split.fit_index, "validation_date"].dt.normalize())
    eval_dates = set(frame.loc[split.eval_index, "validation_date"].dt.normalize())
    assert fit_dates.isdisjoint(eval_dates)


def test_sigmoid_isotonic_and_comparison() -> None:
    y = np.array([0, 1, 0, 1, 0, 1], dtype=float)
    p = np.array([0.2, 0.7, 0.3, 0.8, 0.25, 0.75], dtype=float)
    sig = calibrate_sigmoid(p[:4], y[:4], p[4:])
    iso = calibrate_isotonic(p[:4], y[:4], p[4:], minimum_rows=2)
    assert ((sig >= 0) & (sig <= 1)).all()
    assert iso is not None and ((iso >= 0) & (iso <= 1)).all()
    cmp = compare_probability_variants(y[4:], {"raw": p[4:], "sigmoid": sig, "isotonic": iso})
    assert cmp.iloc[0]["variant"] in {"raw", "sigmoid", "isotonic"}


def test_isotonic_insufficient_support_skip() -> None:
    y = np.array([1, 1, 1], dtype=float)
    p = np.array([0.8, 0.9, 0.85], dtype=float)
    assert calibrate_isotonic(p, y, np.array([0.7, 0.6], dtype=float), minimum_rows=3) is None
