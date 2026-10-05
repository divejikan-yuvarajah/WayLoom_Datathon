"""Synthetic-only freeze evidence and overwrite protection tests."""
import hashlib
import json

import pytest

from src.task2b.priority import OBJECTIVE_LEVELS
from src.task2b.solution import (AUDIT_CHECK_NAMES, REQUIRED_FREEZE_CONFIG_KEYS,
                                 SolutionError, freeze_allocation, regenerate_freeze_manifest,
                                 sha256_file,
                                 validate_freeze_config_paths, validate_freeze_evidence)
from scripts.run_task2b_optimizer import _validate_candidate_output_path


def _passing_checks():
    return {name: True for name in AUDIT_CHECK_NAMES}


def _objective_vector():
    return {name: 0 for name in OBJECTIVE_LEVELS}


def _optimal_stages():
    return [{"level": name,
             "direction": "maximize" if name.startswith("served_") else "minimize",
             "status": "OPTIMAL", "fixed_for_next_stage": True,
             "objective_value": 0}
            for name in OBJECTIVE_LEVELS]


def _config_files(tmp_path):
    paths = {}
    for key in REQUIRED_FREEZE_CONFIG_KEYS:
        path = tmp_path / f"{key}.yaml"
        path.write_text("version: 1\n", encoding="utf-8")
        paths[key] = path
    return paths


def test_freeze_checks_hashes_stages_audit_and_overwrite(tmp_path):
    candidate = tmp_path / "candidate.csv"
    candidate.write_text("scenario,order_ref,outlet_id,decision,vehicle_id,trip_id\nS1,o1,x,deferred,,\n", encoding="utf-8")
    summary = tmp_path / "trips.csv"
    summary.write_text("vehicle_id,trip_id\n", encoding="utf-8")
    configs = _config_files(tmp_path)
    report = tmp_path / "private"
    report.mkdir()
    run = {"phase": 22, "determinism": "PASS", "objective_strategy": "lexicographic",
           "candidate_allocation_sha256": sha256_file(candidate), "trip_summary_sha256": sha256_file(summary),
           "objective_vector": _objective_vector(),
           **{f"{key}_config_hash": sha256_file(path) for key, path in configs.items()}}
    stages = _optimal_stages()
    audit = {"status": "PASS", "all_hard_rules_audited": True, "objective_vector_reconciled": True,
             "checks": _passing_checks()}
    (report / "run_manifest.json").write_text(json.dumps(run), encoding="utf-8")
    (report / "objective_stages.json").write_text(json.dumps(stages), encoding="utf-8")
    (report / "hard_rule_audit.json").write_text(json.dumps(audit), encoding="utf-8")
    output = tmp_path / "frozen.csv"
    with pytest.raises(SolutionError, match="five canonical"):
        freeze_allocation(candidate, summary, report, output, {})
    with pytest.raises(SolutionError, match="five canonical"):
        freeze_allocation(candidate, summary, report, output, {"solver": configs["solver"]})
    manifest = freeze_allocation(candidate, summary, report, output, configs)
    assert manifest["state"] == "FROZEN"
    assert manifest["determinism"] == "PASS"
    assert {key for key in manifest if key.endswith("_config_hash")} == {
        f"{key}_config_hash" for key in REQUIRED_FREEZE_CONFIG_KEYS
    }
    assert all(manifest[f"{key}_config_hash"] == sha256_file(configs[key])
               for key in REQUIRED_FREEZE_CONFIG_KEYS)
    assert sha256_file(output) == manifest["allocation_sha256"]
    with pytest.raises(SolutionError, match="already frozen"):
        freeze_allocation(candidate, summary, report, output, configs)
    output.unlink()
    candidate.write_text(candidate.read_text(encoding="utf-8") + "S1,o2,y,deferred,,\n", encoding="utf-8")
    with pytest.raises(SolutionError, match="already frozen"):
        freeze_allocation(candidate, summary, report, output, configs)


def test_freeze_requires_complete_exact_config_set(tmp_path):
    configs = _config_files(tmp_path)
    with pytest.raises(SolutionError, match="five canonical"):
        validate_freeze_config_paths({})
    with pytest.raises(SolutionError, match="five canonical"):
        validate_freeze_config_paths({"solver": configs["solver"]})
    for missing in REQUIRED_FREEZE_CONFIG_KEYS:
        partial = {key: path for key, path in configs.items() if key != missing}
        with pytest.raises(SolutionError, match="five canonical"):
            validate_freeze_config_paths(partial)
    with pytest.raises(SolutionError, match="five canonical"):
        validate_freeze_config_paths({**configs, "extra": configs["solver"]})
    assert validate_freeze_config_paths(configs) == configs


