"""Phase 16 fixed CatBoost and LightGBM rolling-origin candidates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor, early_stopping

from src.task2a.baseline_evaluation import load_and_verify_phase14_plan
from src.task2a.model_preprocessing import feature_profile, lightgbm_fold_preprocessor, select_predictors


KEYS = ("backtest_id", "depot", "brand", "origin_week_start_date", "target_week_start_date", "horizon_weeks")
TARGETS = {"total": "target_total_volume_m3", "chilled": "target_chilled_volume_m3"}


class AdvancedModelError(ValueError):
    """A Phase 16 frozen model or backtest rule was violated."""


def load_advanced_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    validate_advanced_config(config)
    return config


def validate_advanced_config(config: dict[str, Any]) -> None:
    if not isinstance(config, dict) or config.get("version") != 1:
        raise AdvancedModelError("Phase 16 model configuration version must be 1.")
    if config.get("validation") != {"reuse_phase14_plan": True, "allow_new_splits": False}:
        raise AdvancedModelError("Phase 16 must reuse the frozen Phase 14 plan.")
    if config.get("feature_profile") != {"use_phase13_registry": True,
        "include_prediction_time_safe_only": True, "exclude_metadata_columns": True,
        "exclude_target_columns": True}:
        raise AdvancedModelError("Phase 16 must use only the Phase 13 safe feature registry.")
    for family in ("catboost", "lightgbm"):
        group = config.get(family, {})
        if group.get("enabled") is not True:
            raise AdvancedModelError(f"{family} challenger must be enabled.")
        for target in TARGETS:
            params = group.get(target, {})
            if params.get("candidate_id") != f"{family}_{target}_v1":
                raise AdvancedModelError("Advanced candidate identity has changed.")
            if type(params.get("early_stopping_rounds")) is not int or params["early_stopping_rounds"] < 1:
                raise AdvancedModelError("Early stopping rounds must be positive.")
            iteration_key = "iterations" if family == "catboost" else "n_estimators"
            if type(params.get(iteration_key)) is not int or params[iteration_key] < 2:
                raise AdvancedModelError("Configured model iterations must be at least two.")
            seed_key = "random_seed" if family == "catboost" else "random_state"
            if params.get(seed_key) != 42:
                raise AdvancedModelError("Phase 16 deterministic seed must be 42.")
            if family == "catboost" and (params.get("loss_function") != "MAE" or params.get("eval_metric") != "MAE"
                or params.get("allow_writing_files") is not False or params.get("verbose") is not False
                or params.get("learning_rate") != 0.03 or params.get("depth") != 6
                or params.get("l2_leaf_reg") != 5.0):
                raise AdvancedModelError("CatBoost objective or local-only policy changed.")
            if family == "lightgbm" and (params.get("objective") != "regression_l1" or params.get("metric") != "l1"
                or params.get("n_jobs") != 1 or params.get("learning_rate") != 0.03
                or params.get("num_leaves") != 31 or params.get("min_child_samples") != 20
                or params.get("reg_lambda") != 1.0):
                raise AdvancedModelError("LightGBM objective or deterministic thread policy changed.")
    ensembles = config.get("ensembles", {})
    for name, left, right in (("catboost_lightgbm_equal_weight", "weight_catboost", "weight_lightgbm"),
                              ("advanced_reference_equal_weight", "weight_advanced", "weight_reference_baseline")):
        entry = ensembles.get(name, {})
        if entry.get("enabled") is not True or entry.get(left) != 0.5 or entry.get(right) != 0.5:
            raise AdvancedModelError("Both Phase 16 ensembles must have fixed 50/50 weights.")
    selection = config.get("selection", {})
    if selection != {"primary_metric": "mae", "lower_is_better": True,
        "relative_tie_tolerance_pct": 0.5, "prefer_simpler_within_tolerance": True,
        "tie_breakers": ["rmse", "p90_absolute_error", "backtest_mae_std", "simplicity"]}:
        raise AdvancedModelError("Frozen Phase 16 selection rule changed.")
    if config.get("final_iteration_policy") != {"method": "median_best_iteration", "minimum_iteration": 1}:
        raise AdvancedModelError("Final iteration policy must use valid-fold median.")
    if config.get("prediction_policy") != {"evaluate_raw_predictions": True,
        "clip_negative_in_phase16": False, "enforce_chilled_le_total_in_phase16": False}:
        raise AdvancedModelError("Phase 16 must evaluate unmodified raw predictions.")


def verify_frozen_phase14_plan(path: str | Path, plan: dict[str, Any]) -> str:
    """Check the persisted signature and every stored train/validation index."""
    signature = load_and_verify_phase14_plan(path, plan)
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    if record.get("validation_horizon_weeks", 10) != 10 or len(record["backtests"]) != len(plan["splits"]):
        raise AdvancedModelError("Frozen Phase 14 plan has different validation windows.")
    for stored, split in zip(record["backtests"], plan["splits"], strict=True):
        if stored["backtest_id"] != split.backtest_id:
            raise AdvancedModelError("Frozen Phase 14 backtest order changed.")
        if stored.get("train_indices") != split.train_indices.tolist():
            raise AdvancedModelError("Frozen Phase 14 training indices changed.")
        if stored.get("validation_indices") != split.validation_indices.tolist():
            raise AdvancedModelError("Frozen Phase 14 validation indices changed.")
    return signature


def _fit_fold(family: str, target: str, train: pd.DataFrame, validation: pd.DataFrame,
              profile: dict[str, Any], settings: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    label = TARGETS[target]
    x_train = select_predictors(train, profile)
    x_valid = select_predictors(validation, profile)
    y_train = train[label].to_numpy(dtype=float)
    y_valid = validation[label].to_numpy(dtype=float)
    if not np.isfinite(y_train).all() or not np.isfinite(y_valid).all():
        raise AdvancedModelError("Training or validation labels contain nonfinite values.")
    params = {key: value for key, value in settings.items()
              if key not in {"candidate_id", "early_stopping_rounds"}}
    if family == "catboost":
        model = CatBoostRegressor(**params)
        model.fit(x_train, y_train, cat_features=profile["categorical"],
                  eval_set=(x_valid, y_valid), early_stopping_rounds=settings["early_stopping_rounds"])
        predicted = np.asarray(model.predict(x_valid), dtype=float)
        best_iteration = max(1, int(model.get_best_iteration()) + 1)
        best_metric = float(model.get_best_score()["validation"]["MAE"])
        # CatBoost may retain only the best trees even when it evaluated every
        # configured iteration. Count evaluated rounds for early-stop status.
        trained_iterations = len(model.get_evals_result()["validation"]["MAE"])
    elif family == "lightgbm":
        preprocessor = lightgbm_fold_preprocessor(profile)
        transformed_train = preprocessor.fit_transform(x_train)
        transformed_valid = preprocessor.transform(x_valid)
        model = LGBMRegressor(**params, verbosity=-1)
        model.fit(transformed_train, y_train, eval_X=transformed_valid, eval_y=y_valid,
                  eval_metric="l1", callbacks=[early_stopping(settings["early_stopping_rounds"], verbose=False)])
        predicted = np.asarray(model.predict(transformed_valid), dtype=float)
        best_iteration = max(1, int(model.best_iteration_))
        best_metric = float(model.best_score_["valid_0"]["l1"])
        trained_iterations = int(model.n_estimators_)
    else:
        raise AdvancedModelError("Unknown advanced model family.")
    if predicted.shape != (len(validation),) or not np.isfinite(predicted).all():
        raise AdvancedModelError("Advanced model produced missing or nonfinite predictions.")
    maximum = int(settings["iterations" if family == "catboost" else "n_estimators"])
    return predicted, {"best_iteration": best_iteration, "best_validation_metric": best_metric,
                       "stopped_early": trained_iterations < maximum, "trained_iterations": trained_iterations,
                       "configured_max_iterations": maximum,
                       "training_row_count": len(train), "validation_row_count": len(validation)}


def run_advanced_backtests(plan: dict[str, Any], feature_config: dict[str, Any],
                           model_config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Fit four fixed candidates on the unchanged Phase 14 folds."""
    validate_advanced_config(model_config)
    profile = feature_profile(feature_config)
    table = plan["table"]
    if not plan["leakage_audit"]["training_target_availability_pass"] or plan["leakage_audit"]["forbidden_future_feature_count"]:
        raise AdvancedModelError("Phase 14 lineage audit did not pass.")
    predictions, fold_metadata = [], []
    from src.task2a.baseline_evaluation import phase14_backtest_signature
    signature = phase14_backtest_signature(plan)
    for split in plan["splits"]:
        train_all = table.iloc[split.train_indices]
        valid_all = table.iloc[split.validation_indices]
        if not train_all.target_week_start_date.le(split.origin_week_start_date).all():
            raise AdvancedModelError("Training target is after validation origin.")
        if not valid_all.origin_demand_feature_max_source_week.le(split.origin_week_start_date).all():
            raise AdvancedModelError("Validation predictor source exceeds origin.")
        for family in ("catboost", "lightgbm"):
            for target, label in TARGETS.items():
                train = train_all if target == "total" else train_all.loc[train_all.brand.eq("Fresh")]
                valid = valid_all if target == "total" else valid_all.loc[valid_all.brand.eq("Fresh")]
                if train.empty or valid.empty or (target == "chilled" and not train.brand.eq("Fresh").all()):
                    raise AdvancedModelError("Required model population is unavailable.")
                settings = model_config[family][target]
                values, metadata = _fit_fold(family, target, train, valid, profile, settings)
                candidate_id = settings["candidate_id"]
                fold_metadata.append({"backtest_id": split.backtest_id, "target_name": target,
                                      "candidate_id": candidate_id, **metadata})
                columns = list(dict.fromkeys(["depot", "brand", "origin_week_start_date",
                    "target_week_start_date", "horizon_weeks", label, "target_total_volume_m3"]))
                frame = valid[columns].copy()
                frame.insert(0, "backtest_id", split.backtest_id)
                frame["target_name"] = target
                frame["candidate_id"] = candidate_id
                frame["y_true"] = frame[label].astype(float)
                frame["total_y_true"] = frame.target_total_volume_m3.astype(float)
                frame["y_pred"] = values
                frame["phase14_backtest_signature"] = signature
                predictions.append(frame[[*KEYS, "target_name", "candidate_id", "y_true", "total_y_true",
                                          "y_pred", "phase14_backtest_signature"]])
    return pd.concat(predictions, ignore_index=True), pd.DataFrame(fold_metadata), profile
