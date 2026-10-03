"""Local-only Phase 10 saved-model Task 1 inference. Never retrains."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest  # noqa: E402
from src.task1.final_train import load_frozen_final_config, load_yaml, resolve_negative_service_policy  # noqa: E402
from src.task1.inference import (  # noqa: E402
    assemble_official_predictions,
    assert_saved_models_present,
    join_route_legs_test,
    load_task1_test_inputs,
    prepare_test_features_from_raw,
    run_saved_model_inference,
)
from src.task1.submission import export_task1_submission, fill_official_task1_template  # noqa: E402


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run saved-model Task 1 inference and write the official submission.")
    p.add_argument("--raw-root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--feature-registry", type=Path, required=True)
    p.add_argument("--final-config", type=Path, required=True)
    p.add_argument("--service-model-dir", type=Path, required=True)
    p.add_argument("--late-model-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--report-dir", type=Path, required=True)
    p.add_argument("--inference-config", type=Path, default=PROJECT_ROOT / "configs" / "task1_inference.yaml")
    p.add_argument(
        "--labels",
        type=Path,
        default=PROJECT_ROOT / "data" / "interim" / "task1_training_labels.csv",
        help="Historical train labels only; never Task 1 test labels.",
    )
    return p


def _resolve_official(raw_root: Path, manifest_path: Path, filename: str) -> Path:
    manifest = load_manifest(manifest_path)
    discovered = discover_dataset_files(raw_root, manifest)
    found = discovered.get("found_artifacts") or {}
    if filename in found and found[filename].get("path"):
        return Path(found[filename]["path"])
    matches = list(Path(raw_root).rglob(filename))
    if not matches:
        raise SystemExit(f"Official file not found: {filename}")
    return matches[0]


def main() -> int:
    args = parser().parse_args()
    assert_saved_models_present(args.service_model_dir, args.late_model_dir)
    final_config = load_frozen_final_config(args.final_config)
    inference_config = load_yaml(args.inference_config) if args.inference_config.is_file() else {}
    labels = pd.read_csv(args.labels, low_memory=False) if args.labels and args.labels.is_file() else None
    X_test, trace = prepare_test_features_from_raw(
        args.raw_root,
        args.feature_registry,
        historical_train_labels=labels,
        labels_path=args.labels,
    )
    test_inputs = load_task1_test_inputs(_resolve_official(args.raw_root, args.manifest, "task1_test_inputs.csv"))
    route_legs = pd.read_csv(_resolve_official(args.raw_root, args.manifest, "route_legs_test.csv"))
    join_route_legs_test(test_inputs, route_legs)
    preds = run_saved_model_inference(
        X_test,
        args.service_model_dir,
        args.late_model_dir,
        final_config,
        inference_config,
    )
    if "delivery_id" not in preds.columns:
        preds = preds.copy()
        preds["delivery_id"] = (
            X_test["delivery_id"].to_numpy() if "delivery_id" in X_test.columns else trace["delivery_id"].to_numpy()
        )
    assembled = assemble_official_predictions(test_inputs, preds)
    template = pd.read_csv(_resolve_official(args.raw_root, args.manifest, "submission_task1.csv"))
    submission = fill_official_task1_template(template, assembled)
    policy = resolve_negative_service_policy(final_config, inference_config)
    export_task1_submission(
        submission,
        args.output,
        test_inputs.sort_values("__official_row_order", kind="stable")["delivery_id"],
        template_columns=list(template.columns),
        negative_policy=policy,
    )
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": 10,
        "status": "INFERRED",
        "inferred_at_utc": datetime.now(timezone.utc).isoformat(),
        "n_rows": int(len(submission)),
        "output": str(args.output),
        "retrained_during_inference": False,
    }
    (args.report_dir / "phase10_inference_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
