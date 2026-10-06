"""Validate locally generated Phase 25 Task 1 explainability evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.causal_language import require_causal_language_pass  # noqa: E402
from src.task1.explainability import (  # noqa: E402
    audit_explanation_schema,
    build_explanation_registry,
    frozen_artifact_paths,
    hash_artifacts,
)
from src.task1.explanation_reporting import assert_public_summary_private_id_free  # noqa: E402
from src.task1.final_train import load_frozen_final_config, load_model_bundle, load_yaml  # noqa: E402


REQUIRED_REPORTS = (
    "run_manifest.json",
    "service_feature_importance.csv",
    "late_feature_importance.csv",
    "service_shap_global.csv",
    "late_shap_global.csv",
    "service_local_explanation.json",
    "late_local_explanation.json",
    "business_drivers.json",
    "shap_reconstruction_audit.json",
    "feature_leakage_audit.json",
    "causal_language_audit.json",
    "frozen_artifact_hash_audit.json",
    "phase25_explainability_report.md",
)

REQUIRED_FIGURES = (
    "service_feature_importance.png",
    "late_feature_importance.png",
    "service_shap_bar.png",
    "service_shap_distribution.png",
    "late_shap_bar.png",
    "late_shap_distribution.png",
    "service_local_waterfall.png",
    "late_local_waterfall.png",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--final-model-config", required=True, type=Path)
    parser.add_argument("--service-model-dir", required=True, type=Path)
    parser.add_argument("--late-model-dir", required=True, type=Path)
    parser.add_argument("--submission", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    return parser.parse_args()


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _require_files(report_dir: Path) -> None:
    missing = [name for name in REQUIRED_REPORTS if not (report_dir / name).is_file()]
    missing += [f"figures/{name}" for name in REQUIRED_FIGURES if not (report_dir / "figures" / name).is_file()]
    if missing:
        raise ValueError("Phase 25 evidence is incomplete: " + ", ".join(missing))


def _validate_table(path: Path, schema_features: list[str], required: set[str]) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if not required.issubset(frame.columns):
        raise ValueError(f"Explainability table lacks required columns: {path.name}")
    if frame["feature_name"].duplicated().any() or frame["feature_name"].tolist() == []:
        raise ValueError(f"Explainability feature rows are empty or duplicated: {path.name}")
    if set(frame["feature_name"]) != set(schema_features):
        raise ValueError(f"Explainability table does not cover the exact frozen schema: {path.name}")
    ranks = sorted(pd.to_numeric(frame["rank"], errors="raise").astype(int).tolist())
    if ranks != list(range(1, len(frame) + 1)):
        raise ValueError(f"Explainability ranks are incomplete: {path.name}")
    return frame


def _contains_identifier_key(value: Any) -> bool:
    if isinstance(value, dict):
        if any(str(key).lower() in {"delivery_id", "route_id", "vehicle_id"} for key in value):
            return True
        return any(_contains_identifier_key(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_identifier_key(item) for item in value)
    return False


def main() -> int:
    args = parse_args()
    config = load_yaml(args.config)
    if config.get("version") != 1 or bool((config.get("privacy") or {}).get("external_api_allowed", False)):
        raise ValueError("Phase 25 configuration is invalid or permits an external API.")
    final_config = load_frozen_final_config(args.final_model_config)
    service_bundle = load_model_bundle(args.service_model_dir)
    late_method = str(((final_config.get("lateness_model") or {}).get("calibration") or {}).get("method") or "raw").lower()
    late_bundle = load_model_bundle(args.late_model_dir, require_calibration=late_method not in {"raw", "none", "null", ""})

    _require_files(args.report_dir)
    schema_features = list(service_bundle["schema"].get("feature_columns") or [])
    registry = build_explanation_registry(
        schema_features,
        categorical_columns=list(service_bundle["schema"].get("categorical_columns") or []),
    )
    audit_explanation_schema(service_bundle["schema"], late_bundle["schema"], registry)

    importance_required = {"feature_name", "importance", "importance_type", "rank", "semantic_group", "source_lineage"}
    shap_required = {"feature_name", "mean_abs_shap", "mean_shap", "rank", "sample_count", "semantic_group", "source_lineage", "direction_statement"}
    service_importance = _validate_table(args.report_dir / "service_feature_importance.csv", schema_features, importance_required)
    late_importance = _validate_table(args.report_dir / "late_feature_importance.csv", schema_features, importance_required)
    service_shap = _validate_table(args.report_dir / "service_shap_global.csv", schema_features, shap_required)
    late_shap = _validate_table(args.report_dir / "late_shap_global.csv", schema_features, shap_required)
    if (service_shap["mean_abs_shap"] < 0).any() or (late_shap["mean_abs_shap"] < 0).any():
        raise ValueError("Mean absolute SHAP cannot be negative.")
    if not service_shap["direction_statement"].str.contains("not inferred", regex=False).all():
        raise ValueError("Mean absolute SHAP was improperly used as direction evidence.")

    manifest = _json(args.report_dir / "run_manifest.json")
    if manifest.get("phase") != 25 or manifest.get("status") != "PASS":
        raise ValueError("Phase 25 run manifest is not PASS.")
    if manifest.get("positive_class") != 1 or manifest.get("external_api_used") is not False:
        raise ValueError("Positive class or external-API manifest contract failed.")
    if manifest.get("row_identifiers_recorded") is not False:
        raise ValueError("Run manifest reports private row identifiers.")
    if manifest.get("service_model", {}).get("family") != service_bundle["metadata"].get("model_family"):
        raise ValueError("Service model family differs from the frozen bundle.")
    if manifest.get("late_model", {}).get("family") != late_bundle["metadata"].get("model_family"):
        raise ValueError("Lateness model family differs from the frozen bundle.")
    if not manifest.get("service_shap", {}).get("output_space") or not manifest.get("late_shap", {}).get("output_space"):
        raise ValueError("SHAP output-space metadata is missing.")

    reconstruction = _json(args.report_dir / "shap_reconstruction_audit.json")
    if reconstruction.get("status") != "PASS":
        raise ValueError("SHAP reconstruction audit failed.")
    if not reconstruction.get("service", {}).get("pass") or not reconstruction.get("service", {}).get("postprocessing_bridge_pass"):
        raise ValueError("Service SHAP or post-processing bridge failed.")
    if not reconstruction.get("late", {}).get("base_output_pass") or not reconstruction.get("late", {}).get("calibration_bridge_pass"):
        raise ValueError("Lateness SHAP or calibration bridge failed.")
    if reconstruction.get("late", {}).get("positive_class") != 1:
        raise ValueError("Lateness reconstruction uses the wrong positive class.")

    service_local = _json(args.report_dir / "service_local_explanation.json")
    late_local = _json(args.report_dir / "late_local_explanation.json")
    if service_local.get("example_label") != "SERVICE_EXAMPLE_A" or late_local.get("example_label") != "LATE_EXAMPLE_A":
        raise ValueError("Local example labels are not deterministic/anonymized.")
    if _contains_identifier_key(service_local) or _contains_identifier_key(late_local):
        raise ValueError("Local explanation contains a private identifier key.")
    if not service_local.get("shap_reconstruction_pass") or not late_local.get("shap_reconstruction_pass"):
        raise ValueError("Local SHAP reconstruction failed.")
    if late_local.get("shap_output_space") == "raw_margin_log_odds" and late_local.get("probability_point_interpretation_allowed") is not False:
        raise ValueError("Raw-margin SHAP is mislabeled as probability-point attribution.")

    drivers = _json(args.report_dir / "business_drivers.json")
    for model_name in ("service", "lateness"):
        records = drivers.get(model_name)
        if not isinstance(records, list) or not records:
            raise ValueError(f"Business-driver summary is missing for {model_name}.")
        if any(record.get("driver") not in schema_features for record in records):
            raise ValueError("Business-driver output contains a non-frozen feature.")
        if any("not evidence of a causal effect" not in record.get("causal_caution", "") for record in records):
            raise ValueError("Business-driver causal caution is incomplete.")

    leakage = _json(args.report_dir / "feature_leakage_audit.json")
    if leakage.get("status") != "PASS" or leakage.get("forbidden_direct_count") != 0 or leakage.get("target_feature_count") != 0:
        raise ValueError("Feature-leakage audit failed.")
    causal = _json(args.report_dir / "causal_language_audit.json")
    if causal.get("status") != "PASS" or causal.get("high_risk_phrase_count") != 0:
        raise ValueError("Causal-language audit failed.")

    summary_text = args.summary.read_text(encoding="utf-8")
    private_report = (args.report_dir / "phase25_explainability_report.md").read_text(encoding="utf-8")
    assert_public_summary_private_id_free(summary_text)
    require_causal_language_pass({"summary": summary_text, "private_report": private_report})

    frozen_paths = frozen_artifact_paths(
        args.final_model_config, args.service_model_dir, args.late_model_dir, args.submission
    )
    current = hash_artifacts(frozen_paths, root=PROJECT_ROOT)
    hash_audit = _json(args.report_dir / "frozen_artifact_hash_audit.json")
    if hash_audit.get("status") != "PASS" or hash_audit.get("all_unchanged") is not True:
        raise ValueError("Frozen-artifact audit did not pass.")
    if hash_audit.get("before") != hash_audit.get("after") or current != hash_audit.get("after"):
        raise ValueError("Frozen Task 1 artifacts changed after explainability generation.")

    if any("phase26" in path.name.lower() for path in args.report_dir.rglob("*")):
        raise ValueError("Phase 26 output appeared inside the Phase 25 report directory.")

    print("LOCAL PHASE 25 TASK1 EXPLAINABILITY VALIDATION: PASS")
    print("SERVICE FEATURE IMPORTANCE: PASS")
    print("LATENESS FEATURE IMPORTANCE: PASS")
    print("GLOBAL SHAP - SERVICE: PASS")
    print("GLOBAL SHAP - LATENESS: PASS")
    print("SHAP RECONSTRUCTION: PASS")
    print("POSTPROCESSING AND CALIBRATION BRIDGES: PASS")
    print("FEATURE LEAKAGE AUDIT: PASS")
    print("CAUSAL-LANGUAGE AUDIT: PASS")
    print("FROZEN TASK1 ARTIFACTS UNCHANGED: PASS")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
