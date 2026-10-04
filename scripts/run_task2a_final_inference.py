"""Run Phase 17 Task 2A frozen final inference locally on restricted data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest
from src.task2a.features import load_feature_config
from src.task2a.final_inference import run_final_inference, validate_inference_config
from src.task2a.history import load_history_config
from src.task2a.model_selection import validate_final_model_config
from src.task2a.submission import map_predictions_to_template, write_submission_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--weekly-panel", required=True, type=Path)
    parser.add_argument("--multihorizon-table", required=True, type=Path)
    parser.add_argument("--history-config", required=True, type=Path)
    parser.add_argument("--feature-config", required=True, type=Path)
    parser.add_argument("--final-model-config", required=True, type=Path)
    parser.add_argument("--inference-config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    return parser.parse_args()


def _official_path(raw_root: Path, manifest_path: Path, filename: str) -> Path:
    discovered = discover_dataset_files(raw_root, load_manifest(manifest_path))
    found = discovered.get("found_artifacts", {}).get(filename, {}).get("path")
    if not found:
        raise ValueError(f"Official artifact is unavailable or duplicated: {filename}")
    return Path(found)


def _private_report_dir(path: Path) -> Path:
    allowed = (PROJECT_ROOT / "reports/private/phase17_task2a_final").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as error:
        raise ValueError("Phase 17 report output must be inside reports/private/phase17_task2a_final.") from error
    return resolved


def main() -> int:
    args = parse_args()
    config = yaml.safe_load(args.inference_config.read_text(encoding="utf-8"))
    load_history_config(args.history_config)
    final_config = yaml.safe_load(args.final_model_config.read_text(encoding="utf-8"))
    validate_final_model_config(final_config)
    validate_inference_config(config, final_config)
    report_dir = _private_report_dir(args.report_dir)
    test_inputs = pd.read_csv(_official_path(args.raw_root, args.manifest, "task2a_test_inputs.csv"))
    template = pd.read_csv(_official_path(args.raw_root, args.manifest, "submission_task2a.csv"))
    calendar = pd.read_csv(_official_path(args.raw_root, args.manifest, "calendar.csv"))
    result = run_final_inference(pd.read_csv(args.weekly_panel), pd.read_csv(args.multihorizon_table), calendar,
                                 test_inputs, final_config, load_feature_config(args.feature_config))
    submission = map_predictions_to_template(template, result["predictions"])
    output_report = write_submission_atomic(args.output, submission, template, test_inputs, final_config)
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"phase": 17, "status": "PASS", "model_search_performed": False,
                "ensemble_weight_search_performed": False, "future_actual_demand_used": False,
                "phase16_champion_ids_unchanged": True, "final_origin_resolved": True,
                "horizons_1_to_10": True, "submission_validation": output_report,
                "phase16_champion_ids": {"total": final_config["total"]["candidate_id"],
                                          "chilled_fresh": final_config["chilled_fresh"]["candidate_id"]},
                "corrections": result["corrections"]}
    (report_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for line in ("LOCAL PHASE 17 TASK2A INFERENCE: PASS", "MODEL SEARCH PERFORMED: NO",
                 "OFFICIAL ROW_ID PRESERVED: YES", "PRIVATE FORECAST VALUES PRINTED: NO"):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
