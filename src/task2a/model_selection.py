"""Frozen Phase 16 candidate evaluation, complexity gate, and config freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.task2a.advanced_models import KEYS, TARGETS
from src.task2a.baseline_evaluation import phase14_backtest_signature
from src.task2a.metrics import evaluate_forecast_by_horizon, evaluate_forecast_overall, evaluate_forecast_per_series


class ModelSelectionError(ValueError):
    """A candidate or frozen selection is incomplete or inconsistent."""


def expected_validation_rows(plan: dict[str, Any], target: str) -> pd.DataFrame:
    if target not in TARGETS:
        raise ModelSelectionError("Candidate target must be total or chilled.")
    blocks = []
    for split in plan["splits"]:
        columns = list(dict.fromkeys(["depot", "brand", "origin_week_start_date",
            "target_week_start_date", "horizon_weeks", TARGETS[target], "target_total_volume_m3"]))
        block = plan["table"].iloc[split.validation_indices][columns].copy()
        block.insert(0, "backtest_id", split.backtest_id)
        blocks.append(block)
    expected = pd.concat(blocks, ignore_index=True)
    if target == "chilled":
        expected = expected.loc[expected.brand.eq("Fresh")].copy()
    expected["y_true"] = expected[TARGETS[target]].to_numpy(dtype=float)
    expected["total_y_true"] = expected.target_total_volume_m3.to_numpy(dtype=float)
    return expected[[*KEYS, "y_true", "total_y_true"]].reset_index(drop=True)


def validate_candidate_predictions(rows: pd.DataFrame, plan: dict[str, Any], target: str,
                                   candidate_id: str) -> pd.DataFrame:
    required = [*KEYS, "target_name", "candidate_id", "y_true", "total_y_true", "y_pred",
                "phase14_backtest_signature"]
    if any(name not in rows for name in required):
        raise ModelSelectionError("Candidate predictions lack required frozen-plan fields.")
    frame = rows.loc[rows.candidate_id.eq(candidate_id) & rows.target_name.eq(target), required].copy()
    expected = expected_validation_rows(plan, target)
    if frame.empty or len(frame) != len(expected) or frame.duplicated(list(KEYS)).any():
        raise ModelSelectionError("Candidate is missing or duplicating a frozen validation row.")
    if not frame.phase14_backtest_signature.eq(phase14_backtest_signature(plan)).all():
        raise ModelSelectionError("Candidate Phase 14 backtest signature mismatch.")
    if not np.isfinite(frame.y_pred.to_numpy(dtype=float)).all():
        raise ModelSelectionError("Candidate has NaN or infinite raw predictions.")
    for column in ("origin_week_start_date", "target_week_start_date"):
        frame[column] = pd.to_datetime(frame[column], errors="raise").dt.normalize()
        expected[column] = pd.to_datetime(expected[column], errors="raise").dt.normalize()
    joined = expected.merge(frame, on=list(KEYS), how="outer", indicator=True, validate="one_to_one",
                            suffixes=("_expected", "_actual"))
    if len(joined) != len(expected) or not joined._merge.eq("both").all():
        raise ModelSelectionError("Candidate validation keys differ from the exact Phase 14 plan.")
    for column in ("y_true", "total_y_true"):
        if not np.isclose(joined[f"{column}_expected"], joined[f"{column}_actual"]).all():
            raise ModelSelectionError("Candidate validation labels disagree with the Phase 14 table.")
    return frame.sort_values(list(KEYS), kind="stable").reset_index(drop=True)


def load_phase15_references(directory: str | Path, plan: dict[str, Any],
                            baseline_config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, str]]:
    """Read only the human-local frozen baseline artifacts during the local run."""
    root = Path(directory)
    manifest = json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))
    reference = json.loads((root / "baseline_reference.json").read_text(encoding="utf-8"))
    signature = phase14_backtest_signature(plan)
    if manifest.get("phase14_backtest_signature") != signature or reference.get("phase") != 15:
        raise ModelSelectionError("Phase 15 reference does not use the frozen Phase 14 signature.")
    if reference.get("baseline_config_hash") != manifest.get("baseline_config_hash"):
        raise ModelSelectionError("Phase 15 reference and run manifest disagree on baseline configuration.")
    config_hash = hashlib.sha256(json.dumps(baseline_config, sort_keys=True,
        default=str, separators=(",", ":")).encode()).hexdigest()
    if manifest["baseline_config_hash"] != config_hash:
        raise ModelSelectionError("Phase 15 reference baseline configuration changed.")
    ids = {"total": reference.get("best_total_baseline"), "chilled": reference.get("best_chilled_baseline")}
    if any(not isinstance(ids[target], str) or not ids[target].startswith(f"{target}_") for target in TARGETS):
        raise ModelSelectionError("Phase 15 reference baseline identity is missing or invalid.")
    source = pd.read_csv(root / "backtest_predictions.csv")
    records = []
    for target, candidate_id in ids.items():
        subset = source.loc[source.target_name.eq(target) & source.baseline_name.eq(candidate_id)].copy()
        if target == "chilled":
            structural = subset.loc[subset.brand.isin(["Style", "Tech"])]
            if structural.empty or not structural.y_pred.eq(0).all():
                raise ModelSelectionError("Phase 15 Style/Tech chilled predictions are not exact zero.")
            subset = subset.loc[subset.brand.eq("Fresh")].copy()
        subset["candidate_id"] = candidate_id
        validated = validate_candidate_predictions(subset, plan, target, candidate_id)
        records.append(validated)
    return pd.concat(records, ignore_index=True), ids


def evaluate_candidate(rows: pd.DataFrame, plan: dict[str, Any], target: str,
                       candidate_id: str, counterpart_candidate_id: str) -> dict[str, Any]:
    """Score a candidate with its real, key-aligned opposite-target predictions."""
    frame = validate_candidate_predictions(rows, plan, target, candidate_id)
    total_id = candidate_id if target == "total" else counterpart_candidate_id
    chilled_id = candidate_id if target == "chilled" else counterpart_candidate_id
    total = validate_candidate_predictions(rows, plan, "total", total_id)
    chilled = validate_candidate_predictions(rows, plan, "chilled", chilled_id)
    expected_ids = [split.backtest_id for split in plan["splits"]]
    expected_series = plan["required_series"]
    scoring = total[[*KEYS]].copy()
    scoring["target_total_volume_m3"] = total.y_true.to_numpy(dtype=float)
    scoring["pred_total_volume_m3"] = total.y_pred.to_numpy(dtype=float)
    scoring["target_chilled_volume_m3"] = 0.0
    scoring["pred_chilled_volume_m3"] = 0.0
    fresh = scoring.brand.eq("Fresh")
    aligned = scoring.loc[fresh, list(KEYS)].merge(
        chilled[[*KEYS, "y_true", "y_pred"]], on=list(KEYS), how="left", validate="one_to_one")
    if len(aligned) != len(chilled) or aligned.y_pred.isna().any():
        raise ModelSelectionError("Raw total and Fresh chilled candidate keys do not align.")
    scoring.loc[fresh, "target_chilled_volume_m3"] = aligned.y_true.to_numpy(dtype=float)
    scoring.loc[fresh, "pred_chilled_volume_m3"] = aligned.y_pred.to_numpy(dtype=float)
    overall = evaluate_forecast_overall(scoring, expected_backtest_ids=expected_ids,
                                        expected_series=expected_series)
    series = evaluate_forecast_per_series(scoring, expected_backtest_ids=expected_ids,
                                          expected_series=expected_series)
    horizon = evaluate_forecast_by_horizon(scoring, expected_backtest_ids=expected_ids,
                                            expected_series=expected_series)
    series = series.loc[series.target.eq(target)].reset_index(drop=True)
    if target == "chilled":
        series = series.loc[series.brand.eq("Fresh")].reset_index(drop=True)
    horizon = horizon.loc[horizon.target.eq(target)].reset_index(drop=True)
    primary = overall["total_micro"] if target == "total" else overall["fresh_chilled_micro"]
    backtests = pd.DataFrame(overall["by_backtest"])
    backtests = backtests.loc[backtests.target.eq(target)].copy()
    if len(backtests) != len(expected_ids):
        raise ModelSelectionError("Candidate lacks a required frozen backtest metric.")
    return {"target_name": target, "candidate_id": candidate_id, "backtest_count": len(backtests),
            "prediction_row_count": len(frame), "overall_mae": primary["mae"],
            "overall_rmse": primary["rmse"], "overall_wape": primary["wape"],
            "overall_bias_m3": primary["mean_bias_m3"], "p90_absolute_error": primary["p90_absolute_error"],
            "mean_backtest_mae": float(backtests.mae.mean()),
            "std_backtest_mae": float(backtests.mae.std(ddof=0)),
            "worst_backtest_mae": float(backtests.mae.max()),
            "negative_prediction_count": primary["negative_prediction_count"],
            "chilled_gt_total_count": primary["chilled_gt_total_count"] if target == "chilled" else 0,
            "per_series": series, "per_horizon": horizon, "backtests": backtests}


def relative_improvement_pct(reference_mae: float, candidate_mae: float) -> float:
    if not np.isfinite([reference_mae, candidate_mae]).all() or reference_mae < 0 or candidate_mae < 0:
        raise ModelSelectionError("Reference and candidate MAE must be finite and nonnegative.")
    if reference_mae == 0:
        return 0.0 if candidate_mae == 0 else float("-inf")
    return 100.0 * (reference_mae - candidate_mae) / reference_mae


def select_champion(summaries: list[dict[str, Any]], reference_id: str,
                    *, tolerance_pct: float = 0.5) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if tolerance_pct != 0.5:
        raise ModelSelectionError("Frozen Phase 16 relative tie tolerance is 0.5%.")
    if len({row["candidate_id"] for row in summaries}) != len(summaries):
        raise ModelSelectionError("Duplicate candidate IDs prevent one champion selection.")
    baseline = next((row for row in summaries if row["candidate_id"] == reference_id), None)
    target = "total" if reference_id.startswith("total_") else "chilled" if reference_id.startswith("chilled_") else None
    expected_ids = {reference_id, f"catboost_{target}_v1", f"lightgbm_{target}_v1",
        f"ensemble_cb_lgb_{target}_equal_v1", f"ensemble_advanced_baseline_{target}_equal_v1"}
    if baseline is None or target is None or len(summaries) != 5 or {row["candidate_id"] for row in summaries} != expected_ids:
        raise ModelSelectionError("All five reference, model, and ensemble candidates are required.")
    eligible = []
    for row in summaries:
        candidate = dict(row)
        improvement = relative_improvement_pct(baseline["overall_mae"], candidate["overall_mae"])
        candidate["relative_improvement_vs_reference_pct"] = improvement
        candidate["selection_status"] = ("REFERENCE" if candidate["candidate_id"] == reference_id else
            "ELIGIBLE" if improvement > tolerance_pct else "REJECTED_NO_IMPROVEMENT")
        if candidate["selection_status"] in {"REFERENCE", "ELIGIBLE"}:
            eligible.append(candidate)
    if not eligible:
        raise ModelSelectionError("No eligible champion remains.")
    complexity = {"baseline": 0, "advanced_reference_ensemble": 1, "catboost": 2,
                  "lightgbm": 2, "catboost_lightgbm_ensemble": 3}
    best_mae = min(row["overall_mae"] for row in eligible)
    near_best = [row for row in eligible if (best_mae == 0 and row["overall_mae"] == 0) or
                 (best_mae > 0 and 100 * (row["overall_mae"] - best_mae) / best_mae <= tolerance_pct)]
    champion = sorted(near_best, key=lambda row: (row["overall_rmse"], row["p90_absolute_error"],
        row["std_backtest_mae"], complexity[row["family"]], row["overall_mae"],
        row["candidate_id"]))[0]
    for row in eligible:
        if row["candidate_id"] == champion["candidate_id"]:
            row["selection_status"] = "SELECTED"
    complete = [next(row for row in eligible if row["candidate_id"] == original["candidate_id"])
                if any(row["candidate_id"] == original["candidate_id"] for row in eligible)
                else {**original, "relative_improvement_vs_reference_pct":
                      relative_improvement_pct(baseline["overall_mae"], original["overall_mae"]),
                      "selection_status": "REJECTED_NO_IMPROVEMENT"} for original in summaries]
    return champion, complete


def median_final_iteration(folds: pd.DataFrame, candidate_id: str, maximum: int) -> int:
    selected = folds.loc[folds.candidate_id.eq(candidate_id), "best_iteration"].to_numpy(dtype=float)
    if len(selected) != folds.backtest_id.nunique() or not np.isfinite(selected).all():
        raise ModelSelectionError("Final model iteration lacks a valid value from every backtest.")
    return int(np.clip(np.floor(np.median(selected) + 0.5), 1, maximum))


def validate_final_model_config(config: dict[str, Any]) -> None:
    if not isinstance(config, dict) or config.get("version") != 1 or config.get("state") != "FROZEN":
        raise ModelSelectionError("Task 2A final configuration must be FROZEN.")
    if config.get("source_contracts") != {"history": "phase11", "features": "phase13",
        "validation": "phase14", "baselines": "phase15", "selection": "phase16"}:
        raise ModelSelectionError("A required upstream contract reference is missing.")
    if not config.get("feature_profile", {}).get("registry_hash") or not config.get("validation", {}).get("backtest_signature"):
        raise ModelSelectionError("Frozen feature profile or backtest signature is missing.")
    if config.get("selection_policy") != {"primary_metric": "mae", "relative_tie_tolerance_pct": 0.5,
        "prefer_simpler_within_tolerance": True} or config.get("selection_complete") is not True:
        raise ModelSelectionError("Frozen selection policy is incomplete.")
    if config.get("structural_output_rules") != {"style_chilled_zero": True, "tech_chilled_zero": True}:
        raise ModelSelectionError("Style and Tech chilled zero rules are required.")
    if config.get("phase17_postprocessing") != {"clip_negative": True,
        "enforce_chilled_le_total": True, "rounding": "none"}:
        raise ModelSelectionError("Phase 17 postprocessing ownership changed.")
    candidates = []
    for target in ("total", "chilled_fresh"):
        item = config.get(target)
        if not isinstance(item, dict) or not isinstance(item.get("candidate_id"), str) or not item["candidate_id"]:
            raise ModelSelectionError(f"Exactly one {target} champion is required.")
        if item.get("approach_type") not in {"baseline", "model", "ensemble"}:
            raise ModelSelectionError("Champion approach type is invalid.")
        if isinstance(item.get("candidate_id"), list):
            raise ModelSelectionError("Multiple champions are forbidden.")
        if item["approach_type"] == "baseline":
            if not item.get("parameters") or item.get("final_iteration_policy") != "NOT_APPLICABLE":
                raise ModelSelectionError("Baseline identity, parameters, and iteration policy are required.")
        elif item["approach_type"] == "model":
            if item.get("family") not in {"catboost", "lightgbm"} or not item.get("parameters"):
                raise ModelSelectionError("Model family and exact parameters are required.")
            policy = item.get("final_iteration_policy", {})
            if policy.get("method") != "median_best_iteration" or type(policy.get("value")) is not int or policy["value"] < 1:
                raise ModelSelectionError("Model final iteration policy and value are required.")
        else:
            parts = item.get("component_candidates", [])
            weights = item.get("component_weights", [])
            if len(parts) != 2 or len(weights) != 2 or any(not isinstance(part, dict) or
                not part.get("candidate_id") for part in parts) or weights != [0.5, 0.5]:
                raise ModelSelectionError("Ensemble requires two configured components with frozen 50/50 weights.")
            for part in parts:
                policy = part.get("final_iteration_policy")
                if part.get("approach_type") == "model" and (not part.get("parameters") or
                    not isinstance(policy, dict) or policy.get("method") != "median_best_iteration" or
                    type(policy.get("value")) is not int or policy["value"] < 1):
                    raise ModelSelectionError("Ensemble model component lacks fit parameters or iteration policy.")
        candidates.append(item["candidate_id"])
    if len(set(candidates)) != 2:
        raise ModelSelectionError("Total and chilled champions must be distinct.")
    forbidden = {"overall_mae", "overall_rmse", "overall_wape", "p90_absolute_error",
                 "std_backtest_mae", "worst_backtest_mae", "private_metrics"}
    def scan(value: Any) -> bool:
        if isinstance(value, dict):
            return bool(forbidden.intersection(value)) or any(scan(child) for child in value.values())
        if isinstance(value, list):
            return any(scan(child) for child in value)
        return False
    if scan(config):
        raise ModelSelectionError("Tracked final configuration contains private score fields.")


def load_selection_decisions(path: str | Path) -> dict[str, Any]:
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    if record.get("selection_complete") is not True or not record.get("phase14_backtest_signature"):
        raise ModelSelectionError("Local Phase 16 selection is incomplete.")
    if not isinstance(record.get("total"), dict) or not isinstance(record.get("chilled_fresh"), dict):
        raise ModelSelectionError("Both local champion decisions are required.")
    return record
