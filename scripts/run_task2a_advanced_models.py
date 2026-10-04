"""Run the fixed Phase 16 Task 2A candidates locally on private data."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task2a.advanced_models import KEYS, load_advanced_config, run_advanced_backtests, verify_frozen_phase14_plan
from src.task2a.ensembles import blend_equal_weight
from src.task2a.features import load_feature_config
from src.task2a.model_selection import (evaluate_candidate, load_phase15_references,
    select_champion, validate_candidate_predictions)
from src.task2a.validation import build_rolling_origin_plan, load_validation_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weekly-panel", required=True, type=Path)
    parser.add_argument("--multihorizon-table", required=True, type=Path)
    parser.add_argument("--feature-config", required=True, type=Path)
    parser.add_argument("--validation-config", required=True, type=Path)
    parser.add_argument("--baseline-results", required=True, type=Path)
    parser.add_argument("--model-config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--phase14-plan", type=Path, default=PROJECT_ROOT / "reports/private/phase14_task2a_validation/validation_plan.json")
    return parser.parse_args()


def private_output_dir(path: Path) -> Path:
    allowed = (PROJECT_ROOT / "reports/private/phase16_task2a_advanced").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as error:
        raise ValueError("Phase 16 outputs must be within reports/private/phase16_task2a_advanced.") from error
    return resolved


def _component_spec(candidate_id: str, target: str, model_config: dict, folds: pd.DataFrame,
                    baseline_config: dict) -> dict:
    if candidate_id.startswith(f"{target}_"):
        family = candidate_id.removeprefix(f"{target}_")
        config_key = "recent_mean" if family == "recent_mean_4" else family
        if config_key not in baseline_config["baseline_families"]:
            raise ValueError("Frozen Phase 15 baseline identity is not configured.")
        return {"approach_type": "baseline", "candidate_id": candidate_id, "family": family,
                "parameters": baseline_config["baseline_families"][config_key],
                "final_iteration_policy": "NOT_APPLICABLE"}
    for family in ("catboost", "lightgbm"):
        params = model_config[family][target]
        if candidate_id == params["candidate_id"]:
            maximum = params["iterations" if family == "catboost" else "n_estimators"]
            values = folds.loc[folds.candidate_id.eq(candidate_id), "best_iteration"].to_numpy(dtype=float)
            if len(values) != folds.backtest_id.nunique() or not np.isfinite(values).all():
                raise ValueError("Final iteration requires every valid backtest best iteration.")
            iteration = int(np.clip(np.floor(np.median(values) + 0.5), 1, maximum))
            return {"approach_type": "model", "candidate_id": candidate_id, "family": family,
                    "parameters": params, "feature_profile_id": "task2a_advanced_safe_v1",
                    "preprocessing": "native_categorical" if family == "catboost" else "fold_train_median_onehot",
                    "final_iteration_policy": {"method": "median_best_iteration", "value": iteration}}
    raise ValueError("Unknown Phase 16 component candidate.")


def _champion_spec(candidate_id: str, target: str, model_config: dict, folds: pd.DataFrame,
                   baseline_config: dict, components: dict[str, tuple[str, str]]) -> dict:
    if candidate_id not in components:
        return _component_spec(candidate_id, target, model_config, folds, baseline_config)
    left, right = components[candidate_id]
    return {"approach_type": "ensemble", "candidate_id": candidate_id,
            "family": "catboost_lightgbm_ensemble" if "cb_lgb" in candidate_id else "advanced_reference_ensemble",
            "parameters": {"weight_left": 0.5, "weight_right": 0.5},
            "component_candidates": [_component_spec(part, target, model_config, folds, baseline_config)
                                     for part in (left, right)],
            "component_weights": [0.5, 0.5],
            "final_iteration_policy": "COMPONENT_POLICIES"}


def run_experiment(panel: pd.DataFrame, table: pd.DataFrame, feature_config: dict,
                   validation_config: dict, model_config: dict, baseline_results: Path,
                   phase14_plan: Path, baseline_config: dict) -> dict:
    plan = build_rolling_origin_plan(panel, table, feature_config, validation_config)
    signature = verify_frozen_phase14_plan(phase14_plan, plan)
    reference_predictions, references = load_phase15_references(baseline_results, plan)
    model_predictions, folds, profile = run_advanced_backtests(plan, feature_config, model_config)
    all_predictions = [reference_predictions, model_predictions]
    components: dict[str, tuple[str, str]] = {}
    selection = {}
    summaries = []
    diagnostics = {}
    for target in ("total", "chilled"):
        ids = [references[target], model_config["catboost"][target]["candidate_id"],
               model_config["lightgbm"][target]["candidate_id"]]
        combined = pd.concat(all_predictions, ignore_index=True)
        cb = validate_candidate_predictions(combined, plan, target, ids[1])
        lgb = validate_candidate_predictions(combined, plan, target, ids[2])
        ensemble_a_id = f"ensemble_cb_lgb_{target}_equal_v1"
        ensemble_a = blend_equal_weight(cb, lgb, ensemble_a_id)
        all_predictions.append(ensemble_a)
        components[ensemble_a_id] = (ids[1], ids[2])
        preliminary = [evaluate_candidate(combined, plan, target, candidate_id) for candidate_id in ids[1:]]
        best_advanced = min(preliminary, key=lambda row: (row["overall_mae"], row["overall_rmse"],
            row["p90_absolute_error"], row["std_backtest_mae"], row["candidate_id"]))["candidate_id"]
        advanced = validate_candidate_predictions(combined, plan, target, best_advanced)
        reference = validate_candidate_predictions(combined, plan, target, ids[0])
        ensemble_b_id = f"ensemble_advanced_baseline_{target}_equal_v1"
        ensemble_b = blend_equal_weight(advanced, reference, ensemble_b_id)
        all_predictions.append(ensemble_b)
        components[ensemble_b_id] = (best_advanced, ids[0])
        candidate_ids = [*ids, ensemble_a_id, ensemble_b_id]
        complete = pd.concat(all_predictions, ignore_index=True)
        target_summaries = []
        for candidate_id in candidate_ids:
            result = evaluate_candidate(complete, plan, target, candidate_id)
            result["family"] = ("baseline" if candidate_id == ids[0] else
                "catboost" if candidate_id == ids[1] else "lightgbm" if candidate_id == ids[2] else
                "catboost_lightgbm_ensemble" if candidate_id == ensemble_a_id else "advanced_reference_ensemble")
            diagnostics[candidate_id] = {"per_series": result.pop("per_series"),
                                         "per_horizon": result.pop("per_horizon"),
                                         "backtests": result.pop("backtests")}
            target_summaries.append(result)
        champion, ranked = select_champion(target_summaries, ids[0])
        summaries.extend(ranked)
        selection["total" if target == "total" else "chilled_fresh"] = _champion_spec(
            champion["candidate_id"], target, model_config, folds, baseline_config, components)
    complete = pd.concat(all_predictions, ignore_index=True)
    total_id = selection["total"]["candidate_id"]
    chilled_id = selection["chilled_fresh"]["candidate_id"]
    total = validate_candidate_predictions(complete, plan, "total", total_id)
    chilled = validate_candidate_predictions(complete, plan, "chilled", chilled_id)
    fresh_total = total.loc[total.brand.eq("Fresh"), [*KEYS, "y_pred"]]
    paired = chilled[[*KEYS, "y_pred"]].merge(fresh_total, on=list(KEYS), suffixes=("_chilled", "_total"),
                                               how="left", validate="one_to_one")
    if len(paired) != len(chilled) or paired.y_pred_total.isna().any():
        raise ValueError("Selected Fresh chilled and total raw predictions do not align.")
    chilled_exceeds_total = int(paired.y_pred_chilled.gt(paired.y_pred_total).sum())
    selection.update({"phase14_backtest_signature": signature, "feature_profile_id": profile["profile_id"],
                      "feature_registry_hash": profile["registry_hash"], "selection_complete": True,
                      "style_chilled_zero": True, "tech_chilled_zero": True})
    return {"predictions": complete, "folds": folds, "profile": profile, "summaries": pd.DataFrame(summaries),
            "diagnostics": diagnostics, "selection": selection,
            "chilled_gt_total_count": chilled_exceeds_total, "signature": signature}


def main() -> int:
    args = parse_args()
    output = private_output_dir(args.output_dir)
    feature_config = load_feature_config(args.feature_config)
    validation_config = load_validation_config(args.validation_config)
    model_config = load_advanced_config(args.model_config)
    from src.task2a.baselines import load_baseline_config
    baseline_config = load_baseline_config(PROJECT_ROOT / "configs/task2a_baselines.yaml")
    panel = pd.read_csv(args.weekly_panel)
    table = pd.read_csv(args.multihorizon_table)
    result = run_experiment(panel, table, feature_config, validation_config, model_config,
                            args.baseline_results, args.phase14_plan, baseline_config)
    output.mkdir(parents=True, exist_ok=True)
    result["predictions"].to_csv(output / "candidate_predictions.csv", index=False)
    result["folds"].to_csv(output / "fold_early_stopping.csv", index=False)
    result["summaries"].to_csv(output / "candidate_summary.csv", index=False)
    for candidate, tables in result["diagnostics"].items():
        for name, frame in tables.items():
            frame.to_csv(output / f"{candidate}_{name}.csv", index=False)
    (output / "selection_decisions.json").write_text(json.dumps(result["selection"], indent=2), encoding="utf-8")
    manifest = {"phase": 16, "phase14_backtest_signature": result["signature"],
                "feature_registry_hash": result["profile"]["registry_hash"],
                "forbidden_feature_count": result["profile"]["forbidden_feature_count"],
                "phase15_references_verified": True, "required_backtest_count": int(result["folds"].backtest_id.nunique()),
                "model_fold_count": int(len(result["folds"])),
                "fresh_chilled_gt_raw_total_count": result["chilled_gt_total_count"],
                "model_config_hash": hashlib.sha256(json.dumps(model_config, sort_keys=True).encode()).hexdigest()}
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for line in ("LOCAL PHASE 16 ADVANCED RUN: PASS", "PHASE 14 BACKTEST SIGNATURE MATCH: YES",
                 "PHASE 15 REFERENCE BASELINES MATCH: YES", "CATBOOST TOTAL AND FRESH CHILLED: COMPLETE",
                 "LIGHTGBM TOTAL AND FRESH CHILLED: COMPLETE", "FIXED ENSEMBLES: COMPLETE",
                 "TOTAL AND FRESH CHILLED CHAMPIONS: SELECTED", "PRIVATE PREDICTIONS PRINTED: NO"):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
