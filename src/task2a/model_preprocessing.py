"""Shared Phase 13 semantic predictors with fold-local model representations."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.task2a.features import build_feature_registry, get_task2a_feature_columns


class ModelPreprocessingError(ValueError):
    """The model feature boundary or fold preprocessing was violated."""


def feature_profile(config: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = build_feature_registry(config)
    enabled = registry.loc[registry.role.eq("feature")].copy()
    allowed = {"PAST_DEMAND", "TARGET_WEEK_CALENDAR", "STATIC_SERIES", "FORECAST_HORIZON"}
    if not enabled.prediction_time_safe.all() or enabled.uses_future_actual_demand.any():
        raise ModelPreprocessingError("An enabled Phase 13 predictor is not prediction-time safe.")
    if not set(enabled.availability_type).issubset(allowed):
        raise ModelPreprocessingError("An enabled predictor has an unapproved availability type.")
    columns = get_task2a_feature_columns(config)
    if columns != enabled.feature_name.tolist() or len(columns) != len(set(columns)):
        raise ModelPreprocessingError("Phase 13 feature registry and allow-list disagree.")
    categorical = enabled.loc[enabled.categorical, "feature_name"].tolist()
    identity = hashlib.sha256(json.dumps({"columns": columns, "categorical": categorical},
                                      sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"profile_id": "task2a_advanced_safe_v1", "columns": columns,
            "categorical": categorical, "numeric": [name for name in columns if name not in categorical],
            "registry_hash": identity, "forbidden_feature_count": 0}


def select_predictors(rows: pd.DataFrame, profile: dict[str, Any]) -> pd.DataFrame:
    missing = set(profile["columns"]).difference(rows.columns)
    if missing:
        raise ModelPreprocessingError("Required Phase 13 predictors are missing: " + ", ".join(sorted(missing)))
    frame = rows.loc[:, profile["columns"]].copy()
    if any(name.startswith("target_total_volume_m3") or name.startswith("target_chilled_volume_m3")
           for name in frame.columns):
        raise ModelPreprocessingError("Target label entered model predictors.")
    for column in profile["categorical"]:
        frame[column] = frame[column].fillna("__MISSING__").astype(str)
    for column in profile["numeric"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if np.isinf(frame[column].to_numpy(dtype=float)).any():
            raise ModelPreprocessingError("Infinite numeric predictor cannot be imputed safely.")
    return frame


def lightgbm_fold_preprocessor(profile: dict[str, Any]) -> ColumnTransformer:
    """Return an unfitted transformer; the caller fits on fold training rows."""
    return ColumnTransformer([
        ("numeric", SimpleImputer(strategy="median", keep_empty_features=True), profile["numeric"]),
        ("categorical", Pipeline([
            ("missing", SimpleImputer(strategy="constant", fill_value="__MISSING__", keep_empty_features=True)),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), profile["categorical"]),
    ], remainder="drop")
