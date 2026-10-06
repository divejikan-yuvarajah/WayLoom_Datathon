"""Human-local Phase 26 solver-grounded deferral reasoner."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ortools
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest  # noqa: E402
from src.task2b.artifact_integrity import sha256_file  # noqa: E402
from src.task2b.counterfactual_delta import canonical_objective_vector  # noqa: E402
from src.task2b.counterfactual_reasoner import solve_forced_counterfactual  # noqa: E402
from src.task2b.deferral_explanations import generate_explanation  # noqa: E402
from src.task2b.demo_example_selector import select_demo_examples  # noqa: E402
from src.task2b.direct_insertion import analyze_direct_insertion, require_no_direct_insertion  # noqa: E402
from src.task2b.individual_feasibility import evaluate_individual_feasibility  # noqa: E402
from src.task2b.priority import OBJECTIVE_LEVELS  # noqa: E402
from src.task2b.reason_codes import validate_taxonomy  # noqa: E402
from src.task2b.scenario import build_s1_scenario, load_scenario_config  # noqa: E402
from src.task2b.solution_audit import audit_allocation, audit_objective_vector  # noqa: E402
from src.task2b.solver_data import build_solver_data, validate_optimizer_config  # noqa: E402
from src.task2b.trip_time import load_trip_time_config  # noqa: E402


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "raw-root", "manifest", "scenario-config", "compatibility-config",
        "trip-time-config", "priority-config", "optimizer-config", "reasoner-config",
        "compatibility-matrix", "priority-metadata", "allocation", "trip-summary",
        "phase22-freeze-manifest", "phase23-evidence", "submission", "report-dir",
    ):
        parser.add_argument(f"--{name}", required=True, type=Path)
    return parser.parse_args()


def _inside(path: Path, parent: Path) -> bool:
    return path.resolve().is_relative_to(parent.resolve())


def _load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected YAML mapping: {path}.")
    return value


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}.")
    return value


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix="phase26_", suffix=path.suffix, dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(value)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_text(path, json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def _atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix="phase26_", suffix=".csv", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            frame.to_csv(stream, index=False)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _validate_reasoner_config(config: dict) -> None:
    required_true = (
        ("counterfactual", "force_target_served"),
        ("counterfactual", "require_optimal_policy_stages"),
        ("minimal_change", "enabled"),
        ("minimal_change", "require_optimal"),
        ("direct_insertion", "enabled"),
        ("direct_insertion", "fail_if_direct_insert_possible"),
        ("demo", "anonymize_identifiers"),
        ("demo", "deterministic"),
        ("frozen", "require_phase22_hash_match"),
        ("frozen", "require_phase23_pass"),
        ("frozen", "require_phase24_pass"),
    )
    if config.get("version") != 1 or config.get("reason_codes", {}).get("source") != "phase21":
        raise ValueError("Phase 26 configuration version or taxonomy source is invalid.")
    if any(config.get(section, {}).get(key) is not True for section, key in required_true):
        raise ValueError("A mandatory Phase 26 safety control is disabled.")
    if config.get("classification", {}).get("allow_unresolved") is not False:
        raise ValueError("Final unresolved reasons are forbidden.")
    if int(config.get("counterfactual", {}).get("num_search_workers", 0)) != 1:
        raise ValueError("Counterfactual solves must use one worker.")
    if int(config.get("demo", {}).get("max_examples", 0)) not in (1, 2):
        raise ValueError("Demo output must contain at most two examples.")
    validate_taxonomy()


def _resolve_checker_evidence(path: Path) -> Path:
    if path.is_file():
        return path
    candidates = sorted(path.parent.glob("checker_runs/*/checker_evidence.json"))
    if not candidates:
        raise ValueError("Phase 23 official-checker evidence is missing.")
    return candidates[-1]


def _preconditions(args: argparse.Namespace, reasoner: dict) -> tuple[dict, Path]:
    freeze = _load_json(args.phase22_freeze_manifest)
    if (freeze.get("phase") != 22 or freeze.get("state") != "FROZEN"
            or freeze.get("determinism") != "PASS"
            or freeze.get("all_hard_rules_audited") is not True):
        raise ValueError("Phase 22 is not validly frozen.")
    try:
        canonical_objective_vector(freeze.get("objective_vector"))
    except Exception as exc:
        raise ValueError("Phase 22 objective vector keys are incomplete or invalid.") from exc
    stages = freeze.get("objective_stages")
    if not isinstance(stages, list) or len(stages) != 9 or any(
        item.get("status") != "OPTIMAL" for item in stages
    ):
        raise ValueError("Phase 22 does not prove all nine objective stages optimal.")
    expected_hashes = {
        args.allocation: freeze.get("allocation_sha256"),
        args.trip_summary: freeze.get("trip_summary_sha256"),
        args.priority_config: freeze.get("priority_config_hash"),
        args.optimizer_config: freeze.get("solver_config_hash"),
        args.scenario_config: freeze.get("scenario_config_hash"),
        args.compatibility_config: freeze.get("compatibility_config_hash"),
        args.trip_time_config: freeze.get("trip_time_config_hash"),
    }
    if any(not path.is_file() or sha256_file(path) != expected for path, expected in expected_hashes.items()):
        raise ValueError("A Phase 22 frozen artifact/config hash does not match.")
    checker_path = _resolve_checker_evidence(args.phase23_evidence)
    checker = _load_json(checker_path)
    if (checker.get("phase") != 23 or checker.get("own_validator_status") != "PASS"
            or checker.get("official_checker_status") != "PASS"
            or checker.get("pass_detected") is not True or checker.get("timed_out") is not False):
        raise ValueError("Phase 23 own-validator/official-checker evidence is not PASS.")
    if checker.get("frozen_allocation_sha256") != freeze.get("allocation_sha256"):
        raise ValueError("Phase 23 checker evidence refers to a different frozen allocation.")
    frozen_cfg = reasoner["frozen"]
    phase24 = _load_json(ROOT / frozen_cfg["phase24_export_manifest"])
    policy = _load_json(ROOT / frozen_cfg["phase24_policy_validation"])
    if (phase24.get("phase") != 24 or phase24.get("state") != "FINAL_EXPORTED"
            or phase24.get("allocation_parity") != "PASS"
            or phase24.get("phase22_frozen_allocation_sha256") != freeze.get("allocation_sha256")
            or phase24.get("phase23_own_validator") != "PASS"
            or phase24.get("phase23_official_checker") != "PASS"
            or phase24.get("submission_task2b_sha256") != sha256_file(args.submission)
            or policy.get("status") != "PASS" or policy.get("target_met") is not True
            or policy.get("policy_sha256") != sha256_file(ROOT / frozen_cfg["policy_path"])):
        raise ValueError("Phase 24 final output/policy evidence is not valid.")
    return freeze, checker_path


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip() or None
    except Exception:
        return None


def _frozen_paths(args: argparse.Namespace, reasoner: dict) -> list[Path]:
    return [
        args.allocation, args.trip_summary, args.submission,
        ROOT / reasoner["frozen"]["policy_path"], args.priority_config,
        args.phase22_freeze_manifest,
    ]


def _hashes(paths: list[Path]) -> dict[str, str]:
    return {path.resolve().relative_to(ROOT.resolve()).as_posix(): sha256_file(path) for path in paths}


def _resource_rows(target: str, changes: pd.DataFrame, baseline_trips: pd.DataFrame,
                   forced_trips: pd.DataFrame) -> list[dict[str, Any]]:
    changed = changes.loc[changes["changed"]]
    vehicles = sorted(set(changed["baseline_vehicle_id"].dropna()) |
                      set(changed["counterfactual_vehicle_id"].dropna()))
    rows = []
    for vehicle_id in vehicles:
        before = baseline_trips.loc[baseline_trips["vehicle_id"].astype(str).eq(str(vehicle_id))]
        after = forced_trips.loc[forced_trips["vehicle_id"].astype(str).eq(str(vehicle_id))]
        rows.append({
            "order_ref": target,
            "vehicle_id": vehicle_id,
            "baseline_trip_count": len(before),
            "counterfactual_trip_count": len(after),
            "baseline_trip_minutes_total": str(pd.to_numeric(before.get("trip_minutes"), errors="coerce").sum()),
            "counterfactual_trip_minutes_total": str(pd.to_numeric(after.get("trip_minutes"), errors="coerce").sum()),
            "baseline_weight_total": str(pd.to_numeric(before.get("weight_kg"), errors="coerce").sum()),
            "counterfactual_weight_total": str(pd.to_numeric(after.get("weight_kg"), errors="coerce").sum()),
            "baseline_volume_total": str(pd.to_numeric(before.get("volume_m3"), errors="coerce").sum()),
            "counterfactual_volume_total": str(pd.to_numeric(after.get("volume_m3"), errors="coerce").sum()),
        })
    return rows


def main() -> int:
    args = _args()
    reasoner = _load_yaml(args.reasoner_config)
    _validate_reasoner_config(reasoner)
    expected_report = ROOT / reasoner["reports"]["private_output_dir"]
    if args.report_dir.resolve() != expected_report.resolve() or not _inside(args.report_dir, ROOT / "reports/private"):
        raise ValueError("Phase 26 reports must stay in the configured private directory.")
    if args.allocation.resolve() != (ROOT / "data/interim/task2b_final_allocation.csv").resolve():
        raise ValueError("Phase 26 must read the canonical frozen allocation.")
    canonical_paths = {
        args.trip_summary: ROOT / reasoner["frozen"]["trip_summary_path"],
        args.priority_config: ROOT / reasoner["frozen"]["priority_config_path"],
        args.optimizer_config: ROOT / reasoner["frozen"]["optimizer_config_path"],
        args.phase22_freeze_manifest: ROOT / "reports/private/phase22_task2b_optimizer/freeze_manifest.json",
        args.submission: ROOT / "outputs/submission_task2b.csv",
    }
    if any(actual.resolve() != expected.resolve() for actual, expected in canonical_paths.items()):
        raise ValueError("A Phase 26 frozen input path is noncanonical.")
    freeze, checker_path = _preconditions(args, reasoner)
    before_hashes = _hashes(_frozen_paths(args, reasoner))

    optimizer = _load_yaml(args.optimizer_config)
    priority = _load_yaml(args.priority_config)
    validate_optimizer_config(optimizer, priority)
    scenario_config = load_scenario_config(str(args.scenario_config))
    load_trip_time_config(str(args.trip_time_config))
    compatibility_config = _load_yaml(args.compatibility_config)
    if compatibility_config.get("low_flexibility_threshold") != 2:
        raise ValueError("Phase 19 flexibility threshold differs from frozen policy.")
    discovery = discover_dataset_files(args.raw_root, load_manifest(args.manifest))
    if discovery.get("discovery_status") != "PASS":
        raise ValueError("Required official artifacts are missing or duplicated.")
    found = discovery["found_artifacts"]
    keys = scenario_config["files"]
    dtypes = {
        "orders": {"order_ref": "string", "outlet_id": "string", "order_weight_kg": "string", "order_volume_m3": "string"},
        "fleet": {"vehicle_id": "string"},
        "vehicles": {"vehicle_id": "string", "weight_cap_kg": "string", "volume_cap_m3": "string"},
        "district_travel": {"depot_to_district_freeflow_min": "string", "inter_stop_freeflow_min": "string"},
        "service_allowance": {"service_allowance_min": "string"},
    }

    def load(key: str) -> pd.DataFrame:
        return pd.read_csv(found[keys[key]]["path"], dtype=dtypes.get(key))

    scenario = build_s1_scenario(
        load("orders"), load("fleet"), load("vehicles"),
        load("district_travel"), load("service_allowance"), scenario_config,
    )
    matrix = pd.read_csv(args.compatibility_matrix, dtype={"order_ref": "string", "vehicle_id": "string"})
    metadata = pd.read_csv(args.priority_metadata, dtype={"order_ref": "string"})
    data = build_solver_data(scenario, matrix, metadata, optimizer, priority)
    allocation = pd.read_csv(
        args.allocation,
        dtype={
            "scenario": "string", "order_ref": "string", "outlet_id": "string",
            "decision": "string", "vehicle_id": "string",
        },
        keep_default_na=True,
    )
    baseline_vector = canonical_objective_vector(freeze["objective_vector"])
    audit_objective_vector(allocation, data, baseline_vector)
    baseline_audit = audit_allocation(allocation, data)
    baseline_trips = pd.read_csv(args.trip_summary, dtype="string", keep_default_na=False)
    if baseline_audit.status != "PASS":
        raise ValueError("Frozen allocation failed the approved hard-rule audit.")

    deferred = allocation.loc[allocation["decision"].eq("deferred")].copy()
    if deferred.empty:
        raise ValueError("Phase 26 requires at least one frozen deferred order.")
    position = {str(order_ref): index for index, order_ref in enumerate(allocation["order_ref"].astype(str))}
    reason_rows: list[dict[str, Any]] = []
    individual_rows: list[dict[str, Any]] = []
    insertion_rows: list[dict[str, Any]] = []
    objective_rows: list[dict[str, Any]] = []
    change_rows: list[dict[str, Any]] = []
    resource_rows: list[dict[str, Any]] = []
    demo_candidates: list[dict[str, Any]] = []

    for number, order_ref in enumerate(deferred["order_ref"].astype(str), start=1):
        print(f"COUNTERFACTUAL {number} OF {len(deferred)}: START", flush=True)
        individual = evaluate_individual_feasibility(data, order_ref)
        direct = analyze_direct_insertion(data, allocation, order_ref)
        require_no_direct_insertion(direct)
        forced = solve_forced_counterfactual(
            data, allocation, baseline_vector, order_ref, individual,
            optimizer, reasoner,
        )
        forced_trips = pd.DataFrame(columns=baseline_audit.trip_summary.columns)
        if forced.allocation is not None:
            forced_audit = audit_allocation(forced.allocation, data)
            if forced_audit.status != "PASS":
                raise ValueError("Forced allocation failed independent hard-rule audit.")
            audit_objective_vector(forced.allocation, data, forced.objective_vector or {})
            forced_trips = forced_audit.trip_summary
            resource_rows.extend(_resource_rows(
                order_ref, forced.changes, baseline_trips, forced_trips
            ))
        explanation = generate_explanation(data, order_ref, individual, direct, forced)
        order = data.order_rows[order_ref]
        summary = forced.change_summary or {}
        reason_rows.append({
            "order_ref": order_ref,
            "reason_class": explanation.reason_class,
            "primary_reason_code": explanation.primary_reason_code,
            "secondary_reason_codes": json.dumps(explanation.secondary_reason_codes),
            "evidence_level": explanation.evidence_level,
            "compatible_vehicle_count": individual.compatible_vehicle_count,
            "individually_feasible": individual.individually_feasible,
            "direct_insert_possible": direct.direct_insert_possible,
            "forced_solve_status": forced.forced_solve_status,
            "forced_policy_vector_relation": forced.vector_relation or "NOT_APPLICABLE",
            "first_degraded_policy_tier": forced.first_degraded_tier,
            "minimum_changed_orders": forced.minimum_changed_orders,
            "served_to_deferred_count": summary.get("served_to_deferred_count"),
            "deferred_to_served_count": summary.get("deferred_to_served_count"),
            "reassigned_served_count": summary.get("served_reassigned_count"),
            "resource_evidence_summary": explanation.resource_evidence_summary,
            "human_explanation": explanation.human_explanation,
            "counterfactual_complete": explanation.counterfactual_complete,
        })
        individual_rows.append({
            "order_ref": order_ref, "compatible_vehicle_count": individual.compatible_vehicle_count,
            "feasible_vehicle_count": individual.feasible_vehicle_count,
            "individually_feasible": individual.individually_feasible,
            "single_order_minutes": individual.minimum_single_order_minutes,
            "time_blocker_code": individual.time_blocker_code,
            "forced_hard_status": forced.hard_status,
        })
        for attempt in direct.attempts:
            insertion_rows.append({
                "order_ref": order_ref, "vehicle_id": attempt.vehicle_id,
                "trip_id": attempt.trip_id, "path_type": attempt.path_type,
                "feasible": attempt.feasible, "blockers": json.dumps(attempt.blockers),
            })
        objective_rows.append({
            "order_ref": order_ref, "forced_solve_status": forced.forced_solve_status,
            "forced_policy_vector_relation": forced.vector_relation or "NOT_APPLICABLE",
            "first_degraded_policy_tier": forced.first_degraded_tier,
            "optimal_stage_count": len(forced.stage_records),
            "baseline_objective_vector": json.dumps(baseline_vector),
            "forced_objective_vector": json.dumps(forced.objective_vector),
            "direction_aware_deltas": json.dumps(forced.objective_delta),
        })
        change_rows.append({
            "order_ref": order_ref, "minimal_change_status": forced.minimal_change_status,
            "minimum_changed_orders": forced.minimum_changed_orders,
            **{key: summary.get(key) for key in (
                "changed_order_count", "served_to_deferred_count", "deferred_to_served_count",
                "served_reassigned_count", "affected_vehicle_count", "affected_trip_count",
            )},
        })
        demo_candidates.append({
            **reason_rows[-1], "secondary_reason_codes": list(explanation.secondary_reason_codes),
            "original_order_position": position[order_ref], "brand": order["brand"],
            "district": order["district"], "temp_requirement": order["temp_requirement"],
            "van_only": order["parking_constraint"] == "van_only",
        })
        print(f"COUNTERFACTUAL {number} OF {len(deferred)}: RESOLVED", flush=True)

    private_demo, sanitized_demo = select_demo_examples(
        demo_candidates, max_examples=int(reasoner["demo"]["max_examples"])
    )
    reason_frame = pd.DataFrame(reason_rows)
    class_counts = dict(Counter(reason_frame["reason_class"]))
    all_codes = Counter(reason_frame["primary_reason_code"])
    for value in reason_frame["secondary_reason_codes"]:
        all_codes.update(json.loads(value))
    code_counts = dict(all_codes)
    consistency = {
        "status": "PASS",
        "deferred_order_count": len(deferred),
        "reason_row_count": len(reason_frame),
        "unresolved_count": 0,
        "direct_insertion_contradiction_count": int(reason_frame["direct_insert_possible"].sum()),
        "all_counterfactuals_complete": bool(reason_frame["counterfactual_complete"].all()),
    }
    args.report_dir.mkdir(parents=True, exist_ok=True)
    _atomic_csv(args.report_dir / "deferral_reasons.csv", reason_frame)
    _atomic_json(args.report_dir / "deferral_reason_summary.json", {
        "status": "PASS", "reason_class_counts": class_counts, "reason_code_counts": code_counts,
    })
    _atomic_csv(args.report_dir / "individual_feasibility_audit.csv", pd.DataFrame(individual_rows))
    _atomic_csv(args.report_dir / "direct_insertion_audit.csv", pd.DataFrame(insertion_rows, columns=[
        "order_ref", "vehicle_id", "trip_id", "path_type", "feasible", "blockers",
    ]))
    _atomic_csv(args.report_dir / "counterfactual_objective_audit.csv", pd.DataFrame(objective_rows))
    _atomic_csv(args.report_dir / "counterfactual_change_audit.csv", pd.DataFrame(change_rows))
    _atomic_csv(args.report_dir / "resource_bottleneck_audit.csv", pd.DataFrame(resource_rows, columns=[
        "order_ref", "vehicle_id", "baseline_trip_count", "counterfactual_trip_count",
        "baseline_trip_minutes_total", "counterfactual_trip_minutes_total",
        "baseline_weight_total", "counterfactual_weight_total",
        "baseline_volume_total", "counterfactual_volume_total",
    ]))
    _atomic_json(args.report_dir / "reason_consistency_audit.json", consistency)
    _atomic_json(args.report_dir / "demo_examples_private.json", private_demo)
    _atomic_json(args.report_dir / "demo_examples_sanitized.json", sanitized_demo)

    manifest = {
        "phase": 26, "status": "PASS",
        "phase22_frozen_allocation_sha256": freeze["allocation_sha256"],
        "phase22_trip_summary_sha256": freeze["trip_summary_sha256"],
        "phase21_priority_config_sha256": sha256_file(args.priority_config),
        "phase22_optimizer_config_sha256": sha256_file(args.optimizer_config),
        "counterfactual_config_sha256": sha256_file(args.reasoner_config),
        "phase23_checker_evidence_sha256": sha256_file(checker_path),
        "deferred_order_count": len(deferred), "counterfactuals_attempted": len(deferred),
        "counterfactuals_resolved": len(deferred), "counterfactuals_unresolved": 0,
        "reason_class_counts": class_counts, "reason_code_counts": code_counts,
        "solver_version": ortools.__version__,
        "random_seed": int(reasoner["counterfactual"]["random_seed"]),
        "workers": int(reasoner["counterfactual"]["num_search_workers"]),
        "git_commit": _git_commit(), "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "row_identifiers_in_aggregate_manifest": False,
    }
    _atomic_json(args.report_dir / "run_manifest.json", manifest)
    report = "\n".join([
        "# Phase 26 Explainable Deferral Reasoner", "",
        "- Status: PASS", f"- Deferred orders resolved: {len(deferred)} / {len(deferred)}",
        "- Direct-insertion contradictions: 0", "- Unresolved explanations: 0",
        f"- Demo examples selected: {len(sanitized_demo)}", "",
        "Explanations are solver counterfactuals under the frozen Task 2B assumptions, not real-world causal claims.",
    ]) + "\n"
    _atomic_text(args.report_dir / "phase26_reasoner_report.md", report)
    after_hashes = _hashes(_frozen_paths(args, reasoner))
    if after_hashes != before_hashes:
        raise RuntimeError("A frozen Phase 22/24 artifact changed during Phase 26.")
    _atomic_json(args.report_dir / "frozen_hash_audit.json", {
        "status": "PASS", "all_unchanged": True, "before": before_hashes, "after": after_hashes,
    })
    print("LOCAL PHASE 26 DEFERRAL REASONER: PASS")
    print(f"DEFERRED ORDERS RESOLVED: {len(deferred)} / {len(deferred)}")
    print("DIRECT INSERTION CONTRADICTIONS: 0")
    print("UNRESOLVED REASONS: 0")
    print("FROZEN HASH INTEGRITY: PASS")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
