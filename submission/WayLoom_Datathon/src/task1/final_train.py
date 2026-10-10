"""Phase 10: retrain frozen Task 1 models on the full allowed historical population."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from src.task1.advanced_models import (
    CatBoostClassifier,
    CatBoostRegressor,
    LGBMClassifier,
    LGBMRegressor,
    XGBClassifier,
    XGBRegressor,
    resolve_advanced_feature_columns,
)
from src.task1.feature_registry import FORBIDDEN_DIRECT_TASK1_FEATURES

MISSING_CATEGORY_TOKEN = "__MISSING__"
TARGET_COLUMNS = ("service_minutes", "late_flag", "service_start_dt")
RESERVED_CONSTRUCTOR_KEYS = {
    "iterations",
    "n_estimators",
    "random_seed",
    "random_state",
    "verbose",
    "verbosity",
    "allow_writing_files",
    "class_weight",
    "class_weights",
    "auto_class_weights",
    "scale_pos_weight",
}


class Task1FinalTrainError(ValueError):
    """Raised when frozen Phase 10 training cannot proceed safely."""


def load_yaml(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise Task1FinalTrainError(f"YAML must be a mapping: {path}")
    return payload


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if isinstance(value, list):
        raise Task1FinalTrainError(f"Multiple {name} configurations are forbidden in Phase 10.")
    if not isinstance(value, dict):
        raise Task1FinalTrainError(f"{name} must be a single mapping.")
    return value


def _is_blank(value: Any) -> bool:
    return value is None or str(value).strip().lower() in {"", "null", "none", "nan"}


def assert_no_phase10_model_search(config: dict[str, Any]) -> None:
    search = config.get("search")
    if isinstance(search, dict) and search.get("enabled") is True:
        raise Task1FinalTrainError("Phase 10 must not run model search.")
    for key in ("candidates", "grid", "trial_loop", "optuna", "hyperparameter_search"):
        if key in config:
            raise Task1FinalTrainError(f"Phase 10 must not contain search key: {key}")
    for section_name in ("service_model", "lateness_model"):
        section = config.get(section_name, {})
        if isinstance(section, dict) and section.get("search"):
            raise Task1FinalTrainError(f"Phase 10 must not search inside {section_name}.")


def _assert_no_rebalancing(section: dict[str, Any], name: str) -> None:
    params = dict(section.get("parameters") or {})
    forbidden_values = {
        "class_weight": {"balanced"},
        "auto_class_weights": {"balanced", "sqrtbalanced", "sqrt_balanced"},
    }
    for key, banned in forbidden_values.items():
        raw = params.get(key, section.get(key))
        if raw is not None and str(raw).strip().lower() in banned:
            raise Task1FinalTrainError(f"{name} forbids {key}={raw} in Phase 10.")
    resampling = str(section.get("resampling_policy") or params.get("resampling") or "none").lower()
    if resampling not in {"none", "null", ""}:
        raise Task1FinalTrainError(f"{name} forbids resampling policy {resampling!r}.")


def _contract_flag(config: dict[str, Any], name: str) -> bool:
    contract = config.get("validation_contract") or {}
    if name in config:
        return bool(config.get(name))
    return bool(contract.get(name))


def load_frozen_final_config(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise Task1FinalTrainError(f"Final model config not found: {path}")
    config = load_yaml(path)
    if config.get("status") == "PLACEHOLDER_UNFROZEN":
        raise Task1FinalTrainError("Phase 09 final model config is not frozen.")
    if not _contract_flag(config, "development_selection_complete"):
        raise Task1FinalTrainError("Phase 09 development selection is not complete.")
    if not _contract_flag(config, "final_holdout_confirmation_complete"):
        raise Task1FinalTrainError("Phase 09 final holdout confirmation is not complete.")

    service = _require_mapping(config.get("service_model"), "service_model")
    late = _require_mapping(config.get("lateness_model"), "lateness_model")
    for section, name in ((service, "service_model"), (late, "lateness_model")):
        if _is_blank(section.get("family")) or _is_blank(section.get("config_id")):
            raise Task1FinalTrainError(f"{name} family/config_id is missing; Phase 09 is not frozen.")
        iteration = (section.get("final_iteration_policy") or {}).get("value")
        if iteration is None or int(iteration) <= 0:
            raise Task1FinalTrainError(f"{name} final iteration policy is missing or invalid.")
        _assert_no_rebalancing(section, name)
    assert_no_phase10_model_search(config)
    return config


def resolve_negative_service_policy(final_config: dict[str, Any], inference_config: dict[str, Any] | None = None) -> str:
    service = _require_mapping(final_config.get("service_model"), "service_model")
    post = service.get("prediction_postprocessing") or {}
    if bool(post.get("phase09_clipping")) or str(post.get("policy") or "").strip().lower() == "clip_to_zero":
        return "clip_to_zero"
    if inference_config:
        declared = str((inference_config.get("service") or {}).get("negative_policy") or "").strip().lower()
        if declared == "clip_to_zero":
            return "clip_to_zero"
    return "fail"


def resolve_feature_columns(frame: pd.DataFrame, feature_profile: str) -> list[str]:
    cols = resolve_advanced_feature_columns(frame, feature_profile=feature_profile)
    forbidden = sorted(set(cols) & set(FORBIDDEN_DIRECT_TASK1_FEATURES))
    if forbidden:
        raise Task1FinalTrainError(f"Forbidden features selected: {forbidden}")
    leaked_targets = sorted(set(cols) & set(TARGET_COLUMNS))
    if leaked_targets:
        raise Task1FinalTrainError(f"Target/target-derived fields selected: {leaked_targets}")
    return cols


def categorical_columns(frame: pd.DataFrame, cols: list[str]) -> list[str]:
    return [c for c in cols if not pd.api.types.is_numeric_dtype(frame[c])]


def prepare_model_frame(
    frame: pd.DataFrame,
    feature_columns: list[str],
    cat_columns: list[str],
    *,
    as_category: bool = False,
) -> pd.DataFrame:
    missing = [c for c in feature_columns if c not in frame.columns]
    if missing:
        raise Task1FinalTrainError(f"Missing required feature columns: {missing}")
    out = frame.loc[:, list(feature_columns)].copy()
    extra_targets = [c for c in TARGET_COLUMNS if c in out.columns]
    if extra_targets:
        raise Task1FinalTrainError(f"Target fields leaked into model matrix: {extra_targets}")
    for col in cat_columns:
        out[col] = out[col].astype("string").fillna(MISSING_CATEGORY_TOKEN)
        if as_category:
            out[col] = out[col].astype("category")
    return out


def feature_schema_payload(feature_columns: list[str], cat_columns: list[str], feature_profile: str) -> dict[str, Any]:
    return {
        "feature_columns": list(feature_columns),
        "categorical_columns": list(cat_columns),
        "feature_profile": feature_profile,
        "missing_category_token": MISSING_CATEGORY_TOKEN,
    }


def feature_schema_hash(schema: dict[str, Any]) -> str:
    canonical = json.dumps(
        {"feature_columns": schema["feature_columns"], "categorical_columns": schema["categorical_columns"]},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def assert_feature_schema_equal(saved: dict[str, Any], generated_columns: list[str]) -> None:
    expected = list(saved.get("feature_columns") or [])
    actual = list(generated_columns)
    if expected != actual:
        raise Task1FinalTrainError(
            "Train/test feature schema mismatch "
            f"(names or order). expected={expected} actual={actual}"
        )


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip() or None
    except Exception:
        return None


def _library_versions() -> dict[str, str]:
    versions: dict[str, str] = {"pandas": pd.__version__, "numpy": np.__version__}
    for name in ("sklearn", "catboost", "lightgbm", "xgboost", "joblib"):
        try:
            module = __import__(name)
            versions[name] = str(getattr(module, "__version__", "unknown"))
        except Exception:
            versions[name] = "not_installed"
    return versions


def _training_date_range(frame: pd.DataFrame) -> dict[str, str | None]:
    for col in ("validation_date", "date"):
        if col in frame.columns:
            series = pd.to_datetime(frame[col], errors="coerce")
            if series.notna().any():
                return {
                    "min": str(series.min().date()) if pd.notna(series.min()) else None,
                    "max": str(series.max().date()) if pd.notna(series.max()) else None,
                }
    return {"min": None, "max": None}


def _sanitize_params(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in dict(params or {}).items() if k not in RESERVED_CONSTRUCTOR_KEYS and v is not None}


def _iterations(section: dict[str, Any]) -> int:
    return int((section.get("final_iteration_policy") or {})["value"])


def _uses_category_dtype(family: str) -> bool:
    return str(family).lower() in {"lightgbm", "xgboost"}


def _fit_service_model(family: str, params: dict[str, Any], seed: int, iterations: int, X: pd.DataFrame, y: np.ndarray, cat_idx: list[int]):
    family = family.lower()
    clean = _sanitize_params(params)
    if family == "catboost":
        if CatBoostRegressor is None:
            raise Task1FinalTrainError("CatBoost is not installed.")
        model = CatBoostRegressor(
            iterations=iterations,
            random_seed=seed,
            verbose=False,
            allow_writing_files=False,
            **clean,
        )
        model.fit(X, y, cat_features=cat_idx)
        return model
    if family == "lightgbm":
        if LGBMRegressor is None:
            raise Task1FinalTrainError("LightGBM is not installed.")
        model = LGBMRegressor(n_estimators=iterations, random_state=seed, verbosity=-1, **clean)
        model.fit(X, y)
        return model
    if family == "xgboost":
        if XGBRegressor is None:
            raise Task1FinalTrainError("XGBoost is not installed.")
        model = XGBRegressor(n_estimators=iterations, random_state=seed, verbosity=0, **clean)
        model.fit(X, y)
        return model
    raise Task1FinalTrainError(f"Unsupported service family: {family}")


def _fit_late_model(family: str, params: dict[str, Any], seed: int, iterations: int, X: pd.DataFrame, y: np.ndarray, cat_idx: list[int]):
    family = family.lower()
    clean = _sanitize_params(params)
    if family == "catboost":
        if CatBoostClassifier is None:
            raise Task1FinalTrainError("CatBoost is not installed.")
        model = CatBoostClassifier(
            iterations=iterations,
            random_seed=seed,
            verbose=False,
            allow_writing_files=False,
            auto_class_weights=None,
            **clean,
        )
        model.fit(X, y, cat_features=cat_idx)
        return model
    if family == "lightgbm":
        if LGBMClassifier is None:
            raise Task1FinalTrainError("LightGBM is not installed.")
        model = LGBMClassifier(
            n_estimators=iterations,
            random_state=seed,
            verbosity=-1,
            class_weight=None,
            **clean,
        )
        model.fit(X, y)
        return model
    if family == "xgboost":
        if XGBClassifier is None:
            raise Task1FinalTrainError("XGBoost is not installed.")
        model = XGBClassifier(
            n_estimators=iterations,
            random_state=seed,
            verbosity=0,
            **clean,
        )
        model.fit(X, y)
        return model
    raise Task1FinalTrainError(f"Unsupported lateness family: {family}")


def identify_positive_class_index(model: Any) -> int:
    classes = getattr(model, "classes_", None)
    if classes is None:
        raise Task1FinalTrainError("Classifier has no classes_ metadata; cannot identify late_flag=1.")
    values = [int(c) if str(c).replace(".", "", 1).isdigit() else c for c in list(classes)]
    for marker in (1, 1.0, True, "1"):
        for idx, value in enumerate(values):
            if value == marker or str(value) == str(marker):
                return int(idx)
    raise Task1FinalTrainError(f"Cannot identify late_flag=1 in classes_={list(classes)}")


def predict_positive_probability(model: Any, X: pd.DataFrame, positive_index: int | None = None) -> np.ndarray:
    idx = identify_positive_class_index(model) if positive_index is None else int(positive_index)
    proba = np.asarray(model.predict_proba(X), dtype=float)
    if proba.ndim != 2 or proba.shape[1] <= idx:
        raise Task1FinalTrainError("Classifier probability shape is incompatible with positive-class index.")
    return proba[:, idx]


def fit_frozen_calibrator(method: str, raw_prob: np.ndarray, y: np.ndarray) -> Any | None:
    method = str(method or "raw").strip().lower()
    if method in {"raw", "none", "null", ""}:
        return None
    y = np.asarray(y, dtype=float)
    p = np.asarray(raw_prob, dtype=float)
    if method == "sigmoid":
        eps = np.finfo(float).eps
        logit = np.log(np.clip(p, eps, 1 - eps) / np.clip(1 - p, eps, 1 - eps)).reshape(-1, 1)
        model = LogisticRegression(solver="lbfgs", max_iter=2000, C=1.0, class_weight=None, random_state=42)
        model.fit(logit, y)
        return {"method": "sigmoid", "estimator": model}
    if method == "isotonic":
        model = IsotonicRegression(out_of_bounds="clip")
        model.fit(p, y)
        return {"method": "isotonic", "estimator": model}
    raise Task1FinalTrainError(f"Unsupported frozen calibration method: {method}")


def apply_frozen_calibrator(artifact: Any | None, raw_prob: np.ndarray) -> np.ndarray:
    p = np.asarray(raw_prob, dtype=float)
    if artifact is None:
        return p
    method = str(artifact.get("method") if isinstance(artifact, dict) else getattr(artifact, "method", "")).lower()
    estimator = artifact.get("estimator") if isinstance(artifact, dict) else artifact
    if method == "sigmoid":
        eps = np.finfo(float).eps
        logit = np.log(np.clip(p, eps, 1 - eps) / np.clip(1 - p, eps, 1 - eps)).reshape(-1, 1)
        return np.asarray(estimator.predict_proba(logit)[:, 1], dtype=float)
    if method == "isotonic":
        return np.asarray(estimator.predict(p), dtype=float)
    raise Task1FinalTrainError(f"Cannot apply calibration artifact method={method!r}.")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def save_model_bundle(
    directory: Path,
    *,
    model: Any,
    metadata: dict[str, Any],
    schema: dict[str, Any],
    calibration: Any | None = None,
) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, directory / "model.joblib")
    _write_json(directory / "metadata.json", metadata)
    _write_json(directory / "feature_schema.json", schema)
    if calibration is not None:
        joblib.dump(calibration, directory / "calibration.joblib")
    return directory


def load_model_bundle(directory: Path, *, require_calibration: bool = False) -> dict[str, Any]:
    directory = Path(directory)
    model_path = directory / "model.joblib"
    if not model_path.is_file():
        raise Task1FinalTrainError(f"Saved model missing at {model_path}; inference must not retrain.")
    metadata_path = directory / "metadata.json"
    schema_path = directory / "feature_schema.json"
    if not metadata_path.is_file() or not schema_path.is_file():
        raise Task1FinalTrainError(f"Incomplete model bundle: {directory}")
    calibration_path = directory / "calibration.joblib"
    if require_calibration and not calibration_path.is_file():
        raise Task1FinalTrainError(f"Frozen calibration artifact missing: {calibration_path}")
    return {
        "model": joblib.load(model_path),
        "metadata": json.loads(metadata_path.read_text(encoding="utf-8")),
        "schema": json.loads(schema_path.read_text(encoding="utf-8")),
        "calibration": joblib.load(calibration_path) if calibration_path.is_file() else None,
        "directory": directory,
    }


def _base_metadata(
    *,
    task: str,
    section: dict[str, Any],
    seed: int,
    schema: dict[str, Any],
    row_count: int,
    date_range: dict[str, str | None],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "task": task,
        "model_family": section["family"],
        "config_id": section["config_id"],
        "seed": int(seed),
        "feature_schema_hash": feature_schema_hash(schema),
        "feature_registry_version": 1,
        "library_versions": _library_versions(),
        "training_row_count": int(row_count),
        "training_date_range": date_range,
        "git_commit": _git_commit(),
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "class_weight_policy": None,
        "resampling_policy": "none",
    }
    if extra:
        payload.update(extra)
    return payload


def train_final_models(
    X: pd.DataFrame,
    y_service: pd.Series,
    y_late: pd.Series,
    final_config: dict[str, Any],
) -> dict[str, Any]:
    """Retrain exactly the frozen Phase 09 pair on the full historical population."""
    assert_no_phase10_model_search(final_config)
    service_cfg = _require_mapping(final_config.get("service_model"), "service_model")
    late_cfg = _require_mapping(final_config.get("lateness_model"), "lateness_model")
    profile = str(
        service_cfg.get("feature_profile")
        or (final_config.get("features") or {}).get("profile")
        or "safe_core_plus_history"
    )
    seed = int(final_config.get("seed", 42))
    feature_cols = resolve_feature_columns(X, profile)
    cat_cols = categorical_columns(X, feature_cols)
    schema = feature_schema_payload(feature_cols, cat_cols, profile)
    date_range = _training_date_range(X)

    X_service = prepare_model_frame(X, feature_cols, cat_cols, as_category=_uses_category_dtype(service_cfg["family"]))
    X_late = prepare_model_frame(X, feature_cols, cat_cols, as_category=_uses_category_dtype(late_cfg["family"]))
    y_s = np.asarray(pd.to_numeric(y_service, errors="raise"), dtype=float)
    y_l = np.asarray(pd.to_numeric(y_late, errors="raise"), dtype=float)
    if len(X_service) != len(y_s) or len(X_late) != len(y_l):
        raise Task1FinalTrainError("X/y lengths do not match.")
    if not np.isfinite(y_s).all() or not np.isfinite(y_l).all():
        raise Task1FinalTrainError("Training labels must be finite.")
    if not set(np.unique(y_l)).issubset({0.0, 1.0}):
        raise Task1FinalTrainError("late_flag must contain only 0/1.")

    service_cats = [X_service.columns.get_loc(c) for c in cat_cols]
    late_cats = [X_late.columns.get_loc(c) for c in cat_cols]
    service_model = _fit_service_model(
        service_cfg["family"],
        service_cfg.get("parameters") or {},
        seed,
        _iterations(service_cfg),
        X_service,
        y_s,
        service_cats,
    )
    late_model = _fit_late_model(
        late_cfg["family"],
        late_cfg.get("parameters") or {},
        seed,
        _iterations(late_cfg),
        X_late,
        y_l,
        late_cats,
    )
    positive_index = identify_positive_class_index(late_model)
    raw_prob = predict_positive_probability(late_model, X_late, positive_index)
    calib_cfg = late_cfg.get("calibration") or {}
    calib_method = str(calib_cfg.get("method") or "raw")
    calib_protocol = calib_cfg.get("protocol") or calib_cfg.get("fit_protocol")
    calibrator = fit_frozen_calibrator(calib_method, raw_prob, y_l)
    return {
        "service_model": service_model,
        "late_model": late_model,
        "calibrator": calibrator,
        "schema": schema,
        "feature_columns": feature_cols,
        "categorical_columns": cat_cols,
        "positive_class_index": positive_index,
        "service_metadata": _base_metadata(
            task="task1_service",
            section=service_cfg,
            seed=seed,
            schema=schema,
            row_count=len(X_service),
            date_range=date_range,
            extra={
                "iteration_policy": service_cfg.get("final_iteration_policy"),
                "negative_service_policy": resolve_negative_service_policy(final_config),
            },
        ),
        "late_metadata": _base_metadata(
            task="task1_late",
            section=late_cfg,
            seed=seed,
            schema=schema,
            row_count=len(X_late),
            date_range=date_range,
            extra={
                "iteration_policy": late_cfg.get("final_iteration_policy"),
                "positive_class_index": positive_index,
                "classes": [str(c) for c in getattr(late_model, "classes_", [])],
                "calibration_method": calib_method,
                "calibration_protocol": calib_protocol,
            },
        ),
    }