def test_freeze_rejects_nonexistent_config_file(tmp_path):
    configs = _config_files(tmp_path)
    configs["trip_time"] = tmp_path / "missing.yaml"
    with pytest.raises(SolutionError, match="trip_time"):
        validate_freeze_config_paths(configs)


def test_controlled_reopen_regenerates_only_manifest(tmp_path):
    candidate = tmp_path / "candidate.csv"
    candidate.write_text("scenario,order_ref,outlet_id,decision,vehicle_id,trip_id\nS1,o1,x,deferred,,\n", encoding="utf-8")
    summary = tmp_path / "trips.csv"
    summary.write_text("vehicle_id,trip_id\n", encoding="utf-8")
    configs = _config_files(tmp_path)
    report = tmp_path / "private"
    report.mkdir()
    run = {"phase": 22, "determinism": "PASS", "objective_strategy": "lexicographic",
           "candidate_allocation_sha256": sha256_file(candidate), "trip_summary_sha256": sha256_file(summary),
           "objective_vector": _objective_vector(),
           **{f"{key}_config_hash": sha256_file(path) for key, path in configs.items()}}
    audit = {"status": "PASS", "all_hard_rules_audited": True,
             "objective_vector_reconciled": True, "checks": _passing_checks()}
    for name, record in (("run_manifest.json", run), ("objective_stages.json", _optimal_stages()),
                         ("hard_rule_audit.json", audit)):
        (report / name).write_text(json.dumps(record), encoding="utf-8")
    output = tmp_path / "frozen.csv"
    freeze_allocation(candidate, summary, report, output, configs)
    allocation_before = output.read_bytes()
    summary_before = summary.read_bytes()
    old_manifest = json.loads((report / "freeze_manifest.json").read_text(encoding="utf-8"))
    old_manifest.pop("determinism")
    (report / "freeze_manifest.json").write_text(json.dumps(old_manifest), encoding="utf-8")
    regenerated = regenerate_freeze_manifest(candidate, summary, report, output, configs)
    assert regenerated["determinism"] == "PASS"
    assert output.read_bytes() == allocation_before
    assert summary.read_bytes() == summary_before


def test_controlled_reopen_rejects_candidate_mismatch_without_writes(tmp_path):
    candidate = tmp_path / "candidate.csv"
    candidate.write_text("candidate\n", encoding="utf-8")
    output = tmp_path / "frozen.csv"
    output.write_text("different\n", encoding="utf-8")
    summary = tmp_path / "trips.csv"
    summary.write_text("summary\n", encoding="utf-8")
    report = tmp_path / "private"
    report.mkdir()
    manifest = report / "freeze_manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    before = (output.read_bytes(), summary.read_bytes(), manifest.read_bytes())
    with pytest.raises(SolutionError, match="does not match"):
        regenerate_freeze_manifest(candidate, summary, report, output, _config_files(tmp_path))
    assert (output.read_bytes(), summary.read_bytes(), manifest.read_bytes()) == before


def test_freeze_rejects_feasible_only_stage(tmp_path):
    run = {"phase": 22, "determinism": "PASS", "objective_strategy": "lexicographic",
           "candidate_allocation_sha256": "a", "trip_summary_sha256": "b",
           "objective_vector": _objective_vector()}
    stages = _optimal_stages()
    stages[0]["status"] = "FEASIBLE"
    with pytest.raises(SolutionError, match="OPTIMAL"):
        validate_freeze_evidence(run, stages, {"status": "PASS", "all_hard_rules_audited": True,
                                               "objective_vector_reconciled": True, "checks": _passing_checks()}, "a", "b")


