"""Validated out-of-sample residual adapters for frozen Task 1 and Task 2A."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.task1.advanced_models import build_phase09_candidates, fit_predict_advanced_fold
from src.task1.final_train import resolve_negative_service_policy
from src.task1.inference import apply_service_postprocessing
from src.task1.validation import build_task1_validation_plan


class ResidualSourceError(ValueError):
    """Residual provenance is not a valid frozen out-of-sample source."""


OOS_SOURCE_TYPES = {"frozen_oos_validation", "frozen_rolling_oos"}


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    if not isinstance(value, dict):
        raise ResidualSourceError("Configuration must be a mapping.")
    return value


def validate_oos_residuals(frame: pd.DataFrame, *, source_type: str) -> pd.DataFrame:
    required = {"actual", "prediction", "absolute_residual", "fold", "source_type"}
    if required.difference(frame.columns) or frame.empty:
        raise ResidualSourceError("OOS residual table is empty or incomplete.")
    if source_type not in OOS_SOURCE_TYPES or not frame.source_type.eq(source_type).all():
        raise ResidualSourceError("Residual source is not an approved out-of-sample source.")
    numeric = frame[["actual", "prediction", "absolute_residual"]].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ResidualSourceError("Residual values must be finite.")
    expected = (numeric.actual - numeric.prediction).abs().to_numpy(dtype=float)
    if not np.allclose(expected, numeric.absolute_residual.to_numpy(dtype=float), rtol=0, atol=1e-12):
        raise ResidualSourceError("Absolute residuals do not match actual and OOS prediction.")
    if frame["fold"].isna().any():
        raise ResidualSourceError("Every OOS residual requires fold/origin provenance.")
    return frame.copy()


def recreate_task1_service_oos(
    features: pd.DataFrame,
    labels: pd.DataFrame,
    validation_config: dict[str, Any],
    advanced_config: dict[str, Any],
    final_config: dict[str, Any],
) -> pd.DataFrame:
    """Replay the frozen Phase 9 selected service candidate on Phase 7 folds."""
    service = final_config.get("service_model") or {}
    candidate_id = service.get("config_id")
    candidates = {item.candidate_id: item for item in build_phase09_candidates(advanced_config) if item.target == "service"}
    candidate = candidates.get(candidate_id)
    if candidate is None:
        raise ResidualSourceError("Frozen Task 1 service candidate is absent from the Phase 9 catalog.")
    frozen_params = dict(service.get("parameters") or {})
    for key, value in candidate.params.items():
        if key not in frozen_params or frozen_params[key] != value:
            raise ResidualSourceError("Frozen Task 1 parameters differ from the Phase 9 validation candidate.")
    if len(features) != len(labels) or not features.index.equals(labels.index):
        raise ResidualSourceError("Task 1 feature/label rows are not exactly aligned.")
    if "service_minutes" not in labels:
        raise ResidualSourceError("Task 1 service labels are unavailable.")
    plan = build_task1_validation_plan(labels, validation_config)
    early = advanced_config.get("early_stopping") or {}
    policy = resolve_negative_service_policy(final_config)
    rows: list[pd.DataFrame] = []
    date_col = "route_date" if "route_date" in labels else "date"
    for fold in plan["folds"]:
        result = fit_predict_advanced_fold(
            candidate=candidate,
            X_train=features.loc[fold.train_index],
            y_train=labels.loc[fold.train_index, "service_minutes"],
            X_valid=features.loc[fold.validation_index],
            y_valid=labels.loc[fold.validation_index, "service_minutes"],
            max_iterations=int(early["max_iterations"]),
            patience_rounds=int(early["patience_rounds"]),
            min_iterations=int(early["min_iterations"]),
        )
        prediction, _ = apply_service_postprocessing(result.prediction, policy)
        actual = labels.loc[fold.validation_index, "service_minutes"].to_numpy(dtype=float)
        part = pd.DataFrame({
            "actual": actual,
            "prediction": prediction,
            "fold": int(fold.fold),
            "validation_date": pd.to_datetime(labels.loc[fold.validation_index, date_col]).dt.date.astype(str).to_numpy(),
            "source_type": "frozen_oos_validation",
        })
        part["absolute_residual"] = (part.actual - part.prediction).abs()
        rows.append(part)
    return validate_oos_residuals(pd.concat(rows, ignore_index=True), source_type="frozen_oos_validation")


TASK2A_KEYS = ["backtest_id", "depot", "brand", "origin_week_start_date", "target_week_start_date", "horizon_weeks"]


def load_task2a_frozen_oos(candidate_predictions: pd.DataFrame, final_config: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Select frozen Phase 16 champions and apply Phase 17 point semantics."""
    required = {*TASK2A_KEYS, "target_name", "candidate_id", "y_true", "y_pred", "phase14_backtest_signature"}
    if required.difference(candidate_predictions.columns):
        raise ResidualSourceError("Phase 16 candidate-prediction artifact is incomplete.")
    signature = str((final_config.get("validation") or {}).get("backtest_signature") or "")
    if not signature or not candidate_predictions.phase14_backtest_signature.astype(str).eq(signature).all():
        raise ResidualSourceError("Task 2A OOS predictions do not match the frozen Phase 14 signature.")
    total_id = str((final_config.get("total") or {}).get("candidate_id") or "")
    chilled_id = str((final_config.get("chilled_fresh") or {}).get("candidate_id") or "")
    total = candidate_predictions.loc[
        candidate_predictions.target_name.eq("total") & candidate_predictions.candidate_id.eq(total_id)
    ].copy()
    chilled = candidate_predictions.loc[
        candidate_predictions.target_name.eq("chilled") & candidate_predictions.candidate_id.eq(chilled_id)
    ].copy()
    if total.empty or chilled.empty or total.duplicated(TASK2A_KEYS).any() or chilled.duplicated(TASK2A_KEYS).any():
        raise ResidualSourceError("Frozen Task 2A champion OOS rows are missing or duplicated.")
    total["prediction"] = np.maximum(pd.to_numeric(total.y_pred, errors="raise"), 0.0)
    total["actual"] = pd.to_numeric(total.y_true, errors="raise")
    total["target"] = "total"
    total["fold"] = total.backtest_id
    total["source_type"] = "frozen_rolling_oos"
    fresh_total = total.loc[total.brand.eq("Fresh"), [*TASK2A_KEYS, "prediction"]].rename(
        columns={"prediction": "total_prediction"}
    )
    chilled = chilled.merge(fresh_total, on=TASK2A_KEYS, how="left", validate="one_to_one")
    if chilled.total_prediction.isna().any() or not chilled.brand.eq("Fresh").all():
        raise ResidualSourceError("Fresh chilled OOS predictions do not align with frozen total predictions.")
    chilled["prediction"] = np.minimum(
        np.maximum(pd.to_numeric(chilled.y_pred, errors="raise"), 0.0), chilled.total_prediction
    )
    chilled["actual"] = pd.to_numeric(chilled.y_true, errors="raise")
    chilled["target"] = "chilled"
    chilled["fold"] = chilled.backtest_id
    chilled["source_type"] = "frozen_rolling_oos"
    result: dict[str, pd.DataFrame] = {}
    for name, frame in (("total", total), ("chilled", chilled)):
        frame["absolute_residual"] = (frame.actual - frame.prediction).abs()
        result[name] = validate_oos_residuals(frame, source_type="frozen_rolling_oos")
    return result
