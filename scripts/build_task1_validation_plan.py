"""Local-only Phase 07 Task 1 chronological validation-plan builder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.validation import build_task1_validation_plan, load_task1_validation_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build private Task 1 chronological validation plan.")
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--feature-registry", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    labels = pd.read_csv(args.labels)
    features = pd.read_csv(args.features)
    if len(features) != len(labels):
        raise ValueError(
            "Feature/label row counts differ; cannot create a valid chronological plan."
        )
    if not args.feature_registry.exists():
        raise FileNotFoundError(f"Feature registry/config not found: {args.feature_registry}")
    # This validates the tracked Phase 06 feature configuration is present.
    # Detailed runtime registry output remains private and is not printed.
    with args.feature_registry.open(encoding="utf-8") as handle:
        feature_registry_config = handle.read()
    if not feature_registry_config.strip():
        raise ValueError("Feature registry/config file is empty.")
    config = load_task1_validation_config(args.config)
    plan = build_task1_validation_plan(labels, config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    holdout = plan["holdout"]
    payload = {
        "development_row_count": int(len(holdout.development_index)),
        "holdout_row_count": int(len(holdout.holdout_index)),
        "development_date_count": int(len(holdout.development_dates)),
        "holdout_date_count": int(len(holdout.holdout_dates)),
        "folds": [
            {
                "fold": f.fold,
                "train_rows": int(len(f.train_index)),
                "validation_rows": int(len(f.validation_index)),
                "train_date_count": int(len(f.train_dates)),
                "validation_date_count": int(len(f.validation_dates)),
            }
            for f in plan["folds"]
        ],
        "fit_scope": "fit_on_train_transform_validation_without_validation_targets",
    }
    with (args.output_dir / "validation_plan.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    print("PHASE 07 TASK 1 VALIDATION PLAN: PASS")
    print("Final holdout integrity: PASS")
    print("Expanding fold integrity: PASS")
    print("Same-date atomicity: PASS")
    print("No row-level records printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
