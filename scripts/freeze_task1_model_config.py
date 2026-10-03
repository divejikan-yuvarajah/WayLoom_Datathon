"""Freeze final Task 1 model config after one-time holdout confirmation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.advanced_models import hydrate_provisional_section  # noqa: E402


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
    svc = hydrate_provisional_section(selection["service"], advanced, target="service")
    late = hydrate_provisional_section(selection["lateness"], advanced, target="late")
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
            "family": svc["family"],
            "config_id": svc["candidate_id"],
            "parameters": svc.get("parameters", {}),
            "final_iteration_policy": svc.get(
                "final_iteration_policy", {"method": "median_best_iteration", "value": 200}
            ),
            "prediction_postprocessing": {"phase09_clipping": False},
        },
        "lateness_model": {
            "family": late["family"],
            "config_id": late["candidate_id"],
            "parameters": late.get("parameters", {}),
            "final_iteration_policy": late.get(
                "final_iteration_policy", {"method": "median_best_iteration", "value": 200}
            ),
            "calibration": {
                "method": late.get("calibration_method") or (late.get("calibration") or {}).get("method") or "raw",
                "fit_protocol": late.get("calibration_protocol")
                or (late.get("calibration") or {}).get("fit_protocol")
                or "chronological_oof",
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
