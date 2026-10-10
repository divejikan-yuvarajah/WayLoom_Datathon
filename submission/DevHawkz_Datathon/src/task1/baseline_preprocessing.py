"""Fold-scoped preprocessing for fixed Phase 08 linear/logistic baselines."""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.task1.feature_registry import (
    FORBIDDEN_DIRECT_TASK1_FEATURES,
    build_feature_registry,
    validate_feature_registry,
)


class BaselinePreprocessingError(ValueError):
    """Raised when simple Phase 08 baseline features violate safety rules."""


IDENTIFIER_OR_EXCLUDED = {
    "delivery_id", "leg_id", "route_id", "outlet_id", "vehicle_id",
    "service_start_dt", "service_minutes", "late_flag",
}
HISTORICAL_PREFIXES = ("outlet_prior_", "brand_dock_prior_", "brand_prior_")


def select_simple_baseline_features(
    frame: pd.DataFrame,
    *,
    registry: pd.DataFrame | None = None,
    include_historical_target_features: bool = False,
) -> list[str]:
    """Resolve the fixed Phase 08 input allow-list from Phase 06 registry metadata."""
    if registry is None:
        # This fallback exists for synthetic unit tests only. Runtime callers must
        # provide the Phase 06-derived registry assembled by the runner.
        registry = build_feature_registry(
            list(frame.columns),
            historical_columns={c for c in frame if c.startswith(HISTORICAL_PREFIXES)},
        )
    validate_feature_registry(registry, expected_features=list(frame.columns))
    metadata = registry.set_index("feature_name")
    if not metadata.index.is_unique:
        raise BaselinePreprocessingError("Feature registry has duplicate feature names.")
    forbidden = set(FORBIDDEN_DIRECT_TASK1_FEATURES) | IDENTIFIER_OR_EXCLUDED
    selected: list[str] = []
    for col in frame.columns:
        row = metadata.loc[col]
        if (
            col in forbidden
            or not bool(row["prediction_time_safe"])
            or not bool(row["model_candidate"])
            or str(row["status"]) == "DISABLED"
        ):
            continue
        if (
            bool(row["uses_target_history"])
            or bool(row["requires_fit"])
            or col.startswith(HISTORICAL_PREFIXES)
        ) and not include_historical_target_features:
            continue
        selected.append(col)
    if not selected:
        raise BaselinePreprocessingError("No safe baseline features available.")
    return selected


def build_fold_preprocessor(X_train: pd.DataFrame, feature_columns: list[str]) -> tuple[Pipeline, list[str], list[str]]:
    """Build but do not fit a preprocessor; caller fits it only on fold train."""
    if set(feature_columns) - set(X_train.columns):
        raise BaselinePreprocessingError("Selected baseline features are not available in training frame.")
    numeric = [
        c for c in feature_columns if pd.api.types.is_numeric_dtype(X_train[c])
    ]
    categorical = [c for c in feature_columns if c not in numeric]
    transformers: list[tuple[str, Pipeline, list[str]]] = []
    if numeric:
        transformers.append(
            (
                "numeric",
                Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]),
                numeric,
            )
        )
    if categorical:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
                        ("one_hot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            )
        )
    return Pipeline([("columns", ColumnTransformer(transformers=transformers))]), numeric, categorical
