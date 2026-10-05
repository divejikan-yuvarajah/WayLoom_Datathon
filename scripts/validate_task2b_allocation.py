"""Human-local Phase 23 own-validator command; console output is sanitized."""

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
from src.task2b.artifact_integrity import sha256_file
from src.task2b.allocation_validator import (
    build_official_checker_candidate,
    validate_frozen_task2b_allocation,
    validate_validation_config,
    verify_frozen_integrity,
)
from src.task2b.scenario import build_s1_scenario, load_scenario_config


def _inside(path: Path, parent: Path) -> bool:
    return path.resolve().is_relative_to(parent.resolve())


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="phase23_", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(value)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="phase23_", suffix=".csv", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            frame.to_csv(stream, index=False, na_rep="")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--scenario-config", type=Path, required=True)
    parser.add_argument("--validation-config", type=Path, required=True)
    parser.add_argument("--allocation", type=Path, required=True)
    parser.add_argument("--phase22-freeze-manifest", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    args = parser.parse_args()

    with args.validation_config.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    validate_validation_config(config)
    expected_report = (ROOT / config["reports"]["private_output_dir"]).resolve()
    if args.report_dir.resolve() != expected_report or not _inside(args.report_dir, ROOT / "reports/private"):
        raise ValueError("Phase 23 reports must use the configured private directory.")
    if args.allocation.resolve() != (ROOT / config["allocation"]["path"]).resolve():
        raise ValueError("Phase 23 must validate the canonical frozen allocation.")
    if args.phase22_freeze_manifest.resolve() != (ROOT / config["allocation"]["phase22_freeze_manifest"]).resolve():
        raise ValueError("Phase 22 freeze manifest path differs from validation config.")

    frozen_trip_summary_path = ROOT / config["allocation"]["trip_summary_path"]
    integrity = verify_frozen_integrity(
        args.allocation,
        args.phase22_freeze_manifest,
        frozen_trip_summary_path,
    )
    scenario_config = load_scenario_config(str(args.scenario_config))
    discovered = discover_dataset_files(args.raw_root, load_manifest(args.manifest))
    if discovered["discovery_status"] != "PASS":
        raise ValueError("Required official artifacts are missing or duplicated.")
    found = discovered["found_artifacts"]
    file_keys = scenario_config["files"]
    dtypes = {
        "orders": {"order_ref": "string", "outlet_id": "string", "order_weight_kg": "string", "order_volume_m3": "string"},
        "fleet": {"vehicle_id": "string"},
        "vehicles": {"vehicle_id": "string", "weight_cap_kg": "string", "volume_cap_m3": "string"},
        "district_travel": {"depot_to_district_freeflow_min": "string", "inter_stop_freeflow_min": "string"},
        "service_allowance": {"service_allowance_min": "string"},
    }

    def load(key: str) -> pd.DataFrame:
        return pd.read_csv(found[file_keys[key]]["path"], dtype=dtypes.get(key))

    scenario = build_s1_scenario(
        load("orders"), load("fleet"), load("vehicles"),
        load("district_travel"), load("service_allowance"), scenario_config,
    )
    allocation = pd.read_csv(args.allocation, dtype="string", keep_default_na=False)
    frozen_trip_summary = pd.read_csv(
        frozen_trip_summary_path, dtype="string", keep_default_na=False
    )
    report = validate_frozen_task2b_allocation(
        allocation, scenario["orders_s1"], scenario["fleet_s1"], scenario["vehicles_ref"],
        scenario["district_travel_ref"], scenario["service_allowance_ref"], config,
        frozen_trip_summary,
    )
    if (sha256_file(args.allocation) != integrity["allocation_sha256"]
            or sha256_file(frozen_trip_summary_path) != integrity["trip_summary_sha256"]
            or sha256_file(args.phase22_freeze_manifest) != integrity["freeze_manifest_sha256"]):
        raise RuntimeError("Read-only validation inputs changed during validation.")

    args.report_dir.mkdir(parents=True, exist_ok=True)
    summary = report.summary()
    summary.update({
        "frozen_allocation_sha256": integrity["allocation_sha256"],
        "phase22_freeze_manifest_sha256": integrity["freeze_manifest_sha256"],
        "trip_summary_sha256": integrity["trip_summary_sha256"],
    })
    identity_rules = ("allocation_schema", "scenario_values", "order_ref_coverage")
    decision_rules = ("decision_domain", "served_fields", "deferred_fields", "trip_id_domain")
    hard_rules = tuple(name for name in report.rules if name not in identity_rules + decision_rules)
    _atomic_text(args.report_dir / "allocation_identity_audit.json", json.dumps({
        "rules": {name: report.rules[name].__dict__ for name in identity_rules},
        "violations": {name: report.violations[name] for name in identity_rules},
    }, indent=2, sort_keys=True))
    _atomic_text(args.report_dir / "decision_schema_audit.json", json.dumps({
        "rules": {name: report.rules[name].__dict__ for name in decision_rules},
        "violations": {name: report.violations[name] for name in decision_rules},
    }, indent=2, sort_keys=True))
    _atomic_text(args.report_dir / "hard_rule_audit.json", json.dumps({
        "rules": {name: report.rules[name].__dict__ for name in hard_rules},
        "violations": {name: report.violations[name] for name in hard_rules},
    }, indent=2, sort_keys=True))
    _atomic_csv(report.trip_time_audit, args.report_dir / "trip_time_audit.csv")
    _atomic_csv(report.vehicle_budget_audit, args.report_dir / "vehicle_budget_audit.csv")
    _atomic_text(args.report_dir / "warnings.json", json.dumps(report.warnings, indent=2))
    _atomic_text(args.report_dir / "phase23_validation_report.md", "\n".join([
        "# Phase 23 Task 2B validation",
        "",
        f"- Overall status: {report.overall_status}",
        f"- Frozen integrity: {integrity['status']}",
        f"- Checked orders: {report.checked_order_count}",
        f"- Checked trips: {report.checked_trip_count}",
        "- Validator mode: independent, read-only, source-grounded",
    ]) + "\n")

    if report.overall_status == "PASS":
        candidate = build_official_checker_candidate(allocation, scenario["orders_s1"])
        candidate_path = args.report_dir / "checker_workspace" / "submission_task2b.csv"
        _atomic_csv(candidate, candidate_path)
        summary["checker_candidate_sha256"] = sha256_file(candidate_path)
        summary["checker_candidate_path"] = str(candidate_path.resolve())
    _atomic_text(args.report_dir / "validation_summary.json", json.dumps(summary, indent=2, sort_keys=True))

    print(f"LOCAL PHASE 23 OWN VALIDATOR: {report.overall_status}")
    print(f"FROZEN HASH INTEGRITY: {integrity['status']}")
    print(f"CHECKED ORDER COUNT: {report.checked_order_count}")
    print(f"CHECKED TRIP COUNT: {report.checked_trip_count}")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0 if report.overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
