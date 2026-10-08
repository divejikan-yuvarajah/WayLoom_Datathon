"""Phase 34 test-to-requirement traceability and collection contract."""

from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path, PurePosixPath

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "configs" / "phase34_test_traceability.yaml"
EXPECTED_TASKS = tuple(f"DT-{number}" for number in range(438, 451))
REQUIRED_COVERAGE = {"positive", "negative", "boundary"}
FORBIDDEN_TEST_PATH_TEXT = ("data/raw", "data/interim", "reports/private")
FILE_READ_CALLS = {"open", "read_csv", "read_parquet", "read_text", "read_bytes"}
REQUIRED_REMEDIATION_NODES = {
    "DT-438": {
        "tests/test_phase34_traceability.py::test_remediation_evidence_is_mapped_to_the_correct_tasks",
    },
    "DT-439": {
        "tests/test_final_submission_contract.py::test_strict_csv_preflight_rejects_bad_csv",
        "tests/test_final_submission_task1.py::test_case_mismatched_columns_are_rejected",
        "tests/test_final_submission_task1.py::test_header_only_submission_is_rejected",
        "tests/test_data_quality.py::test_dt039_semantic_type_validation",
    },
    "DT-441": {
        "tests/test_task1_labels.py::test_dt063_leap_day_midnight_transitions",
        "tests/test_task1_labels.py::test_dt062_invalid_non_leap_february_29_rejected",
    },
    "DT-444": {
        "tests/test_task1_inference.py::test_train_test_feature_schema_and_order",
    },
    "DT-445": {
        "tests/test_task2a_history.py::test_duplicate_ids_across_sources_are_a_hard_blocker",
        "tests/test_task2a_history.py::test_confirmed_zero_interior_week_is_filled_but_boundary_is_not",
    },
    "DT-448": {
        "tests/test_task2b_allocation_validator.py::test_identity_decision_and_served_field_mutations_fail",
    },
    "DT-449": {
        "tests/test_task2b_solution_audit.py::test_recomputes_hard_rules_from_extracted_rows",
    },
    "DT-450": {
        "tests/test_artifact_security.py::test_unknown_serializer_and_corrupt_registered_file_fail_safely",
        "tests/test_artifact_registry.py::test_secured_loader_rejects_unsupported_registry_schema_before_artifact_access",
        "tests/test_artifact_registry.py::test_secured_loader_rejects_schema_and_preprocessor_reference_mismatches_before_artifact_access",
        "tests/test_preprocessing_artifacts.py::test_external_preprocessor_requires_registered_state",
    },
}


def _load_manifest() -> dict:
    value = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Phase 34 traceability manifest must be a mapping.")
    return value


def _validate_manifest(value: dict) -> None:
    if value.get("version") != 1 or value.get("phase") != 34:
        raise ValueError("Phase 34 traceability version/phase is invalid.")
    if value.get("expected_task_count") != len(EXPECTED_TASKS):
        raise ValueError("Phase 34 expected task count is invalid.")
    if value.get("task_range") != {"first": "DT-438", "last": "DT-450"}:
        raise ValueError("Phase 34 task range is invalid.")
    execution = value.get("execution", {})
    if execution != {
        "runner": "pytest",
        "synthetic_only": True,
        "deterministic": True,
        "private_data_required": False,
    }:
        raise ValueError("Phase 34 execution safeguards are invalid.")
    tasks = value.get("tasks")
    if not isinstance(tasks, dict) or tuple(tasks) != EXPECTED_TASKS:
        raise ValueError("Phase 34 must map exactly DT-438 through DT-450 in order.")
    for task, entry in tasks.items():
        if not isinstance(entry, dict) or not str(entry.get("requirement", "")).strip():
            raise ValueError(f"{task} requirement is missing.")
        coverage = entry.get("coverage")
        if not isinstance(coverage, dict) or set(coverage) != REQUIRED_COVERAGE:
            raise ValueError(f"{task} must document positive, negative, and boundary coverage.")
        if any(not str(coverage[kind]).strip() for kind in REQUIRED_COVERAGE):
            raise ValueError(f"{task} has blank coverage evidence.")
        nodes = entry.get("nodes")
        if not isinstance(nodes, list) or not nodes or len(nodes) != len(set(nodes)):
            raise ValueError(f"{task} must map unique pytest nodes.")


