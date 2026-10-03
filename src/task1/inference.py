"""Phase 10 saved-model Task 1 inference. Never trains models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.task1.features import build_task1_feature_tables, load_task1_features_config
from src.task1.final_train import (
    TARGET_COLUMNS,
    Task1FinalTrainError,
    apply_frozen_calibrator,
    assert_feature_schema_equal,
    load_frozen_final_config,
    load_model_bundle,
    load_yaml,
    prepare_model_frame,
    predict_positive_probability,
    resolve_feature_columns,
    resolve_negative_service_policy,
)
from src.task1.feature_registry import FORBIDDEN_DIRECT_TASK1_FEATURES
from src.task1.historical_features import Task1HistoricalFeatureTransformer
from src.task1.labels import TASK1_FORBIDDEN_DIRECT_FEATURES

OFFICIAL_ROW_ORDER = "__official_row_order"
FORBIDDEN_INFERENCE_FEATURES = set(FORBIDDEN_DIRECT_TASK1_FEATURES) | set(TASK1_FORBIDDEN_DIRECT_FEATURES) | set(
    TARGET_COLUMNS
)


class Task1InferenceError(ValueError):
    """Raised when saved-model inference violates the Phase 10 contract."""


def assert_saved_models_present(service_dir: Path, late_dir: Path) -> None:
    missing = [str(p) for p in (Path(service_dir) / "model.joblib", Path(late_dir) / "model.joblib") if not p.is_file()]
    if missing:
        raise Task1InferenceError(
            "Saved model artifacts missing; inference must not retrain. Missing: " + ", ".join(missing)
        )


def load_task1_test_inputs(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if OFFICIAL_ROW_ORDER in frame.columns:
        raise Task1InferenceError("Official test inputs already contain the reserved row-order marker.")
    out = frame.copy()
    out.insert(0, OFFICIAL_ROW_ORDER, np.arange(len(out), dtype=int))
    required = {"delivery_id", "route_id", "seq_in_route"}
    missing = sorted(required - set(out.columns))
    if missing:
        raise Task1InferenceError(f"task1_test_inputs missing required columns: {missing}")
    delivery = out["delivery_id"].astype("string").str.strip()
    if delivery.isna().any() or (delivery == "").any():
        raise Task1InferenceError("delivery_id must exist and be non-blank.")
    if delivery.duplicated().any():
        raise Task1InferenceError("delivery_id must be unique in official test inputs.")
    return out


def restore_official_row_order(frame: pd.DataFrame) -> pd.DataFrame:
    if OFFICIAL_ROW_ORDER not in frame.columns:
        raise Task1InferenceError("Cannot restore official order: marker missing.")
    return frame.sort_values(OFFICIAL_ROW_ORDER, kind="stable").reset_index(drop=True)


def assert_delivery_id_integrity(original: pd.Series, final: pd.Series) -> None:
    left = original.astype("string").tolist()
    right = final.astype("string").tolist()
    if left != right:
        raise Task1InferenceError("Official delivery_id ordered sequence was changed.")


def join_route_legs_test(test_inputs: pd.DataFrame, route_legs_test: pd.DataFrame) -> pd.DataFrame:
    if "seq" not in route_legs_test.columns:
        raise Task1InferenceError("route_legs_test must contain seq.")
    left_key = test_inputs["route_id"].astype("string") + "||" + test_inputs["seq_in_route"].astype("string")
    right_key = route_legs_test["route_id"].astype("string") + "||" + route_legs_test["seq"].astype("string")
    if left_key.duplicated().any():
        raise Task1InferenceError("Duplicate official test route keys (route_id, seq_in_route).")
    if right_key.duplicated().any():
        raise Task1InferenceError("Duplicate route_legs_test keys (route_id, seq).")
    original_n = len(test_inputs)
    joined = test_inputs.merge(
        route_legs_test,
        left_on=["route_id", "seq_in_route"],
        right_on=["route_id", "seq"],
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    if len(joined) != original_n:
        raise Task1InferenceError("Official test join changed the row count.")
    if not (joined["_merge"] == "both").all():
        raise Task1InferenceError("Unmatched official Task 1 test orders after route_legs_test join.")
    if joined["delivery_id"].astype("string").duplicated().any():
        raise Task1InferenceError("delivery_id is no longer unique after the official test join.")
    if "outlet_id" in joined.columns and "to_outlet" in joined.columns:
        left = joined["outlet_id"].astype("string")
        right = joined["to_outlet"].astype("string")
        comparable = left.notna() & right.notna() & (left != "<NA>") & (right != "<NA>")
        if comparable.any() and not (left[comparable] == right[comparable]).all():
            raise Task1InferenceError("Destination mismatch: outlet_id != to_outlet.")
    return joined.drop(columns=["_merge"])


def assert_no_forbidden_inference_features(columns: list[str]) -> None:
    forbidden = sorted(set(columns) & FORBIDDEN_INFERENCE_FEATURES)
    if forbidden:
        raise Task1InferenceError(f"Forbidden inference features present: {forbidden}")


def apply_service_postprocessing(raw: np.ndarray, policy: str) -> tuple[np.ndarray, dict[str, Any]]:
    values = np.asarray(raw, dtype=float)
    if not np.isfinite(values).all():
        raise Task1InferenceError("Service predictions contain NaN/Inf.")
    policy = str(policy or "fail").strip().lower()
    if policy in {"abs", "absolute", "abs_value"}:
        raise Task1InferenceError("Taking abs() of negative service predictions is forbidden.")
    n_neg = int((values < 0).sum())
    report = {
        "negative_raw_prediction_count": n_neg,
        "minimum_raw_prediction": float(values.min()) if len(values) else None,
        "postprocessing_policy": policy,
        "postprocessed_count": 0,
    }
    if n_neg == 0:
        report["postprocessing_policy"] = "noop_no_negatives"
        return values, report
    if policy == "clip_to_zero":
        out = np.maximum(values, 0.0)
        report["postprocessed_count"] = n_neg
        return out, report
    if policy == "fail":
        raise Task1InferenceError("Negative service predictions occurred and no clip_to_zero policy was frozen.")
    raise Task1InferenceError(f"Unknown negative service policy: {policy}")


def assert_probabilities_valid(prob: np.ndarray) -> np.ndarray:
    values = np.asarray(prob, dtype=float)
    if not np.isfinite(values).all():
        raise Task1InferenceError("Lateness probabilities contain NaN/Inf.")
    if (values < 0).any() or (values > 1).any():
        raise Task1InferenceError("Lateness probabilities are outside [0, 1]; silent clamping is forbidden.")
    return values


def transform_historical_features_for_unseen_test(
    transformer: Task1HistoricalFeatureTransformer,
    X_test: pd.DataFrame,
) -> pd.DataFrame:
    leaked = [c for c in TARGET_COLUMNS if c in X_test.columns]
    if leaked:
        raise Task1InferenceError(f"Historical test transform must not receive test labels: {leaked}")
    return transformer.transform(X_test)


def _family_uses_category(family: str) -> bool:
    return str(family).lower() in {"lightgbm", "xgboost"}


def predict_service_from_bundle(bundle: dict[str, Any], X: pd.DataFrame) -> np.ndarray:
    schema = bundle["schema"]
    cols = list(schema["feature_columns"])
    cats = list(schema.get("categorical_columns") or [])
    family = str((bundle.get("metadata") or {}).get("model_family") or "")
    frame = prepare_model_frame(X, cols, cats, as_category=_family_uses_category(family))
    pred = np.asarray(bundle["model"].predict(frame), dtype=float).reshape(-1)
    if len(pred) != len(X):
        raise Task1InferenceError("Service model did not return one prediction per row.")
    if not np.isfinite(pred).all():
        raise Task1InferenceError("Service predictions contain NaN/Inf.")
    return pred


def predict_late_from_bundle(bundle: dict[str, Any], X: pd.DataFrame) -> np.ndarray:
    schema = bundle["schema"]
    cols = list(schema["feature_columns"])
    cats = list(schema.get("categorical_columns") or [])
    metadata = bundle.get("metadata") or {}
    family = str(metadata.get("model_family") or "")
    frame = prepare_model_frame(X, cols, cats, as_category=_family_uses_category(family))
    stored_index = metadata.get("positive_class_index")
    raw = predict_positive_probability(bundle["model"], frame, stored_index)
    method = str(metadata.get("calibration_method") or "raw").lower()
    if method not in {"raw", "none", "null", ""}:
        if bundle.get("calibration") is None:
            raise Task1InferenceError("Frozen calibration method requires a saved calibration artifact.")
        out = apply_frozen_calibrator(bundle["calibration"], raw)
    else:
        out = raw
    return assert_probabilities_valid(out)


def run_saved_model_inference(
    X_test: pd.DataFrame,
    service_dir: Path,
    late_dir: Path,
    final_config: dict[str, Any],
    inference_config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    assert_saved_models_present(service_dir, late_dir)
    service_bundle = load_model_bundle(service_dir)
    late_cfg = final_config.get("lateness_model") or {}
    require_cal = str((late_cfg.get("calibration") or {}).get("method") or "raw").lower() not in {
        "raw",
        "none",
        "null",
        "",
    }
    late_bundle = load_model_bundle(late_dir, require_calibration=require_cal)
    assert_no_forbidden_inference_features(list(X_test.columns))
    assert_feature_schema_equal(service_bundle["schema"], list(service_bundle["schema"]["feature_columns"]))
    generated = list(service_bundle["schema"]["feature_columns"])
    missing = [c for c in generated if c not in X_test.columns]
    if missing:
        raise Task1InferenceError(f"Test features missing saved training columns: {missing}")
    assert_feature_schema_equal(service_bundle["schema"], generated)
    if list(late_bundle["schema"]["feature_columns"]) != generated:
        raise Task1InferenceError("Service and lateness saved feature schemas differ.")

    raw_service = predict_service_from_bundle(service_bundle, X_test)
    policy = resolve_negative_service_policy(final_config, inference_config)
    service, _service_report = apply_service_postprocessing(raw_service, policy)
    late = predict_late_from_bundle(late_bundle, X_test)
    return pd.DataFrame(
        {
            "pred_service_min": service,
            "pred_late_prob": late,
        },
        index=X_test.index,
    )


def _manifest_file(raw_root: Path, filename: str) -> Path:
    matches = list(Path(raw_root).rglob(filename))
    if not matches:
        raise Task1InferenceError(f"Official file not found under raw root: {filename}")
    return matches[0]


def _resolve_historical_train_labels(
    historical_train_labels: pd.DataFrame | None,
    labels_path: Path | None,
) -> pd.DataFrame:
    if historical_train_labels is not None:
        return historical_train_labels
    candidates = []
    if labels_path is not None:
        candidates.append(Path(labels_path))
    candidates.append(Path("data/interim/task1_training_labels.csv"))
    for path in candidates:
        if path.is_file():
            return pd.read_csv(path, low_memory=False)
    raise Task1InferenceError(
        "Historical train labels are required to fit Phase 06 historical features. "
        "Pass --labels data/interim/task1_training_labels.csv"
    )


def prepare_test_features_from_raw(
    raw_root: Path,
    feature_registry_path: Path,
    historical_train_labels: pd.DataFrame | None = None,
    *,
    labels_path: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reuse the canonical Phase 06 builder. Historical state is fit on train only."""
    labels_train = _resolve_historical_train_labels(historical_train_labels, labels_path)
    config = load_task1_features_config(feature_registry_path)
    deliveries_train = pd.read_csv(_manifest_file(raw_root, "deliveries_train.csv"), low_memory=False)
    task1_test_inputs = load_task1_test_inputs(_manifest_file(raw_root, "task1_test_inputs.csv"))
    route_legs_train = pd.read_csv(_manifest_file(raw_root, "route_legs_train.csv"), low_memory=False)
    route_legs_test = pd.read_csv(_manifest_file(raw_root, "route_legs_test.csv"), low_memory=False)
    outlets = pd.read_csv(_manifest_file(raw_root, "outlets.csv"), low_memory=False)
    vehicles = pd.read_csv(_manifest_file(raw_root, "vehicles.csv"), low_memory=False)
    calendar = pd.read_csv(_manifest_file(raw_root, "calendar.csv"), low_memory=False)
    district_travel = pd.read_csv(_manifest_file(raw_root, "district_travel.csv"), low_memory=False)
    service_allowance = pd.read_csv(_manifest_file(raw_root, "service_allowance.csv"), low_memory=False)
    traffic_matches = list(Path(raw_root).rglob("traffic_speed.csv"))
    road_matches = list(Path(raw_root).rglob("road_conditions.csv"))
    traffic_speed = pd.read_csv(traffic_matches[0], low_memory=False) if traffic_matches else None
    road_conditions = pd.read_csv(road_matches[0], low_memory=False) if road_matches else None
    orders_test = task1_test_inputs.drop(columns=[OFFICIAL_ROW_ORDER])
    tables = build_task1_feature_tables(
        orders_train=deliveries_train,
        orders_test=orders_test,
        route_legs_train=route_legs_train,
        route_legs_test=route_legs_test,
        outlets=outlets,
        vehicles=vehicles,
        district_travel=district_travel,
        service_allowance=service_allowance,
        calendar=calendar,
        labels_train=labels_train,
        config=config,
        road_conditions=road_conditions,
        traffic_speed=traffic_speed,
    )
    X_test = tables["X_test"]
    assert_no_forbidden_inference_features(list(X_test.columns))
    train_cols = list(tables["X_train"].columns)
    test_cols = list(X_test.columns)
    if train_cols != test_cols:
        raise Task1InferenceError("Phase 06 train/test feature names or order differ.")
    trace = task1_test_inputs[[OFFICIAL_ROW_ORDER, "delivery_id"]].copy()
    if "delivery_id" in X_test.columns:
        aligned = X_test.copy()
    else:
        aligned = X_test.copy()
        aligned["delivery_id"] = orders_test["delivery_id"].to_numpy()
    return aligned, trace


