"""Verified local SHAP adapters for frozen Task 1 models.

The adapter keeps attribution space separate from post-processing and
calibration.  No function in this module fits or mutates a model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


class ShapAdapterError(ValueError):
    """Raised when a frozen model cannot be explained faithfully."""


@dataclass(frozen=True)
class ShapResult:
    values: np.ndarray
    base_values: np.ndarray
    raw_predictions: np.ndarray
    method: str
    output_space: str
    max_abs_reconstruction_error: float
    reconstruction_pass: bool


def _as_2d(values: Any, *, n_rows: int, n_features: int,
           positive_class_index: int | None = None) -> np.ndarray:
    """Normalize common SHAP-library output shapes to rows x features."""
    if isinstance(values, (list, tuple)):
        if not values:
            raise ShapAdapterError("SHAP output is empty.")
        index = 0 if positive_class_index is None else int(positive_class_index)
        if index >= len(values):
            raise ShapAdapterError("Positive-class SHAP output is unavailable.")
        values = values[index]
    array = np.asarray(values, dtype=float)
    if array.ndim == 2 and array.shape == (n_rows, n_features):
        return array
    if array.ndim == 3:
        index = 0 if positive_class_index is None else int(positive_class_index)
        # Modern shap.Explanation uses rows x features x outputs.  Prefer
        # that convention when feature/output counts happen to be equal.
        if array.shape[0] == n_rows and array.shape[1] == n_features:
            if index >= array.shape[2]:
                raise ShapAdapterError("Positive-class SHAP axis is unavailable.")
            return array[:, :, index]
        if array.shape[0] == n_rows and array.shape[2] == n_features:
            if index >= array.shape[1]:
                raise ShapAdapterError("Positive-class SHAP axis is unavailable.")
            return array[:, index, :]
        if array.shape[1] == n_rows and array.shape[2] == n_features:
            if index >= array.shape[0]:
                raise ShapAdapterError("Positive-class SHAP axis is unavailable.")
            return array[index, :, :]
    raise ShapAdapterError(
        f"Unsupported SHAP shape {array.shape}; expected ({n_rows}, {n_features})."
    )


def normalize_contributions(raw: Any, *, n_rows: int, n_features: int,
                            positive_class_index: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Split native contribution output into feature values and base values."""
    if isinstance(raw, (list, tuple)):
        if not raw:
            raise ShapAdapterError("Native contribution output is empty.")
        index = 0 if positive_class_index is None else int(positive_class_index)
        if index >= len(raw):
            raise ShapAdapterError("Positive-class contribution output is unavailable.")
        raw = raw[index]
    array = np.asarray(raw, dtype=float)
    if array.ndim == 2 and array.shape == (n_rows, n_features + 1):
        return array[:, :-1], array[:, -1]
    if array.ndim == 3:
        index = 0 if positive_class_index is None else int(positive_class_index)
        if array.shape[0] == n_rows and array.shape[2] == n_features + 1:
            if index >= array.shape[1]:
                raise ShapAdapterError("Positive-class contribution axis is unavailable.")
            selected = array[:, index, :]
            return selected[:, :-1], selected[:, -1]
        if array.shape[1] == n_rows and array.shape[2] == n_features + 1:
            if index >= array.shape[0]:
                raise ShapAdapterError("Positive-class contribution axis is unavailable.")
            selected = array[index, :, :]
            return selected[:, :-1], selected[:, -1]
    raise ShapAdapterError(
        "Native contribution output must contain one base-value column after "
        f"{n_features} feature columns; got shape {array.shape}."
    )


def _base_array(base: Any, *, n_rows: int, positive_class_index: int | None = None) -> np.ndarray:
    array = np.asarray(base, dtype=float)
    if array.ndim == 0:
        return np.full(n_rows, float(array), dtype=float)
    if array.ndim == 1:
        if len(array) == n_rows:
            return array.astype(float)
        index = 0 if positive_class_index is None else int(positive_class_index)
        if index < len(array):
            return np.full(n_rows, float(array[index]), dtype=float)
    if array.ndim == 2 and array.shape[0] == n_rows:
        index = 0 if positive_class_index is None else int(positive_class_index)
        if index < array.shape[1]:
            return array[:, index].astype(float)
    raise ShapAdapterError(f"Unsupported SHAP base-value shape {array.shape}.")


def _finish(values: np.ndarray, base: np.ndarray, raw_predictions: Any, *,
            method: str, output_space: str, tolerance: float) -> ShapResult:
    pred = np.asarray(raw_predictions, dtype=float).reshape(-1)
    if values.shape[0] != len(pred) or len(base) != len(pred):
        raise ShapAdapterError("SHAP rows do not align with raw model predictions.")
    if not np.isfinite(values).all() or not np.isfinite(base).all() or not np.isfinite(pred).all():
        raise ShapAdapterError("SHAP output or raw predictions contain NaN/Inf.")
    reconstructed = base + values.sum(axis=1)
    error = float(np.max(np.abs(reconstructed - pred))) if len(pred) else 0.0
    passed = bool(error <= float(tolerance))
    if not passed:
        raise ShapAdapterError(
            f"SHAP reconstruction failed: max_abs_error={error:.12g}, tolerance={tolerance:.12g}."
        )
    return ShapResult(values, base, pred, method, output_space, error, passed)


