from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.task1.metrics import (
    Task1MetricError,
    lateness_probability_metrics,
    lateness_segment_metrics,
    regression_metrics,
    regression_segment_metrics,
)


def test_dt127_regression_metrics_hand_calculated_and_negative_diagnostic() -> None:
    result = regression_metrics([1, 2, 3], [1, 0, 5])
    assert result["mae"] == pytest.approx(4 / 3)
    assert result["rmse"] == pytest.approx(np.sqrt(8 / 3))
    assert result["median_absolute_error"] == 2.0
    assert result["p90_absolute_error"] == pytest.approx(2.0)
    assert regression_metrics([1], [-1])["negative_prediction_count"] == 1
    assert regression_metrics([1, 2], [1, 2])["mae"] == 0.0


def test_dt127_rejects_invalid_lengths_and_nonfinite() -> None:
    with pytest.raises(Task1MetricError, match="equal length"):
        regression_metrics([1], [1, 2])
    with pytest.raises(Task1MetricError, match="finite"):
        regression_metrics([1], [np.nan])


def test_dt128_probability_metrics_and_single_class_behavior() -> None:
    result = lateness_probability_metrics([0, 1], [0.1, 0.8])
    assert result["brier_score"] == pytest.approx((0.01 + 0.04) / 2)
    assert result["log_loss"] > 0
    assert result["roc_auc"] == 1.0
    single = lateness_probability_metrics([0, 0], [0.1, 0.2])
    assert single["roc_auc"] is None
    assert single["average_precision"] is None


def test_dt128_rejects_invalid_probabilities() -> None:
    with pytest.raises(Task1MetricError, match=r"\[0,1\]"):
        lateness_probability_metrics([0, 1], [0.0, 1.1])


def test_dt129_segment_metrics_report_low_support_and_safe_fields() -> None:
    frame = pd.DataFrame({"brand": ["Fresh", "Fresh", "Style"], "dock_type": ["rear", "rear", "street"]})
    reg = regression_segment_metrics(frame, [1, 2, 3], [1, 3, 4], "brand", minimum_n=3)
    assert all(x["support_status"] == "LOW_SUPPORT" for x in reg)
    prob = lateness_segment_metrics(
        frame, [0, 1, 0], [0.2, 0.8, 0.3], "brand",
        minimum_n=3, minimum_positive_for_auc=2, minimum_negative_for_auc=2,
    )
    assert all(x["support_status"] == "LOW_SUPPORT" for x in prob)
    assert all(x["roc_auc"] is None for x in prob)
    with pytest.raises(Task1MetricError, match="Forbidden"):
        regression_segment_metrics(frame.assign(arrival_time="x"), [1, 2, 3], [1, 2, 3], "arrival_time")
