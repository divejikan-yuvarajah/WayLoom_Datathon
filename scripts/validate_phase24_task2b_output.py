"""Human-local final Phase 24 validation without optimizer or checker execution."""

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
from src.task2b.policy_evidence import (
    load_phase23_candidate_if_available,
    load_phase23_pass_evidence,
    validate_policy_evidence,
)
from src.task2b.policy_writer import validate_policy_text
from src.task2b.submission import validate_output_config, validate_task2b_submission


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix="phase24_", suffix=path.suffix, dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(value)
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
    parser.add_argument("--submission", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--allocation", required=True, type=Path)
    parser.add_argument("--phase22-freeze-manifest", required=True, type=Path)
    parser.add_argument("--phase23-evidence", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    args = parser.parse_args()

    config = yaml.safe_load(args.output_config.read_text(encoding="utf-8"))
    validate_output_config(config)
    expected_paths = {
        "submission": ROOT / config["output"]["path"],
        "policy": ROOT / config["policy"]["output_path"],
        "allocation": ROOT / config["phase22"]["allocation_path"],
        "phase22_freeze_manifest": ROOT / config["phase22"]["freeze_manifest_path"],
        "report_dir": ROOT / config["policy"]["private_report_dir"],
    }
    for name, expected in expected_paths.items():
        if getattr(args, name).resolve() != expected.resolve():
            raise ValueError(f"Phase 24 {name.replace('_', ' ')} path differs from configuration.")
    if not args.submission.is_file() or args.submission.name != "submission_task2b.csv":
        raise ValueError("Canonical outputs/submission_task2b.csv is missing.")
    if not args.policy.is_file() or args.policy.name != "task2b_policy.md":
        raise ValueError("Canonical docs/task2b_policy.md is missing.")

    trip_summary = ROOT / config["phase22"]["trip_summary_path"]
    integrity = verify_frozen_integrity(args.allocation, args.phase22_freeze_manifest, trip_summary)
    evidence, evidence_path = load_phase23_pass_evidence(
        args.phase23_evidence,
        expected_frozen_allocation_sha256=integrity["allocation_sha256"],
    )
    phase23_candidate, _ = load_phase23_candidate_if_available(evidence_path, evidence)
    discovery = discover_dataset_files(args.raw_root, load_manifest(args.manifest))
    if discovery["discovery_status"] != "PASS":
        raise ValueError("Official dataset discovery failed.")
    found = discovery["found_artifacts"]
    template_path = _artifact(found, config["output"]["official_template_filename"])
    orders_path = _artifact(found, config["source_files"]["orders"])
    fleet_path = _artifact(found, config["source_files"]["fleet"])
    template = pd.read_csv(template_path, dtype="string", keep_default_na=False)
    orders = pd.read_csv(orders_path, dtype="string", keep_default_na=False)
    orders = orders.loc[orders.scenario.eq(config["scenario"]["expected_id"])].copy()
    fleet = pd.read_csv(fleet_path, dtype="string", keep_default_na=False)
    allocation = pd.read_csv(args.allocation, dtype="string", keep_default_na=False)
    submission = pd.read_csv(args.submission, dtype="string", keep_default_na=False)
    submission_report = validate_task2b_submission(
        submission,
        template,
        allocation,
        orders,
        known_vehicle_ids=fleet.vehicle_id,
        phase23_candidate=phase23_candidate,
    )

    export_manifest_path = args.report_dir / "export_manifest.json"
    policy_evidence_path = args.report_dir / "policy_evidence_context.json"
    fact_validation_path = args.report_dir / "policy_fact_validation.json"
    if not all(path.is_file() for path in (export_manifest_path, policy_evidence_path, fact_validation_path)):
        raise ValueError("Phase 24 export and policy evidence are incomplete.")
    export_manifest = json.loads(export_manifest_path.read_text(encoding="utf-8"))
    expected_manifest = {
        "phase": 24,
        "state": "FINAL_EXPORTED",
        "official_template_sha256": sha256_file(template_path),
        "phase22_frozen_allocation_sha256": integrity["allocation_sha256"],
        "phase23_checker_input_sha256": evidence["checker_input_sha256"],
        "submission_task2b_sha256": sha256_file(args.submission),
        "row_count": submission_report["row_count"],
        "column_list": submission_report["column_list"],
        "identity_preservation": "PASS",
        "placeholder_audit": "PASS",
        "allocation_parity": "PASS",
        "phase23_own_validator": "PASS",
        "phase23_official_checker": "PASS",
    }
    if any(export_manifest.get(key) != value for key, value in expected_manifest.items()):
        raise ValueError("Phase 24 export manifest does not match current validated artifacts.")

    policy_evidence = json.loads(policy_evidence_path.read_text(encoding="utf-8"))
    validate_policy_evidence(policy_evidence)
    expected_bindings = {
        "phase22_frozen_allocation_sha256": integrity["allocation_sha256"],
        "phase23_checker_input_sha256": evidence["checker_input_sha256"],
        "trip_summary_sha256": integrity["trip_summary_sha256"],
    }
    if policy_evidence.get("bindings") != expected_bindings:
        raise ValueError("Policy evidence is bound to different frozen/checker artifacts.")
    fact_validation = json.loads(fact_validation_path.read_text(encoding="utf-8"))
    policy = args.policy.read_text(encoding="utf-8")
    private_ids = set(orders.order_ref.astype(str)) | set(orders.outlet_id.astype(str)) | set(fleet.vehicle_id.astype(str))
    private_ids = {value for value in private_ids if len(value) >= 4}
    policy_report = validate_policy_text(
        policy,
        policy_evidence,
        used_facts=fact_validation.get("used_facts", {}),
        private_identifiers=private_ids,
        target_max_words=config["policy"]["target_max_words"],
        warn_above_words=config["policy"]["warn_above_words"],
    )
    if fact_validation.get("policy_sha256") != sha256_file(args.policy):
        raise ValueError("Policy changed after fact validation.")
    if sha256_file(args.allocation) != integrity["allocation_sha256"] or sha256_file(trip_summary) != integrity["trip_summary_sha256"]:
        raise RuntimeError("Frozen Phase 22 evidence changed during Phase 24 validation.")

    report = "\n".join([
        "# Phase 24 Task 2B output validation",
        "",
        "- Phase 22 frozen integrity: PASS",
        "- Phase 23 own validator: PASS",
        "- Phase 23 official checker: PASS",
        "- Official template identity preservation: PASS",
        "- Placeholder audit: PASS",
        "- Frozen allocation parity: PASS",
        f"- Phase 23 checker-candidate parity: {submission_report['phase23_checker_candidate_parity']}",
        "- Policy fact provenance: PASS",
        f"- Policy word count: {policy_report['word_count']}",
        f"- Preferred length target met: {'YES' if policy_report['target_met'] else 'NO'}",
        "- Private row identifiers in policy: NO",
    ]) + "\n"
    _atomic_text(args.report_dir / "phase24_output_report.md", report)
    print("LOCAL PHASE 24 TASK2B OUTPUT VALIDATION: PASS")
    print("PHASE23 PRECONDITION: PASS")
    print("PHASE22 FROZEN HASH: PASS")
    print("OFFICIAL TEMPLATE AND IDENTITY: PASS")
    print("PLACEHOLDERS REMOVED: PASS")
    print("FROZEN ALLOCATION PARITY: PASS")
    print("POLICY FACTS AND LENGTH: PASS")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
