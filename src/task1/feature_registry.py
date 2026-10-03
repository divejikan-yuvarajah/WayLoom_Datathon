from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


FORBIDDEN_DIRECT_TASK1_FEATURES = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
    "service_start_dt",
    "service_minutes",
    "late_flag",
}

REGISTRY_REQUIRED_FIELDS = [
    "feature_name",
    "feature_group",
    "source_table",
    "source_columns",
    "formula_or_mapping",
    "semantic_type",
    "prediction_time_safe",
    "uses_target_history",
    "requires_fit",
    "fit_scope",
    "missing_value_policy",
    "train_available",
    "test_available",
    "categorical",
    "model_candidate",
    "rationale",
    "status",
]


class FeatureRegistryError(ValueError):
    """Raised when the feature registry is incomplete or inconsistent."""


def _default_meta(feature_name: str) -> dict[str, Any]:
    return {
        "feature_name": feature_name,
        "feature_group": "UNSPECIFIED",
        "source_table": "derived",
        "source_columns": [feature_name],
        "formula_or_mapping": "direct_or_derived",
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
        "rationale": "Task 1 engineered feature.",
        "status": "ENABLED",
    }


def build_feature_registry(
    feature_columns: list[str],
    *,
    historical_columns: set[str] | None = None,
) -> pd.DataFrame:
    """Build a complete registry table for produced feature columns."""
    historical_columns = historical_columns or set()

    rows: list[dict[str, Any]] = []
    for col in feature_columns:
        meta = _default_meta(col)
        if col in FORBIDDEN_DIRECT_TASK1_FEATURES:
            meta.update(
                {
                    "prediction_time_safe": False,
                    "model_candidate": False,
                    "status": "DISABLED",
                    "rationale": "Forbidden direct leakage field.",
                }
            )
        if col in historical_columns:
            meta.update(
                {
                    "feature_group": "HISTORICAL_FOLD_SAFE",
                    "uses_target_history": True,
                    "requires_fit": True,
                    "fit_scope": "training_fold_only",
                    "status": "HISTORICAL_FOLD_SAFE_ONLY",
                }
            )
        if col in {"brand", "district", "depot", "dock_type", "parking_constraint", "festival", "fuel_type"}:
            meta["categorical"] = True
            meta["semantic_type"] = "categorical"
        rows.append(meta)

    registry = pd.DataFrame(rows)
    validate_feature_registry(registry, expected_features=feature_columns)
    return registry


def validate_feature_registry(registry: pd.DataFrame, *, expected_features: list[str]) -> None:
    missing_cols = [c for c in REGISTRY_REQUIRED_FIELDS if c not in registry.columns]
    if missing_cols:
        raise FeatureRegistryError(
            "Feature registry missing required fields: " + ", ".join(missing_cols)
        )

    if registry["feature_name"].duplicated().any():
        raise FeatureRegistryError("Feature registry has duplicate feature_name entries.")

    actual = list(registry["feature_name"])
    missing = sorted(set(expected_features) - set(actual))
    extra = sorted(set(actual) - set(expected_features))
    if missing or extra:
        raise FeatureRegistryError(
            f"Feature registry mismatch. missing={missing}, extra={extra}"
        )

    for _, row in registry.iterrows():
        if row["status"] == "DISABLED" and bool(row["model_candidate"]):
            raise FeatureRegistryError(
                f"Disabled feature must not be a model candidate: {row['feature_name']}"
            )
        if bool(row["uses_target_history"]) and not bool(row["requires_fit"]):
            raise FeatureRegistryError(
                f"Historical feature requires fit metadata: {row['feature_name']}"
            )