def _node_parts(node: str) -> tuple[Path, str]:
    pieces = str(node).split("::")
    if len(pieces) != 2 or not pieces[1].startswith("test_"):
        raise ValueError(f"Invalid pytest node: {node}")
    pure = PurePosixPath(pieces[0])
    if pure.is_absolute() or ".." in pure.parts or pure.parts[0:1] != ("tests",):
        raise ValueError(f"Pytest node escapes tests/: {node}")
    return ROOT.joinpath(*pure.parts), pieces[1]


def _validate_remediation_mappings(value: dict) -> None:
    _validate_manifest(value)
    owners: dict[str, set[str]] = {}
    for task, entry in value["tasks"].items():
        for node in entry["nodes"]:
            owners.setdefault(node, set()).add(task)
    for expected_task, required_nodes in REQUIRED_REMEDIATION_NODES.items():
        for node in required_nodes:
            actual = owners.get(node, set())
            if not actual:
                raise ValueError(f"Required remediation evidence is missing: {node}")
            if actual != {expected_task}:
                raise ValueError(
                    f"Remediation evidence is incorrectly targeted: {node} -> {sorted(actual)}"
                )


def _literal_private_reads(tree: ast.AST) -> list[str]:
    violations: list[str] = []
    for item in ast.walk(tree):
        if not isinstance(item, ast.Call) or not item.args:
            continue
        name = item.func.attr if isinstance(item.func, ast.Attribute) else (
            item.func.id if isinstance(item.func, ast.Name) else ""
        )
        argument = item.args[0]
        if name not in FILE_READ_CALLS or not isinstance(argument, ast.Constant):
            continue
        if not isinstance(argument.value, str):
            continue
        normalized = argument.value.replace("\\", "/").lower()
        if any(value in normalized for value in FORBIDDEN_TEST_PATH_TEXT):
            violations.append(argument.value)
    return violations


def test_phase34_manifest_has_exact_master_inventory() -> None:
    manifest = _load_manifest()
    _validate_manifest(manifest)
    assert tuple(manifest["tasks"]) == EXPECTED_TASKS
    assert len(manifest["tasks"]) == 13


def test_malformed_traceability_is_rejected() -> None:
    manifest = _load_manifest()
    missing = deepcopy(manifest)
    missing["tasks"].pop("DT-450")
    with pytest.raises(ValueError, match="exactly DT-438 through DT-450"):
        _validate_manifest(missing)

    empty_nodes = deepcopy(manifest)
    empty_nodes["tasks"]["DT-439"]["nodes"] = []
    with pytest.raises(ValueError, match="unique pytest nodes"):
        _validate_manifest(empty_nodes)

    missing_boundary = deepcopy(manifest)
    missing_boundary["tasks"]["DT-448"]["coverage"].pop("boundary")
    with pytest.raises(ValueError, match="positive, negative, and boundary"):
        _validate_manifest(missing_boundary)


def test_mapped_nodes_exist_and_are_synthetic_only() -> None:
    manifest = _load_manifest()
    _validate_manifest(manifest)
    parsed_files: dict[Path, set[str]] = {}
    for entry in manifest["tasks"].values():
        for node in entry["nodes"]:
            path, function = _node_parts(node)
            assert path.is_file(), f"Mapped test file is missing: {path.relative_to(ROOT)}"
            if path not in parsed_files:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(path))
                assert _literal_private_reads(tree) == []
                parsed_files[path] = {
                    item.name for item in ast.walk(tree)
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
            assert function in parsed_files[path], f"Mapped pytest function is missing: {node}"


def test_traceability_manifest_is_deterministic() -> None:
    first = _load_manifest()
    second = _load_manifest()
    _validate_manifest(first)
    _validate_manifest(second)
    assert first == second
    assert yaml.safe_dump(first, sort_keys=False) == yaml.safe_dump(second, sort_keys=False)


def test_remediation_evidence_is_mapped_to_the_correct_tasks() -> None:
    manifest = _load_manifest()
    _validate_remediation_mappings(manifest)

    missing = deepcopy(manifest)
    required = sorted(REQUIRED_REMEDIATION_NODES["DT-450"])[0]
    missing["tasks"]["DT-450"]["nodes"].remove(required)
    with pytest.raises(ValueError, match="evidence is missing"):
        _validate_remediation_mappings(missing)

    mistargeted = deepcopy(manifest)
    required = sorted(REQUIRED_REMEDIATION_NODES["DT-449"])[0]
    mistargeted["tasks"]["DT-448"]["nodes"].append(required)
    with pytest.raises(ValueError, match="incorrectly targeted"):
        _validate_remediation_mappings(mistargeted)