def assemble_official_predictions(
    test_inputs: pd.DataFrame,
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    if "delivery_id" not in predictions.columns:
        work = test_inputs[[OFFICIAL_ROW_ORDER, "delivery_id"]].copy()
        pred = predictions.copy()
        pred[OFFICIAL_ROW_ORDER] = test_inputs[OFFICIAL_ROW_ORDER].to_numpy()
        work = work.merge(pred, on=OFFICIAL_ROW_ORDER, how="left", validate="one_to_one")
    else:
        work = test_inputs[[OFFICIAL_ROW_ORDER, "delivery_id"]].merge(
            predictions,
            on="delivery_id",
            how="left",
            validate="one_to_one",
        )
    ordered = restore_official_row_order(work)
    assert_delivery_id_integrity(test_inputs.sort_values(OFFICIAL_ROW_ORDER, kind="stable")["delivery_id"], ordered["delivery_id"])
    if ordered[["pred_service_min", "pred_late_prob"]].isna().any().any():
        raise Task1InferenceError("Predictions are missing for one or more official delivery_id values.")
    return ordered


def run_task1_inference(
    *,
    raw_root: Path,
    feature_registry_path: Path,
    final_config_path: Path,
    service_model_dir: Path,
    late_model_dir: Path,
    inference_config_path: Path | None = None,
    historical_train_labels: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Full saved-model inference path used by the local script. Does not train."""
    assert_saved_models_present(service_model_dir, late_model_dir)
    final_config = load_frozen_final_config(final_config_path)
    inference_config = load_yaml(inference_config_path) if inference_config_path else {}
    X_test, trace = prepare_test_features_from_raw(
        raw_root,
        feature_registry_path,
        historical_train_labels=historical_train_labels,
    )
    service_bundle = load_model_bundle(service_model_dir)
    generated = resolve_feature_columns(
        X_test,
        str(service_bundle["schema"].get("feature_profile") or "safe_core_plus_history"),
    )
    try:
        assert_feature_schema_equal(service_bundle["schema"], generated)
    except Task1FinalTrainError as exc:
        raise Task1InferenceError(str(exc)) from exc
    preds = run_saved_model_inference(
        X_test,
        service_model_dir,
        late_model_dir,
        final_config,
        inference_config,
    )
    preds = preds.copy()
    preds["delivery_id"] = X_test["delivery_id"].to_numpy() if "delivery_id" in X_test.columns else trace["delivery_id"].to_numpy()
    assembled = assemble_official_predictions(
        trace.assign(**{c: X_test[c] for c in ("delivery_id",) if c in X_test.columns}),
        preds,
    )
    return {
        "predictions": assembled,
        "test_inputs": trace,
        "final_config": final_config,
        "inference_config": inference_config,
    }
