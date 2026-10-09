"""Frozen Task 1 Phase 08 development-fold baselines."""

from __future__ import annotations

from dataclasses import dataclass
import warnings
from typing import Any

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LinearRegression, LogisticRegression

from src.task1.baseline_preprocessing import build_fold_preprocessor, select_simple_baseline_features
from src.task1.metrics import (
    lateness_probability_metrics, lateness_segment_metrics, regression_metrics,
    regression_segment_metrics,
)
from src.task1.validation import TemporalFold


class Task1BaselineError(ValueError):
    """Raised when a baseline cannot obey frozen Phase 07/08 safety rules."""


def _target(y: Any, *, binary: bool = False) -> np.ndarray:
    arr = np.asarray(y, dtype=float)
    if not len(arr) or not np.isfinite(arr).all():
        raise Task1BaselineError("Baseline training targets must be nonempty and finite.")
    if binary and not set(np.unique(arr)).issubset({0.0, 1.0}):
        raise Task1BaselineError("Lateness targets must be binary.")
    return arr


class GlobalMedianServiceBaseline:
    def fit(self, X: pd.DataFrame, y: Any) -> "GlobalMedianServiceBaseline":
        self.value_ = float(np.median(_target(y)))
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.value_, dtype=float)


class HierarchicalServiceMedianBaseline:
    """Train-only brand+dock -> brand -> global service medians."""
    def __init__(self, *, use_dock: bool = True) -> None:
        self.use_dock = use_dock

    def fit(self, X: pd.DataFrame, y: Any) -> "HierarchicalServiceMedianBaseline":
        required = {"brand", "dock_type"} if self.use_dock else {"brand"}
        if not required <= set(X.columns):
            raise Task1BaselineError(f"Service baseline requires: {sorted(required)}.")
        work = X[[c for c in ("brand", "dock_type") if c in X]].copy()
        work["brand"] = work["brand"].fillna("__MISSING__")
        if "dock_type" in work:
            work["dock_type"] = work["dock_type"].fillna("__MISSING__")
        work["_y"] = _target(y)
        self.global_ = float(work["_y"].median())
        self.brand_ = work.groupby("brand", dropna=False)["_y"].median().to_dict()
        self.brand_dock_ = (
            work.groupby(["brand", "dock_type"], dropna=False)["_y"].median().to_dict()
            if self.use_dock else {}
        )
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        required = {"brand", "dock_type"} if self.use_dock else {"brand"}
        if not required <= set(X.columns):
            raise Task1BaselineError(f"Service baseline requires: {sorted(required)}.")
        return np.array([
            float(
                self.brand_dock_.get(
                    (r["brand"] if pd.notna(r["brand"]) else "__MISSING__", r["dock_type"] if pd.notna(r["dock_type"]) else "__MISSING__"),
                    self.brand_.get(r["brand"] if pd.notna(r["brand"]) else "__MISSING__", self.global_),
                )
                if self.use_dock else self.brand_.get(r["brand"] if pd.notna(r["brand"]) else "__MISSING__", self.global_)
            )
            for _, r in X.iterrows()
        ])


class ConstantLateProbabilityBaseline:
    def fit(self, X: pd.DataFrame, y: Any) -> "ConstantLateProbabilityBaseline":
        self.value_ = float(np.mean(_target(y, binary=True)))
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.value_, dtype=float)


class HierarchicalLateRateBaseline:
    """Train-only brand+dock -> brand -> global empirical late rates."""
    def fit(self, X: pd.DataFrame, y: Any) -> "HierarchicalLateRateBaseline":
        if not {"brand", "dock_type"} <= set(X.columns):
            raise Task1BaselineError("Grouped late-rate baseline requires brand and dock_type.")
        work = X[["brand", "dock_type"]].copy()
        work["brand"] = work["brand"].fillna("__MISSING__")
        work["dock_type"] = work["dock_type"].fillna("__MISSING__")
        work["_y"] = _target(y, binary=True)
        self.global_ = float(work["_y"].mean())
        self.brand_ = work.groupby("brand", dropna=False)["_y"].mean().to_dict()
        self.brand_dock_ = work.groupby(["brand", "dock_type"], dropna=False)["_y"].mean().to_dict()
        self.count_ = work.groupby(["brand", "dock_type"], dropna=False).size().to_dict()
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        self.validation_group_counts_ = []
        out = []
        for _, r in X.iterrows():
            brand = r["brand"] if pd.notna(r["brand"]) else "__MISSING__"
            dock = r["dock_type"] if pd.notna(r["dock_type"]) else "__MISSING__"
            key = (brand, dock)
            self.validation_group_counts_.append(int(self.count_.get(key, 0)))
            out.append(float(self.brand_dock_.get(key, self.brand_.get(brand, self.global_))))
        return np.asarray(out, dtype=float)


