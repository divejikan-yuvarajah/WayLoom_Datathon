from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.task1.advanced_models import (
    AdvancedCandidate,
    Task1AdvancedModelError,
    fit_predict_advanced_fold,
    high_confidence_classification_errors,
    hydrate_provisional_section,
    overfitting_summary,
    resolve_advanced_feature_columns,
    resolve_candidate_family,
    worst_regression_errors,
    xgboost_available,
)


def _X(n: int = 24) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "brand": ["Fresh", "Style", "Tech"] * (n // 3) + ["Fresh"] * (n % 3),
            "dock_type": ["rear", "street", "mall"] * (n // 3) + ["rear"] * (n % 3),
            "depot": ["Peliyagoda", "Kandy"] * (n // 2) + ["Peliyagoda"] * (n % 2),
            "numeric_1": np.arange(n, dtype=float),
            "numeric_2": np.linspace(0, 1, n),
            "route_id": [f"r{i}" for i in range(n)],
            "date": pd.date_range("2025-01-01", periods=n, freq="D"),
            "outlet_prior_service_median": np.linspace(8, 18, n),
        }
    )


def test_feature_resolver_blocks_forbidden() -> None:
    x = _X(6).assign(service_minutes=1.0, late_flag=0)
    cols = resolve_advanced_feature_columns(x, feature_profile="safe_core")
    assert "service_minutes" not in cols and "late_flag" not in cols and "route_id" not in cols
    assert "outlet_prior_service_median" not in cols


@pytest.mark.parametrize(
    ("family", "target"),
    [("catboost", "service"), ("catboost", "late"), ("lightgbm", "service"), ("lightgbm", "late")],
)
def test_advanced_model_fold_smoke(family: str, target: str) -> None:
    x = _X(24)
    train = x.iloc[:16].reset_index(drop=True)
    valid = x.iloc[16:].reset_index(drop=True)
    y_service = np.linspace(10, 20, len(x))
    y_late = np.array(([0, 1] * 12), dtype=float)
    candidate = AdvancedCandidate(f"{family}_{target}", family, target, {})
    result = fit_predict_advanced_fold(
        candidate=candidate,
        X_train=train,
        y_train=y_service[:16] if target == "service" else y_late[:16],
        X_valid=valid,
        y_valid=y_service[16:] if target == "service" else y_late[16:],
        max_iterations=60,
        patience_rounds=10,
        min_iterations=10,
    )
    assert len(result.prediction) == len(valid)
    assert np.isfinite(result.prediction).all()
    if target == "late":
        assert ((result.prediction >= 0) & (result.prediction <= 1)).all()


def test_single_class_late_fold_rejected() -> None:
    x = _X(12)
    candidate = AdvancedCandidate("catboost_late", "catboost", "late", {})
    with pytest.raises(Task1AdvancedModelError):
        fit_predict_advanced_fold(
            candidate=candidate,
            X_train=x.iloc[:8],
            y_train=np.zeros(8),
            X_valid=x.iloc[8:],
            y_valid=np.array([0, 1, 0, 1], dtype=float),
        )


def test_overfitting_and_error_analytics() -> None:
    summary = overfitting_summary(
        pd.DataFrame(
            [
                {"candidate_id": "a", "target": "service", "fold_id": 1, "train_metric": 1.0, "validation_metric": 2.0, "best_iteration": 10, "max_iterations": 50},
                {"candidate_id": "a", "target": "service", "fold_id": 2, "train_metric": 1.1, "validation_metric": 2.3, "best_iteration": 50, "max_iterations": 50},
            ]
        )
    )
    assert "warning_codes" in summary.columns
    errors = worst_regression_errors(pd.DataFrame({"service_minutes": [10, 11], "pred_service_min": [1, 10], "brand": ["Fresh", "Tech"]}), n_top=1)
    assert len(errors) == 1
    conf = high_confidence_classification_errors(
        pd.DataFrame({"pred_late_prob": [0.8, 0.2, 0.9], "late_flag": [0, 1, 1], "brand": ["Fresh", "Style", "Tech"]})
    )
    assert set(conf["error_type"]) == {"HIGH_CONFIDENCE_FALSE_POSITIVE", "HIGH_CONFIDENCE_FALSE_NEGATIVE"}
    assert xgboost_available() is False


def test_family_resolved_from_candidate_id_when_missing() -> None:
    assert resolve_candidate_family({"candidate_id": "catboost_regression_default"}) == "catboost"
    assert resolve_candidate_family({"candidate_id": "lightgbm_classifier_default"}) == "lightgbm"
    assert resolve_candidate_family({"family": "CatBoost", "candidate_id": "x"}) == "catboost"
    with pytest.raises(Task1AdvancedModelError):
        resolve_candidate_family({"candidate_id": "mystery_model"})


def test_hydrate_old_provisional_selection_without_family() -> None:
    model_cfg = {
        "seed": 42,
        "features": {"profile": "safe_core_plus_history"},
        "catboost": {
            "regression": {
                "enabled": True,
                "depth": 7,
                "learning_rate": 0.05,
                "l2_leaf_reg": 5,
                "loss_function": "MAE",
                "eval_metric": "MAE",
                "allow_writing_files": False,
                "verbose": False,
            },
            "classification": {"enabled": False},
        },
    }
    hydrated = hydrate_provisional_section(
        {"candidate_id": "catboost_regression_default"},
        model_cfg,
        target="service",
    )
    assert hydrated["family"] == "catboost"
    assert hydrated["parameters"]["depth"] == 7
    assert hydrated["feature_profile"] == "safe_core_plus_history"
