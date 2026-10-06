"""Validate private Phase 26 evidence without rerunning counterfactual solves."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.task2b.artifact_integrity import sha256_file  # noqa: E402
from src.task2b.counterfactual_delta import canonical_objective_vector  # noqa: E402
from src.task2b.priority import OBJECTIVE_LEVELS  # noqa: E402
from src.task2b.reason_codes import (  # noqa: E402
    ALTERNATIVE_OPTIMUM,
    POLICY_TRADEOFF,
    UNAVOIDABLE_HARD,
    validate_reason_assignment,
)


REQUIRED_FILES = (
    "run_manifest.json", "deferral_reasons.csv", "deferral_reason_summary.json",
    "individual_feasibility_audit.csv", "direct_insertion_audit.csv",
    "counterfactual_objective_audit.csv", "counterfactual_change_audit.csv",
    "resource_bottleneck_audit.csv", "reason_consistency_audit.json",
    "demo_examples_private.json", "demo_examples_sanitized.json",
    "frozen_hash_audit.json", "phase26_reasoner_report.md",
)


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reasoner-config", required=True, type=Path)
    parser.add_argument("--allocation", required=True, type=Path)
    parser.add_argument("--submission", required=True, type=Path)
    parser.add_argument("--phase22-freeze-manifest", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    return parser.parse_args()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_bool(value: object) -> bool:
    if value is True or str(value).strip().lower() == "true":
        return True
    if value is False or str(value).strip().lower() == "false":
        return False
    raise ValueError("Expected Boolean evidence value.")


def _no_identifier_keys(value: Any) -> bool:
    forbidden = {"order_ref", "vehicle_id", "outlet_id", "trip_id"}
    if isinstance(value, dict):
        return not forbidden.intersection(map(str, value)) and all(_no_identifier_keys(item) for item in value.values())
    if isinstance(value, list):
        return all(_no_identifier_keys(item) for item in value)
    return True


def main() -> int:
    args = _args()
    config = yaml.safe_load(args.reasoner_config.read_text(encoding="utf-8"))
    if (config.get("version") != 1
            or config.get("reason_codes", {}).get("source") != "phase21"
            or config.get("classification", {}).get("allow_unresolved") is not False
            or config.get("counterfactual", {}).get("require_optimal_policy_stages") is not True
            or config.get("minimal_change", {}).get("require_optimal") is not True
            or config.get("direct_insertion", {}).get("fail_if_direct_insert_possible") is not True):
        raise ValueError("Phase 26 safety configuration is invalid.")
    expected_report = ROOT / config["reports"]["private_output_dir"]
    if args.report_dir.resolve() != expected_report.resolve():
        raise ValueError("Phase 26 report directory differs from configuration.")
    missing = [name for name in REQUIRED_FILES if not (args.report_dir / name).is_file()]
    if missing:
        raise ValueError("Phase 26 evidence is incomplete: " + ", ".join(missing))
    freeze = _json(args.phase22_freeze_manifest)
    manifest = _json(args.report_dir / "run_manifest.json")
    try:
        frozen_vector = canonical_objective_vector(freeze.get("objective_vector"))
    except Exception as exc:
        raise ValueError("Phase 22 freeze evidence has an invalid objective vector.") from exc
    if freeze.get("phase") != 22 or freeze.get("state") != "FROZEN":
        raise ValueError("Phase 22 freeze evidence is invalid.")
    if (manifest.get("phase") != 26 or manifest.get("status") != "PASS"
            or manifest.get("counterfactuals_unresolved") != 0
            or manifest.get("row_identifiers_in_aggregate_manifest") is not False):
        raise ValueError("Phase 26 run manifest is not publishable.")
    trip_summary = ROOT / config["frozen"]["trip_summary_path"]
    priority = ROOT / config["frozen"]["priority_config_path"]
    optimizer = ROOT / config["frozen"]["optimizer_config_path"]
    policy = ROOT / config["frozen"]["policy_path"]
    checks = {
        "allocation": sha256_file(args.allocation) == freeze.get("allocation_sha256"),
        "trip_summary": sha256_file(trip_summary) == freeze.get("trip_summary_sha256"),
        "priority": sha256_file(priority) == freeze.get("priority_config_hash"),
        "optimizer": sha256_file(optimizer) == freeze.get("solver_config_hash"),
        "submission": sha256_file(args.submission) == _json(
            ROOT / config["frozen"]["phase24_export_manifest"]
        ).get("submission_task2b_sha256"),
        "policy": sha256_file(policy) == _json(
            ROOT / config["frozen"]["phase24_policy_validation"]
        ).get("policy_sha256"),
    }
    if not all(checks.values()):
        raise ValueError("A frozen Phase 22/24 artifact hash changed.")
    if (manifest.get("phase22_frozen_allocation_sha256") != freeze.get("allocation_sha256")
            or manifest.get("phase22_trip_summary_sha256") != freeze.get("trip_summary_sha256")
            or manifest.get("phase21_priority_config_sha256") != sha256_file(priority)
            or manifest.get("phase22_optimizer_config_sha256") != sha256_file(optimizer)
            or manifest.get("counterfactual_config_sha256") != sha256_file(args.reasoner_config)):
        raise ValueError("Phase 26 manifest hashes do not match current frozen inputs/config.")
    hash_audit = _json(args.report_dir / "frozen_hash_audit.json")
    if (hash_audit.get("status") != "PASS" or hash_audit.get("all_unchanged") is not True
            or hash_audit.get("before") != hash_audit.get("after")):
        raise ValueError("Phase 26 frozen-hash audit failed.")
    current_paths = [args.allocation, trip_summary, args.submission, policy, priority, args.phase22_freeze_manifest]
    current_hashes = {
        path.resolve().relative_to(ROOT.resolve()).as_posix(): sha256_file(path)
        for path in current_paths
    }
    if current_hashes != hash_audit.get("after"):
        raise ValueError("Current frozen artifacts differ from the completed Phase 26 hash audit.")

    allocation = pd.read_csv(args.allocation, dtype="string", keep_default_na=False)
    deferred = allocation.loc[allocation["decision"].eq("deferred"), "order_ref"].astype(str)
    reasons = pd.read_csv(args.report_dir / "deferral_reasons.csv", dtype={"order_ref": "string"})
    required = {
        "order_ref", "reason_class", "primary_reason_code", "secondary_reason_codes",
        "individually_feasible", "direct_insert_possible", "forced_solve_status",
        "forced_policy_vector_relation", "minimum_changed_orders", "counterfactual_complete",
        "human_explanation",
    }
    if required.difference(reasons.columns) or reasons.order_ref.duplicated().any():
        raise ValueError("Deferral reason table schema/grain is invalid.")
    if set(reasons.order_ref.astype(str)) != set(deferred) or len(reasons) != len(deferred):
        raise ValueError("Deferral reason coverage differs from the frozen allocation.")
    if (manifest.get("deferred_order_count") != len(deferred)
            or manifest.get("counterfactuals_attempted") != len(deferred)
            or manifest.get("counterfactuals_resolved") != len(deferred)):
        raise ValueError("Phase 26 manifest counts differ from private reason evidence.")
    for row in reasons.to_dict("records"):
        secondary = json.loads(row["secondary_reason_codes"])
        validate_reason_assignment(row["reason_class"], row["primary_reason_code"], secondary)
        individually_feasible = _as_bool(row["individually_feasible"])
        if _as_bool(row["direct_insert_possible"]):
            raise ValueError("Direct insertion contradiction is present.")
        if not _as_bool(row["counterfactual_complete"]):
            raise ValueError("Unresolved deferral explanation is present.")
        if str(row["order_ref"]) in str(row["human_explanation"]):
            raise ValueError("Human-readable explanation contains its private order reference.")
        if row["reason_class"] == UNAVOIDABLE_HARD:
            if individually_feasible or row["forced_solve_status"] != "INFEASIBLE":
                raise ValueError("Hard-unavoidable classification lacks hard-infeasibility proof.")
        elif row["reason_class"] == POLICY_TRADEOFF:
            if not individually_feasible or row["forced_solve_status"] != "OPTIMAL" or row["forced_policy_vector_relation"] != "WORSE":
                raise ValueError("Policy-tradeoff classification lacks optimal worse-vector proof.")
        elif row["reason_class"] == ALTERNATIVE_OPTIMUM:
            if not individually_feasible or row["forced_solve_status"] != "OPTIMAL" or row["forced_policy_vector_relation"] != "EQUAL":
                raise ValueError("Alternative optimum lacks equal-vector proof.")
        else:
            raise ValueError("Unknown final reason class.")
        if row["reason_class"] != UNAVOIDABLE_HARD and pd.isna(row["minimum_changed_orders"]):
            raise ValueError("Hard-feasible reason lacks proven minimum-change evidence.")

    objectives = pd.read_csv(args.report_dir / "counterfactual_objective_audit.csv")
    for row in objectives.to_dict("records"):
        baseline = json.loads(row["baseline_objective_vector"])
        if tuple(baseline) != OBJECTIVE_LEVELS or baseline != frozen_vector:
            raise ValueError("Baseline objective vector differs from frozen Phase 22 evidence.")
        if row["forced_solve_status"] == "OPTIMAL" and int(row["optimal_stage_count"]) != 9:
            raise ValueError("A forced counterfactual lacks nine optimal stages.")
    changes = pd.read_csv(args.report_dir / "counterfactual_change_audit.csv")
    if changes["order_ref"].astype(str).duplicated().any():
        raise ValueError("Counterfactual change audit has duplicate target rows.")
    feasible_orders = set(reasons.loc[reasons["reason_class"].ne(UNAVOIDABLE_HARD), "order_ref"].astype(str))
    change_status = changes.set_index(changes["order_ref"].astype(str))["minimal_change_status"].to_dict()
    if any(change_status.get(order_ref) != "OPTIMAL" for order_ref in feasible_orders):
        raise ValueError("A hard-feasible target lacks an optimal minimal-change witness.")

    consistency = _json(args.report_dir / "reason_consistency_audit.json")
    if (consistency.get("status") != "PASS" or consistency.get("unresolved_count") != 0
            or consistency.get("direct_insertion_contradiction_count") != 0
            or consistency.get("all_counterfactuals_complete") is not True):
        raise ValueError("Reason-consistency audit failed.")
    sanitized = _json(args.report_dir / "demo_examples_sanitized.json")
    if not isinstance(sanitized, list) or not (1 <= len(sanitized) <= 2) or not _no_identifier_keys(sanitized):
        raise ValueError("Sanitized demo examples violate count/privacy requirements.")
    serialized = json.dumps(sanitized, sort_keys=True)
    if any(order_ref and order_ref in serialized for order_ref in allocation["order_ref"].astype(str)):
        raise ValueError("Sanitized demo examples expose a real order reference.")
    phase27 = [path for root in (ROOT / "src", ROOT / "scripts", ROOT / "configs", ROOT / "tests")
               for path in root.rglob("*") if "phase27" in path.name.lower()]
    if phase27:
        raise ValueError("Phase 27 implementation exists before the Phase 26 gate.")

    print("LOCAL PHASE 26 DEFERRAL REASONER VALIDATION: PASS")
    print(f"DEFERRED REASON COVERAGE: {len(reasons)} / {len(deferred)}")
    print("REASON CONSISTENCY: PASS")
    print("COUNTERFACTUAL OPTIMALITY EVIDENCE: PASS")
    print("DEMO ANONYMIZATION: PASS")
    print("FROZEN HASH INTEGRITY: PASS")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
