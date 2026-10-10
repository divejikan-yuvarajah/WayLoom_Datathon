"""Phase 15 prediction generation, frozen-plan checks, and baseline ranking."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.task2a.baselines import (CHILLED_BASELINES, TOTAL_BASELINES, BaselineError,
    ForecastRequest, build_history_as_of_origin, predict_baseline, validate_baseline_config)
from src.task2a.metrics import (evaluate_forecast_by_horizon, evaluate_forecast_overall,
    evaluate_forecast_per_series)


class BaselineEvaluationError(ValueError):
    """A baseline does not exactly reuse the frozen Phase 14 evaluation plan."""


BASELINE_FAMILIES = ("last_week", "recent_mean_4", "same_week_last_year", "seasonal_recent_weighted")
SIMPLICITY = {name: index for index, name in enumerate(BASELINE_FAMILIES)}


def phase14_backtest_signature(plan: dict[str, Any]) -> str:
    """Hash only deterministic plan metadata, never demand values or row labels."""
    return phase14_backtest_signature_from_metadata(phase14_plan_metadata(plan))


def phase14_plan_metadata(plan: dict[str, Any]) -> dict[str, Any]:
    """Canonical non-value metadata shared by Phase 14 and Phase 15."""
    return {
        "required_series": [list(series) for series in plan["required_series"]],
        "backtests": [{"backtest_id": split.backtest_id,
                       "origin_week_start_date": split.origin_week_start_date.date().isoformat(),
                       "validation_target_start_date": split.validation_target_start_date.date().isoformat(),
                       "validation_target_end_date": split.validation_target_end_date.date().isoformat()}
                      for split in plan["splits"]],
    }


def phase14_backtest_signature_from_metadata(metadata: dict[str, Any]) -> str:
    """Validate and hash persisted Phase 14 split metadata without demand rows."""
    if not isinstance(metadata, dict) or not isinstance(metadata.get("required_series"), list) or not isinstance(metadata.get("backtests"), list):
        raise BaselineEvaluationError("Frozen Phase 14 plan metadata is malformed.")
    required_series = metadata["required_series"]
    backtests = metadata["backtests"]
    if not required_series or not backtests or any(not isinstance(series, list) or len(series) != 2 for series in required_series):
        raise BaselineEvaluationError("Frozen Phase 14 plan has invalid required-series metadata.")
    normalized = []
    for backtest in backtests:
        if not isinstance(backtest, dict) or set(("backtest_id", "origin_week_start_date", "validation_target_start_date", "validation_target_end_date")).difference(backtest):
            raise BaselineEvaluationError("Frozen Phase 14 plan has incomplete backtest metadata.")
        normalized.append({"backtest_id": str(backtest["backtest_id"]),
                           "origin": pd.Timestamp(backtest["origin_week_start_date"]).date().isoformat(),
                           "start": pd.Timestamp(backtest["validation_target_start_date"]).date().isoformat(),
                           "end": pd.Timestamp(backtest["validation_target_end_date"]).date().isoformat()})
    payload = {"required_series": [[str(value) for value in series] for series in required_series], "backtests": normalized}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_and_verify_phase14_plan(path: str | Path, plan: dict[str, Any]) -> str:
    """Require a rebuilt plan to match the persisted, frozen Phase 14 plan exactly."""
    try:
        record = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BaselineEvaluationError("Frozen Phase 14 validation_plan.json is unavailable or invalid.") from error
    expected = phase14_backtest_signature_from_metadata(record)
    actual = phase14_backtest_signature(plan)
    if actual != expected:
        raise BaselineEvaluationError("Phase 14 backtest signature mismatch; Phase 15 must reuse the frozen plan exactly.")
    return actual


def _validation_rows(plan: dict[str, Any]) -> pd.DataFrame:
    table = plan["table"]
    frames = []
    for split in plan["splits"]:
        frame = table.iloc[split.validation_indices].copy()
        frame["backtest_id"] = split.backtest_id
        if not frame.origin_week_start_date.eq(split.origin_week_start_date).all():
            raise BaselineEvaluationError("Phase 14 validation indices do not match the frozen origin.")
        frames.append(frame)
    result = pd.concat(frames, ignore_index=True)
    if result.duplicated(["backtest_id", "depot", "brand", "horizon_weeks"]).any():
        raise BaselineEvaluationError("Frozen Phase 14 validation rows have duplicate keys.")
    return result.sort_values(["backtest_id", "depot", "brand", "horizon_weeks"], kind="stable").reset_index(drop=True)


def generate_backtest_baseline_predictions(panel: pd.DataFrame, plan: dict[str, Any], config: dict[str, Any]) -> pd.DataFrame:
    """Generate all Phase 15 candidates from history sliced at each frozen origin."""
    validate_baseline_config(config)
    rows = _validation_rows(plan)
    records: list[dict[str, Any]] = []
    for backtest_id, block in rows.groupby("backtest_id", sort=True):
        origin = block.origin_week_start_date.iloc[0]
        history = build_history_as_of_origin(panel, origin)
        for _, row in block.iterrows():
            request = ForecastRequest(str(row.depot), str(row.brand), pd.Timestamp(row.origin_week_start_date),
                                      pd.Timestamp(row.target_week_start_date), int(row.target_iso_year),
                                      int(row.target_iso_week), int(row.horizon_weeks))
            for target_name, column, families in (
                ("total", "target_total_volume_m3", TOTAL_BASELINES),
                ("chilled", "target_chilled_volume_m3", CHILLED_BASELINES),
            ):
                for baseline_name in families:
                    family = baseline_name.removeprefix(f"{target_name}_")
                    if target_name == "chilled" and request.brand in {"Style", "Tech"}:
                        prediction = (0.0, "STRUCTURAL_ZERO", False, False)
                    else:
                        result = predict_baseline(history, request, target_name, family)
                        prediction = (result.value, result.fallback_status, result.seasonal_exact_used, result.seasonal_fallback_used)
                    records.append({
                        "backtest_id": backtest_id, "depot": request.depot, "brand": request.brand,
                        "origin_week_start_date": request.origin_week_start_date,
                        "target_week_start_date": request.target_week_start_date,
                        "horizon_weeks": request.forecast_horizon, "baseline_name": baseline_name,
                        "target_name": target_name, "y_true": float(row[column]),
                        "total_y_true": float(row["target_total_volume_m3"]), "y_pred": prediction[0],
                        "fallback_status": prediction[1], "seasonal_exact_used": prediction[2],
                        "seasonal_fallback_used": prediction[3],
                        "phase14_backtest_signature": phase14_backtest_signature(plan),
                    })
    return pd.DataFrame(records).sort_values(
        ["target_name", "baseline_name", "backtest_id", "depot", "brand", "horizon_weeks"], kind="stable"
    ).reset_index(drop=True)


def _expected_keys(plan: dict[str, Any]) -> pd.DataFrame:
    return _validation_rows(plan)[["backtest_id", "depot", "brand", "origin_week_start_date", "target_week_start_date", "horizon_weeks"]]


def validate_baseline_predictions(predictions: pd.DataFrame, plan: dict[str, Any]) -> None:
    required = ["backtest_id", "depot", "brand", "origin_week_start_date", "target_week_start_date", "horizon_weeks",
                "baseline_name", "target_name", "y_true", "total_y_true", "y_pred", "fallback_status", "phase14_backtest_signature"]
    missing = [column for column in required if column not in predictions]
    if missing:
        raise BaselineEvaluationError("Baseline predictions missing columns: " + ", ".join(missing))
    signature = phase14_backtest_signature(plan)
    if not predictions.phase14_backtest_signature.eq(signature).all():
        raise BaselineEvaluationError("Baseline predictions do not match the frozen Phase 14 signature.")
    expected = _expected_keys(plan)
    for target, baselines in (("total", TOTAL_BASELINES), ("chilled", CHILLED_BASELINES)):
        for baseline in baselines:
            subset = predictions.loc[predictions.target_name.eq(target) & predictions.baseline_name.eq(baseline)]
            if subset.y_pred.isna().any():
                raise BaselineEvaluationError(f"{baseline} has unavailable predictions; candidates cannot be silently dropped.")
            actual = subset[expected.columns].sort_values(list(expected.columns), kind="stable").reset_index(drop=True)
            wanted = expected.sort_values(list(expected.columns), kind="stable").reset_index(drop=True)
            for column in ("backtest_id", "depot", "brand"):
                actual[column] = actual[column].astype(str)
                wanted[column] = wanted[column].astype(str)
            for column in ("origin_week_start_date", "target_week_start_date"):
                actual[column] = pd.to_datetime(actual[column]).dt.normalize()
                wanted[column] = pd.to_datetime(wanted[column]).dt.normalize()
            if not actual.equals(wanted) or subset.duplicated(list(expected.columns)).any():
                raise BaselineEvaluationError(f"{baseline} does not use every exact frozen Phase 14 validation row.")
            if not np.isfinite(subset.y_pred.to_numpy(dtype=float)).all():
                raise BaselineEvaluationError(f"{baseline} contains a nonfinite raw prediction.")


def _to_phase14_scoring_rows(subset: pd.DataFrame, target_name: str) -> pd.DataFrame:
    frame = subset[["backtest_id", "depot", "brand", "horizon_weeks"]].copy()
    if target_name == "total":
        frame["target_total_volume_m3"] = subset.y_true.to_numpy()
        frame["pred_total_volume_m3"] = subset.y_pred.to_numpy()
        frame["target_chilled_volume_m3"] = 0.0
        frame["pred_chilled_volume_m3"] = 0.0
    else:
        frame["target_total_volume_m3"] = subset.total_y_true.to_numpy(dtype=float)
        frame["pred_total_volume_m3"] = frame["target_total_volume_m3"]
        frame["target_chilled_volume_m3"] = subset.y_true.to_numpy()
        frame["pred_chilled_volume_m3"] = subset.y_pred.to_numpy()
    return frame


def evaluate_baseline_predictions(predictions: pd.DataFrame, plan: dict[str, Any]) -> dict[str, Any]:
    """Evaluate candidates using Phase 14 metric and coverage helpers directly."""
    validate_baseline_predictions(predictions, plan)
    expected_ids = [split.backtest_id for split in plan["splits"]]
    expected_series = plan["required_series"]
    results: dict[str, Any] = {}
    for (target, baseline), subset in predictions.groupby(["target_name", "baseline_name"], sort=True):
        scored = _to_phase14_scoring_rows(subset, target)
        overall = evaluate_forecast_overall(scored, expected_backtest_ids=expected_ids, expected_series=expected_series)
        per_series = evaluate_forecast_per_series(scored, expected_backtest_ids=expected_ids, expected_series=expected_series)
        by_horizon = evaluate_forecast_by_horizon(scored, expected_backtest_ids=expected_ids, expected_series=expected_series)
        primary = overall["total_micro"] if target == "total" else overall["fresh_chilled_micro"]
        backtests = pd.DataFrame(overall["by_backtest"]).loc[lambda f: f.target.eq(target)]
        results[f"{target}:{baseline}"] = {"target_name": target, "baseline_name": baseline,
            "overall": primary, "per_series": per_series, "by_horizon": by_horizon,
            "backtests": backtests, "overall_detail": overall,
            "seasonal_fallback_count": int(subset.seasonal_fallback_used.sum()),
            "unavailable_prediction_count": int(subset.y_pred.isna().sum())}
    return results


def _summary_row(result: dict[str, Any]) -> dict[str, Any]:
    overall, backtests = result["overall"], result["backtests"]
    return {"target_name": result["target_name"], "baseline_name": result["baseline_name"],
            "eligible_backtest_count": int(len(backtests)), "overall_mae": overall["mae"],
            "overall_rmse": overall["rmse"], "overall_wape": overall["wape"],
            "overall_bias_m3": overall["mean_bias_m3"], "p90_absolute_error": overall["p90_absolute_error"],
            "mean_backtest_mae": float(backtests.mae.mean()), "std_backtest_mae": float(backtests.mae.std(ddof=0)),
            "median_backtest_mae": float(backtests.mae.median()), "worst_backtest_mae": float(backtests.mae.max()),
            "unavailable_prediction_count": result["unavailable_prediction_count"],
            "seasonal_fallback_count": result["seasonal_fallback_count"],
            "negative_prediction_count": overall["negative_prediction_count"],
            "chilled_gt_total_count": overall["chilled_gt_total_count"]}


def rank_reference_baselines(evaluated: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, str]]:
    summary = pd.DataFrame([_summary_row(value) for value in evaluated.values()])
    if set(summary.loc[summary.target_name.eq("total"), "baseline_name"]) != set(TOTAL_BASELINES) or set(summary.loc[summary.target_name.eq("chilled"), "baseline_name"]) != set(CHILLED_BASELINES):
        raise BaselineEvaluationError("A required baseline candidate is missing; reference selection cannot omit it.")
    rows = []
    references: dict[str, str] = {}
    for target, group in summary.groupby("target_name", sort=True):
        ranked = group.assign(_simplicity=group.baseline_name.str.removeprefix(f"{target}_").map(SIMPLICITY)).sort_values(
            ["overall_mae", "overall_rmse", "p90_absolute_error", "std_backtest_mae", "_simplicity", "baseline_name"], kind="stable"
        ).reset_index(drop=True)
        ranked["rank"] = np.arange(1, len(ranked) + 1)
        rows.append(ranked.drop(columns="_simplicity"))
        references[target] = str(ranked.iloc[0].baseline_name)
    return pd.concat(rows, ignore_index=True), references


def build_baseline_run_manifest(baseline_config: dict[str, Any], validation_config: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    def stable_hash(value: Any) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return {"phase": 15, "created_at": datetime.now(timezone.utc).isoformat(), "git_commit": commit,
            "baseline_config_hash": stable_hash(baseline_config), "validation_config_hash": stable_hash(validation_config),
            "phase14_backtest_signature": phase14_backtest_signature(plan),
            "weekly_panel_schema": ["depot", "brand", "iso_year", "iso_week", "week_start_date", "total_volume_m3", "chilled_volume_m3"],
            "metric_contract_version": 1, "library_versions": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
            "PHASE 14 SPLITS REUSED": "YES", "NEW SPLITS CREATED": "NO", "FUTURE DEMAND USED": "NO",
            "BASELINE WEIGHTS TUNED": "NO", "ADVANCED MODEL TRAINED": "NO", "TASK 1 ARTIFACTS CHANGED": "NO"}
