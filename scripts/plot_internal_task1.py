r"""Human-local Task 1 charts. Never run this through an AI agent.

Run from repository root:
  .\.venv\Scripts\python.exe scripts\plot_internal_task1.py
Optional paired validation export (NOT currently a known repository artifact):
  ... scripts\plot_internal_task1.py --pairs reports/private/<pairs>.csv \
      --pairs-manifest reports/private/<pairs>.json

The optional CSV must contain delivery_id, service_minutes, pred_service_min;
its JSON must contain sha256, row_count, candidate_id,
scope="full_matched_chronological_validation", validation_ids_path and
validation_ids_sha256. The separate private validation-ID CSV must be derived
from the authoritative frozen split and contain delivery_id. An error-only or
partial prediction export cannot pass the exact ID-set check. Do not upload.

Other sources: configs/task1_final_models.yaml, configs/task1_explainability.yaml,
reports/private/phase09_task1_models/calibration_curve.csv, and Phase 25
run_manifest.json plus service_shap_global.csv and late_shap_global.csv.

Outputs (never public): reports/private/internal_results_charts/
  task1_service_actual_vs_predicted.png (only with a full matched export)
  task1_lateness_calibration_oof_eval.png
  task1_service_global_shap.png
  task1_lateness_global_shap.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from internal_charts_common import (
    ACCENT, BLUE, ChartEvidenceError, ROOT, canvas, columns, csv_source,
    json_source, numeric, private_path, save, sha256, skip, yaml_source,
)


def _frozen() -> dict:
    config = yaml_source("configs/task1_final_models.yaml")
    if (config.get("validation_contract", {}).get("development_selection_complete") is not True
            or config.get("service_model", {}).get("config_id") != "catboost_regression_default"
            or config.get("lateness_model", {}).get("config_id") != "catboost_classifier_default"
            or config.get("lateness_model", {}).get("calibration", {}).get("method") != "raw"):
        raise ChartEvidenceError("Frozen Task 1 selection/calibration metadata differs.")
    return config


def service_pairs(csv_path: Path, manifest_path: Path, config: dict) -> None:
    csv_path, manifest_path = private_path(csv_path), private_path(manifest_path)
    if not csv_path.is_file() or not manifest_path.is_file():
        raise ChartEvidenceError("Optional full paired-validation evidence is missing.")
    manifest = json_source(str(manifest_path.relative_to(ROOT)), private=True)
    reference_relative = manifest.get("validation_ids_path")
    if not isinstance(reference_relative, str):
        raise ChartEvidenceError("Independent frozen validation-ID reference is missing.")
    reference_path = private_path(ROOT / reference_relative)
    if not reference_path.is_file() or reference_path in (csv_path, manifest_path):
        raise ChartEvidenceError("Independent frozen validation-ID reference is unavailable.")
    if (manifest.get("scope") != "full_matched_chronological_validation"
            or manifest.get("candidate_id") != config["service_model"]["config_id"]
            or manifest.get("sha256") != sha256(csv_path)
            or manifest.get("validation_ids_sha256") != sha256(reference_path)):
        raise ChartEvidenceError("Paired-validation provenance does not match the frozen model.")
    pairs = csv_source(str(csv_path.relative_to(ROOT)), private=True)
    ids = csv_source(str(reference_path.relative_to(ROOT)), private=True)
    columns(pairs, ("delivery_id", "service_minutes", "pred_service_min"))
    columns(ids, ("delivery_id",))
    if (len(pairs) != manifest.get("row_count") or pairs["delivery_id"].isna().any()
            or pairs["delivery_id"].duplicated().any()
            or ids["delivery_id"].isna().any() or ids["delivery_id"].duplicated().any()
            or set(pairs["delivery_id"].astype(str)) != set(ids["delivery_id"].astype(str))):
        raise ChartEvidenceError("Paired-validation coverage or unique IDs fail.")
    actual = numeric(pairs, "service_minutes", nonnegative=True)
    predicted = numeric(pairs, "pred_service_min")
    fig, ax = canvas("Task 1 · actual vs predicted service time",
                     "Full matched chronological validation · frozen CatBoost service candidate",
                     "Predicted service time (minutes)")
    ax.scatter(actual, predicted, s=12, alpha=0.35, color=BLUE, edgecolors="none")
    low = min(float(actual.min()), float(predicted.min()))
    high = max(float(actual.max()), float(predicted.max()))
    ax.plot([low, high], [low, high], color=ACCENT, linewidth=2, label="Perfect agreement")
    ax.set_xlabel("Actual service time (minutes)")
    ax.legend(frameon=False)
    save(fig, "task1_service_actual_vs_predicted.png")


def calibration() -> None:
    curve = csv_source("reports/private/phase09_task1_models/calibration_curve.csv", private=True)
    columns(curve, ("bin", "n", "mean_predicted_probability", "observed_late_rate", "absolute_gap"))
    bins = numeric(curve, "bin")
    n = numeric(curve, "n")
    expected = numeric(curve, "mean_predicted_probability")
    observed = numeric(curve, "observed_late_rate")
    gaps = numeric(curve, "absolute_gap")
    if (len(curve) > 10 or not np.array_equal(bins.to_numpy(), np.arange(len(curve)))
            or (n <= 0).any() or not np.equal(n, np.floor(n)).all()
            or (expected > 1).any() or (expected < 0).any()
            or (observed > 1).any() or (observed < 0).any()
            or not np.allclose(gaps, abs(expected - observed), atol=1e-10)):
        raise ChartEvidenceError("Raw Phase 09 calibration bins are invalid.")
    fig, ax = canvas("Task 1 · lateness calibration",
                     "Phase 09 chronological OOF calibration-evaluation subset · raw CatBoost classifier; not final holdout/test",
                     "Observed late rate")
    ax.plot([0, 1], [0, 1], color=ACCENT, linewidth=2, label="Perfect calibration")
    ax.scatter(expected, observed, s=70, color=BLUE, label="Recorded quantile bins")
    ax.set(xlabel="Mean predicted lateness probability", xlim=(0, 1), ylim=(0, 1))
    ax.legend(frameon=False)
    save(fig, "task1_lateness_calibration_oof_eval.png")


def shap_charts() -> None:
    config = yaml_source("configs/task1_explainability.yaml")
    manifest = json_source("reports/private/phase25_task1_explainability/run_manifest.json", private=True)
    population = manifest.get("explanation_population", {})
    if (config.get("population", {}).get("source") != "task1_test_features"
            or manifest.get("status") != "PASS"
            or population.get("source") != "task1_test_features"
            or not isinstance(population.get("sample_size"), int)
            or population["sample_size"] <= 0):
        raise ChartEvidenceError("SHAP inference-population provenance is not established.")
    for model, filename, manifest_key in (
        ("service", "task1_service_global_shap.png", "service_shap"),
        ("lateness", "task1_lateness_global_shap.png", "late_shap"),
    ):
        meta = manifest.get(manifest_key, {})
        if not isinstance(meta.get("output_space"), str) or not meta["output_space"].strip():
            skip(filename, "SHAP model-output unit metadata is missing")
            continue
        table = csv_source(f"reports/private/phase25_task1_explainability/{'service' if model == 'service' else 'late'}_shap_global.csv", private=True)
        columns(table, ("feature_name", "mean_abs_shap", "rank", "sample_count"))
        values = numeric(table, "mean_abs_shap", nonnegative=True)
        ranks = numeric(table, "rank")
        samples = numeric(table, "sample_count")
        if (table.feature_name.isna().any() or table.feature_name.duplicated().any()
                or not np.array_equal(ranks.to_numpy(), np.arange(1, len(table) + 1))
                or not samples.eq(population["sample_size"]).all()
                or not values.is_monotonic_decreasing):
            skip(filename, "SHAP summary does not match its recorded sample")
            continue
        top = table.head(15).iloc[::-1]
        fig, ax = canvas(f"Task 1 · global {model} SHAP importance",
                         "Phase 25 deterministic Task 1 inference-feature sample · association, not causation",
                         "Feature")
        ax.barh(top.feature_name.astype(str), top.mean_abs_shap.astype(float), color=BLUE)
        ax.set_xlabel(f"Mean |SHAP| ({meta['output_space']} model-output units)")
        save(fig, filename)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=Path, help="Optional PRIVATE full matched validation CSV")
    parser.add_argument("--pairs-manifest", type=Path, help="Matching PRIVATE provenance JSON")
    args = parser.parse_args()
    try:
        config = _frozen()
    except (ChartEvidenceError, KeyError):
        print("SKIPPED: all Task 1 charts — frozen selection evidence is inconsistent")
        return 1
    if bool(args.pairs) != bool(args.pairs_manifest):
        skip("task1_service_actual_vs_predicted.png", "both optional paired sources are required")
    elif args.pairs:
        try:
            service_pairs(args.pairs, args.pairs_manifest, config)
        except (ChartEvidenceError, KeyError, ValueError):
            skip("task1_service_actual_vs_predicted.png", "full matched validation evidence failed validation")
    else:
        skip("task1_service_actual_vs_predicted.png", "no full matched validation export was located")
    for job, name in ((calibration, "task1_lateness_calibration_oof_eval.png"),
                      (shap_charts, "Task 1 SHAP charts")):
        try:
            job()
        except (ChartEvidenceError, KeyError, ValueError):
            skip(name, "required private evidence is missing or inconsistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
