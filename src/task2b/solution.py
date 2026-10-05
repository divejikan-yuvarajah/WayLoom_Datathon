"""Extract one decision per order from an optimal Phase 22 CP-SAT solution."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import ortools

from src.task2b.artifact_integrity import ALLOCATION_COLUMNS, sha256_file
from src.task2b.cp_scaling import from_scaled_int
from src.task2b.lexicographic_solver import SolveResult
from src.task2b.optimizer import ModelBundle


class SolutionError(ValueError):
    """The solved model does not yield the expected allocation grain."""


AUDIT_CHECK_NAMES = (
    "order_decisions", "assignment", "available_fleet", "same_brand", "same_district",
    "refrigeration", "van_only", "home_depot", "whole_order", "weight", "volume",
    "trip_time", "max_two_trips", "fresh_budget", "style_tech_budget",
)
REQUIRED_FREEZE_CONFIG_KEYS = (
    "solver",
    "scenario",
    "compatibility",
    "trip_time",
    "priority",
)


def extract_allocation(bundle: ModelBundle, result: SolveResult) -> pd.DataFrame:
    rows = []
    solver = result.solver
    for o in bundle.data.order_ids:
        assignments = [(v, t) for (oo, v, t), var in bundle.x.items()
                       if oo == o and solver.Value(var) == 1]
        served = solver.Value(bundle.serve[o]) == 1
        if len(assignments) != int(served) or solver.Value(bundle.defer[o]) != int(not served):
            raise SolutionError("Extracted order decision is inconsistent.")
        v, t = assignments[0] if served else (None, None)
        source = bundle.data.order_rows[o]
        rows.append({"scenario": "S1", "order_ref": o, "outlet_id": source["outlet_id"],
                     "decision": "served" if served else "deferred", "vehicle_id": v, "trip_id": t})
    return pd.DataFrame(rows, columns=ALLOCATION_COLUMNS)


def extract_solver_trip_minutes(bundle: ModelBundle, result: SolveResult) -> dict[tuple[str, int], object]:
    return {(v, t): from_scaled_int(result.solver.Value(variable), bundle.data.scales["time"])
            for (v, t), variable in bundle.trip_minutes.items()}


def validate_freeze_evidence(run: dict, stages: list[dict], audit: dict,
                             candidate_hash: str, summary_hash: str) -> None:
    from src.task2b.priority import OBJECTIVE_LEVELS

    if run.get("phase") != 22 or run.get("determinism") != "PASS" or run.get("objective_strategy") != "lexicographic":
        raise SolutionError("Phase 22 run evidence is incomplete.")
    if run.get("candidate_allocation_sha256") != candidate_hash or run.get("trip_summary_sha256") != summary_hash:
        raise SolutionError("Candidate files changed after the audited solve.")
    objective_vector = run.get("objective_vector")
    if not isinstance(objective_vector, dict) or tuple(objective_vector) != OBJECTIVE_LEVELS:
        raise SolutionError("The final objective vector is incomplete or out of order.")
    if tuple(record.get("level") for record in stages) != OBJECTIVE_LEVELS or any(
        record.get("status") != "OPTIMAL"
        or record.get("fixed_for_next_stage") is not True
        or record.get("direction") != ("maximize" if record.get("level", "").startswith("served_") else "minimize")
        or record.get("objective_value") != objective_vector[record.get("level")]
        for record in stages
    ):
        raise SolutionError("Every frozen objective stage must be proven OPTIMAL and fixed.")
    checks = audit.get("checks")
    if (audit.get("status") != "PASS" or audit.get("all_hard_rules_audited") is not True or
        audit.get("objective_vector_reconciled") is not True or not isinstance(checks, dict) or
        set(checks) != set(AUDIT_CHECK_NAMES) or any(value is not True for value in checks.values())):
        raise SolutionError("Independent hard-rule audit did not pass.")


def validate_freeze_config_paths(config_paths: dict[str, Path]) -> dict[str, Path]:
    """Require the complete, stable Phase 22 configuration evidence set."""
    if not isinstance(config_paths, dict) or set(config_paths) != set(REQUIRED_FREEZE_CONFIG_KEYS):
        raise SolutionError("Freeze requires exactly the five canonical configuration files.")
    validated = {}
    for key in REQUIRED_FREEZE_CONFIG_KEYS:
        path = Path(config_paths[key])
        if not path.exists() or not path.is_file():
            raise SolutionError(f"Freeze configuration file is missing or invalid: {key}.")
        validated[key] = path
    return validated


def _build_freeze_manifest(candidate: Path, trip_summary: Path, report_dir: Path,
                           config_paths: dict[str, Path], git_commit: str | None) -> dict:
    config_paths = validate_freeze_config_paths(config_paths)
    candidate_hash = sha256_file(candidate)
    summary_hash = sha256_file(trip_summary)
    run = json.loads((report_dir / "run_manifest.json").read_text(encoding="utf-8"))
    stages = json.loads((report_dir / "objective_stages.json").read_text(encoding="utf-8"))
    audit = json.loads((report_dir / "hard_rule_audit.json").read_text(encoding="utf-8"))
    validate_freeze_evidence(run, stages, audit, candidate_hash, summary_hash)
    if any(run.get(f"{key}_config_hash") != sha256_file(path) for key, path in config_paths.items()):
        raise SolutionError("A config changed after the audited optimization run.")
    manifest = {"phase": 22, "state": "FROZEN", "solver_engine": "OR-Tools CP-SAT",
                "ortools_version": ortools.__version__, "objective_strategy": "lexicographic",
                "determinism": "PASS",
                "allocation_sha256": candidate_hash, "trip_summary_sha256": summary_hash,
                "objective_stages": stages, "objective_vector": run["objective_vector"],
                "all_hard_rules_audited": True, "manual_independent_trip_audit": "PASS",
                "frozen_at": datetime.now(timezone.utc).isoformat(), "git_commit": git_commit}
    manifest.update({f"{key}_config_hash": sha256_file(config_paths[key])
                     for key in REQUIRED_FREEZE_CONFIG_KEYS})
    return manifest


def _write_manifest_atomically(report_dir: Path, manifest: dict) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="phase22_freeze_manifest_", suffix=".json", dir=report_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2, sort_keys=True)
        os.replace(temporary, report_dir / "freeze_manifest.json")
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def freeze_allocation(candidate: Path, trip_summary: Path, report_dir: Path, output: Path,
                      config_paths: dict[str, Path], *, git_commit: str | None = None) -> dict:
    if output.exists() or (report_dir / "freeze_manifest.json").exists():
        raise SolutionError("Canonical Phase 22 allocation is already frozen or exists; refusing overwrite.")
    manifest = _build_freeze_manifest(candidate, trip_summary, report_dir, config_paths, git_commit)
    candidate_hash = manifest["allocation_sha256"]
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="task2b_freeze_", suffix=".csv", dir=output.parent)
    try:
        with os.fdopen(fd, "wb") as stream, candidate.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                stream.write(chunk)
        if sha256_file(Path(temporary)) != candidate_hash:
            raise SolutionError("Atomic freeze copy failed its checksum.")
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    _write_manifest_atomically(report_dir, manifest)
    return manifest


def regenerate_freeze_manifest(candidate: Path, trip_summary: Path, report_dir: Path, output: Path,
                               config_paths: dict[str, Path], *, git_commit: str | None = None) -> dict:
    """Regenerate freeze evidence without rewriting either frozen data artifact."""
    manifest_path = report_dir / "freeze_manifest.json"
    if not output.is_file() or not manifest_path.is_file():
        raise SolutionError("Controlled freeze-evidence reopen requires an existing frozen allocation and manifest.")
    if candidate.resolve() == output.resolve():
        raise SolutionError("Controlled reopen requires the separate audited candidate artifact.")
    allocation_hash = sha256_file(output)
    summary_hash = sha256_file(trip_summary)
    if sha256_file(candidate) != allocation_hash:
        raise SolutionError("Candidate does not match the existing frozen allocation.")
    manifest = _build_freeze_manifest(candidate, trip_summary, report_dir, config_paths, git_commit)
    if manifest["allocation_sha256"] != allocation_hash or manifest["trip_summary_sha256"] != summary_hash:
        raise SolutionError("Controlled freeze evidence does not match the frozen artifacts.")
    if sha256_file(output) != allocation_hash or sha256_file(trip_summary) != summary_hash:
        raise SolutionError("Frozen artifacts changed during controlled freeze validation.")
    _write_manifest_atomically(report_dir, manifest)
    if sha256_file(output) != allocation_hash or sha256_file(trip_summary) != summary_hash:
        raise SolutionError("Frozen artifacts changed during controlled manifest regeneration.")
    return manifest
