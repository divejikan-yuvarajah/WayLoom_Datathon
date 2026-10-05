"""Human-local Phase 24 export from the frozen allocation and official template."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest
from src.task2b.allocation_validator import verify_frozen_integrity
from src.task2b.artifact_integrity import sha256_file
from src.task2b.policy_evidence import (
    load_phase23_candidate_if_available,
    load_phase23_pass_evidence,
)
from src.task2b.submission import (
    build_task2b_submission,
    validate_output_config,
    write_task2b_submission_atomic,
)


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
    parser.add_argument("--output-config", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--allocation", required=True, type=Path)
    parser.add_argument("--phase22-freeze-manifest", required=True, type=Path)
    parser.add_argument("--phase23-evidence", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(args.output_config.read_text(encoding="utf-8"))
    validate_output_config(config)
    expected_output = (ROOT / config["output"]["path"]).resolve()
    expected_allocation = (ROOT / config["phase22"]["allocation_path"]).resolve()
    expected_freeze = (ROOT / config["phase22"]["freeze_manifest_path"]).resolve()
    expected_reports = (ROOT / config["policy"]["private_report_dir"]).resolve()
    if args.output.resolve() != expected_output or args.output.name != config["output"]["filename"]:
        raise ValueError("Phase 24 output path or filename differs from the canonical contract.")
    if args.allocation.resolve() != expected_allocation or args.phase22_freeze_manifest.resolve() != expected_freeze:
        raise ValueError("Phase 24 must use the canonical frozen Phase 22 allocation and manifest.")
    if args.report_dir.resolve() != expected_reports:
        raise ValueError("Phase 24 reports must use the configured private directory.")
    if args.template.name != config["output"]["official_template_filename"]:
        raise ValueError("The requested template filename is not the official Task 2B template.")

    discovery = discover_dataset_files(args.raw_root, load_manifest(args.manifest))
    if discovery["discovery_status"] != "PASS":
        raise ValueError("Official dataset discovery failed.")
    found = discovery["found_artifacts"]
    template_path = _artifact(found, config["output"]["official_template_filename"])
    orders_path = _artifact(found, config["source_files"]["orders"])
    fleet_path = _artifact(found, config["source_files"]["fleet"])

    integrity = verify_frozen_integrity(args.allocation, args.phase22_freeze_manifest)
    evidence, evidence_path = load_phase23_pass_evidence(
        args.phase23_evidence,
        expected_frozen_allocation_sha256=integrity["allocation_sha256"],
    )
    phase23_candidate, _ = load_phase23_candidate_if_available(evidence_path, evidence)

    template = pd.read_csv(template_path, dtype="string", keep_default_na=False)
    allocation = pd.read_csv(args.allocation, dtype="string", keep_default_na=False)
    orders = pd.read_csv(orders_path, dtype="string", keep_default_na=False)
    orders = orders.loc[orders.scenario.eq(config["scenario"]["expected_id"])].copy()
    fleet = pd.read_csv(fleet_path, dtype="string", keep_default_na=False)
    fleet = fleet.loc[fleet.scenario.eq(config["scenario"]["expected_id"])].copy()
    submission = build_task2b_submission(template, allocation, orders)

    export_manifest_path = args.report_dir / "export_manifest.json"
    existing_manifest = None
    if export_manifest_path.is_file():
        existing_manifest = json.loads(export_manifest_path.read_text(encoding="utf-8"))
    if export_manifest_path.exists() and not args.output.exists() and not args.force:
        raise ValueError("Export evidence already exists without the canonical output; refusing an ambiguous rerun.")
    report = write_task2b_submission_atomic(
        args.output,
        submission,
        template,
        allocation,
        orders,
        source_allocation_sha256=integrity["allocation_sha256"],
        known_vehicle_ids=fleet.vehicle_id,
        phase23_candidate=phase23_candidate,
        force=args.force,
        existing_export_manifest=existing_manifest,
    )
    if sha256_file(args.allocation) != integrity["allocation_sha256"]:
        raise RuntimeError("Frozen Phase 22 allocation changed during export.")

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    manifest = {
        "phase": 24,
        "state": "FINAL_EXPORTED",
        "official_template_sha256": sha256_file(template_path),
        "phase22_frozen_allocation_sha256": integrity["allocation_sha256"],
        "phase23_checker_input_sha256": evidence.get("checker_input_sha256"),
        "submission_task2b_sha256": report["submission_task2b_sha256"],
        "row_count": report["row_count"],
        "column_list": report["column_list"],
        "identity_preservation": report["identity_preservation"],
        "placeholder_audit": report["placeholder_audit"],
        "allocation_parity": report["allocation_parity"],
        "phase23_checker_candidate_parity": report["phase23_checker_candidate_parity"],
        "phase23_own_validator": evidence["own_validator_status"],
        "phase23_official_checker": evidence["official_checker_status"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit.stdout.strip() if commit.returncode == 0 else None,
    }
    _atomic_json(export_manifest_path, manifest)
    _atomic_json(args.report_dir / "template_identity_audit.json", {
        "status": "PASS", "row_count": report["row_count"],
        "scenario_preserved": True, "order_ref_preserved": True,
        "outlet_id_preserved": True, "template_order_preserved": True,
    })
    _atomic_json(args.report_dir / "placeholder_audit.json", {
        "status": "PASS", "remaining_placeholder_count": 0,
    })
    _atomic_json(args.report_dir / "allocation_parity_audit.json", {
        "status": "PASS", "phase22_allocation_parity": "PASS",
        "phase23_checker_candidate_parity": report["phase23_checker_candidate_parity"],
    })
    print("LOCAL PHASE 24 TASK2B EXPORT: PASS")
    print(f"EXPORTED ROW COUNT: {report['row_count']}")
    print("IDENTITY PRESERVATION: PASS")
    print("PLACEHOLDER AUDIT: PASS")
    print("FROZEN ALLOCATION PARITY: PASS")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
