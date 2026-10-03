"""Freeze final Task 1 model config after one-time holdout confirmation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Freeze final Task 1 model configuration.")
    p.add_argument("--selection", type=Path, required=True)
    p.add_argument("--holdout-confirmation", type=Path, required=True)
    p.add_argument("--advanced-config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    return p


def main() -> int:
    args = parser().parse_args()
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    confirmation = json.loads(args.holdout_confirmation.read_text(encoding="utf-8"))
    advanced = yaml.safe_load(args.advanced_config.read_text(encoding="utf-8")) or {}
    if not bool(confirmation.get("success")):
        raise ValueError("Cannot freeze final config before successful holdout confirmation.")
    if int(confirmation.get("service_configs_evaluated_on_holdout", 0)) != 1:
        raise ValueError("Holdout confirmation must include exactly one service config.")
    if int(confirmation.get("lateness_configs_evaluated_on_holdout", 0)) != 1:
        raise ValueError("Holdout confirmation must include exactly one lateness config.")
    output = {
        "version": 1,
        "seed": int(advanced.get("seed", 42)),
        "validation_contract": {
            "config": "configs/task1_validation.yaml",
            "development_selection_complete": True,
            "final_holdout_confirmation_complete": True,
            "final_holdout_access_count_per_target": 1,
        },
        "features": {
            "registry": "configs/task1_features.yaml",
            "profile": advanced.get("features", {}).get("profile", "safe_core_plus_history"),
        },
        "service_model": {
            "family": selection["service"].get("family", str(selection["service"]["candidate_id"]).split("_")[0]),
            "config_id": selection["service"]["candidate_id"],
            "parameters": selection["service"].get("parameters", {}),
            "final_iteration_policy": selection["service"].get(
                "final_iteration_policy", {"method": "median_best_iteration", "value": 200}
            ),
            "prediction_postprocessing": {"phase09_clipping": False},
        },
        "lateness_model": {
            "family": selection["lateness"].get("family", str(selection["lateness"]["candidate_id"]).split("_")[0]),
            "config_id": selection["lateness"]["candidate_id"],
            "parameters": selection["lateness"].get("parameters", {}),
            "final_iteration_policy": selection["lateness"].get(
                "final_iteration_policy", {"method": "median_best_iteration", "value": 200}
            ),
            "calibration": {
                "method": selection["lateness"].get("calibration_method", "raw"),
                "fit_protocol": selection["lateness"].get("calibration_protocol", "chronological_oof"),
            },
        },
        "selection": {
            "regression_primary_metric": "mae",
            "lateness_primary_metric": "log_loss",
            "baseline_comparison_completed": True,
            "brand_diagnostic_completed": True,
            "depot_diagnostic_completed": True,
            "calibration_comparison_completed": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(output, sort_keys=False), encoding="utf-8")
    print("FINAL CONFIG WRITTEN: YES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
