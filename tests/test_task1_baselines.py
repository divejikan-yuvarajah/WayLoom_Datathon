from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.task1.baselines import (
    ConstantLateProbabilityBaseline, GlobalMedianServiceBaseline,
    HierarchicalLateRateBaseline, HierarchicalServiceMedianBaseline,
    Task1BaselineError, aggregate_fold_results, fit_predict_logistic_baseline,
)


def _X() -> pd.DataFrame:
    return pd.DataFrame(
        {"brand": ["Fresh", "Fresh", "Style", "Tech"], "dock_type": ["rear", "street", "rear", "mall"],
         "order_units": [1, 2, 3, 4], "category": ["a", "b", "a", "b"]}
    )


def test_dt130_global_median_even_and_validation_y_invariant() -> None:
    model = GlobalMedianServiceBaseline().fit(_X().iloc[:2], [10, 20])
    assert model.value_ == 15
    p1 = model.predict(_X().iloc[2:])
    p2 = model.predict(_X().iloc[2:])
    np.testing.assert_array_equal(p1, p2)
    with pytest.raises(Task1BaselineError):
        GlobalMedianServiceBaseline().fit(_X().iloc[:0], [])
    with pytest.raises(Task1BaselineError):
        GlobalMedianServiceBaseline().fit(_X().iloc[:1], [np.nan])


def test_dt131_dt132_hierarchical_service_fallbacks() -> None:
    x, y = _X().iloc[:3], [10, 30, 50]
    brand = HierarchicalServiceMedianBaseline(use_dock=False).fit(x, y)
    assert brand.predict(pd.DataFrame({"brand": ["Fresh", "Unknown"], "dock_type": ["mall", "x"]})).tolist() == [20.0, 30.0]
    brand_only = HierarchicalServiceMedianBaseline(use_dock=False).fit(x[["brand"]], y)
    assert brand_only.predict(pd.DataFrame({"brand": ["Fresh", "Unknown"]})).tolist() == [20.0, 30.0]
    dock = HierarchicalServiceMedianBaseline().fit(x, y)
    pred = dock.predict(pd.DataFrame({"brand": ["Fresh", "Fresh", "Unknown"], "dock_type": ["rear", "mall", "x"]}))
    assert pred.tolist() == [10.0, 20.0, 30.0]
    missing = dock.predict(pd.DataFrame({"brand": ["Fresh"], "dock_type": [None]}))
    assert missing.tolist() == [20.0]


def test_dt133_dt134_probability_baselines_and_fallbacks() -> None:
    x, y = _X().iloc[:3], [0, 1, 1]
    assert ConstantLateProbabilityBaseline().fit(x, y).predict_proba(_X().iloc[:1])[0] == pytest.approx(2 / 3)
    grouped = HierarchicalLateRateBaseline().fit(x, y)
    pred = grouped.predict_proba(pd.DataFrame({"brand": ["Fresh", "Fresh", "Unknown"], "dock_type": ["rear", "mall", "x"]}))
    assert pred[0] == 0.0
    assert pred[1] == 0.5
    assert pred[2] == pytest.approx(2 / 3)
    assert grouped.validation_group_counts_ == [1, 0, 0]
    assert ConstantLateProbabilityBaseline().fit(x, [0, 0, 0]).value_ == 0
    assert ConstantLateProbabilityBaseline().fit(x, [1, 1, 1]).value_ == 1
    assert np.all((pred >= 0) & (pred <= 1))


def test_dt136_single_class_logistic_is_unsupported_not_rebalanced() -> None:
    result = fit_predict_logistic_baseline(_X().iloc[:2], [0, 0], _X().iloc[2:])
    assert result.unsupported is True
    assert result.predictions is None


def test_dt137_aggregate_fold_results_schema_and_extrema() -> None:
    summary = aggregate_fold_results(pd.DataFrame([
        {"model_name": "service_global_median", "target": "service", "metric_name": "mae", "metric_value": 3.0, "fold_id": 1},
        {"model_name": "service_global_median", "target": "service", "metric_name": "mae", "metric_value": 1.0, "fold_id": 2},
    ]))
    row = summary.iloc[0]
    assert set(("fold_count", "mean", "std", "median", "min", "max", "best_fold", "worst_fold")) <= set(summary)
    assert row["fold_count"] == 2
    assert row["best_fold"] == 2
    assert row["worst_fold"] == 1
