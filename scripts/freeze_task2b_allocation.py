"""Freeze an already audited private Phase 22 candidate exactly once."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.task2b.solution import (REQUIRED_FREEZE_CONFIG_KEYS, freeze_allocation,
                                 regenerate_freeze_manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("candidate-allocation", "trip-summary", "optimizer-config", "scenario-config",
                 "compatibility-config", "trip-time-config", "priority-config", "report-dir", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--controlled-reopen-freeze-evidence", action="store_true")
    args = parser.parse_args()
    with args.optimizer_config.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if args.output.resolve() != (ROOT / config["freeze"]["canonical_allocation_path"]).resolve():
        raise ValueError("Freeze output differs from the configured canonical allocation path.")
    if args.trip_summary.resolve() != (ROOT / config["freeze"]["canonical_trip_summary_path"]).resolve():
        raise ValueError("Freeze trip summary differs from the configured canonical path.")
    if not args.output.resolve().is_relative_to((ROOT / "data" / "interim").resolve()) or not args.report_dir.resolve().is_relative_to((ROOT / "reports/private/phase22_task2b_optimizer").resolve()):
        raise ValueError("Freeze outputs must remain private.")
    run = json.loads((args.report_dir / "run_manifest.json").read_text(encoding="utf-8"))
    paths = {
        "solver": args.optimizer_config,
        "scenario": args.scenario_config,
        "compatibility": args.compatibility_config,
        "trip_time": args.trip_time_config,
        "priority": args.priority_config,
    }
    recorded_paths = run.get("config_paths")
    if (not isinstance(recorded_paths, dict)
            or set(recorded_paths) != set(REQUIRED_FREEZE_CONFIG_KEYS)
            or any(Path(recorded_paths[key]).resolve() != paths[key].resolve()
                   for key in REQUIRED_FREEZE_CONFIG_KEYS)):
        raise ValueError("Freeze config paths differ from the audited run.")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
    freeze_action = regenerate_freeze_manifest if args.controlled_reopen_freeze_evidence else freeze_allocation
    freeze_action(args.candidate_allocation, args.trip_summary, args.report_dir, args.output,
                  paths, git_commit=commit.stdout.strip() if commit.returncode == 0 else None)
    if args.controlled_reopen_freeze_evidence:
        print("LOCAL PHASE 22 TASK2B FREEZE EVIDENCE: REGENERATED")
        print("FROZEN ALLOCATION MODIFIED: NO")
        print("TRIP SUMMARY MODIFIED: NO")
    else:
        print("LOCAL PHASE 22 TASK2B ALLOCATION: FROZEN")
    print("PRIVATE ALLOCATION VALUES PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
