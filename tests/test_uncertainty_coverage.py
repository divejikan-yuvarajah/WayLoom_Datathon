import pandas as pd
import pytest

from src.uncertainty.coverage import (CoverageError, assert_no_future_fold_leakage,
    coverage_by_horizon, interval_diagnostics, sequential_backtest_coverage, validate_coverage_language)


def rolling():
    rows = []
    for fold, origin in enumerate(pd.date_range("2025-01-06", periods=3, freq="28D"), 1):
        for horizon in (1, 2):
            rows.append({"origin_week_start_date": origin, "horizon_weeks": horizon,
                "actual": 10 + fold, "prediction": 10.0, "absolute_residual": float(fold),
                "source_type": "frozen_rolling_oos", "fold": fold})
    return pd.DataFrame(rows)


def test_empirical_coverage_and_width():
    result = interval_diagnostics(pd.Series([1, 5]), pd.Series([0, 0]), pd.Series([2, 4]))
    assert result["empirical_coverage"] == 0.5
    assert result["average_interval_width"] == 3.0


def test_by_horizon_aggregation():
    frame = pd.DataFrame({"horizon": [1, 1, 2], "actual": [1, 3, 2],
                          "lower": [0, 0, 1], "upper": [2, 2, 3]})
    assert coverage_by_horizon(frame).horizon.tolist() == [1, 2]


def test_sequential_uses_only_earlier_folds_and_marks_early_unavailable():
    result = sequential_backtest_coverage(rolling(), [0.8], minimum_per_horizon=1, minimum_pooled=2)
    earliest = result.loc[result.evaluation_origin.eq("2025-01-06")]
    assert earliest.status.eq("UNAVAILABLE_INSUFFICIENT_EARLIER_FOLDS").all()
    later = result.loc[result.status.eq("AVAILABLE")]
    assert not later.empty
    assert later.diagnostic_type.eq("sequential_historical_backtest").all()


def test_future_fold_leakage_rejected():
    with pytest.raises(CoverageError):
        assert_no_future_fold_leakage(pd.Series(["2025-02-01"]), "2025-01-01")


def test_no_unsupported_confidence_guarantee_language():
    validate_coverage_language("90% target-coverage conformal-style interval")
    with pytest.raises(CoverageError):
        validate_coverage_language("Guaranteed 90% coverage")
