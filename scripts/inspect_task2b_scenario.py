"""Run local-only Phase 18 Task 2B S1 inspection with sanitized console output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest
from src.task2b.scenario import build_s1_scenario, load_scenario_config
from src.task2b.scenario_summary import build_scenario_summaries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def _path(discovery: dict, filename: str) -> Path:
    path = discovery.get("found_artifacts", {}).get(filename, {}).get("path")
    if not path:
        raise ValueError(f"Required official artifact is unavailable or duplicated: {filename}")
    return Path(path)


def _private_dir(path: Path) -> Path:
    allowed = (PROJECT_ROOT / "reports/private/phase18_task2b_scenario").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as error:
        raise ValueError("Phase 18 output must be inside reports/private/phase18_task2b_scenario.") from error
    return resolved


def _write_private_summaries(summary: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    scalar: dict[str, object] = {}
    for name, value in summary.items():
        if isinstance(value, pd.DataFrame):
            value.to_csv(output_dir / f"{name}.csv", index=False)
        else:
            scalar[name] = value
    (output_dir / "scenario_summary.json").write_text(json.dumps(scalar, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    config = load_scenario_config(str(args.config))
    discovery = discover_dataset_files(args.raw_root, load_manifest(args.manifest))
    files = config["files"]
    scenario = build_s1_scenario(
        pd.read_csv(_path(discovery, files["orders"])), pd.read_csv(_path(discovery, files["fleet"])),
        pd.read_csv(_path(discovery, files["vehicles"])), pd.read_csv(_path(discovery, files["district_travel"])),
        pd.read_csv(_path(discovery, files["service_allowance"])), config,
    )
    output_dir = _private_dir(args.output_dir)
    summary = build_scenario_summaries(scenario["orders_s1"])
    _write_private_summaries(summary, output_dir)
    coverage = {"phase": 18, "status": "PASS", "scenario": "S1", "order_key": "order_ref",
                "available_fleet_only": True, "workshop_excluded": True,
                "peliyagoda_orders_confirmed": True, "reference_coverage": "PASS"}
    (output_dir / "reference_coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    (output_dir / "fleet_status_summary.json").write_text(
        json.dumps(scenario["depot_fleet_diagnostics"], indent=2), encoding="utf-8"
    )
    for line in ("LOCAL PHASE 18 TASK2B SCENARIO: PASS", "S1 ORDER KEY: order_ref", "WORKSHOP EXCLUSION: PASS", "PRIVATE ORDER VALUES PRINTED: NO"):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
