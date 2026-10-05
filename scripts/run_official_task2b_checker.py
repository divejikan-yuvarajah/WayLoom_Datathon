"""Human-local wrapper for the inspected organizer Task 2B checker interface."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.data_inventory import load_manifest
from src.task2b.artifact_integrity import sha256_file
from src.task2b.allocation_validator import validate_validation_config, verify_frozen_integrity
from src.task2b.checker_evidence import (
    build_checker_evidence,
    require_successful_cross_validation,
    save_checker_evidence,
)
from src.task2b.checker_runner import (
    discover_official_checker_interface,
    locate_official_checker,
    run_official_checker,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--validation-config", type=Path, required=True)
    parser.add_argument("--allocation", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    args = parser.parse_args()

    with args.validation_config.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    validate_validation_config(config)
    if args.report_dir.resolve() != (ROOT / config["reports"]["private_output_dir"]).resolve():
        raise ValueError("Official checker reports must use the configured private directory.")
    if args.allocation.resolve() != (ROOT / config["allocation"]["path"]).resolve():
        raise ValueError("Official checker wrapper requires the frozen canonical allocation.")
    integrity = verify_frozen_integrity(
        args.allocation,
        ROOT / config["allocation"]["phase22_freeze_manifest"],
        ROOT / config["allocation"]["trip_summary_path"],
    )
    summary_path = args.report_dir / "validation_summary.json"
    if not summary_path.is_file():
        raise ValueError("Run the Phase 23 own validator before the official checker.")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if (summary.get("status") != "PASS"
            or summary.get("frozen_allocation_sha256") != integrity["allocation_sha256"]
            or summary.get("phase22_freeze_manifest_sha256") != integrity["freeze_manifest_sha256"]
            or summary.get("trip_summary_sha256") != integrity["trip_summary_sha256"]):
        raise ValueError("Own-validator PASS for the current frozen allocation is required.")
    checker_config = config["official_checker"]
    candidate = Path(summary.get("checker_candidate_path", ""))
    expected_candidate = (ROOT / checker_config["private_workspace"] / "submission_task2b.csv").resolve()
    if (candidate.resolve() != expected_candidate or not candidate.is_file()
            or sha256_file(candidate) != summary.get("checker_candidate_sha256")):
        raise ValueError("Private checker candidate is missing or changed.")

    checker_path = locate_official_checker(
        ROOT, args.raw_root, load_manifest(args.manifest), checker_config["repository_path"]
    )
    interface = discover_official_checker_interface(checker_path, config)
    result = run_official_checker(interface, candidate)
    if verify_frozen_integrity(
        args.allocation,
        ROOT / config["allocation"]["phase22_freeze_manifest"],
        ROOT / config["allocation"]["trip_summary_path"],
    ) != integrity:
        raise RuntimeError("Frozen Phase 22 evidence changed during checker execution.")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True, check=False)
    timestamp = datetime.now(timezone.utc)
    evidence = build_checker_evidence(
        result,
        frozen_allocation_sha256=integrity["allocation_sha256"],
        phase22_freeze_manifest_sha256=integrity["freeze_manifest_sha256"],
        python_version=sys.version,
        own_validator_status="PASS",
        git_commit=commit.stdout.strip() if commit.returncode == 0 else None,
        timestamp=timestamp.isoformat(),
    )
    run_name = timestamp.strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir = ROOT / checker_config["evidence_runs_dir"] / run_name
    save_checker_evidence(run_dir, evidence, result.stdout, result.stderr)
    print(f"LOCAL PHASE 23 OFFICIAL CHECKER: {evidence['official_checker_status']}")
    print(f"OWN VALIDATOR: {evidence['own_validator_status']}")
    print("CHECKER OUTPUT CAPTURED PRIVATELY: YES")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    require_successful_cross_validation(evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
