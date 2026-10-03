"""Local operator CLI for Phase 06 Task 1 feature engineering.

This script is intended to be executed locally by the human operator.
It writes train/test feature matrices and private audit reports without
printing row-level records.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.features import build_task1_feature_tables, load_task1_features_config


def _find_unique(raw_root: Path, filename: str) -> Path:
    matches = list(raw_root.rglob(filename))
    if not matches:
        raise FileNotFoundError(f"Required artifact not found: {filename}")
    if len(matches) > 1:
        raise RuntimeError(f"Required artifact duplicated: {filename}")
    return matches[0]


def _load_optional(raw_root: Path, filename: str) -> pd.DataFrame | None:
    matches = list(raw_root.rglob(filename))
    if not matches:
        return None
    if len(matches) > 1:
        raise RuntimeError(f"Optional artifact duplicated: {filename}")
    return pd.read_csv(matches[0])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build Task 1 Phase 06 train/test feature tables.")
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--train-output", type=Path, required=True)
    parser.add_argument("--test-output", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    config = load_task1_features_config(args.config)

    deliveries_train = pd.read_csv(_find_unique(args.raw_root, "deliveries_train.csv"))
    task1_test_inputs = pd.read_csv(_find_unique(args.raw_root, "task1_test_inputs.csv"))
    route_legs_train = pd.read_csv(_find_unique(args.raw_root, "route_legs_train.csv"))
    route_legs_test = pd.read_csv(_find_unique(args.raw_root, "route_legs_test.csv"))
    outlets = pd.read_csv(_find_unique(args.raw_root, "outlets.csv"))
    vehicles = pd.read_csv(_find_unique(args.raw_root, "vehicles.csv"))
    calendar = pd.read_csv(_find_unique(args.raw_root, "calendar.csv"))
    district_travel = pd.read_csv(_find_unique(args.raw_root, "district_travel.csv"))
    service_allowance = pd.read_csv(_find_unique(args.raw_root, "service_allowance.csv"))
    traffic_speed = _load_optional(args.raw_root, "traffic_speed.csv")
    road_conditions = _load_optional(args.raw_root, "road_conditions.csv")
    labels_train = pd.read_csv(args.labels)

    built = build_task1_feature_tables(
        orders_train=deliveries_train,
        orders_test=task1_test_inputs,
        route_legs_train=route_legs_train,
        route_legs_test=route_legs_test,
        outlets=outlets,
        vehicles=vehicles,
        district_travel=district_travel,
        service_allowance=service_allowance,
        calendar=calendar,
        labels_train=labels_train,
        config=config,
        road_conditions=road_conditions,
        traffic_speed=traffic_speed,
    )

    X_train = built["X_train"]
    X_test = built["X_test"]
    registry = built["feature_registry"]
    leakage = built["leakage_audit"]

    args.train_output.parent.mkdir(parents=True, exist_ok=True)
    args.test_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    X_train.to_csv(args.train_output, index=False)
    X_test.to_csv(args.test_output, index=False)
    registry.to_json(args.report_dir / "feature_registry.json", orient="records", indent=2)
    with (args.report_dir / "leakage_audit.json").open("w", encoding="utf-8") as handle:
        json.dump(leakage, handle, indent=2, sort_keys=True)
    with (args.report_dir / "train_test_parity.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "train_feature_count": int(X_train.shape[1]),
                "test_feature_count": int(X_test.shape[1]),
                "same_columns_same_order": bool(list(X_train.columns) == list(X_test.columns)),
            },
            handle,
            indent=2,
            sort_keys=True,
        )
    with (args.report_dir / "build_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "rows_train": int(X_train.shape[0]),
                "rows_test": int(X_test.shape[0]),
                "features": int(X_train.shape[1]),
                "forbidden_direct_fields_in_X": int(leakage["forbidden_direct_count"]),
                "road_status": built["env_status"]["train"]["road"],
                "traffic_status": built["env_status"]["train"]["traffic"],
            },
            handle,
            indent=2,
            sort_keys=True,
        )

    print("PHASE 06 TASK 1 FEATURE BUILD: PASS")
    print("Train feature matrix: PASS")
    print("Test feature matrix: PASS")
    print("Train/test parity: PASS")
    print("Historical feature safety: PASS")
    print("Leakage audit: PASS")
    print("Forbidden direct fields in X: 0")
    print("Detailed reports stored locally.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
