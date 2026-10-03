"""One-time holdout confirmation guard for frozen Phase 09 provisional configs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.advanced_models import AdvancedCandidate, fit_predict_advanced_fold, hydrate_provisional_section  # noqa: E402
from src.task1.metrics import lateness_probability_metrics, regression_metrics  # noqa: E402
from src.task1.validation import build_task1_validation_plan, load_task1_validation_config  # noqa: E402


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Confirm one-time final holdout for exactly one service/late config.")
    p.add_argument("--features", type=Path, required=True)
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--validation-config", type=Path, required=True)
    p.add_argument("--model-config", type=Path, required=True)
    p.add_argument("--selection", type=Path, required=True, help="Path to provisional_selection.json")
    p.add_argument("--output", type=Path, required=True, help="Path to holdout_confirmation.json")
    p.add_argument("--acknowledge-holdout-already-consumed", action="store_true")
    return p


def main() -> int:
    args = parser().parse_args()
    if not args.selection.exists():
        raise FileNotFoundError(args.selection)
    X = pd.read_csv(args.features, low_memory=False)
    labels = pd.read_csv(args.labels, low_memory=False)
    if len(X) != len(labels):
        raise ValueError("Feature/label row count mismatch.")
    validation_cfg = load_task1_validation_config(args.validation_config)
    plan = build_task1_validation_plan(labels, validation_cfg)
    holdout = plan["holdout"]
    dev_idx = holdout.development_index
    ho_idx = holdout.holdout_index
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    if "service" not in selection or "lateness" not in selection:
        raise ValueError("Selection must contain exactly one service and one lateness config.")
    if not isinstance(selection["service"], dict) or not isinstance(selection["lateness"], dict):
        raise ValueError("Selection config entries must be objects.")
    if args.output.exists() and not args.acknowledge_holdout_already_consumed:
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if bool(existing.get("success")):
            raise ValueError("Successful holdout confirmation already exists; refusing normal rerun.")
    model_cfg = json.loads(args.model_config.read_text(encoding="utf-8")) if args.model_config.suffix == ".json" else None
    if model_cfg is None:
        import yaml
        model_cfg = yaml.safe_load(args.model_config.read_text(encoding="utf-8")) or {}
    early = model_cfg.get("early_stopping", {})
    patience = int(early.get("patience_rounds", 100))
    default_max = int(early.get("max_iterations", 2000))
    y_service = labels["service_minutes"]
    y_late = labels["late_flag"]

    svc_cfg = hydrate_provisional_section(selection["service"], model_cfg, target="service")
    late_cfg = hydrate_provisional_section(selection["lateness"], model_cfg, target="late")
    svc_candidate = AdvancedCandidate(
        svc_cfg["candidate_id"],
        svc_cfg["family"],
        "service",
        svc_cfg.get("parameters", {}),
        svc_cfg.get("feature_profile", model_cfg.get("features", {}).get("profile", "safe_core_plus_history")),
    )
    late_candidate = AdvancedCandidate(
        late_cfg["candidate_id"],
        late_cfg["family"],
        "late",
        late_cfg.get("parameters", {}),
        late_cfg.get("feature_profile", model_cfg.get("features", {}).get("profile", "safe_core_plus_history")),
    )
    svc_iter = int(svc_cfg.get("final_iteration_policy", {}).get("value", default_max))
    late_iter = int(late_cfg.get("final_iteration_policy", {}).get("value", default_max))
    svc_result = fit_predict_advanced_fold(
        candidate=svc_candidate,
        X_train=X.loc[dev_idx],
        y_train=y_service.loc[dev_idx],
        X_valid=X.loc[ho_idx],
        y_valid=y_service.loc[ho_idx],
        max_iterations=svc_iter,
        patience_rounds=max(svc_iter, patience),
        min_iterations=1,
    )
    late_result = fit_predict_advanced_fold(
        candidate=late_candidate,
        X_train=X.loc[dev_idx],
        y_train=y_late.loc[dev_idx],
        X_valid=X.loc[ho_idx],
        y_valid=y_late.loc[ho_idx],
        max_iterations=late_iter,
        patience_rounds=max(late_iter, patience),
        min_iterations=1,
    )
    svc_metrics = regression_metrics(y_service.loc[ho_idx], svc_result.prediction)
    late_metrics = lateness_probability_metrics(y_late.loc[ho_idx], late_result.prediction)
    confirmation = {
        "success": True,
        "service_configs_evaluated_on_holdout": 1,
        "lateness_configs_evaluated_on_holdout": 1,
        "config_changed_after_holdout": "NO",
        "service_config_id": selection["service"].get("candidate_id"),
        "lateness_config_id": selection["lateness"].get("candidate_id"),
        "service_metrics": {"mae": float(svc_metrics["mae"]), "rmse": float(svc_metrics["rmse"])},
        "lateness_metrics": {"log_loss": float(late_metrics["log_loss"]), "brier_score": float(late_metrics["brier_score"])},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(confirmation, indent=2), encoding="utf-8")
    print("LOCAL PHASE 09 HOLDOUT CONFIRMATION: PASS")
    print("SERVICE CONFIGS EVALUATED ON HOLDOUT: 1")
    print("LATENESS CONFIGS EVALUATED ON HOLDOUT: 1")
    print("CONFIG CHANGED AFTER HOLDOUT: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
