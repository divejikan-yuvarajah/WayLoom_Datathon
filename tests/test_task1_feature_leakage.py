from __future__ import annotations

import pandas as pd
import pytest

from src.task1.feature_registry import build_feature_registry
from src.task1.features import Task1FeatureBlockerError, audit_feature_leakage


def test_dt121_direct_forbidden_column_rejected() -> None:
    X_train = pd.DataFrame({"actual_travel_duration_min": [10.0], "f1": [1.0]})
    X_test = pd.DataFrame({"actual_travel_duration_min": [9.0], "f1": [2.0]})
    registry = build_feature_registry(["actual_travel_duration_min", "f1"])
    with pytest.raises(Task1FeatureBlockerError, match="Forbidden direct feature"):
        audit_feature_leakage(X_train, X_test, registry)


def test_dt121_lineage_rejects_renamed_leakage() -> None:
    X_train = pd.DataFrame({"delay_like_feature": [1.0]})
    X_test = pd.DataFrame({"delay_like_feature": [2.0]})
    registry = pd.DataFrame(
        [
            {
                "feature_name": "delay_like_feature",
                "feature_group": "DERIVED",
                "source_table": "route_legs_train.csv",
                "source_columns": ["arrival_time", "planned_arrival_time"],
                "formula_or_mapping": "arrival-planned",
                "semantic_type": "numeric",
                "prediction_time_safe": True,
                "uses_target_history": False,
                "requires_fit": False,
                "fit_scope": "none",
                "missing_value_policy": "preserve_missing",
                "train_available": True,
                "test_available": True,
                "categorical": False,
                "model_candidate": True,
                "rationale": "fake",
                "status": "ENABLED",
            }
        ]
    )
    with pytest.raises(Task1FeatureBlockerError, match="forbidden lineage"):
        audit_feature_leakage(X_train, X_test, registry)


def test_dt121_train_test_parity_rejected_on_order_or_name_mismatch() -> None:
    X_train = pd.DataFrame({"f1": [1], "f2": [2]})
    X_test = pd.DataFrame({"f2": [2], "f1": [1]})
    registry = build_feature_registry(["f1", "f2"])
    with pytest.raises(Task1FeatureBlockerError, match="must match exactly"):
        audit_feature_leakage(X_train, X_test, registry)


def test_dt121_dt122_pass_clean_matrix() -> None:
    cols = ["f_brand", "f_route_seq", "outlet_prior_late_rate"]
    X_train = pd.DataFrame({c: [1.0, 2.0] for c in cols})
    X_test = pd.DataFrame({c: [0.5, 1.5] for c in cols})
    registry = build_feature_registry(cols, historical_columns={"outlet_prior_late_rate"})
    summary = audit_feature_leakage(X_train, X_test, registry)
    assert summary["forbidden_direct_count"] == 0
    assert summary["train_test_parity"] is True
