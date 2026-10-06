from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from catboost import CatBoostClassifier, CatBoostRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from src.task1.explainability import deterministic_sample_positions
from src.task1.shap_adapter import (
    ShapAdapterError,
    explain_model,
    normalize_contributions,
)


def test_normalize_contribution_shapes_and_positive_class() -> None:
    two_dimensional = np.arange(12, dtype=float).reshape(3, 4)
    values, base = normalize_contributions(two_dimensional, n_rows=3, n_features=3)
    assert values.shape == (3, 3)
    assert base.tolist() == [3.0, 7.0, 11.0]
    three_dimensional = np.stack([two_dimensional, two_dimensional + 100], axis=1)
    values, base = normalize_contributions(
        three_dimensional, n_rows=3, n_features=3, positive_class_index=1
    )
    assert values[0, 0] == 100.0
    assert base[0] == 103.0


def test_catboost_regression_shap_reconstructs_raw_prediction() -> None:
    frame = pd.DataFrame({"x": np.linspace(-2, 2, 30), "z": np.arange(30) % 3})
    target = 2.0 * frame["x"] + frame["z"]
    model = CatBoostRegressor(iterations=25, depth=3, verbose=False, random_seed=42, allow_writing_files=False)
    model.fit(frame, target)
    result = explain_model(model, frame.iloc[:8], family="catboost", task="service", tolerance=1e-6)
    assert result.output_space == "raw_service_prediction"
    assert result.reconstruction_pass
    assert result.values.shape == (8, 2)


def test_catboost_binary_shap_reconstructs_positive_raw_margin_with_categories() -> None:
    train = pd.DataFrame({
        "category": ["a", "b"] * 20,
        "x": np.linspace(-2, 2, 40),
    })
    target = ((train["category"] == "b") | (train["x"] > 0)).astype(int)
    model = CatBoostClassifier(iterations=30, depth=3, verbose=False, random_seed=42, allow_writing_files=False)
    model.fit(train, target, cat_features=[0])
    explain = pd.DataFrame({"category": ["a", "unseen", None], "x": [-1.0, 0.5, np.nan]})
    explain["category"] = explain["category"].astype("string").fillna("__MISSING__")
    result = explain_model(
        model, explain, family="catboost", task="lateness",
        categorical_columns=["category"], positive_class_index=1, tolerance=1e-6,
    )
    assert result.output_space == "raw_margin_log_odds"
    assert result.reconstruction_pass
    assert np.isfinite(result.values).all()


def test_deterministic_sample_is_stable_and_small_population_uses_all_rows() -> None:
    frame = pd.DataFrame({"x": np.arange(100), "category": ["a", "b"] * 50})
    first = deterministic_sample_positions(frame, max_rows=15, seed=42)
    second = deterministic_sample_positions(frame, max_rows=15, seed=42)
    np.testing.assert_array_equal(first, second)
    np.testing.assert_array_equal(
        deterministic_sample_positions(frame.iloc[:4], max_rows=15, seed=42), np.arange(4)
    )


def test_unsupported_family_and_missing_positive_class_fail_cleanly() -> None:
    frame = pd.DataFrame({"x": [1.0]})
    with pytest.raises(ShapAdapterError, match="Unsupported"):
        explain_model(object(), frame, family="mystery", task="service")
    with pytest.raises(ShapAdapterError, match="positive-class"):
        explain_model(object(), frame, family="catboost", task="lateness")


def test_local_shap_tree_fallback_reconstructs_regression_and_positive_class() -> None:
    frame = pd.DataFrame({"x": [0.0, 1.0, 2.0, 3.0], "constant": [1.0] * 4})
    regressor = DecisionTreeRegressor(random_state=42).fit(frame, [1.0, 2.0, 4.0, 6.0])
    service = explain_model(regressor, frame.iloc[[0]], family="sklearn_tree", task="service")
    assert service.reconstruction_pass
    assert service.values.shape == (1, 2)
    assert service.values[0, 1] == pytest.approx(0.0)

    classifier = DecisionTreeClassifier(random_state=42).fit(frame, [0, 0, 1, 1])
    lateness = explain_model(
        classifier, frame, family="sklearn_tree", task="lateness", positive_class_index=1
    )
    assert lateness.output_space == "base_probability"
    assert lateness.reconstruction_pass
