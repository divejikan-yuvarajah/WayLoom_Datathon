"""Synthetic Phase 16 predictor and fold-only preprocessing checks."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.task2a.model_preprocessing import (ModelPreprocessingError, feature_profile,
    lightgbm_fold_preprocessor, select_predictors)


def test_safe_phase13_profile_excludes_labels_and_metadata() -> None:
    profile = feature_profile()
    assert profile["forbidden_feature_count"] == 0
    assert "depot" in profile["categorical"] and "brand" in profile["categorical"]
    assert "target_total_volume_m3" not in profile["columns"]
    assert "target_chilled_volume_m3" not in profile["columns"]
    assert "origin_week_start_date" not in profile["columns"]
    assert profile["registry_hash"] == feature_profile()["registry_hash"]


def test_lightgbm_preprocessing_fits_train_only_and_accepts_unseen_category() -> None:
    profile = {"columns": ["depot", "brand", "total_lag_1"],
               "categorical": ["depot", "brand"], "numeric": ["total_lag_1"]}
    train = pd.DataFrame({"depot": ["A", "A", "B"], "brand": ["Fresh"] * 3,
                          "total_lag_1": [1.0, np.nan, 3.0], "target_total_volume_m3": [9, 9, 9]})
    valid = pd.DataFrame({"depot": ["UNSEEN"], "brand": [None], "total_lag_1": [np.nan],
                          "target_total_volume_m3": [999]})
    x_train, x_valid = select_predictors(train, profile), select_predictors(valid, profile)
    transformer = lightgbm_fold_preprocessor(profile)
    transformer.fit(x_train)
    transformed = transformer.transform(x_valid)
    assert transformed.shape[0] == 1
    assert np.isfinite(transformed.toarray() if hasattr(transformed, "toarray") else transformed).all()
    assert transformer.named_transformers_["numeric"].statistics_[0] == 2.0
    assert "UNSEEN" not in transformer.named_transformers_["categorical"].named_steps["onehot"].categories_[0]
    assert "target_total_volume_m3" not in x_train and "target_total_volume_m3" not in x_valid


def test_missing_or_infinite_predictor_is_rejected() -> None:
    profile = {"columns": ["depot", "total_lag_1"], "categorical": ["depot"],
               "numeric": ["total_lag_1"]}
    with pytest.raises(ModelPreprocessingError, match="missing"):
        select_predictors(pd.DataFrame({"depot": ["A"]}), profile)
    with pytest.raises(ModelPreprocessingError, match="Infinite"):
        select_predictors(pd.DataFrame({"depot": ["A"], "total_lag_1": [np.inf]}), profile)
