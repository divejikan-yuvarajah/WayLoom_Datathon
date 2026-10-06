"""Build private Phase 25 explanations for the frozen Task 1 models."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_inventory import load_manifest  # noqa: E402
from src.task1.causal_language import require_causal_language_pass  # noqa: E402
from src.task1.explainability import (  # noqa: E402
    NONCAUSAL_DISCLAIMER,
    assert_hashes_unchanged,
    assert_prediction_parity,
    audit_explanation_schema,
    build_explanation_registry,
    build_feature_importance,
    deterministic_sample_positions,
    frozen_artifact_paths,
    hash_artifacts,
    lateness_probability_bridge,
    local_contributors,
    prepare_frozen_model_frame,
    select_late_example,
    select_service_example,
    service_prediction_bridge,
    summarize_shap,
)
from src.task1.explanation_reporting import (  # noqa: E402
    atomic_write_csv,
    atomic_write_json,
    atomic_write_text,
    build_business_drivers,
    plot_importance,
    plot_local_waterfall,
    plot_shap_bar,
    plot_shap_distribution,
    render_private_report,
    render_public_summary,
)
from src.task1.final_train import (  # noqa: E402
    feature_schema_hash,
    load_frozen_final_config,
    load_model_bundle,
    load_yaml,
    resolve_feature_columns,
    resolve_negative_service_policy,
)
from src.task1.inference import (  # noqa: E402
    OFFICIAL_ROW_ORDER,
    assert_no_forbidden_inference_features,
    prepare_test_features_from_raw,
    run_saved_model_inference,
)
from src.task1.shap_adapter import explain_model  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--final-model-config", required=True, type=Path)
    parser.add_argument("--explainability-config", required=True, type=Path)
    parser.add_argument("--service-model-dir", required=True, type=Path)
    parser.add_argument("--late-model-dir", required=True, type=Path)
    parser.add_argument("--submission", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    return parser.parse_args()


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL, text=True,
        ).strip() or None
    except Exception:
        return None


def _versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("python", "numpy", "pandas", "catboost", "lightgbm", "shap", "matplotlib"):
        if name == "python":
            versions[name] = sys.version.split()[0]
            continue
        try:
            module = __import__(name)
            versions[name] = str(getattr(module, "__version__", "unknown"))
        except Exception:
            versions[name] = "not_installed"
    return versions


def _verify_schema_hash(bundle: dict[str, Any], label: str) -> str:
    actual = feature_schema_hash(bundle["schema"])
    recorded = str((bundle.get("metadata") or {}).get("feature_schema_hash") or "")
    if not recorded or actual != recorded:
        raise ValueError(f"{label} feature-schema hash does not match saved metadata.")
    return actual


def _required_config(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("version") != 1:
        raise ValueError("Phase 25 explainability config version must be 1.")
    if bool((config.get("privacy") or {}).get("external_api_allowed", False)):
        raise ValueError("External APIs are forbidden for Task 1 explainability.")
    return config


def main() -> int:
    args = parse_args()
    load_manifest(args.manifest)
    explain_config = _required_config(load_yaml(args.explainability_config))
    final_config = load_frozen_final_config(args.final_model_config)
    if not args.submission.is_file() or args.submission.name != "submission_task1.csv":
        raise ValueError("The validated official submission_task1.csv is required.")

    frozen_paths = frozen_artifact_paths(
        args.final_model_config, args.service_model_dir, args.late_model_dir, args.submission
    )
    before_hashes = hash_artifacts(frozen_paths, root=PROJECT_ROOT)

    service_bundle = load_model_bundle(args.service_model_dir)
    late_method = str(((final_config.get("lateness_model") or {}).get("calibration") or {}).get("method") or "raw").lower()
    late_bundle = load_model_bundle(
        args.late_model_dir,
        require_calibration=late_method not in {"raw", "none", "null", ""},
    )
    service_schema_hash = _verify_schema_hash(service_bundle, "Service")
    late_schema_hash = _verify_schema_hash(late_bundle, "Lateness")

    feature_pipeline = explain_config.get("feature_pipeline") or {}
    feature_config_path = Path(feature_pipeline.get(
        "config", "configs/task1_features.yaml"
    ))
    frozen_test_features = Path(feature_pipeline.get(
        "frozen_test_features", "data/interim/task1_features_test.csv"
    ))
    prefer_materialized = bool(feature_pipeline.get("prefer_frozen_materialized_features", True))
    if prefer_materialized and frozen_test_features.is_file():
        # This is the materialized output of the canonical Phase 06 pipeline,
        # not a separate explainability transformation.  Using it avoids
        # rebuilding the full chronological training-history state and is
        # validated below against both the saved schema and frozen predictions.
        X_test = pd.read_csv(frozen_test_features, low_memory=False)
        _trace = None
        population_source = "frozen_phase06_materialized_task1_test_features"
    else:
        X_test, _trace = prepare_test_features_from_raw(args.raw_root, feature_config_path)
        population_source = "canonical_phase06_rebuild_task1_test_features"
    assert_no_forbidden_inference_features(list(X_test.columns))
    schema_columns = list(service_bundle["schema"]["feature_columns"])
    profile = str(service_bundle["schema"].get("feature_profile") or "safe_core_plus_history")
    # Phase 10 inference selects/reorders columns from the saved schema.  The
    # canonical builder may carry an identifier or present otherwise eligible
    # columns in a different order after joins; neither is a model input.  Fail
    # only when a frozen model feature is no longer available/eligible, then
    # construct the explanation frame in the exact saved order below.
    eligible_columns = resolve_feature_columns(X_test, profile)
    missing_frozen = [name for name in schema_columns if name not in eligible_columns]
    if missing_frozen:
        raise ValueError(
            "Canonical inference features are missing frozen model columns: "
            + ", ".join(missing_frozen)
        )
    registry = build_explanation_registry(
        schema_columns,
        categorical_columns=list(service_bundle["schema"].get("categorical_columns") or []),
    )
    leakage_audit = audit_explanation_schema(service_bundle["schema"], late_bundle["schema"], registry)

    service_frame = prepare_frozen_model_frame(service_bundle, X_test)
    late_frame = prepare_frozen_model_frame(late_bundle, X_test)
    if list(service_frame.columns) != schema_columns:
        raise ValueError("Service explanation frame does not preserve the exact frozen schema order.")
    if list(service_frame.columns) != list(late_frame.columns):
        raise ValueError("Frozen service and lateness explanation frames differ.")

    predictions = run_saved_model_inference(
        X_test,
        args.service_model_dir,
        args.late_model_dir,
        final_config,
        load_yaml(Path((explain_config.get("feature_pipeline") or {}).get(
            "inference_config", "configs/task1_inference.yaml"
        ))),
    )
    submission = pd.read_csv(args.submission)
    expected_columns = ["delivery_id", "pred_service_min", "pred_late_prob"]
    if list(submission.columns) != expected_columns or len(submission) != len(predictions):
        raise ValueError("Task 1 submission schema/row count differs from frozen inference output.")
    actual_ids = submission["delivery_id"].astype("string").reset_index(drop=True)
    if actual_ids.isna().any() or actual_ids.str.strip().eq("").any() or actual_ids.duplicated().any():
        raise ValueError("Task 1 submission identifiers must remain complete and unique.")
    if _trace is not None:
        expected_ids = _trace.sort_values(OFFICIAL_ROW_ORDER, kind="stable")["delivery_id"].astype("string").reset_index(drop=True)
        if not actual_ids.equals(expected_ids):
            raise ValueError("Task 1 submission identity/order differs from the canonical inference population.")
    assert_prediction_parity(submission["pred_service_min"], predictions["pred_service_min"], label="Service")
    assert_prediction_parity(submission["pred_late_prob"], predictions["pred_late_prob"], label="Lateness")

    population = explain_config.get("population") or {}
    max_rows = int(population.get("max_rows", 2000))
    minimum = int(population.get("min_rows_if_available", 200))
    seed = int(population.get("random_seed", 42))
    if len(service_frame) >= minimum and max_rows < minimum:
        raise ValueError("Configured SHAP maximum is below the required minimum sample size.")
    sample_positions = deterministic_sample_positions(service_frame, max_rows=max_rows, seed=seed)
    service_sample = service_frame.iloc[sample_positions].reset_index(drop=True)
    late_sample = late_frame.iloc[sample_positions].reset_index(drop=True)

    tolerance = float((explain_config.get("shap") or {}).get("reconstruction_tolerance", 1e-6))
    service_family = str(service_bundle["metadata"]["model_family"])
    late_family = str(late_bundle["metadata"]["model_family"])
    positive_index = int(late_bundle["metadata"]["positive_class_index"])
    service_shap_result = explain_model(
        service_bundle["model"], service_sample, family=service_family, task="service",
        categorical_columns=list(service_bundle["schema"].get("categorical_columns") or []),
        tolerance=tolerance,
    )
    late_shap_result = explain_model(
        late_bundle["model"], late_sample, family=late_family, task="lateness",
        categorical_columns=list(late_bundle["schema"].get("categorical_columns") or []),
        positive_class_index=positive_index, tolerance=tolerance,
    )
    service_shap = summarize_shap(service_shap_result, schema_columns, registry)
    late_shap = summarize_shap(late_shap_result, schema_columns, registry)
    service_importance = build_feature_importance(
        service_bundle["model"], family=service_family, feature_names=schema_columns,
        registry=registry, shap_summary=service_shap,
    )
    late_importance = build_feature_importance(
        late_bundle["model"], family=late_family, feature_names=schema_columns,
        registry=registry, shap_summary=late_shap,
    )

    service_policy = resolve_negative_service_policy(
        final_config,
        load_yaml(Path((explain_config.get("feature_pipeline") or {}).get(
            "inference_config", "configs/task1_inference.yaml"
        ))),
    )
    sample_service_final, service_post_report = service_prediction_bridge(
        service_shap_result.raw_predictions, service_policy
    )
    service_bridge_error = assert_prediction_parity(
        predictions.iloc[sample_positions]["pred_service_min"], sample_service_final,
        label="Service post-processing bridge", tolerance=tolerance,
    )
    late_bridge = lateness_probability_bridge(late_bundle, late_sample)
    late_bridge_error = assert_prediction_parity(
        predictions.iloc[sample_positions]["pred_late_prob"], late_bridge["final_probability"],
        label="Lateness calibration bridge", tolerance=tolerance,
    )

    service_position = select_service_example(predictions["pred_service_min"].to_numpy())
    late_position = select_late_example(predictions["pred_late_prob"].to_numpy())
    service_local_frame = service_frame.iloc[[service_position]].reset_index(drop=True)
    late_local_frame = late_frame.iloc[[late_position]].reset_index(drop=True)
    service_local_shap = explain_model(
        service_bundle["model"], service_local_frame, family=service_family, task="service",
        categorical_columns=list(service_bundle["schema"].get("categorical_columns") or []),
        tolerance=tolerance,
    )
    late_local_shap = explain_model(
        late_bundle["model"], late_local_frame, family=late_family, task="lateness",
        categorical_columns=list(late_bundle["schema"].get("categorical_columns") or []),
        positive_class_index=positive_index, tolerance=tolerance,
    )
    local_cfg = explain_config.get("local") or {}
    top_positive = int(local_cfg.get("top_positive", 8))
    top_negative = int(local_cfg.get("top_negative", 8))
    service_local_final, service_local_post = service_prediction_bridge(service_local_shap.raw_predictions, service_policy)
    late_local_bridge = lateness_probability_bridge(late_bundle, late_local_frame)
    assert_prediction_parity(
        np.asarray([predictions.iloc[service_position]["pred_service_min"]]), service_local_final,
        label="Local service explanation bridge", tolerance=tolerance,
    )
    assert_prediction_parity(
        np.asarray([predictions.iloc[late_position]["pred_late_prob"]]),
        late_local_bridge["final_probability"],
        label="Local lateness explanation bridge", tolerance=tolerance,
    )
    service_local = {
        "example_label": "SERVICE_EXAMPLE_A",
        "raw_model_prediction": float(service_local_shap.raw_predictions[0]),
        "final_pred_service_min": float(service_local_final[0]),
        "postprocessing_policy": service_local_post["postprocessing_policy"],
        "expected_value": float(service_local_shap.base_values[0]),
        "shap_output_space": service_local_shap.output_space,
        "shap_reconstruction_error": service_local_shap.max_abs_reconstruction_error,
        "shap_reconstruction_pass": service_local_shap.reconstruction_pass,
        **local_contributors(service_local_shap, service_local_frame, row_position=0, registry=registry,
                             top_positive=top_positive, top_negative=top_negative),
        "interpretation_note": "Contributors move this model prediction relative to its baseline; they are not causal effects.",
        "noncausal_disclaimer": NONCAUSAL_DISCLAIMER,
    }
    late_local = {
        "example_label": "LATE_EXAMPLE_A",
        "base_raw_classifier_score": float(late_local_shap.raw_predictions[0]),
        "base_probability": float(late_local_bridge["base_probability"][0]),
        "final_pred_late_prob": float(late_local_bridge["final_probability"][0]),
        "calibration_method": late_local_bridge["calibration_method"],
        "expected_value": float(late_local_shap.base_values[0]),
        "shap_output_space": late_local_shap.output_space,
        "probability_point_interpretation_allowed": late_local_shap.output_space == "base_probability",
        "shap_reconstruction_error": late_local_shap.max_abs_reconstruction_error,
        "shap_reconstruction_pass": late_local_shap.reconstruction_pass,
        **local_contributors(late_local_shap, late_local_frame, row_position=0, registry=registry,
                             top_positive=top_positive, top_negative=top_negative),
        "interpretation_note": "SHAP explains the base classifier score; calibration separately maps its probability to the submitted probability.",
        "noncausal_disclaimer": NONCAUSAL_DISCLAIMER,
    }

    driver_top = int((explain_config.get("business_drivers") or {}).get("top_n_per_model", 10))
    drivers = {
        "definition": "driver means model driver or predictive association, not causal driver",
        "service": build_business_drivers("service", service_importance, service_shap, top_n=driver_top),
        "lateness": build_business_drivers("lateness", late_importance, late_shap, top_n=driver_top),
        "correlated_feature_caution": (
            "Attribution can be shared among correlated or redundant features; rank does not establish actionability."
        ),
        "noncausal_disclaimer": NONCAUSAL_DISCLAIMER,
    }

    manifest_record = {
        "phase": 25,
        "status": "PASS",
        "service_model": {"family": service_family, "config_id": service_bundle["metadata"]["config_id"]},
        "late_model": {"family": late_family, "config_id": late_bundle["metadata"]["config_id"]},
        "calibration_method": late_bridge["calibration_method"],
        "service_postprocessing_policy": service_policy,
        "positive_class": 1,
        "service_feature_schema_hash": service_schema_hash,
        "late_feature_schema_hash": late_schema_hash,
        "frozen_artifact_hashes": before_hashes,
        "submission_task1_sha256": before_hashes[
            args.submission.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
        ],
        "explanation_population": {
            "source": population_source,
            "population_row_count": int(len(service_frame)),
            "sample_size": int(len(sample_positions)),
            "sample_selection_rule": "stable_dataframe_hash_then_original_position",
            "random_seed": seed,
        },
        "service_importance_method": str(service_importance.iloc[0]["importance_type"]),
        "late_importance_method": str(late_importance.iloc[0]["importance_type"]),
        "service_shap": {"method": service_shap_result.method, "output_space": service_shap_result.output_space},
        "late_shap": {"method": late_shap_result.method, "output_space": late_shap_result.output_space},
        "library_versions": _versions(),
        "git_commit": _git_commit(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "external_api_used": False,
        "row_identifiers_recorded": False,
    }
    reconstruction = {
        "status": "PASS",
        "service": {
            "method": service_shap_result.method,
            "output_space": service_shap_result.output_space,
            "rows_checked": len(service_sample),
            "max_abs_reconstruction_error": service_shap_result.max_abs_reconstruction_error,
            "tolerance": tolerance,
            "pass": True,
            "postprocessing_policy": service_post_report["postprocessing_policy"],
            "postprocessing_bridge_max_abs_error": service_bridge_error,
            "postprocessing_bridge_pass": True,
        },
        "late": {
            "method": late_shap_result.method,
            "output_space": late_shap_result.output_space,
            "positive_class": 1,
            "rows_checked": len(late_sample),
            "max_abs_reconstruction_error": late_shap_result.max_abs_reconstruction_error,
            "tolerance": tolerance,
            "base_output_pass": True,
            "calibration_method": late_bridge["calibration_method"],
            "calibration_bridge_max_abs_error": late_bridge_error,
            "calibration_bridge_pass": True,
        },
    }

    summary = render_public_summary(
        service_metadata=service_bundle["metadata"], late_metadata=late_bundle["metadata"],
        service_shap=service_shap, late_shap=late_shap,
        service_local=service_local, late_local=late_local, sample_size=len(sample_positions),
    )
    private_report = render_private_report(
        manifest=manifest_record, service_importance=service_importance,
        late_importance=late_importance, service_shap=service_shap, late_shap=late_shap,
    )
    causal_audit = require_causal_language_pass({
        "task1_explainability.md": summary,
        "phase25_explainability_report.md": private_report,
    })

    report_dir = args.report_dir
    figures = report_dir / "figures"
    report_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_csv(report_dir / "service_feature_importance.csv", service_importance)
    atomic_write_csv(report_dir / "late_feature_importance.csv", late_importance)
    atomic_write_csv(report_dir / "service_shap_global.csv", service_shap)
    atomic_write_csv(report_dir / "late_shap_global.csv", late_shap)
    atomic_write_json(report_dir / "service_local_explanation.json", service_local)
    atomic_write_json(report_dir / "late_local_explanation.json", late_local)
    atomic_write_json(report_dir / "business_drivers.json", drivers)
    atomic_write_json(report_dir / "shap_reconstruction_audit.json", reconstruction)
    atomic_write_json(report_dir / "feature_leakage_audit.json", leakage_audit)
    atomic_write_json(report_dir / "causal_language_audit.json", causal_audit)
    atomic_write_json(report_dir / "run_manifest.json", manifest_record)
    atomic_write_text(report_dir / "phase25_explainability_report.md", private_report)
    atomic_write_text(args.summary_output, summary)

    top_n = int((explain_config.get("importance") or {}).get("top_n", 20))
    plot_importance(service_importance, figures / "service_feature_importance.png",
                    title="Service model feature importance", top_n=top_n)
    plot_importance(late_importance, figures / "late_feature_importance.png",
                    title="Lateness base-classifier feature importance", top_n=top_n)
    plot_shap_bar(service_shap, figures / "service_shap_bar.png",
                  title="Service model global SHAP", top_n=top_n)
    plot_shap_distribution(service_shap_result.values, schema_columns, service_shap,
                           figures / "service_shap_distribution.png",
                           title="Service model SHAP distribution", top_n=top_n, seed=seed)
    plot_shap_bar(late_shap, figures / "late_shap_bar.png",
                  title=f"Lateness SHAP ({late_shap_result.output_space})", top_n=top_n)
    plot_shap_distribution(late_shap_result.values, schema_columns, late_shap,
                           figures / "late_shap_distribution.png",
                           title=f"Lateness SHAP distribution ({late_shap_result.output_space})",
                           top_n=top_n, seed=seed)
    plot_local_waterfall(service_local, figures / "service_local_waterfall.png",
                         title="SERVICE_EXAMPLE_A model contributions")
    plot_local_waterfall(late_local, figures / "late_local_waterfall.png",
                         title=f"LATE_EXAMPLE_A contributions ({late_local_shap.output_space})")

    after_hashes = hash_artifacts(frozen_paths, root=PROJECT_ROOT)
    assert_hashes_unchanged(before_hashes, after_hashes)
    hash_audit = {
        "status": "PASS",
        "before": before_hashes,
        "after": after_hashes,
        "all_unchanged": True,
    }
    atomic_write_json(report_dir / "frozen_artifact_hash_audit.json", hash_audit)

    print("WAYLOOM - PHASE 25 TASK 1 EXPLAINABILITY")
    print("FROZEN MODEL CONFIG: PASS")
    print("FEATURE SCHEMA PARITY: PASS")
    print("FEATURE LEAKAGE AUDIT: PASS")
    print("SERVICE FEATURE IMPORTANCE: PASS")
    print("LATENESS FEATURE IMPORTANCE: PASS")
    print("GLOBAL SHAP - SERVICE: PASS")
    print("GLOBAL SHAP - LATENESS: PASS")
    print("SERVICE SHAP RECONSTRUCTION: PASS")
    print("LATENESS SHAP RECONSTRUCTION: PASS")
    print("SERVICE POSTPROCESSING BRIDGE: PASS")
    print("LATENESS CALIBRATION BRIDGE: PASS")
    print("CAUSAL-LANGUAGE AUDIT: PASS")
    print("FROZEN MODEL HASHES UNCHANGED: PASS")
    print("submission_task1.csv UNCHANGED: PASS")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    print("PHASE 25: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
