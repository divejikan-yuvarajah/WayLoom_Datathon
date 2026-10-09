"""Read-only explainability primitives for the frozen Task 1 models."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from src.task1.feature_registry import (
    FORBIDDEN_DIRECT_TASK1_FEATURES,
    build_feature_registry,
    validate_feature_registry,
)
from src.task1.features import HISTORICAL_FEATURE_COLUMNS
from src.task1.final_train import (
    TARGET_COLUMNS,
    apply_frozen_calibrator,
    identify_positive_class_index,
    predict_positive_probability,
    prepare_model_frame,
)
from src.task1.inference import apply_service_postprocessing, assert_probabilities_valid
from src.task1.shap_adapter import ShapResult, native_feature_importance


class ExplainabilityError(ValueError):
    """Raised when an explanation would violate the frozen Task 1 contract."""


NONCAUSAL_DISCLAIMER = (
    "These explanations describe how the trained model uses observed features. "
    "They reflect model associations and attribution, not causal effects."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frozen_artifact_paths(final_model_config: Path, service_model_dir: Path,
                          late_model_dir: Path, submission: Path) -> list[Path]:
    paths = [Path(final_model_config), Path(submission)]
    for directory in (Path(service_model_dir), Path(late_model_dir)):
        for name in ("model.joblib", "metadata.json", "feature_schema.json"):
            paths.append(directory / name)
        calibration = directory / "calibration.joblib"
        if calibration.is_file():
            paths.append(calibration)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise ExplainabilityError("Frozen artifact missing: " + ", ".join(missing))
    return paths


def hash_artifacts(paths: Iterable[Path], *, root: Path | None = None) -> dict[str, str]:
    base = Path(root).resolve() if root else None
    result: dict[str, str] = {}
    for item in paths:
        path = Path(item).resolve()
        try:
            key = path.relative_to(base).as_posix() if base else path.as_posix()
        except ValueError:
            key = path.as_posix()
        result[key] = sha256_file(path)
    return dict(sorted(result.items()))


def assert_hashes_unchanged(before: dict[str, str], after: dict[str, str]) -> None:
    if before != after:
        changed = sorted(set(before) | set(after))
        changed = [name for name in changed if before.get(name) != after.get(name)]
        raise ExplainabilityError("Frozen Task 1 artifact hash changed: " + ", ".join(changed))


def semantic_group(feature_name: str) -> str:
    name = str(feature_name).lower()
    if name in HISTORICAL_FEATURE_COLUMNS or ("_prior_" in name and ("service" in name or "late" in name)):
        return "chronology_safe_historical_behavior"
    if any(token in name for token in ("slack", "planned_arrival", "planned_depart", "planned_travel")):
        return "planned_time_and_slack"
    if any(token in name for token in ("order_units", "order_weight", "order_volume", "density", "per_unit")):
        return "order_size_and_composition"
    if any(token in name for token in ("route_", "seq", "prior_stop", "prior_planned", "leg_distance", "inter_stop")):
        return "route_position_and_planned_workload"
    if any(token in name for token in ("service_allowance", "dock", "parking", "mall_window")):
        return "access_and_reference_service_context"
    if any(token in name for token in ("vehicle", "weight_cap", "volume_cap", "fuel", "utilization")):
        return "vehicle_and_capacity_context"
    if any(token in name for token in ("festival", "holiday", "weekend", "payday", "monsoon", "iso_", "dow", "date")):
        return "calendar_and_environment_context"
    if any(token in name for token in ("brand", "district", "depot", "temp_requirement", "road_class")):
        return "commercial_and_location_context"
    if any(token in name for token in ("distance", "freeflow", "speed")):
        return "planned_travel_and_distance"
    return "other_prediction_time_context"


def build_explanation_registry(feature_columns: list[str], *,
                               categorical_columns: list[str] | None = None) -> pd.DataFrame:
    registry = build_feature_registry(
        list(feature_columns), historical_columns=set(feature_columns) & set(HISTORICAL_FEATURE_COLUMNS)
    )
    registry = registry.copy()
    categorical = set(categorical_columns or [])
    unknown_categorical = sorted(categorical - set(feature_columns))
    if unknown_categorical:
        raise ExplainabilityError(
            "Frozen categorical schema contains unknown features: " + ", ".join(unknown_categorical)
        )
    if categorical:
        mask = registry["feature_name"].isin(categorical)
        registry.loc[mask, "categorical"] = True
        registry.loc[mask, "semantic_type"] = "categorical"
    registry["semantic_group"] = registry["feature_name"].map(semantic_group)
    validate_feature_registry(registry, expected_features=list(feature_columns))
    return registry


def audit_explanation_schema(service_schema: dict[str, Any], late_schema: dict[str, Any],
                             registry: pd.DataFrame) -> dict[str, Any]:
    service = list(service_schema.get("feature_columns") or [])
    late = list(late_schema.get("feature_columns") or [])
    if not service or service != late:
        raise ExplainabilityError("Service and lateness frozen feature schemas must match exactly.")
    service_categorical = list(service_schema.get("categorical_columns") or [])
    late_categorical = list(late_schema.get("categorical_columns") or [])
    if service_categorical != late_categorical:
        raise ExplainabilityError("Service and lateness frozen categorical schemas must match exactly.")
    if service_schema.get("missing_category_token") != late_schema.get("missing_category_token"):
        raise ExplainabilityError("Service and lateness frozen missing-category semantics differ.")
    if service_schema.get("feature_profile") != late_schema.get("feature_profile"):
        raise ExplainabilityError("Service and lateness frozen feature profiles differ.")
    validate_feature_registry(registry, expected_features=service)
    registry_categorical = registry.set_index("feature_name")["categorical"].astype(bool)
    if [name for name in service if bool(registry_categorical.at[name])] != service_categorical:
        raise ExplainabilityError("Explanation registry does not preserve frozen categorical semantics.")
    explained = set(service)
    forbidden = sorted(explained & set(FORBIDDEN_DIRECT_TASK1_FEATURES))
    targets = sorted(explained & set(TARGET_COLUMNS))
    if forbidden or targets:
        raise ExplainabilityError(
            f"Forbidden actual/outcome or target feature in explanation schema: {sorted(set(forbidden + targets))}"
        )
    unsafe = registry.loc[
        registry["feature_name"].isin(service)
        & (~registry["prediction_time_safe"].astype(bool)),
        "feature_name",
    ].tolist()
    if unsafe:
        raise ExplainabilityError("Prediction-time-unsafe explanation features: " + ", ".join(sorted(unsafe)))
    historical = registry[registry["uses_target_history"].astype(bool)]
    invalid_history = historical[
        (~historical["requires_fit"].astype(bool))
        | (historical["fit_scope"] != "training_fold_only")
    ]["feature_name"].tolist()
    if invalid_history:
        raise ExplainabilityError("Historical explanation feature lacks frozen fit-scope safety.")
    return {
        "status": "PASS",
        "feature_count": len(service),
        "service_late_schema_parity": True,
        "registry_complete": True,
        "forbidden_direct_count": 0,
        "target_feature_count": 0,
        "unsafe_lineage_count": 0,
        "historical_feature_count": int(len(historical)),
        "historical_features_frozen_chronology_safe": True,
    }


def prepare_frozen_model_frame(bundle: dict[str, Any], features: pd.DataFrame) -> pd.DataFrame:
    schema = bundle["schema"]
    columns = list(schema.get("feature_columns") or [])
    categorical = list(schema.get("categorical_columns") or [])
    family = str((bundle.get("metadata") or {}).get("model_family") or "").lower()
    if not columns:
        raise ExplainabilityError("Frozen feature schema is empty.")
    missing = [name for name in columns if name not in features.columns]
    if missing:
        raise ExplainabilityError("Explanation features are missing frozen columns: " + ", ".join(missing))
    try:
        return prepare_model_frame(
            features,
            columns,
            categorical,
            as_category=family in {"lightgbm", "xgboost"},
        )
    except Exception as exc:
        raise ExplainabilityError(str(exc)) from exc


def deterministic_sample_positions(frame: pd.DataFrame, *, max_rows: int, seed: int) -> np.ndarray:
    if max_rows <= 0:
        raise ExplainabilityError("SHAP max_rows must be positive.")
    count = len(frame)
    if count == 0:
        raise ExplainabilityError("Explanation population is empty.")
    if count <= max_rows:
        return np.arange(count, dtype=int)
    hashed = pd.util.hash_pandas_object(frame, index=False).to_numpy(dtype=np.uint64)
    mixed = hashed ^ np.uint64(int(seed) & ((1 << 64) - 1))
    positions = np.arange(count, dtype=int)
    order = np.lexsort((positions, mixed))
    return np.sort(order[:max_rows].astype(int))


def summarize_shap(result: ShapResult, feature_names: list[str],
                   registry: pd.DataFrame) -> pd.DataFrame:
    if result.values.shape[1] != len(feature_names):
        raise ExplainabilityError("SHAP columns do not match frozen feature names.")
    meta = registry.set_index("feature_name")
    rows: list[dict[str, Any]] = []
    for index, name in enumerate(feature_names):
        values = result.values[:, index]
        rows.append({
            "feature_name": name,
            "mean_abs_shap": float(np.mean(np.abs(values))),
            "mean_shap": float(np.mean(values)),
            "sample_count": int(len(values)),
            "semantic_group": str(meta.at[name, "semantic_group"]),
            "source_lineage": json.dumps(meta.at[name, "source_columns"], sort_keys=True),
            "direction_statement": "context-dependent/not inferred from mean absolute SHAP",
        })
    output = pd.DataFrame(rows).sort_values(
        ["mean_abs_shap", "feature_name"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    output["rank"] = np.arange(1, len(output) + 1)
    return output[[
        "feature_name", "mean_abs_shap", "mean_shap", "rank", "sample_count",
        "semantic_group", "source_lineage", "direction_statement",
    ]]


def build_feature_importance(model: Any, *, family: str, feature_names: list[str],
                             registry: pd.DataFrame, shap_summary: pd.DataFrame) -> pd.DataFrame:
    native = native_feature_importance(model, family=family, feature_names=feature_names)
    if native is None:
        lookup = shap_summary.set_index("feature_name")["mean_abs_shap"]
        values = np.asarray([float(lookup.at[name]) for name in feature_names])
        importance_type = "mean_abs_shap_fallback"
    else:
        values, importance_type = native
    meta = registry.set_index("feature_name")
    rows = []
    for name, value in zip(feature_names, values, strict=True):
        rows.append({
            "feature_name": name,
            "importance": float(value),
            "importance_type": importance_type,
            "semantic_group": str(meta.at[name, "semantic_group"]),
            "source_lineage": json.dumps(meta.at[name, "source_columns"], sort_keys=True),
        })
    output = pd.DataFrame(rows).sort_values(
        ["importance", "feature_name"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    output["rank"] = np.arange(1, len(output) + 1)
    return output[["feature_name", "importance", "importance_type", "rank", "semantic_group", "source_lineage"]]


def select_service_example(final_predictions: np.ndarray) -> int:
    values = np.asarray(final_predictions, dtype=float).reshape(-1)
    if len(values) == 0 or not np.isfinite(values).all():
        raise ExplainabilityError("Service predictions are empty or nonfinite.")
    median = float(np.median(values))
    return int(np.argmin(np.abs(values - median)))


def select_late_example(final_probabilities: np.ndarray) -> int:
    values = assert_probabilities_valid(np.asarray(final_probabilities, dtype=float).reshape(-1))
    if len(values) == 0:
        raise ExplainabilityError("Lateness predictions are empty.")
    return int(np.argmax(values))


def service_prediction_bridge(raw_predictions: np.ndarray, policy: str) -> tuple[np.ndarray, dict[str, Any]]:
    return apply_service_postprocessing(np.asarray(raw_predictions, dtype=float), policy)


def lateness_probability_bridge(bundle: dict[str, Any], frame: pd.DataFrame) -> dict[str, Any]:
    metadata = bundle.get("metadata") or {}
    stored = metadata.get("positive_class_index")
    detected = identify_positive_class_index(bundle["model"])
    if stored is None or int(stored) != detected:
        raise ExplainabilityError("Frozen lateness positive class is absent or ambiguous.")
    base_probability = predict_positive_probability(bundle["model"], frame, detected)
    method = str(metadata.get("calibration_method") or "raw").strip().lower()
    if method in {"raw", "none", "null", ""}:
        final = base_probability.copy()
        applied = False
    else:
        if bundle.get("calibration") is None:
            raise ExplainabilityError("Frozen calibration artifact is missing.")
        final = apply_frozen_calibrator(bundle["calibration"], base_probability)
        applied = True
    assert_probabilities_valid(final)
    return {
        "positive_class": 1,
        "positive_class_index": int(detected),
        "calibration_method": method or "raw",
        "calibration_applied": applied,
        "base_probability": np.asarray(base_probability, dtype=float),
        "final_probability": np.asarray(final, dtype=float),
    }


def _safe_value(value: Any) -> Any:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return str(pd.Timestamp(value))
    return str(value)


def local_contributors(result: ShapResult, frame: pd.DataFrame, *, row_position: int,
                       registry: pd.DataFrame, top_positive: int, top_negative: int) -> dict[str, list[dict[str, Any]]]:
    if row_position < 0 or row_position >= len(frame) or result.values.shape[0] != len(frame):
        raise ExplainabilityError("Local explanation row is outside the SHAP frame.")
    meta = registry.set_index("feature_name")
    entries = [{
        "feature_name": name,
        "shap_value": float(result.values[row_position, index]),
        "feature_value": _safe_value(frame.iloc[row_position, index]),
        "semantic_group": str(meta.at[name, "semantic_group"]),
    } for index, name in enumerate(frame.columns)]
    positive = sorted((item for item in entries if item["shap_value"] > 0),
                      key=lambda item: (-item["shap_value"], item["feature_name"]))[:top_positive]
    negative = sorted((item for item in entries if item["shap_value"] < 0),
                      key=lambda item: (item["shap_value"], item["feature_name"]))[:top_negative]
    return {"top_positive_contributors": positive, "top_negative_contributors": negative}


def assert_prediction_parity(expected: np.ndarray, actual: np.ndarray, *, label: str,
                             tolerance: float = 1e-12) -> float:
    left = np.asarray(expected, dtype=float).reshape(-1)
    right = np.asarray(actual, dtype=float).reshape(-1)
    if len(left) != len(right) or not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ExplainabilityError(f"{label} prediction parity inputs are invalid.")
    error = float(np.max(np.abs(left - right))) if len(left) else 0.0
    if error > tolerance:
        raise ExplainabilityError(f"{label} predictions changed during explainability (max error {error}).")
    return error
