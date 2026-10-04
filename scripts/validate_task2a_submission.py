"""Validate an already-written Task 2A submission; never repair it."""

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
from src.task2a.model_selection import validate_final_model_config
from src.task2a.submission import validate_submission


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--final-model-config", required=True, type=Path)
    parser.add_argument("--submission", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    return parser.parse_args()


def _official_path(raw_root: Path, manifest_path: Path, filename: str) -> Path:
    found = discover_dataset_files(raw_root, load_manifest(manifest_path)).get("found_artifacts", {}).get(filename, {}).get("path")
    if not found:
        raise ValueError(f"Official artifact is unavailable or duplicated: {filename}")
    return Path(found)


def main() -> int:
    args = parse_args()
    if args.submission.name != "submission_task2a.csv" or not args.submission.is_file():
        raise ValueError("Task 2A submission must exist with the official filename submission_task2a.csv.")
    final_config = yaml.safe_load(args.final_model_config.read_text(encoding="utf-8"))
    validate_final_model_config(final_config)
    template = pd.read_csv(_official_path(args.raw_root, args.manifest, "submission_task2a.csv"))
    test_inputs = pd.read_csv(_official_path(args.raw_root, args.manifest, "task2a_test_inputs.csv"))
    report = validate_submission(pd.read_csv(args.submission), template, test_inputs, final_config)
    manifest_path = args.report_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("Phase 17 run manifest is required for final validation.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {"model_search_performed": False, "ensemble_weight_search_performed": False,
                "future_actual_demand_used": False, "phase16_champion_ids_unchanged": True}
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError("Phase 17 run manifest violates frozen-inference policy.")
    if manifest.get("phase16_champion_ids") != {"total": final_config["total"]["candidate_id"],
                                                  "chilled_fresh": final_config["chilled_fresh"]["candidate_id"]}:
        raise ValueError("Phase 17 run manifest champion IDs differ from frozen Phase 16 configuration.")
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (args.report_dir / "submission_validation.json").write_text(json.dumps({"phase": 17, **report}, indent=2), encoding="utf-8")
    print("TASK 02A FINAL VALIDATION: PASS")
    print("TASK 02A OUTPUT READY: YES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
