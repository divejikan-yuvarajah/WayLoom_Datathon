"""Frozen Phase 16 Task 2A component fitting for Phase 17 inference only."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor

from src.task2a.baselines import ForecastRequest, build_history_as_of_origin, predict_baseline
from src.task2a.model_preprocessing import lightgbm_fold_preprocessor, select_predictors


class FinalFitError(ValueError):
    """A frozen Phase 16 component cannot be safely executed."""


@dataclass
class FittedComponent:
    spec: dict[str, Any]
    target: str
    model: Any | None = None
    preprocessor: Any | None = None
    components: tuple["FittedComponent", "FittedComponent"] | None = None


def _target_column(target: str) -> str:
    if target == "total":
        return "target_total_volume_m3"
    if target == "chilled":
        return "target_chilled_volume_m3"
    raise FinalFitError("Final target must be total or chilled.")


def final_training_rows(table: pd.DataFrame, origin: pd.Timestamp, target: str) -> pd.DataFrame:
    """Return only labels that were knowable at the one final forecast origin."""
    label = _target_column(target)
    required = {"target_week_start_date", "brand", label}
    missing = required.difference(table.columns)
    if missing:
        raise FinalFitError("Final training table is missing: " + ", ".join(sorted(missing)))
    rows = table.copy()
    rows["target_week_start_date"] = pd.to_datetime(rows["target_week_start_date"], errors="raise").dt.normalize()
    origin = pd.Timestamp(origin).normalize()
    rows = rows.loc[rows.target_week_start_date.le(origin)].copy()
    if target == "chilled":
        rows = rows.loc[rows.brand.eq("Fresh")].copy()
    if rows.empty or not rows.target_week_start_date.le(origin).all():
        raise FinalFitError("Final training contains no target-safe rows.")
    values = pd.to_numeric(rows[label], errors="raise").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise FinalFitError("Final training labels contain NaN/Inf.")
    return rows.reset_index(drop=True)


def _fit_model(spec: dict[str, Any], target: str, rows: pd.DataFrame, profile: dict[str, Any]) -> FittedComponent:
    params = dict(spec.get("parameters") or {})
    family = spec.get("family")
    policy = spec.get("final_iteration_policy") or {}
    if policy.get("method") != "median_best_iteration" or type(policy.get("value")) is not int:
        raise FinalFitError("Frozen ML component lacks its final iteration value.")
    iteration = int(policy["value"])
    x_train = select_predictors(rows, profile)
    y_train = rows[_target_column(target)].to_numpy(dtype=float)
    if family == "catboost":
        params.pop("candidate_id", None)
        params.pop("early_stopping_rounds", None)
        params["iterations"] = iteration
        model = CatBoostRegressor(**params)
        model.fit(x_train, y_train, cat_features=profile["categorical"])
        return FittedComponent(spec, target, model=model)
    if family == "lightgbm":
        params.pop("candidate_id", None)
        params.pop("early_stopping_rounds", None)
        params["n_estimators"] = iteration
        preprocessor = lightgbm_fold_preprocessor(profile)
        transformed = preprocessor.fit_transform(x_train)
        model = LGBMRegressor(**params, verbosity=-1)
        model.fit(transformed, y_train)
        return FittedComponent(spec, target, model=model, preprocessor=preprocessor)
    raise FinalFitError("Frozen model component family is unsupported.")


def fit_frozen_component(spec: dict[str, Any], target: str, training_table: pd.DataFrame,
                         origin: pd.Timestamp, profile: dict[str, Any]) -> FittedComponent:
    """Fit one frozen component.  This function has no tuning or search path."""
    approach = spec.get("approach_type")
    if approach == "baseline":
        if not str(spec.get("candidate_id", "")).startswith(f"{target}_"):
            raise FinalFitError("Frozen baseline target identity is invalid.")
        return FittedComponent(spec, target)
    if approach == "model":
        return _fit_model(spec, target, final_training_rows(training_table, origin, target), profile)
    if approach == "ensemble":
        parts = spec.get("component_candidates")
        weights = spec.get("component_weights")
        if not isinstance(parts, list) or len(parts) != 2 or weights != [0.5, 0.5]:
            raise FinalFitError("Frozen ensemble must contain exactly two fixed 50/50 components.")
        return FittedComponent(spec, target, components=(
            fit_frozen_component(parts[0], target, training_table, origin, profile),
            fit_frozen_component(parts[1], target, training_table, origin, profile),
        ))
    raise FinalFitError("Frozen champion approach is invalid.")


def predict_frozen_component(component: FittedComponent, features: pd.DataFrame, history: pd.DataFrame,
                             origin: pd.Timestamp, profile: dict[str, Any]) -> np.ndarray:
    """Return one raw prediction per keyed feature row, preserving Phase 16 raw values."""
    spec = component.spec
    approach = spec["approach_type"]
    if approach == "baseline":
        family = str(spec["candidate_id"]).removeprefix(f"{component.target}_")
        safe_history = build_history_as_of_origin(history, origin)
        values = []
        for row in features.itertuples(index=False):
            request = ForecastRequest(str(row.depot), str(row.brand), pd.Timestamp(origin).normalize(),
                pd.Timestamp(row.target_week_start_date).normalize(), int(row.target_iso_year),
                int(row.target_iso_week), int(row.horizon_weeks))
            prediction = predict_baseline(safe_history, request, component.target, family)
            if prediction.value is None:
                raise FinalFitError("Frozen baseline is unavailable for an official inference row.")
            values.append(float(prediction.value))
        output = np.asarray(values, dtype=float)
    elif approach == "model":
        x = select_predictors(features, profile)
        if spec["family"] == "lightgbm":
            output = np.asarray(component.model.predict(component.preprocessor.transform(x)), dtype=float)
        else:
            output = np.asarray(component.model.predict(x), dtype=float)
    elif approach == "ensemble":
        if component.components is None:
            raise FinalFitError("Frozen ensemble components are unavailable.")
        left = predict_frozen_component(component.components[0], features, history, origin, profile)
        right = predict_frozen_component(component.components[1], features, history, origin, profile)
        if "row_id" not in features or features.row_id.duplicated().any():
            raise FinalFitError("Frozen ensemble requires unique official row_id alignment keys.")
        left_rows = features[["row_id"]].copy()
        left_rows["left"] = left
        right_rows = features[["row_id"]].copy()
        right_rows["right"] = right
        paired = left_rows.merge(right_rows, on="row_id", how="outer", validate="one_to_one", indicator=True)
        if len(paired) != len(features) or not paired._merge.eq("both").all():
            raise FinalFitError("Frozen ensemble component keys do not align.")
        output = 0.5 * paired.left.to_numpy(dtype=float) + 0.5 * paired.right.to_numpy(dtype=float)
    else:  # pragma: no cover - guarded at fit time
        raise FinalFitError("Unknown frozen component approach.")
    if output.shape != (len(features),) or not np.isfinite(output).all():
        raise FinalFitError("Frozen component produced missing or nonfinite raw predictions.")
    return output
