"""Validate private Phase 27 artifacts without rebuilding calibration models."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.uncertainty.coverage import validate_coverage_language
from src.uncertainty.quantiles import validate_coverage_levels
from src.uncertainty.reporting import (assert_points_unchanged, guard_official_schema, hash_artifacts,
    require_private_path, sha256_file)
from src.uncertainty.residual_sources import load_yaml


class Phase27ValidationError(ValueError):
    """Phase 27 evidence is incomplete or inconsistent."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate completed private Phase 27 uncertainty evidence.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--task1-final-config", required=True, type=Path)
    parser.add_argument("--task1-submission", required=True, type=Path)
    parser.add_argument("--task2a-final-config", required=True, type=Path)
    parser.add_argument("--task2a-submission", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase27ValidationError(f"Expected JSON object: {path.name}")
    return value


def main() -> int:
    args = parse_args()
    config = load_yaml(args.config)
    levels = validate_coverage_levels(config.get("coverage_levels", []))
    if config.get("quantile") != {"method": "finite_sample_higher", "require_oos_residuals": True}:
        raise Phase27ValidationError("Quantile/OOS configuration is invalid.")
    report_dir = require_private_path(args.report_dir, repository_root=ROOT)
    required = ["run_manifest.json", "task1_service_residual_calibration.json",
        "task1_service_uncertainty.csv", "task1_service_uncertainty_summary.json",
        "task2a_total_residual_calibration.csv", "task2a_chilled_residual_calibration.csv",
        "task2a_forecast_uncertainty.csv", "task2a_uncertainty_summary.json",
        "coverage_diagnostics.json", "fallback_diagnostics.json", "official_schema_guard.json",
        "frozen_hash_audit.json", "phase27_uncertainty_report.md"]
    missing = [name for name in required if not (report_dir / name).is_file()]
    if missing:
        raise Phase27ValidationError("Phase 27 evidence is incomplete: " + ", ".join(missing))
    task1 = pd.read_csv(args.task1_submission, dtype={
        "delivery_id": "string", "pred_service_min": "string", "pred_late_prob": "string"
    }, keep_default_na=False)
    task2a = pd.read_csv(args.task2a_submission, dtype={
        "row_id": "string", "pred_total_volume_m3": "string", "pred_chilled_volume_m3": "string"
    }, keep_default_na=False)
    guard_official_schema(task1, "task1")
    guard_official_schema(task2a, "task2a")
    service = pd.read_csv(report_dir / "task1_service_uncertainty.csv", dtype={
        "delivery_id": "string", "pred_service_min": "string"
    }, keep_default_na=False)
    forecast = pd.read_csv(report_dir / "task2a_forecast_uncertainty.csv", dtype={
        "row_id": "string", "pred_total_volume_m3": "string", "pred_chilled_volume_m3": "string"
    }, keep_default_na=False)
    assert_points_unchanged(service, task1, task="task1")
    assert_points_unchanged(forecast, task2a, task="task2a")
    service_point = pd.to_numeric(service.pred_service_min, errors="raise")
    total_point = pd.to_numeric(forecast.pred_total_volume_m3, errors="raise")
    for level in levels:
        suffix = int(level * 100)
        low, high = f"service_lower_{suffix}", f"service_upper_{suffix}"
        if not {low, high, f"service_width_{suffix}"}.issubset(service.columns):
            raise Phase27ValidationError("Service interval columns are incomplete.")
        if (service[low] < 0).any() or (service[low] > service_point).any() or (service[high] < service_point).any():
            raise Phase27ValidationError("Service interval invariant failed.")
        required_forecast = {f"total_lower_{suffix}", f"total_upper_{suffix}",
            f"chilled_lower_{suffix}_raw", f"chilled_upper_{suffix}_raw",
            f"chilled_lower_{suffix}", f"chilled_upper_{suffix}"}
        if required_forecast.difference(forecast.columns):
            raise Phase27ValidationError("Forecast interval columns are incomplete.")
        if (forecast[f"total_lower_{suffix}"] < 0).any() or (forecast[f"total_lower_{suffix}"] > total_point).any() or (forecast[f"total_upper_{suffix}"] < total_point).any():
            raise Phase27ValidationError("Total interval invariant failed.")
        structural = forecast.brand.isin(config["task2a"]["chilled_zero_brands"])
        chilled_cols = [f"chilled_lower_{suffix}_raw", f"chilled_upper_{suffix}_raw",
                        f"chilled_lower_{suffix}", f"chilled_upper_{suffix}"]
        if not forecast.loc[structural, chilled_cols].eq(0.0).all().all():
            raise Phase27ValidationError("Style/Tech chilled intervals are not [0,0].")
        if (forecast[f"chilled_upper_{suffix}"] > forecast[f"total_upper_{suffix}"]).any():
            raise Phase27ValidationError("Coherent chilled interval exceeds total interval.")
    manifest = _load_json(report_dir / "run_manifest.json")
    if (manifest.get("phase") != 27 or manifest.get("status") != "PASS"
            or manifest.get("service_residual_count", 0) < config["task1_service"]["min_global_residuals"]
            or manifest.get("task2a_fold_origin_count", 0) < 1
            or manifest.get("quantile_method") != "finite_sample_higher"
            or manifest.get("private_row_values_in_manifest") is not False):
        raise Phase27ValidationError("Run manifest does not prove valid OOS uncertainty calibration.")
    expected_hashes = {
        "task1_final_config_sha256": sha256_file(args.task1_final_config),
        "task1_submission_sha256": sha256_file(args.task1_submission),
        "task2a_final_config_sha256": sha256_file(args.task2a_final_config),
        "task2a_submission_sha256": sha256_file(args.task2a_submission),
        "uncertainty_config_sha256": sha256_file(args.config),
    }
    if any(manifest.get(key) != value for key, value in expected_hashes.items()):
        raise Phase27ValidationError("Current frozen config/submission hash differs from the Phase 27 run.")
    audit = _load_json(report_dir / "frozen_hash_audit.json")
    if audit.get("status") != "PASS" or audit.get("all_unchanged") is not True or audit.get("before") != audit.get("after"):
        raise Phase27ValidationError("Frozen hash audit did not pass.")
    current = hash_artifacts([Path(path) for path in audit["after"]])
    if current != audit["after"]:
        raise Phase27ValidationError("A frozen artifact changed after the Phase 27 build.")
    schema = _load_json(report_dir / "official_schema_guard.json")
    if schema.get("status") != "PASS" or schema.get("schemas_unchanged") is not True or schema.get("before") != schema.get("after"):
        raise Phase27ValidationError("Official schema/hash evidence did not pass.")
    summary_text = args.summary.read_text(encoding="utf-8")
    validate_coverage_language(summary_text)
    phase28 = [path for root in (ROOT / "src", ROOT / "scripts", ROOT / "configs", ROOT / "tests")
               for path in root.rglob("*") if "phase28" in path.name.lower() or "phase_28" in path.name.lower()]
    if phase28:
        raise Phase27ValidationError("Phase 28 implementation exists before the Phase 27 gate.")
    if not np.isfinite(service.select_dtypes(include="number").to_numpy()).all() or not np.isfinite(forecast.select_dtypes(include="number").to_numpy()).all():
        raise Phase27ValidationError("Private uncertainty artifact contains nonfinite numeric values.")
    print("LOCAL PHASE 27 UNCERTAINTY VALIDATION: PASS")
    print("TASK1 SERVICE UNCERTAINTY: PASS")
    print("TASK2A HORIZON UNCERTAINTY: PASS")
    print("STYLE/TECH CHILLED [0,0]: PASS")
    print("POINT PREDICTIONS AND OFFICIAL HASHES: PASS")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
