"""Phase 09 advanced Task 1 model adapters and fold-safe diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss as sk_log_loss
from sklearn.metrics import mean_absolute_error

from src.task1.baseline_preprocessing import IDENTIFIER_OR_EXCLUDED, HISTORICAL_PREFIXES
from src.task1.feature_registry import FORBIDDEN_DIRECT_TASK1_FEATURES, build_feature_registry
from src.task1.metrics import lateness_probability_metrics, regression_metrics

try:
    from catboost import CatBoostClassifier, CatBoostRegressor
except Exception:  # pragma: no cover
    CatBoostClassifier = None
    CatBoostRegressor = None

try:
    from lightgbm import LGBMClassifier, LGBMRegressor
except Exception:  # pragma: no cover
    LGBMClassifier = None
    LGBMRegressor = None

try:
    from xgboost import XGBClassifier, XGBRegressor
except Exception:  # pragma: no cover
    XGBClassifier = None
    XGBRegressor = None


class Task1AdvancedModelError(ValueError):
    """Raised when advanced modeling violates frozen competition contracts."""


@dataclass(frozen=True)
class AdvancedCandidate:
    candidate_id: str
    family: str
    target: str  # "service" | "late"
    params: dict[str, Any]
    feature_profile: str = "safe_core_plus_history"


@dataclass
class FoldPredictionResult:
    prediction: np.ndarray
    train_metric: float
    validation_metric: float
    best_iteration: int
    stopped_early: bool
    max_iterations: int
    training_seconds: float
    warning_codes: list[str]


def xgboost_available() -> bool:
    return XGBRegressor is not None and XGBClassifier is not None


def resolve_advanced_feature_columns(
    frame: pd.DataFrame,
    *,
    feature_profile: str = "safe_core_plus_history",
) -> list[str]:
    if feature_profile not in {"safe_core", "safe_core_plus_history"}:
        raise Task1AdvancedModelError(f"Unsupported feature profile: {feature_profile}")
    registry = build_feature_registry(
        list(frame.columns),
        historical_columns={c for c in frame.columns if c.startswith(HISTORICAL_PREFIXES)},
    )
    meta = registry.set_index("feature_name")
    cols: list[str] = []
    forbidden = set(FORBIDDEN_DIRECT_TASK1_FEATURES) | IDENTIFIER_OR_EXCLUDED
    for col in frame.columns:
        row = meta.loc[col]
        if (
            col in forbidden
            or not bool(row["prediction_time_safe"])
            or not bool(row["model_candidate"])
            or str(row["status"]) == "DISABLED"
        ):
            continue
        if pd.api.types.is_datetime64_any_dtype(frame[col]):
            # Keep advanced models deterministic across libraries by avoiding
            # raw datetime-typed columns in direct model inputs.
            continue
        if feature_profile == "safe_core" and (
            bool(row["uses_target_history"]) or col.startswith(HISTORICAL_PREFIXES)
        ):
            continue
        cols.append(col)
    if not cols:
        raise Task1AdvancedModelError("No safe advanced-model features selected.")
    return cols


def _categorical_columns(frame: pd.DataFrame, cols: list[str]) -> list[str]:
    return [c for c in cols if not pd.api.types.is_numeric_dtype(frame[c])]


def _validate_targets(y: Any, *, binary: bool) -> np.ndarray:
    arr = np.asarray(y, dtype=float)
    if len(arr) == 0 or not np.isfinite(arr).all():
        raise Task1AdvancedModelError("Targets must be finite and non-empty.")
    if binary and not set(np.unique(arr)).issubset({0.0, 1.0}):
        raise Task1AdvancedModelError("Binary target must contain only 0/1.")
    return arr


def _catboost_regressor(candidate: AdvancedCandidate, max_iterations: int) -> Any:
    if CatBoostRegressor is None:
        raise Task1AdvancedModelError("catboost is not installed.")
    params = dict(candidate.params)
    params.setdefault("loss_function", "MAE")
    params.setdefault("eval_metric", "MAE")
    params.setdefault("random_seed", 42)
    params.setdefault("allow_writing_files", False)
    params.setdefault("verbose", False)
    params["iterations"] = max_iterations
    return CatBoostRegressor(**params)


def _catboost_classifier(candidate: AdvancedCandidate, max_iterations: int) -> Any:
    if CatBoostClassifier is None:
        raise Task1AdvancedModelError("catboost is not installed.")
    params = dict(candidate.params)
    params.setdefault("loss_function", "Logloss")
    params.setdefault("eval_metric", "Logloss")
    params.setdefault("random_seed", 42)
    params.setdefault("auto_class_weights", None)
    params.setdefault("allow_writing_files", False)
    params.setdefault("verbose", False)
    params["iterations"] = max_iterations
    return CatBoostClassifier(**params)


def _lightgbm_regressor(candidate: AdvancedCandidate, max_iterations: int) -> Any:
    if LGBMRegressor is None:
        raise Task1AdvancedModelError("lightgbm is not installed.")
    params = dict(candidate.params)
    params.setdefault("random_state", 42)
    params.setdefault("verbosity", -1)
    params.setdefault("n_estimators", max_iterations)
    return LGBMRegressor(**params)


def _lightgbm_classifier(candidate: AdvancedCandidate, max_iterations: int) -> Any:
    if LGBMClassifier is None:
        raise Task1AdvancedModelError("lightgbm is not installed.")
    params = dict(candidate.params)
    params.setdefault("random_state", 42)
    params.setdefault("verbosity", -1)
    params.setdefault("n_estimators", max_iterations)
    return LGBMClassifier(**params)


def _train(
    *,
    candidate: AdvancedCandidate,
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_valid: pd.DataFrame,
    y_valid: np.ndarray,
    max_iterations: int,
    patience_rounds: int,
) -> tuple[np.ndarray, np.ndarray, Any, float]:
    columns = resolve_advanced_feature_columns(X_train, feature_profile=candidate.feature_profile)
    xtr = X_train[columns].copy()
    xva = X_valid[columns].copy()
    cat_cols = _categorical_columns(xtr, columns)
    if cat_cols:
        # CatBoost requires categorical values to be string/int (not NaN float).
        # Use a stable missing token across train/validation.
        for c in cat_cols:
            xtr[c] = xtr[c].astype("string").fillna("__MISSING__")
            xva[c] = xva[c].astype("string").fillna("__MISSING__")
    start = perf_counter()

    if candidate.family == "catboost":
        cat_idx = [columns.index(c) for c in cat_cols]
        if candidate.target == "service":
            model = _catboost_regressor(candidate, max_iterations)
            model.fit(
                xtr,
                y_train,
                eval_set=(xva, y_valid),
                cat_features=cat_idx,
                early_stopping_rounds=patience_rounds,
            )
            pred = np.asarray(model.predict(xva), dtype=float)
            pred_train = np.asarray(model.predict(xtr), dtype=float)
        else:
            model = _catboost_classifier(candidate, max_iterations)
            model.fit(
                xtr,
                y_train,
                eval_set=(xva, y_valid),
                cat_features=cat_idx,
                early_stopping_rounds=patience_rounds,
            )
            pred = np.asarray(model.predict_proba(xva)[:, 1], dtype=float)
            pred_train = np.asarray(model.predict_proba(xtr)[:, 1], dtype=float)
    elif candidate.family == "lightgbm":
        for c in cat_cols:
            xtr[c] = xtr[c].astype("category")
            xva[c] = xva[c].astype("category")
        if candidate.target == "service":
            model = _lightgbm_regressor(candidate, max_iterations)
            model.fit(
                xtr,
                y_train,
                eval_X=xva,
                eval_y=y_valid,
                eval_metric="l1",
                callbacks=[],
            )
            pred = np.asarray(model.predict(xva), dtype=float)
            pred_train = np.asarray(model.predict(xtr), dtype=float)
        else:
            model = _lightgbm_classifier(candidate, max_iterations)
            model.fit(
                xtr,
                y_train,
                eval_X=xva,
                eval_y=y_valid,
                eval_metric="binary_logloss",
                callbacks=[],
            )
            pred = np.asarray(model.predict_proba(xva)[:, 1], dtype=float)
            pred_train = np.asarray(model.predict_proba(xtr)[:, 1], dtype=float)
    elif candidate.family == "xgboost":
        if not xgboost_available():
            raise Task1AdvancedModelError("xgboost optional dependency not available.")
        xtr = pd.get_dummies(xtr, dummy_na=True)
        xva = pd.get_dummies(xva, dummy_na=True).reindex(columns=xtr.columns, fill_value=0)
        if candidate.target == "service":
            model = XGBRegressor(
                n_estimators=max_iterations,
                random_state=42,
                eval_metric="mae",
                **candidate.params,
            )
            model.fit(xtr, y_train, eval_set=[(xva, y_valid)], verbose=False)
            pred = np.asarray(model.predict(xva), dtype=float)
            pred_train = np.asarray(model.predict(xtr), dtype=float)
        else:
            model = XGBClassifier(
                n_estimators=max_iterations,
                random_state=42,
                eval_metric="logloss",
                **candidate.params,
            )
            model.fit(xtr, y_train, eval_set=[(xva, y_valid)], verbose=False)
            pred = np.asarray(model.predict_proba(xva)[:, 1], dtype=float)
            pred_train = np.asarray(model.predict_proba(xtr)[:, 1], dtype=float)
    else:
        raise Task1AdvancedModelError(f"Unsupported model family: {candidate.family}")
    return pred, pred_train, model, perf_counter() - start


def fit_predict_advanced_fold(
    *,
    candidate: AdvancedCandidate,
    X_train: pd.DataFrame,
    y_train: Any,
    X_valid: pd.DataFrame,
    y_valid: Any,
    max_iterations: int = 2000,
    patience_rounds: int = 100,
    min_iterations: int = 50,
) -> FoldPredictionResult:
    train = _validate_targets(y_train, binary=(candidate.target == "late"))
    valid = _validate_targets(y_valid, binary=(candidate.target == "late"))
    if candidate.target == "late" and len(np.unique(train)) < 2:
        raise Task1AdvancedModelError("Single-class training fold is unsupported for advanced late classifiers.")
    pred, pred_train, model, elapsed = _train(
        candidate=candidate,
        X_train=X_train,
        y_train=train,
        X_valid=X_valid,
        y_valid=valid,
        max_iterations=max_iterations,
        patience_rounds=patience_rounds,
    )
    if candidate.target == "service":
        train_metric = float(mean_absolute_error(train, pred_train))
        validation_metric = float(regression_metrics(valid, pred)["mae"])
    else:
        if ((pred < 0) | (pred > 1)).any():
            raise Task1AdvancedModelError("Classifier probabilities must remain in [0,1].")
        train_metric = float(sk_log_loss(train, np.clip(pred_train, np.finfo(float).eps, 1 - np.finfo(float).eps)))
        validation_metric = float(lateness_probability_metrics(valid, pred)["log_loss"])
    best_iter = int(getattr(model, "best_iteration_", getattr(model, "best_iteration", max_iterations)))
    if best_iter <= 0:
        best_iter = max_iterations
    warning_codes: list[str] = []
    if best_iter < min_iterations:
        warning_codes.append("VERY_LOW_BEST_ITERATION")
    if best_iter >= max_iterations:
        warning_codes.append("NEVER_EARLY_STOPPED")
    return FoldPredictionResult(
        prediction=pred,
        train_metric=train_metric,
        validation_metric=validation_metric,
        best_iteration=best_iter,
        stopped_early=best_iter < max_iterations,
        max_iterations=max_iterations,
        training_seconds=float(elapsed),
        warning_codes=warning_codes,
    )


def overfitting_summary(rows: pd.DataFrame, *, threshold_gap: float = 0.25, threshold_cv: float = 0.20) -> pd.DataFrame:
    """Create deterministic candidate-level overfitting and stability diagnostics."""
    required = {"candidate_id", "target", "fold_id", "train_metric", "validation_metric", "best_iteration"}
    if not required <= set(rows.columns):
        raise Task1AdvancedModelError("Overfitting summary requires train/validation fold rows.")
    out: list[dict[str, Any]] = []
    for (candidate_id, target), grp in rows.groupby(["candidate_id", "target"], sort=True):
        val = pd.to_numeric(grp["validation_metric"])
        tr = pd.to_numeric(grp["train_metric"])
        mean_val = float(val.mean())
        gap = float((val - tr).mean())
        warnings: list[str] = []
        if mean_val > 0 and gap / mean_val > threshold_gap:
            warnings.append("LARGE_GENERALIZATION_GAP")
        if mean_val > 0 and float(val.std(ddof=0)) / mean_val > threshold_cv:
            warnings.append("HIGH_FOLD_VARIANCE")
        if int(pd.to_numeric(grp["best_iteration"]).min()) < 25:
            warnings.append("VERY_LOW_BEST_ITERATION")
        if not bool((pd.to_numeric(grp["best_iteration"]) < pd.to_numeric(grp["max_iterations"])).any()):
            warnings.append("NEVER_EARLY_STOPPED")
        out.append(
            {
                "candidate_id": candidate_id,
                "target": target,
                "fold_count": int(len(grp)),
                "train_metric_mean": float(tr.mean()),
                "validation_metric_mean": mean_val,
                "train_validation_gap_mean": gap,
                "validation_metric_std": float(val.std(ddof=0)),
                "worst_fold_metric": float(val.max()),
                "warning_codes": ",".join(warnings),
            }
        )
    return pd.DataFrame(out)


def worst_regression_errors(
    frame: pd.DataFrame,
    *,
    y_true_col: str = "service_minutes",
    y_pred_col: str = "pred_service_min",
    n_top: int = 100,
) -> pd.DataFrame:
    work = frame.copy(deep=True)
    work["absolute_error"] = (pd.to_numeric(work[y_true_col]) - pd.to_numeric(work[y_pred_col])).abs()
    cols = [c for c in ("validation_date", "brand", "depot", "district", "dock_type", y_true_col, y_pred_col, "absolute_error") if c in work.columns]
    return work.sort_values(["absolute_error"], ascending=[False], kind="stable").head(int(n_top))[cols]


def high_confidence_classification_errors(
    frame: pd.DataFrame,
    *,
    prob_col: str = "pred_late_prob",
    label_col: str = "late_flag",
    high_positive: float = 0.80,
    high_negative: float = 0.20,
) -> pd.DataFrame:
    work = frame.copy(deep=True)
    p = pd.to_numeric(work[prob_col], errors="coerce")
    y = pd.to_numeric(work[label_col], errors="coerce")
    fp = (p >= high_positive) & (y == 0)
    fn = (p <= high_negative) & (y == 1)
    work["error_type"] = np.where(fp, "HIGH_CONFIDENCE_FALSE_POSITIVE", np.where(fn, "HIGH_CONFIDENCE_FALSE_NEGATIVE", ""))
    keep = work["error_type"] != ""
    cols = [c for c in ("validation_date", "brand", "depot", "district", "dock_type", prob_col, label_col, "error_type") if c in work.columns]
    return work.loc[keep, cols].sort_values(cols[:1], kind="stable") if cols else work.loc[keep]

