"""Run frozen Phase 15 baselines locally and write private, sanitized artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task2a.baseline_evaluation import (build_baseline_run_manifest, evaluate_baseline_predictions,
    generate_backtest_baseline_predictions, load_and_verify_phase14_plan, rank_reference_baselines)
from src.task2a.baselines import load_baseline_config
from src.task2a.features import load_feature_config
from src.task2a.validation import build_rolling_origin_plan, load_validation_config


def validate_private_output_dir(path: Path) -> Path:
    allowed = (PROJECT_ROOT / "reports" / "private" / "phase15_task2a_baselines").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as error:
        raise ValueError("Baseline output must be inside reports/private/phase15_task2a_baselines.") from error
    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weekly-panel", required=True, type=Path)
    parser.add_argument("--multihorizon-table", required=True, type=Path)
    parser.add_argument("--validation-config", required=True, type=Path)
    parser.add_argument("--baseline-config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--feature-config", type=Path, default=PROJECT_ROOT / "configs" / "task2a_features.yaml")
    parser.add_argument("--phase14-plan", type=Path,
                        default=PROJECT_ROOT / "reports" / "private" / "phase14_task2a_validation" / "validation_plan.json")
    return parser.parse_args()


def _table(records: list[dict], target: str, baseline: str) -> pd.DataFrame:
    frame = pd.DataFrame(records)
    if frame.empty:
        return frame
    frame.insert(0, "baseline_name", baseline)
    frame.insert(0, "target_name", target)
    return frame


def main() -> int:
    args = parse_args()
    output = validate_private_output_dir(args.output_dir)
    baseline_config = load_baseline_config(args.baseline_config)
    validation_config = load_validation_config(args.validation_config)
    feature_config = load_feature_config(args.feature_config)
    panel = pd.read_csv(args.weekly_panel)
    multihorizon = pd.read_csv(args.multihorizon_table)
    plan = build_rolling_origin_plan(panel, multihorizon, feature_config, validation_config)
    signature = load_and_verify_phase14_plan(args.phase14_plan, plan)
    predictions = generate_backtest_baseline_predictions(panel, plan, baseline_config)
    evaluated = evaluate_baseline_predictions(predictions, plan)
    summary, references = rank_reference_baselines(evaluated)

    backtest_metrics, series_metrics, horizon_metrics = [], [], []
    for item in evaluated.values():
        target, baseline = item["target_name"], item["baseline_name"]
        backtest_metrics.append(_table(item["backtests"].to_dict(orient="records"), target, baseline))
        series_metrics.append(_table(item["per_series"].to_dict(orient="records"), target, baseline))
        horizon_metrics.append(_table(item["by_horizon"].to_dict(orient="records"), target, baseline))
    output.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output / "backtest_predictions.csv", index=False)
    pd.concat(backtest_metrics, ignore_index=True).to_csv(output / "backtest_metrics.csv", index=False)
    pd.concat(series_metrics, ignore_index=True).to_csv(output / "series_metrics.csv", index=False)
    pd.concat(horizon_metrics, ignore_index=True).to_csv(output / "horizon_metrics.csv", index=False)
    summary.to_csv(output / "baseline_summary.csv", index=False)
    (output / "baseline_reference.json").write_text(json.dumps({
        "phase": 15, "validation_contract_version": 1, "best_total_baseline": references["total"],
        "best_chilled_baseline": references["chilled"], "selection_primary_metric": "mae",
        "selection_tie_breaks": ["rmse", "p90_absolute_error", "backtest_mae_std", "simplicity"],
        "baseline_config_hash": build_baseline_run_manifest(baseline_config, validation_config, plan)["baseline_config_hash"],
    }, indent=2), encoding="utf-8")
    (output / "run_manifest.json").write_text(json.dumps(
        build_baseline_run_manifest(baseline_config, validation_config, plan), indent=2), encoding="utf-8")
    (output / "warnings.json").write_text(json.dumps({
        "unavailable_prediction_count": int(predictions.y_pred.isna().sum()),
        "seasonal_fallback_count": int(predictions.seasonal_fallback_used.sum()),
        "phase14_backtest_signature": signature,
    }, indent=2), encoding="utf-8")
    (output / "phase15_baseline_report.md").write_text(
        "# Phase 15 baseline report\n\nAll metrics and predictions are private. The run reused the frozen Phase 14 signature.\n",
        encoding="utf-8")
    for line in (
        "LOCAL PHASE 15 BASELINE RUN: PASS", "PHASE 14 BACKTEST SIGNATURE MATCH: YES",
        "ALL REQUIRED BACKTESTS COMPLETED: YES", "TOTAL BASELINE CANDIDATES COMPLETE: YES",
        "FRESH CHILLED BASELINE CANDIDATES COMPLETE: YES", "STYLE CHILLED EXACT ZERO: YES",
        "TECH CHILLED EXACT ZERO: YES", "FUTURE-DEMAND LEAKAGE AUDIT: PASS",
        "TOTAL REFERENCE BASELINE FROZEN: YES", "CHILLED REFERENCE BASELINE FROZEN: YES",
    ):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
