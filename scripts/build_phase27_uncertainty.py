"""Build private Phase 27 uncertainty artifacts; never changes official points."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.uncertainty.coverage import sequential_backtest_coverage
from src.uncertainty.forecast_intervals import build_forecast_intervals
from src.uncertainty.quantiles import finite_sample_quantile, validate_coverage_levels
from src.uncertainty.reporting import (assert_points_unchanged, hash_artifacts, official_schema_guard,
    require_private_path, sha256_file, write_csv_atomic, write_json_atomic)
from src.uncertainty.residual_sources import (load_task2a_frozen_oos, load_yaml,
    recreate_task1_service_oos)
from src.uncertainty.service_intervals import build_service_intervals


class Phase27BuildError(ValueError):
    """The optional uncertainty layer cannot be built honestly."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build private Phase 27 residual uncertainty intervals.")
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--uncertainty-config", required=True, type=Path)
    parser.add_argument("--task1-final-config", required=True, type=Path)
    parser.add_argument("--task1-submission", required=True, type=Path)
    parser.add_argument("--task2a-final-config", required=True, type=Path)
    parser.add_argument("--task2a-submission", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    return parser.parse_args()


def _validate_config(config: dict) -> tuple[float, ...]:
    if config.get("version") != 1:
        raise Phase27BuildError("Phase 27 configuration version is invalid.")
    levels = validate_coverage_levels(config.get("coverage_levels", []))
    if (config.get("quantile") != {"method": "finite_sample_higher", "require_oos_residuals": True}
            or config.get("task1_service", {}).get("calibration_source") != "frozen_oos_validation"
            or config.get("task2a", {}).get("calibration_source") != "frozen_rolling_oos"
            or config.get("task2a", {}).get("fallback") != "pooled_target"):
        raise Phase27BuildError("Phase 27 OOS/quantile/fallback contract changed.")
    if config.get("task2a", {}).get("chilled_zero_brands") != ["Style", "Tech"]:
        raise Phase27BuildError("Structural chilled-zero brands changed.")
    return levels


def _find_unique(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if len(matches) != 1:
        raise Phase27BuildError(f"Expected exactly one official {filename} below raw root.")
    return matches[0]


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _versions() -> dict[str, str]:
    values = {"python": sys.version.split()[0]}
    for package in ("numpy", "pandas", "catboost", "lightgbm"):
        try:
            values[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            values[package] = "NOT_INSTALLED"
    return values


def _calibration_table(residuals: pd.DataFrame, levels: tuple[float, ...]) -> pd.DataFrame:
    rows = []
    for horizon, group in residuals.groupby("horizon_weeks", sort=True):
        row = {"forecast_horizon": int(horizon), "calibration_n": int(len(group)),
               "mean_absolute_residual": float(group.absolute_residual.mean()),
               "median_absolute_residual": float(group.absolute_residual.median())}
        for level in levels:
            row[f"q{int(level * 100)}"] = finite_sample_quantile(group.absolute_residual, level)
        rows.append(row)
    return pd.DataFrame(rows)


def _summary_markdown(service_summary: dict, forecast_summary: dict, coverage: pd.DataFrame) -> str:
    available = int(coverage.status.eq("AVAILABLE").sum()) if not coverage.empty else 0
    return f"""# Phase 27 — Forecast uncertainty

## Scope

This optional WayLoom engineering layer adds private uncertainty artifacts around the frozen Task 1 service-time and Task 2A demand point predictions. Official CSV schemas and point predictions remain unchanged.

## Task 1 service uncertainty method

The service interval uses {service_summary['calibration_residual_count']} out-of-sample expanding-fold residuals from the frozen Phase 7/9 validation procedure. For each target coverage, the additive score is the finite-sample higher order statistic of absolute residuals. Lower bounds are clipped at zero. Independent coverage evaluation is not available; calibration residual coverage is not presented as independent evidence.

## Task 2A forecast uncertainty method

The forecast intervals use frozen Phase 16 rolling-origin OOS predictions with Phase 17 post-processing. Calibration is horizon-specific when sample size permits and otherwise uses the predeclared pooled-target fallback. The targets are total volume and Fresh chilled volume. Style and Tech chilled intervals remain exactly [0,0].

## Coverage and interval diagnostics

Sequential historical backtest diagnostics calibrate each evaluated origin only from earlier eligible origins. Available diagnostic groups: {available}. These are empirical historical diagnostics, not guaranteed future coverage.

## Physical constraints

All bounds are nonnegative. Raw Fresh chilled bounds are retained, and a separate presentation-coherent view clips chilled upper bounds to total upper bounds. That transformation is not claimed to preserve unchanged marginal coverage.

## Limitations

Intervals are conformal-style residual intervals conditional on historical error behavior. Time dependence, distribution shift, festival/payday/monsoon regimes, and Task 1 heteroscedasticity can make future uncertainty differ. No universal finite-sample or probabilistic coverage guarantee is claimed.

## Official schema guard

`submission_task1.csv` remains `delivery_id,pred_service_min,pred_late_prob`. `submission_task2a.csv` remains `row_id,pred_total_volume_m3,pred_chilled_volume_m3`. Unofficial interval fields are written only below `reports/private/phase27_uncertainty/`.
"""


def main() -> int:
    args = parse_args()
    config = load_yaml(args.uncertainty_config)
    levels = _validate_config(config)
    report_dir = require_private_path(args.report_dir, repository_root=ROOT)
    configured = (ROOT / config["privacy"]["private_report_dir"]).resolve()
    if report_dir != configured:
        raise Phase27BuildError("Report directory differs from the configured private Phase 27 path.")
    if args.summary_output.resolve() != (ROOT / "docs/phase27_uncertainty.md").resolve():
        raise Phase27BuildError("Aggregate summary path must be docs/phase27_uncertainty.md.")
    frozen_paths = [(ROOT / path).resolve() for path in config["frozen_artifacts"]]
    before = hash_artifacts(frozen_paths)
    schema_before = official_schema_guard(args.task1_submission, args.task2a_submission)
    task1_final = load_yaml(args.task1_final_config)
    task2a_final = load_yaml(args.task2a_final_config)
    task1_cfg = config["task1_service"]
    features = pd.read_csv(ROOT / task1_cfg["features_path"], low_memory=False)
    labels = pd.read_csv(ROOT / task1_cfg["labels_path"])
    service_oos = recreate_task1_service_oos(features, labels,
        load_yaml(ROOT / task1_cfg["validation_config_path"]),
        load_yaml(ROOT / task1_cfg["advanced_config_path"]), task1_final)
    task1_submission = pd.read_csv(args.task1_submission, dtype={
        "delivery_id": "string", "pred_service_min": "string", "pred_late_prob": "string"
    }, keep_default_na=False)
    service_private, service_summary = build_service_intervals(task1_submission, service_oos, levels,
        minimum_count=int(task1_cfg["min_global_residuals"]))
    task2_cfg = config["task2a"]
    candidate_predictions = pd.read_csv(ROOT / task2_cfg["candidate_predictions_path"])
    task2_oos = load_task2a_frozen_oos(candidate_predictions, task2a_final)
    task2_submission = pd.read_csv(args.task2a_submission, dtype={
        "row_id": "string", "pred_total_volume_m3": "string", "pred_chilled_volume_m3": "string"
    }, keep_default_na=False)
    task2_inputs = pd.read_csv(_find_unique(args.raw_root, "task2a_test_inputs.csv"))
    forecast_private, forecast_summary, fallback = build_forecast_intervals(
        task2_submission, task2_inputs, task2_oos["total"], task2_oos["chilled"], levels,
        minimum_per_horizon=int(task2_cfg["min_residuals_per_horizon"]),
        minimum_pooled=int(task2_cfg["min_pooled_target_residuals"]),
        chilled_zero_brands=tuple(task2_cfg["chilled_zero_brands"]),
    )
    assert_points_unchanged(service_private, task1_submission, task="task1")
    assert_points_unchanged(forecast_private, task2_submission, task="task2a")
    coverage_parts = []
    for target, residuals in task2_oos.items():
        part = sequential_backtest_coverage(residuals, levels,
            minimum_per_horizon=int(task2_cfg["min_residuals_per_horizon"]),
            minimum_pooled=int(task2_cfg["min_pooled_target_residuals"]))
        part.insert(0, "target", target)
        coverage_parts.append(part)
    coverage = pd.concat(coverage_parts, ignore_index=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    write_csv_atomic(report_dir / "task1_service_uncertainty.csv", service_private)
    write_json_atomic(report_dir / "task1_service_residual_calibration.json", service_summary)
    write_json_atomic(report_dir / "task1_service_uncertainty_summary.json", service_summary)
    write_csv_atomic(report_dir / "task2a_total_residual_calibration.csv", _calibration_table(task2_oos["total"], levels))
    write_csv_atomic(report_dir / "task2a_chilled_residual_calibration.csv", _calibration_table(task2_oos["chilled"], levels))
    write_csv_atomic(report_dir / "task2a_forecast_uncertainty.csv", forecast_private)
    write_json_atomic(report_dir / "task2a_uncertainty_summary.json", forecast_summary)
    write_json_atomic(report_dir / "coverage_diagnostics.json", json.loads(coverage.to_json(orient="records")))
    write_json_atomic(report_dir / "fallback_diagnostics.json", fallback)
    after = hash_artifacts(frozen_paths)
    if before != after:
        raise Phase27BuildError("A frozen artifact changed during Phase 27.")
    schema_after = official_schema_guard(args.task1_submission, args.task2a_submission)
    schema_guard = {"status": "PASS", "before": schema_before, "after": schema_after,
                    "schemas_unchanged": schema_before == schema_after}
    write_json_atomic(report_dir / "official_schema_guard.json", schema_guard)
    write_json_atomic(report_dir / "frozen_hash_audit.json",
                      {"status": "PASS", "before": before, "after": after, "all_unchanged": before == after})
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_text = _summary_markdown(service_summary, forecast_summary, coverage)
    args.summary_output.write_text(summary_text, encoding="utf-8")
    (report_dir / "phase27_uncertainty_report.md").write_text(summary_text, encoding="utf-8")
    manifest = {
        "phase": 27, "status": "PASS", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "task1_final_config_sha256": sha256_file(args.task1_final_config),
        "task1_submission_sha256": sha256_file(args.task1_submission),
        "task2a_final_config_sha256": sha256_file(args.task2a_final_config),
        "task2a_submission_sha256": sha256_file(args.task2a_submission),
        "uncertainty_config_sha256": sha256_file(args.uncertainty_config),
        "service_residual_provenance": "deterministic_replay_phase07_phase09_frozen_oos",
        "service_residual_count": int(len(service_oos)),
        "task2a_residual_provenance": "phase16_frozen_champion_rolling_oos_with_phase17_postprocessing",
        "task2a_fold_origin_count": int(task2_oos["total"].origin_week_start_date.nunique()),
        "coverage_levels": list(levels), "quantile_method": "finite_sample_higher",
        "horizon_grouping": "target+horizon", "fallback_policy": "pooled_target",
        "library_versions": _versions(), "git_commit": _git_commit(), "private_row_values_in_manifest": False,
    }
    write_json_atomic(report_dir / "run_manifest.json", manifest)
    print("LOCAL PHASE 27 UNCERTAINTY BUILD: PASS")
    print("TASK1 SERVICE OOS RESIDUAL SOURCE: PASS")
    print("TASK2A ROLLING OOS RESIDUAL SOURCE: PASS")
    print("OFFICIAL SCHEMA AND HASH GUARD: PASS")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
