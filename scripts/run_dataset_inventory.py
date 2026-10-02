#!/usr/bin/env python
"""WayLoom Datathon - Phase 02 Raw Dataset Inventory CLI.

This script executes Phase 02 dataset discovery, CSV loadability checks,
schema inventory, and availability classification locally.

CRITICAL DATA SAFETY NOTICE:
- Never prints DataFrames, row values, or samples to stdout/stderr.
- Writes purely structural metadata JSON to the ignored private report directory.
- Exits with code 0 on PASS, and code 1 on any blocker.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_inventory import run_inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute Phase 02 Raw Dataset Inventory safely without displaying competition rows."
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Path to the directory containing raw extracted competition files (default: data/raw)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "configs" / "dataset_manifest.yaml",
        help="Path to the dataset manifest YAML (default: configs/dataset_manifest.yaml)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "reports" / "private" / "phase02_inventory",
        help="Path to the private report output directory (default: reports/private/phase02_inventory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    raw_root = args.raw_root.resolve()
    manifest_path = args.manifest.resolve()
    output_dir = args.output_dir.resolve()

    if not raw_root.exists():
        print(f"PHASE 02 LOCAL INVENTORY: FAIL\nDirectory does not exist: {raw_root}")
        return 1

    if not manifest_path.exists():
        print(f"PHASE 02 LOCAL INVENTORY: FAIL\nManifest file does not exist: {manifest_path}")
        return 1

    try:
        summary = run_inventory(
            raw_root=raw_root,
            manifest_path=manifest_path,
            output_dir=output_dir,
        )
    except Exception as e:
        print(f"PHASE 02 LOCAL INVENTORY: FAIL\nExecution error: {type(e).__name__}: {str(e)}")
        return 1

    if summary.get("status") == "PASS":
        print("PHASE 02 LOCAL INVENTORY: PASS")
        print("Required artifacts located: PASS")
        print("CSV loadability: PASS")
        print(f"Structural inventory written to: {output_dir}")
        print("No row values were printed.")
        return 0
    else:
        print("PHASE 02 LOCAL INVENTORY: FAIL")
        missing = summary.get("missing_required", [])
        if missing:
            print(f"Missing required files ({len(missing)}): {', '.join(missing)}")
        dups = summary.get("duplicate_required", {})
        if dups:
            print(f"Duplicate required files ({len(dups)}): {', '.join(dups.keys())}")
        unreadable = summary.get("unreadable_csvs", [])
        if unreadable:
            print(f"Unreadable CSV files ({len(unreadable)}): {', '.join(unreadable)}")
        print(f"Detailed diagnostics written to: {output_dir / 'validation_summary.json'}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
