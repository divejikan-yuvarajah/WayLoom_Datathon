from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.task1.explainability import build_explanation_registry, build_feature_importance
from src.task1.shap_adapter import ShapAdapterError, native_feature_importance


class FakeCatBoost:
    def __init__(self, values):
        self.values = values

    def get_feature_importance(self, *, type):
        assert type == "PredictionValuesChange"
        return self.values


def _summary(names: list[str], values: list[float]) -> pd.DataFrame:
    return pd.DataFrame({
        "feature_name": names,
        "mean_abs_shap": values,
        "rank": range(1, len(names) + 1),
    })


def test_native_importance_maps_names_and_ranks_deterministically() -> None:
    names = ["brand", "order_weight_kg", "planned_slack_to_close_min"]
    registry = build_explanation_registry(names)
    result = build_feature_importance(
        FakeCatBoost([0.4, 0.4, 0.1]), family="catboost", feature_names=names,
        registry=registry, shap_summary=_summary(names, [0.2, 0.1, 0.05]),
    )
    assert result["feature_name"].tolist() == ["brand", "order_weight_kg", "planned_slack_to_close_min"]
    assert result["rank"].tolist() == [1, 2, 3]
    assert set(result["importance_type"]) == {"catboost_prediction_values_change"}


def test_mean_abs_shap_is_explicit_fallback_not_fabricated_native_importance() -> None:
    names = ["a", "b"]
    result = build_feature_importance(
        object(), family="unsupported_for_native", feature_names=names,
        registry=build_explanation_registry(names), shap_summary=_summary(names, [0.1, 0.7]),
    )
    assert result["feature_name"].tolist() == ["b", "a"]
    assert set(result["importance_type"]) == {"mean_abs_shap_fallback"}


def test_bad_native_importance_shape_fails() -> None:
    with pytest.raises(ShapAdapterError, match="align"):
        native_feature_importance(FakeCatBoost([1.0]), family="catboost", feature_names=["a", "b"])


def test_unknown_feature_mapping_fails() -> None:
    names = ["a", "b"]
    with pytest.raises(KeyError):
        build_feature_importance(
            object(), family="none", feature_names=names,
            registry=build_explanation_registry(names), shap_summary=_summary(["a"], [1.0]),
        )