def _catboost_pool(frame: pd.DataFrame, categorical_columns: list[str]) -> Any:
    try:
        from catboost import Pool
    except Exception as exc:  # pragma: no cover - dependency guard
        raise ShapAdapterError("CatBoost is unavailable for native SHAP.") from exc
    cat_indices = [frame.columns.get_loc(name) for name in categorical_columns]
    return Pool(frame, cat_features=cat_indices)


def _catboost_shap(model: Any, frame: pd.DataFrame, *, task: str,
                   categorical_columns: list[str], positive_class_index: int | None,
                   tolerance: float) -> ShapResult:
    pool = _catboost_pool(frame, categorical_columns)
    native = model.get_feature_importance(pool, type="ShapValues")
    values, base = normalize_contributions(
        native,
        n_rows=len(frame),
        n_features=frame.shape[1],
        positive_class_index=positive_class_index if task == "lateness" else None,
    )
    if task == "service":
        raw = model.predict(pool)
        space = "raw_service_prediction"
    else:
        raw = model.predict(pool, prediction_type="RawFormulaVal")
        raw_array = np.asarray(raw, dtype=float)
        if raw_array.ndim == 2:
            index = 0 if positive_class_index is None else int(positive_class_index)
            raw = raw_array[:, index]
        space = "raw_margin_log_odds"
    return _finish(values, base, raw, method="catboost_native_shap",
                   output_space=space, tolerance=tolerance)


def _lightgbm_shap(model: Any, frame: pd.DataFrame, *, task: str,
                   positive_class_index: int | None, tolerance: float) -> ShapResult:
    booster = getattr(model, "booster_", model)
    native = booster.predict(frame, pred_contrib=True)
    values, base = normalize_contributions(
        native,
        n_rows=len(frame),
        n_features=frame.shape[1],
        positive_class_index=positive_class_index if task == "lateness" else None,
    )
    raw = booster.predict(frame, raw_score=(task == "lateness"))
    if np.asarray(raw).ndim == 2:
        index = 0 if positive_class_index is None else int(positive_class_index)
        raw = np.asarray(raw)[:, index]
    return _finish(
        values,
        base,
        raw,
        method="lightgbm_native_pred_contrib",
        output_space="raw_margin_log_odds" if task == "lateness" else "raw_service_prediction",
        tolerance=tolerance,
    )


def _xgboost_shap(model: Any, frame: pd.DataFrame, *, task: str,
                  positive_class_index: int | None, tolerance: float) -> ShapResult:
    try:
        import xgboost as xgb
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ShapAdapterError("XGBoost is unavailable for native SHAP.") from exc
    booster = model.get_booster() if hasattr(model, "get_booster") else model
    matrix = xgb.DMatrix(frame, feature_names=list(frame.columns), enable_categorical=True)
    native = booster.predict(matrix, pred_contribs=True)
    values, base = normalize_contributions(
        native,
        n_rows=len(frame),
        n_features=frame.shape[1],
        positive_class_index=positive_class_index if task == "lateness" else None,
    )
    raw = booster.predict(matrix, output_margin=(task == "lateness"))
    if np.asarray(raw).ndim == 2:
        index = 0 if positive_class_index is None else int(positive_class_index)
        raw = np.asarray(raw)[:, index]
    return _finish(
        values,
        base,
        raw,
        method="xgboost_native_pred_contribs",
        output_space="raw_margin_log_odds" if task == "lateness" else "raw_service_prediction",
        tolerance=tolerance,
    )


