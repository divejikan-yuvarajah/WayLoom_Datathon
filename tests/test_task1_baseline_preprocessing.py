from __future__ import annotations

import pandas as pd
import pytest

from src.task1.baseline_preprocessing import (
    build_fold_preprocessor, select_simple_baseline_features,
)
from src.task1.baselines import fit_predict_linear_baseline, fit_predict_logistic_baseline
from src.task1.feature_registry import build_feature_registry


def _train() -> pd.DataFrame:
    return pd.DataFrame(
        {"numeric": [1.0, None, 3.0, 4.0], "cat": ["a", "a", None, "b"],
         "brand": ["Fresh", "Fresh", "Style", "Style"], "dock_type": ["rear", "street", "rear", "street"],
         "outlet_id": ["id1", "id2", "id3", "id4"], "actual_travel_duration_min": [9, 9, 9, 9]}
    )


def test_dt135_registry_style_allow_list_excludes_identifiers_forbidden_and_history() -> None:
    x = _train().assign(outlet_prior_late_rate=0.5)
    columns = select_simple_baseline_features(x)
    assert "outlet_id" not in columns
    assert "actual_travel_duration_min" not in columns
    assert "outlet_prior_late_rate" not in columns
    assert {"numeric", "cat", "brand", "dock_type"} <= set(columns)


def test_dt135_fold_preprocess_train_only_and_unseen_category() -> None:
    train = _train().drop(columns=["actual_travel_duration_min"])
    valid = pd.DataFrame({"numeric": [100.0], "cat": ["unseen"], "brand": ["Tech"], "dock_type": ["mall"], "outlet_id": ["x"]})
    cols = select_simple_baseline_features(train)
    prep, _, _ = build_fold_preprocessor(train, cols)
    Xt = prep.fit_transform(train[cols])
    Xv = prep.transform(valid[cols])
    assert Xt.shape[1] == Xv.shape[1]
    linear = fit_predict_linear_baseline(train, [1, 2, 3, 4], valid)
    assert len(linear.predictions) == 1
    logistic = fit_predict_logistic_baseline(train, [0, 0, 1, 1], valid)
    assert logistic.predictions is not None
    assert 0 <= logistic.predictions[0] <= 1
    assert logistic.feature_columns == tuple(cols)
    assert logistic.convergence_warning is False


def test_dt135_preprocessor_statistics_and_vocabulary_are_train_only() -> None:
    train = pd.DataFrame({"numeric": [1.0, None, 3.0], "cat": ["a", "b", "a"]})
    valid = pd.DataFrame({"numeric": [999.0], "cat": ["future_only"]})
    registry = build_feature_registry(list(train.columns))
    result = fit_predict_linear_baseline(train, [2.0, 1.0, 0.0], valid, registry=registry)
    columns = result.preprocessor.named_steps["columns"]
    numeric = columns.named_transformers_["numeric"].named_steps["imputer"]
    categorical = columns.named_transformers_["categorical"].named_steps["one_hot"]
    assert numeric.statistics_.tolist() == [2.0]
    assert categorical.categories_[0].tolist() == ["a", "b"]
    assert result.predictions[0] < 0  # raw extrapolated prediction; no clipping.


def test_dt136_probability_shape_bounds_and_validation_y_invariance() -> None:
    train = pd.DataFrame({"numeric": [0.0, 1.0, 2.0, 3.0], "cat": ["a", "a", "b", "b"]})
    valid = pd.DataFrame({"numeric": [1.5, 2.5], "cat": ["unseen", "a"]})
    registry = build_feature_registry(list(train.columns))
    first = fit_predict_logistic_baseline(train, [0, 0, 1, 1], valid, registry=registry)
    second = fit_predict_logistic_baseline(train, [0, 0, 1, 1], valid, registry=registry)
    assert first.predictions.shape == (2,)
    assert ((first.predictions >= 0) & (first.predictions <= 1)).all()
    assert first.predictions.tolist() == pytest.approx(second.predictions.tolist())


def test_dt135_forbidden_and_target_columns_never_enter_model_inputs() -> None:
    train = pd.DataFrame({"planned_distance": [1, 2], "service_minutes": [9, 10], "late_flag": [0, 1]})
    assert select_simple_baseline_features(train) == ["planned_distance"]