@dataclass
class FoldModelResult:
    predictions: np.ndarray | None
    unsupported: bool = False
    convergence_warning: bool = False
    preprocessor: Any | None = None
    feature_columns: tuple[str, ...] = ()


def fit_predict_linear_baseline(
    X_train: pd.DataFrame, y_train: Any, X_valid: pd.DataFrame, *, registry: pd.DataFrame | None = None,
) -> FoldModelResult:
    columns = select_simple_baseline_features(
        X_train, registry=registry, include_historical_target_features=False,
    )
    preprocessor, _, _ = build_fold_preprocessor(X_train, columns)
    Xt = preprocessor.fit_transform(X_train[columns])
    Xv = preprocessor.transform(X_valid[columns])
    model = LinearRegression().fit(Xt, _target(y_train))
    return FoldModelResult(model.predict(Xv), preprocessor=preprocessor, feature_columns=tuple(columns))


def fit_predict_logistic_baseline(
    X_train: pd.DataFrame, y_train: Any, X_valid: pd.DataFrame, *,
    max_iter: int = 2000, C: float = 1.0, random_state: int = 42, registry: pd.DataFrame | None = None,
) -> FoldModelResult:
    y = _target(y_train, binary=True)
    if len(np.unique(y)) < 2:
        return FoldModelResult(None, unsupported=True)
    columns = select_simple_baseline_features(
        X_train, registry=registry, include_historical_target_features=False,
    )
    preprocessor, _, _ = build_fold_preprocessor(X_train, columns)
    Xt = preprocessor.fit_transform(X_train[columns])
    Xv = preprocessor.transform(X_valid[columns])
    model = LogisticRegression(
        solver="lbfgs", max_iter=max_iter, C=C, class_weight=None, random_state=random_state
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(Xt, y)
    return FoldModelResult(
        model.predict_proba(Xv)[:, 1],
        convergence_warning=any(issubclass(w.category, ConvergenceWarning) for w in caught),
        preprocessor=preprocessor,
        feature_columns=tuple(columns),
    )


def evaluate_baseline_fold(
    *, model_name: str, target: str, fold: TemporalFold, y_valid: Any, prediction: Any,
    segment_frame: pd.DataFrame, segment_fields: list[str], segment_config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Evaluate with frozen Phase 07 metrics; the holdout is never supplied."""
    if target == "service":
        metrics = regression_metrics(y_valid, prediction)
        segment_fn = regression_segment_metrics
    elif target == "late":
        metrics = lateness_probability_metrics(y_valid, prediction)
        segment_fn = lateness_segment_metrics
    else:
        raise Task1BaselineError(f"Unknown baseline target: {target}")
    common = {
        "model_name": model_name, "target": target, "fold_id": fold.fold,
        "train_start_date": str(min(fold.train_dates).date()),
        "train_end_date": str(max(fold.train_dates).date()),
        "validation_start_date": str(min(fold.validation_dates).date()),
        "validation_end_date": str(max(fold.validation_dates).date()),
        "train_n": len(fold.train_index), "validation_n": len(fold.validation_index),
    }
    rows = [{**common, "metric_name": key, "metric_value": value} for key, value in metrics.items() if isinstance(value, (int, float))]
    segment_rows: list[dict[str, Any]] = []
    for field in segment_fields:
        if field not in segment_frame.columns:
            continue
        kwargs = {
            "minimum_n": int(segment_config["minimum_n"]),
        }
        if target == "late":
            kwargs.update(
                minimum_positive_for_auc=int(segment_config["minimum_positive_for_auc"]),
                minimum_negative_for_auc=int(segment_config["minimum_negative_for_auc"]),
            )
        for row in segment_fn(segment_frame, y_valid, prediction, field, **kwargs):
            segment_rows.append({**common, **row})
    return rows, segment_rows


def aggregate_fold_results(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return pd.DataFrame()
    numeric = rows[pd.to_numeric(rows["metric_value"], errors="coerce").notna()].copy()
    numeric["metric_value"] = pd.to_numeric(numeric["metric_value"])
    grouped = numeric.groupby(["model_name", "target", "metric_name"])["metric_value"]
    summary = grouped.agg(
        fold_count="count", mean="mean", std="std", median="median", min="min", max="max"
    ).reset_index()
    best = numeric.loc[numeric.groupby(["model_name", "target", "metric_name"])["metric_value"].idxmin()]
    worst = numeric.loc[numeric.groupby(["model_name", "target", "metric_name"])["metric_value"].idxmax()]
    summary = summary.merge(
        best[["model_name", "target", "metric_name", "fold_id"]].rename(columns={"fold_id": "best_fold"}),
        on=["model_name", "target", "metric_name"], how="left",
    ).merge(
        worst[["model_name", "target", "metric_name", "fold_id"]].rename(columns={"fold_id": "worst_fold"}),
        on=["model_name", "target", "metric_name"], how="left",
    )
    return summary