def test_freeze_rejects_missing_incomplete_or_false_audit_checks():
    run = {"phase": 22, "determinism": "PASS", "objective_strategy": "lexicographic",
           "candidate_allocation_sha256": "a", "trip_summary_sha256": "b",
           "objective_vector": _objective_vector()}
    stages = _optimal_stages()
    audit = {"status": "PASS", "all_hard_rules_audited": True,
             "objective_vector_reconciled": True, "checks": _passing_checks()}
    validate_freeze_evidence(run, stages, audit, "a", "b")
    malformed = [
        {key: value for key, value in audit.items() if key != "checks"},
        {**audit, "checks": None},
        {**audit, "checks": {}},
        {**audit, "checks": {"order_decisions": True}},
        {**audit, "checks": {**_passing_checks(), "extra": True}},
        {**audit, "checks": {**_passing_checks(), "trip_time": False}},
        {**audit, "checks": {**_passing_checks(), "trip_time": 1}},
    ]
    for record in malformed:
        with pytest.raises(SolutionError, match="audit"):
            validate_freeze_evidence(run, stages, record, "a", "b")


def test_freeze_rejects_wrong_objective_direction_or_value():
    run = {"phase": 22, "determinism": "PASS", "objective_strategy": "lexicographic",
           "candidate_allocation_sha256": "a", "trip_summary_sha256": "b",
           "objective_vector": _objective_vector()}
    audit = {"status": "PASS", "all_hard_rules_audited": True,
             "objective_vector_reconciled": True, "checks": _passing_checks()}
    stages = _optimal_stages()
    stages[0]["direction"] = "minimize"
    with pytest.raises(SolutionError, match="OPTIMAL"):
        validate_freeze_evidence(run, stages, audit, "a", "b")
    stages = _optimal_stages()
    stages[0]["objective_value"] = 1
    with pytest.raises(SolutionError, match="OPTIMAL"):
        validate_freeze_evidence(run, stages, audit, "a", "b")


def test_optimizer_candidate_path_cannot_be_canonical_even_when_absent(tmp_path):
    canonical = tmp_path / "data" / "interim" / "task2b_final_allocation.csv"
    assert not canonical.exists()
    with pytest.raises(ValueError, match="cannot be the canonical"):
        _validate_candidate_output_path(canonical, canonical)
    normalized_alias = canonical.parent / ".." / "interim" / canonical.name
    with pytest.raises(ValueError, match="cannot be the canonical"):
        _validate_candidate_output_path(normalized_alias, canonical)
    candidate = canonical.parent / "task2b_solver_allocation_candidate.csv"
    _validate_candidate_output_path(candidate, canonical)
    assert not canonical.exists()


def test_synthetic_solve_audit_rerun_and_freeze(tmp_path):
    from src.task2b.lexicographic_solver import assert_deterministic, solve_lexicographic
    from src.task2b.optimizer import build_optimizer_model
    from src.task2b.solution import extract_allocation, extract_solver_trip_minutes
    from src.task2b.solution_audit import audit_allocation
    from src.task2b.solver_data import build_solver_data
    from tests.test_task2b_solver_data import _case

    scenario, matrix, metadata, config, priority = _case()
    data = build_solver_data(scenario, matrix, metadata, config, priority)
    first = build_optimizer_model(data)
    result_a = solve_lexicographic(first, config)
    allocation = extract_allocation(first, result_a)
    audit = audit_allocation(allocation, data, extract_solver_trip_minutes(first, result_a))
    second = build_optimizer_model(data)
    result_b = solve_lexicographic(second, config)
    assert_deterministic((result_a, allocation), (result_b, extract_allocation(second, result_b)))
    assert audit.status == "PASS"
    candidate, summary, output = (tmp_path / name for name in ("candidate.csv", "trips.csv", "final.csv"))
    allocation.to_csv(candidate, index=False)
    audit.trip_summary.to_csv(summary, index=False)
    report = tmp_path / "report"
    report.mkdir()
    configs = _config_files(tmp_path)
    run = {"phase": 22, "determinism": "PASS", "objective_strategy": "lexicographic",
           "candidate_allocation_sha256": sha256_file(candidate), "trip_summary_sha256": sha256_file(summary),
           "objective_vector": result_a.objective_vector,
           **{f"{key}_config_hash": sha256_file(path) for key, path in configs.items()}}
    for name, record in (("run_manifest.json", run), ("objective_stages.json", result_a.stage_records),
                         ("hard_rule_audit.json", {"status": "PASS", "all_hard_rules_audited": True,
                                                   "objective_vector_reconciled": True, "checks": audit.checks})):
        (report / name).write_text(json.dumps(record), encoding="utf-8")
    frozen = freeze_allocation(candidate, summary, report, output, configs)
    assert frozen["state"] == "FROZEN" and output.read_bytes() == candidate.read_bytes()
