"""Local/private Phase 22 optimization; console output is status only."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import ortools
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest
from src.task2b.lexicographic_solver import assert_deterministic, solve_lexicographic
from src.task2b.optimizer import build_optimizer_model
from src.task2b.scenario import build_s1_scenario, load_scenario_config
from src.task2b.solution import extract_allocation, extract_solver_trip_minutes, sha256_file
from src.task2b.solution_audit import audit_allocation, audit_objective_vector
from src.task2b.solver_data import build_solver_data, validate_optimizer_config
from src.task2b.trip_time import load_trip_time_config


def _inside(path: Path, parent: Path) -> bool:
    return path.resolve().is_relative_to(parent.resolve())


def _write_csv_atomically(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="phase22_", suffix=".csv", dir=path.parent)
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as stream:
            frame.to_csv(stream, index=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _validate_candidate_output_path(candidate_output: Path, canonical_allocation: Path) -> None:
    """Keep the normal optimizer from ever writing the canonical allocation."""
    if candidate_output.resolve() == canonical_allocation.resolve():
        raise ValueError("The optimizer candidate output cannot be the canonical frozen allocation path.")


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("raw-root", "manifest", "scenario-config", "compatibility-config", "trip-time-config",
                 "priority-config", "optimizer-config", "compatibility-matrix", "priority-metadata",
                 "candidate-output", "trip-summary-output", "report-dir"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    args = parser.parse_args()
    private_data = ROOT / "data" / "interim"
    private_reports = ROOT / "reports" / "private" / "phase22_task2b_optimizer"
    if not all(_inside(path, private_data) for path in (args.candidate_output, args.trip_summary_output)) or not _inside(args.report_dir, private_reports):
        raise ValueError("Phase 22 outputs must remain in their private locations.")
    with args.optimizer_config.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    with args.priority_config.open(encoding="utf-8") as stream:
        priority = yaml.safe_load(stream)
    validate_optimizer_config(config, priority)
    canonical = (ROOT / config["freeze"]["canonical_allocation_path"]).resolve()
    _validate_candidate_output_path(args.candidate_output, canonical)
    scenario_config = load_scenario_config(str(args.scenario_config))
    load_trip_time_config(str(args.trip_time_config))
    with args.compatibility_config.open(encoding="utf-8") as stream:
        compatibility_config = yaml.safe_load(stream)
    if compatibility_config.get("low_flexibility_threshold") != 2:
        raise ValueError("Phase 19 flexibility threshold differs from frozen Phase 21 policy.")
    if canonical.exists() or (args.report_dir / "freeze_manifest.json").exists():
        raise ValueError("Phase 22 allocation is already frozen; refusing optimizer overwrite.")
    if args.trip_summary_output.resolve() != (ROOT / config["freeze"]["canonical_trip_summary_path"]).resolve():
        raise ValueError("Trip summary path differs from the frozen Phase 22 configuration.")
    found = discover_dataset_files(args.raw_root, load_manifest(args.manifest))["found_artifacts"]
    file_keys = scenario_config["files"]
    numeric_types = {
        "orders": {"order_weight_kg": "string", "order_volume_m3": "string"},
        "vehicles": {"weight_cap_kg": "string", "volume_cap_m3": "string"},
        "district_travel": {"depot_to_district_freeflow_min": "string", "inter_stop_freeflow_min": "string"},
        "service_allowance": {"service_allowance_min": "string"},
    }
    def load(key: str) -> pd.DataFrame:
        return pd.read_csv(found[file_keys[key]]["path"], dtype=numeric_types.get(key))
    scenario = build_s1_scenario(load("orders"), load("fleet"), load("vehicles"),
                                 load("district_travel"), load("service_allowance"), scenario_config)
    matrix = pd.read_csv(args.compatibility_matrix)
    metadata = pd.read_csv(args.priority_metadata)
    data = build_solver_data(scenario, matrix, metadata, config, priority)
    bundle_a = build_optimizer_model(data)
    print("DETERMINISTIC RUN 1 OF 2", flush=True)
    solve_a = solve_lexicographic(bundle_a, config, on_progress=lambda message: print(message, flush=True))
    allocation_a = extract_allocation(bundle_a, solve_a)
    audit_a = audit_allocation(allocation_a, data, extract_solver_trip_minutes(bundle_a, solve_a))
    bundle_b = build_optimizer_model(data)
    print("DETERMINISTIC RUN 2 OF 2", flush=True)
    solve_b = solve_lexicographic(bundle_b, config, on_progress=lambda message: print(message, flush=True))
    allocation_b = extract_allocation(bundle_b, solve_b)
    audit_b = audit_allocation(allocation_b, data, extract_solver_trip_minutes(bundle_b, solve_b))
    audit_objective_vector(allocation_a, data, solve_a.objective_vector)
    audit_objective_vector(allocation_b, data, solve_b.objective_vector)
    assert_deterministic((solve_a, allocation_a), (solve_b, allocation_b))
    if audit_a.status != "PASS" or audit_b.status != "PASS" or not audit_a.trip_summary.equals(audit_b.trip_summary):
        raise ValueError("Independent audit or deterministic trip summary failed.")
    _write_csv_atomically(allocation_a, args.candidate_output)
    _write_csv_atomically(audit_a.trip_summary, args.trip_summary_output)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    config_paths = {"solver": args.optimizer_config, "scenario": args.scenario_config,
                    "compatibility": args.compatibility_config, "trip_time": args.trip_time_config,
                    "priority": args.priority_config}
    run = {"phase": 22, "solver": "OR-Tools CP-SAT", "ortools_version": ortools.__version__,
           "objective_strategy": "lexicographic", "determinism": "PASS",
           "smoke_status": solve_a.smoke_status, "objective_vector": solve_a.objective_vector,
           "candidate_allocation_sha256": sha256_file(args.candidate_output),
           "trip_summary_sha256": sha256_file(args.trip_summary_output),
           "scales": data.scales, "order_count": len(data.order_ids), "usable_vehicle_count": len(data.vehicle_ids),
           "assignment_variable_count": len(bundle_a.x), "trip_use_variable_count": len(bundle_a.use_trip),
           "group_use_variable_count": len(bundle_a.use_group),
           "config_paths": {key: str(path.resolve()) for key, path in config_paths.items()},
           **{f"{key}_config_hash": sha256_file(path) for key, path in config_paths.items()}}
    (args.report_dir / "run_manifest.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
    (args.report_dir / "objective_stages.json").write_text(json.dumps(solve_a.stage_records, indent=2), encoding="utf-8")
    (args.report_dir / "hard_rule_audit.json").write_text(json.dumps({"status": "PASS", "all_hard_rules_audited": True,
        "objective_vector_reconciled": True, "checks": audit_a.checks}, indent=2), encoding="utf-8")
    print("LOCAL PHASE 22 TASK2B OPTIMIZER: PASS")
    print("ALL OBJECTIVE STAGES OPTIMAL: YES")
    print("INDEPENDENT HARD-RULE AUDIT: PASS")
    print("DETERMINISTIC RERUN: PASS")
    print("PRIVATE ALLOCATION VALUES PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
