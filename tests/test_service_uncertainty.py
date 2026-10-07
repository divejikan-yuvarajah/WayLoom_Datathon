import numpy as np
import pandas as pd
import pytest

from src.uncertainty.service_intervals import (ServiceIntervalError, build_service_intervals,
    calibrate_service_quantiles, calibrate_service_segment)


def residuals(scores=(1.0, 2.0, 3.0, 4.0), *, source="frozen_oos_validation"):
    actual = np.asarray(scores, dtype=float) + 10
    return pd.DataFrame({"actual": actual, "prediction": np.full(len(actual), 10.0),
        "absolute_residual": scores, "fold": range(1, len(actual) + 1), "source_type": source,
        "brand": ["Fresh"] * len(actual)})


def submission(points=(1.0, 10.0)):
    return pd.DataFrame({"delivery_id": [f"d{i}" for i in range(len(points))],
        "pred_service_min": points, "pred_late_prob": [0.2] * len(points)})


def test_oos_required_and_in_sample_rejected():
    with pytest.raises(ServiceIntervalError):
        calibrate_service_quantiles(residuals(source="in_sample"), [0.8])


def test_interval_invariants_nested_clipping_and_point_unchanged():
    official = submission()
    result, _ = build_service_intervals(official, residuals(), [0.8, 0.9])
    assert result.pred_service_min.tolist() == official.pred_service_min.tolist()
    assert (result.service_lower_80 >= 0).all()
    assert (result.service_lower_80 <= result.pred_service_min).all()
    assert (result.service_upper_80 >= result.pred_service_min).all()
    assert (result.service_width_80 <= result.service_width_90).all()
    assert result.service_lower_90.iloc[0] == 0.0


def test_zero_residual_gives_zero_width():
    result, _ = build_service_intervals(submission(), residuals((0, 0, 0, 0)), [0.8])
    assert result.service_width_80.eq(0).all()


def test_deterministic_calibration():
    assert calibrate_service_quantiles(residuals(), [0.8, 0.9]) == calibrate_service_quantiles(residuals(), [0.8, 0.9])


def test_segment_falls_back_to_global_when_sparse():
    q, source, n = calibrate_service_segment(residuals(), 0.8, segment_column="brand",
        segment_value="Fresh", minimum_segment_count=30)
    assert (q, source, n) == (4.0, "global_fallback", 4)


def test_insufficient_global_residuals_rejected():
    with pytest.raises(ServiceIntervalError):
        calibrate_service_quantiles(residuals(), [0.8], minimum_count=5)
