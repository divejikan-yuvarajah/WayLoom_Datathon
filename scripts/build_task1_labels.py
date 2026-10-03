"""Local operator CLI for the canonical Task 1 label builder.

This script is intended to be run by the human operator against local,
ignored competition data. It never prints rows or row-level identifiers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

# When invoked as `python scripts/build_task1_labels.py`, Python places only
# `scripts/` on sys.path. Add the repository root so `src.task1` is importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.labels import build_task1_training_labels


def _find_unique(raw_root: Path, filename: str) -> Path:
    matches = list(raw_root.rglob(filename))
    if not matches:
        raise FileNotFoundError(f"Required artifact not found: {filename}")
    if len(matches) > 1:
        raise RuntimeError(f"Required artifact is duplicated: {filename}")
    return matches[0]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build local Task 1 training labels.")
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional tracked dataset manifest accepted for operator compatibility.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--travel-tolerance-min", type=float, default=5.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    deliveries_path = _find_unique(args.raw_root, "deliveries_train.csv")
    route_legs_path = _find_unique(args.raw_root, "route_legs_train.csv")

    deliveries = pd.read_csv(deliveries_path)
    route_legs = pd.read_csv(route_legs_path)
    labels, diagnostics = build_task1_training_labels(
        deliveries,
        route_legs,
        travel_tolerance_min=args.travel_tolerance_min,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    labels.to_csv(args.output, index=False)
    with (args.report_dir / "build_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, indent=2, sort_keys=True)

    print("PHASE 04 LOCAL TASK 1 LABEL BUILD: PASS")
    print("Canonical labels written locally.")
    print("No row values were printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