def _generic_local_shap(model: Any, frame: pd.DataFrame, *, task: str,
                        positive_class_index: int | None, tolerance: float) -> ShapResult:
    if any(not pd.api.types.is_numeric_dtype(frame[col]) for col in frame.columns):
        raise ShapAdapterError(
            "Generic SHAP cannot alter frozen categorical semantics; use a verified native adapter."
        )
    try:
        import shap
    except Exception as exc:  # pragma: no cover - dependency guard
        raise ShapAdapterError("The local SHAP package is unavailable.") from exc
    try:
        if hasattr(model, "feature_importances_"):
            explainer = shap.TreeExplainer(model)
            raw_values = explainer.shap_values(frame)
            base = explainer.expected_value
            method = "shap_tree_explainer"
        elif hasattr(model, "coef_"):
            explainer = shap.LinearExplainer(model, frame)
            explanation = explainer(frame)
            raw_values = explanation.values
            base = explanation.base_values
            method = "shap_linear_explainer"
        else:
            raise ShapAdapterError("Unsupported model family has no verified local SHAP adapter.")
    except ShapAdapterError:
        raise
    except Exception as exc:
        raise ShapAdapterError("Local SHAP explainer failed for the frozen model.") from exc

    values = _as_2d(
        raw_values,
        n_rows=len(frame),
        n_features=frame.shape[1],
        positive_class_index=positive_class_index if task == "lateness" else None,
    )
    bases = _base_array(
        base,
        n_rows=len(frame),
        positive_class_index=positive_class_index if task == "lateness" else None,
    )
    reconstructed = bases + values.sum(axis=1)
    candidates: list[tuple[str, np.ndarray]] = []
    if task == "service":
        candidates.append(("raw_service_prediction", np.asarray(model.predict(frame), dtype=float)))
    else:
        if hasattr(model, "decision_function"):
            decision = np.asarray(model.decision_function(frame), dtype=float)
            if decision.ndim == 2:
                index = 0 if positive_class_index is None else int(positive_class_index)
                decision = decision[:, index]
            candidates.append(("raw_margin_log_odds", decision))
        if hasattr(model, "predict_proba"):
            index = 1 if positive_class_index is None else int(positive_class_index)
            candidates.append(("base_probability", np.asarray(model.predict_proba(frame), dtype=float)[:, index]))
    if not candidates:
        raise ShapAdapterError("No supported prediction output exists for SHAP reconstruction.")
    space, prediction = min(
        candidates,
        key=lambda item: float(np.max(np.abs(reconstructed - np.asarray(item[1]).reshape(-1)))),
    )
    return _finish(values, bases, prediction, method=method, output_space=space, tolerance=tolerance)


def explain_model(model: Any, frame: pd.DataFrame, *, family: str, task: str,
                  categorical_columns: list[str] | None = None,
                  positive_class_index: int | None = None,
                  tolerance: float = 1e-6) -> ShapResult:
    """Explain an already-fitted model without changing it or its inputs."""
    if task not in {"service", "lateness"}:
        raise ShapAdapterError(f"Unknown Task 1 explanation target: {task}")
    if task == "lateness" and positive_class_index is None:
        raise ShapAdapterError("Lateness explanation requires an explicit positive-class index.")
    if frame.empty:
        raise ShapAdapterError("Explanation frame is empty.")
    family_key = str(family or "").strip().lower()
    cats = list(categorical_columns or [])
    if family_key == "catboost":
        return _catboost_shap(model, frame, task=task, categorical_columns=cats,
                              positive_class_index=positive_class_index, tolerance=tolerance)
    if family_key == "lightgbm":
        return _lightgbm_shap(model, frame, task=task,
                              positive_class_index=positive_class_index, tolerance=tolerance)
    if family_key == "xgboost":
        return _xgboost_shap(model, frame, task=task,
                             positive_class_index=positive_class_index, tolerance=tolerance)
    if family_key in {"sklearn_tree", "sklearn_linear", "random_forest", "extra_trees",
                      "gradient_boosting", "linear", "logistic_regression"}:
        return _generic_local_shap(model, frame, task=task,
                                   positive_class_index=positive_class_index, tolerance=tolerance)
    raise ShapAdapterError(f"Unsupported model family for verified SHAP: {family_key or '<blank>'}.")


def native_feature_importance(model: Any, *, family: str, feature_names: list[str]) -> tuple[np.ndarray, str] | None:
    """Return trustworthy model-native importance, or ``None`` for SHAP fallback."""
    family_key = str(family or "").strip().lower()
    values: np.ndarray | None = None
    kind = ""
    if family_key == "catboost" and hasattr(model, "get_feature_importance"):
        values = np.asarray(model.get_feature_importance(type="PredictionValuesChange"), dtype=float)
        kind = "catboost_prediction_values_change"
    elif family_key == "lightgbm":
        booster = getattr(model, "booster_", model)
        if hasattr(booster, "feature_importance"):
            values = np.asarray(booster.feature_importance(importance_type="gain"), dtype=float)
            kind = "lightgbm_gain"
    elif family_key == "xgboost" and hasattr(model, "get_booster"):
        scores = model.get_booster().get_score(importance_type="gain")
        values = np.asarray([
            float(scores.get(name, scores.get(f"f{index}", 0.0)))
            for index, name in enumerate(feature_names)
        ])
        kind = "xgboost_gain"
    elif hasattr(model, "feature_importances_"):
        values = np.asarray(model.feature_importances_, dtype=float)
        kind = "sklearn_feature_importances"
    elif hasattr(model, "coef_"):
        coef = np.asarray(model.coef_, dtype=float)
        if coef.ndim == 2:
            coef = coef[-1]
        values = np.abs(coef.reshape(-1))
        kind = "absolute_linear_coefficient"
    if values is None:
        return None
    values = values.reshape(-1)
    if len(values) != len(feature_names) or not np.isfinite(values).all() or (values < 0).any():
        raise ShapAdapterError("Native feature importance does not align with the frozen schema.")
    return values, kind
