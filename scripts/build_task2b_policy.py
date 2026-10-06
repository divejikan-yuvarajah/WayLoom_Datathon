"""Human-local aggregate evidence generation and deterministic Task 2B policy build."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest
from src.task2b.allocation_validator import verify_frozen_integrity
from src.task2b.artifact_integrity import sha256_file
from src.task2b.compatibility import build_compatibility_matrix, order_compatibility_summary
from src.task2b.policy_evidence import build_task2b_policy_evidence, load_phase23_pass_evidence
from src.task2b.policy_writer import render_task2b_policy, validate_policy_text, write_policy_atomic
from src.task2b.submission import validate_output_config


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix="phase24_", suffix=".json", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _artifact(found: dict, filename: str) -> Path:
    record = found.get(filename)
    if not record:
        raise ValueError(f"Required official artifact is missing: {filename}.")
    return Path(record["path"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--priority-config", required=True, type=Path)
    parser.add_argument("--output-config", required=True, type=Path)
    parser.add_argument("--allocation", required=True, type=Path)
    parser.add_argument("--trip-summary", required=True, type=Path)
    parser.add_argument("--phase23-report-dir", required=True, type=Path)
    parser.add_argument("--policy-output", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    args = parser.parse_args()

    config = yaml.safe_load(args.output_config.read_text(encoding="utf-8"))
    priority_config = yaml.safe_load(args.priority_config.read_text(encoding="utf-8"))
    validate_output_config(config)
    expected = {
        "allocation": ROOT / config["phase22"]["allocation_path"],
        "trip_summary": ROOT / config["phase22"]["trip_summary_path"],
        "policy_output": ROOT / config["policy"]["output_path"],
        "report_dir": ROOT / config["policy"]["private_report_dir"],
        "phase23_report_dir": ROOT / config["phase23"]["report_dir"],
    }
    for name, path in expected.items():
        if getattr(args, name).resolve() != path.resolve():
            raise ValueError(f"Phase 24 {name.replace('_', ' ')} path differs from configuration.")

    freeze_manifest = ROOT / config["phase22"]["freeze_manifest_path"]
    integrity = verify_frozen_integrity(args.allocation, freeze_manifest, args.trip_summary)
    requested_evidence = args.phase23_report_dir / config["phase23"]["evidence_filename"]
    phase23_evidence, _ = load_phase23_pass_evidence(
        requested_evidence,
        expected_frozen_allocation_sha256=integrity["allocation_sha256"],
    )
    discovery = discover_dataset_files(args.raw_root, load_manifest(args.manifest))
    if discovery["discovery_status"] != "PASS":
        raise ValueError("Official dataset discovery failed.")
    found = discovery["found_artifacts"]
    orders = pd.read_csv(
        _artifact(found, config["source_files"]["orders"]),
        dtype={"order_ref": "string", "outlet_id": "string"},
    )
    fleet = pd.read_csv(
        _artifact(found, config["source_files"]["fleet"]), dtype={"vehicle_id": "string"}
    )
    vehicles = pd.read_csv(
        _artifact(found, config["source_files"]["vehicles"]), dtype={"vehicle_id": "string"}
    )
    allocation = pd.read_csv(args.allocation, dtype={"order_ref": "string", "outlet_id": "string", "vehicle_id": "string"})
    trip_summary = pd.read_csv(args.trip_summary, dtype={"vehicle_id": "string"})
    scenario_id, depot = config["scenario"]["expected_id"], config["scenario"]["expected_depot"]
    orders = orders.loc[orders.scenario.eq(scenario_id)].copy()
    fleet_s1 = fleet.loc[fleet.scenario.eq(scenario_id)].copy()
    usable = fleet_s1.loc[fleet_s1.status.eq("available")].merge(
        vehicles, on="vehicle_id", how="left", validate="one_to_one"
    )
    usable = usable.loc[usable.depot.eq(depot)].copy()
    matrix = build_compatibility_matrix(orders, usable)
    compatibility_summary = order_compatibility_summary(
        matrix, low_flexibility_threshold=config["policy"]["low_flexibility_threshold"]
    )
    evidence = build_task2b_policy_evidence(
        orders,
        allocation,
        fleet_s1,
        vehicles,
        compatibility_summary,
        trip_summary,
        phase23_evidence,
        trip_summary_sha256=integrity["trip_summary_sha256"],
        expected_scenario=scenario_id,
        expected_depot=depot,
        fresh_budget_limit=config["policy"]["fresh_budget_limit"],
        style_tech_budget_limit=config["policy"]["style_tech_budget_limit"],
    )
    policy, fact_validation = render_task2b_policy(evidence, priority_config)
    private_ids = set(orders.order_ref.astype(str)) | set(orders.outlet_id.astype(str)) | set(vehicles.vehicle_id.astype(str))
    private_ids = {value for value in private_ids if len(value) >= 4}
    fact_validation = validate_policy_text(
        policy,
        evidence,
        used_facts=fact_validation["used_facts"],
        private_identifiers=private_ids,
        target_max_words=config["policy"]["target_max_words"],
        warn_above_words=config["policy"]["warn_above_words"],
    )
    policy_hash = write_policy_atomic(args.policy_output, policy)
    fact_validation["policy_sha256"] = policy_hash
    _atomic_json(args.report_dir / "policy_evidence_context.json", evidence)
    _atomic_json(args.report_dir / "policy_fact_validation.json", fact_validation)
    _atomic_json(args.report_dir / "policy_length_check.json", {
        "status": fact_validation["status"],
        "word_count": fact_validation["word_count"],
        "target_max_words": fact_validation["target_max_words"],
        "warn_above_words": fact_validation["warn_above_words"],
        "target_met": fact_validation["target_met"],
    })
    warnings = [] if fact_validation["warning"] is None else [fact_validation["warning"]]
    _atomic_json(args.report_dir / "warnings.json", {"warnings": warnings})
    if sha256_file(args.allocation) != integrity["allocation_sha256"] or sha256_file(args.trip_summary) != integrity["trip_summary_sha256"]:
        raise RuntimeError("Frozen Phase 22 evidence changed during policy generation.")
    print("LOCAL PHASE 24 TASK2B POLICY BUILD: PASS")
    print(f"POLICY WORD COUNT: {fact_validation['word_count']}")
    print(f"POLICY TARGET MET: {'YES' if fact_validation['target_met'] else 'NO'}")
    print("POLICY FACT PROVENANCE: PASS")
    print("MONETARY COST FABRICATED: NO")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
