"""Synthetic immutable evidence and cross-validator tests for Phase 23."""

import json
import sys

import pytest

from src.task2b.artifact_integrity import sha256_file
from src.task2b.allocation_validator import validate_frozen_task2b_allocation
from src.task2b.checker_evidence import (
    CheckerEvidenceError,
    build_checker_evidence,
    require_successful_cross_validation,
    save_checker_evidence,
    sha256_text,
)
from src.task2b.checker_runner import CheckerRunResult, OfficialCheckerInterface, run_official_checker
from tests.test_task2b_allocation_validator import _case


def _result(*, passed=True):
    return CheckerRunResult(
        status="PASS" if passed else "FAIL", pass_detected=passed,
        exit_code=0 if passed else 1, stdout="passed" if passed else "failed",
        stderr="", timed_out=False, command=(sys.executable, "checker.py", "candidate.csv"),
        working_directory="workspace", checker_sha256="a" * 64,
        candidate_sha256="b" * 64,
        invocation_mode="python_script_single_positional_candidate",
    )


def _evidence(result):
    return build_checker_evidence(
        result, frozen_allocation_sha256="c" * 64,
        phase22_freeze_manifest_sha256="d" * 64,
        python_version="test-python", own_validator_status="PASS",
        git_commit="commit", timestamp="2026-01-01T00:00:00+00:00",
    )


def test_evidence_hashes_status_and_required_fields():
    result = _result()
    evidence = _evidence(result)
    require_successful_cross_validation(evidence)
    assert evidence["phase"] == 23 and evidence["task"] == "DT-330"
    assert evidence["stdout_sha256"] == sha256_text(result.stdout)
    assert evidence["stderr_sha256"] == sha256_text(result.stderr)
    assert evidence["official_checker_status"] == "PASS"
    assert evidence["timestamp"]


def test_failed_run_cannot_be_pass_evidence_and_own_pass_is_required():
    evidence = _evidence(_result(passed=False))
    assert evidence["official_checker_status"] == "FAIL" and evidence["pass_detected"] is False
    with pytest.raises(CheckerEvidenceError, match="both PASS"):
        require_successful_cross_validation(evidence)
    with pytest.raises(CheckerEvidenceError, match="own-validator"):
        build_checker_evidence(
            _result(), frozen_allocation_sha256="c", phase22_freeze_manifest_sha256="d",
            python_version="python", own_validator_status="FAIL", git_commit=None,
        )


def test_inconsistent_runner_result_and_incomplete_evidence_cannot_pass():
    inconsistent = CheckerRunResult(
        status="PASS", pass_detected=True, exit_code=1, stdout="passed", stderr="",
        timed_out=False, command=(sys.executable, "checker.py", "candidate.csv"),
        working_directory="workspace", checker_sha256="a" * 64,
        candidate_sha256="b" * 64,
        invocation_mode="python_script_single_positional_candidate",
    )
    evidence = _evidence(inconsistent)
    assert evidence["official_checker_status"] == "FAIL"
    with pytest.raises(CheckerEvidenceError, match="both PASS"):
        require_successful_cross_validation(evidence)
    del evidence["checker_sha256"]
    with pytest.raises(CheckerEvidenceError, match="incomplete"):
        require_successful_cross_validation(evidence)


def test_evidence_files_are_complete_and_overwrite_protected(tmp_path):
    result = _result()
    evidence = _evidence(result)
    run_dir = tmp_path / "run"
    save_checker_evidence(run_dir, evidence, result.stdout, result.stderr)
    assert (run_dir / "checker_stdout.txt").read_text(encoding="utf-8") == result.stdout
    assert json.loads((run_dir / "checker_evidence.json").read_text(encoding="utf-8")) == evidence
    assert (run_dir / "checker_input_sha256.txt").read_text(encoding="utf-8").strip() == evidence["checker_input_sha256"]
    assert (run_dir / "official_checker_sha256.txt").read_text(encoding="utf-8").strip() == evidence["checker_sha256"]
    with pytest.raises(CheckerEvidenceError, match="already exists"):
        save_checker_evidence(run_dir, evidence, result.stdout, result.stderr)


def test_evidence_rejects_mismatched_stream_hash(tmp_path):
    result = _result()
    evidence = _evidence(result)
    with pytest.raises(CheckerEvidenceError, match="stream hashes"):
        save_checker_evidence(tmp_path / "run", evidence, "changed", result.stderr)
    assert not (tmp_path / "run").exists()


def test_end_to_end_synthetic_validator_checker_and_evidence(tmp_path):
    own = validate_frozen_task2b_allocation(*_case())
    assert own.overall_status == "PASS"
    candidate = tmp_path / "candidate.csv"
    candidate.write_text("synthetic\n", encoding="utf-8")
    checker = tmp_path / "mock_checker.py"
    marker = "FEASIBILITY: PASSED - every rule satisfied."
    checker.write_text(f"print({marker!r})\n", encoding="utf-8")
    interface = OfficialCheckerInterface(
        checker.resolve(), "python_script", "single_positional", tmp_path.resolve(),
        (0,), marker, ("FAIL:", "FEASIBILITY: FAILED"), 2, sha256_file(checker),
    )
    result = run_official_checker(interface, candidate)
    evidence = build_checker_evidence(
        result, frozen_allocation_sha256="c" * 64,
        phase22_freeze_manifest_sha256="d" * 64,
        python_version="python", own_validator_status=own.overall_status,
        git_commit=None,
    )
    require_successful_cross_validation(evidence)
    save_checker_evidence(tmp_path / "evidence", evidence, result.stdout, result.stderr)

    invalid = list(_case())
    invalid[0].loc[0, "decision"] = "invalid"
    own_failed = validate_frozen_task2b_allocation(*tuple(invalid))
    assert own_failed.overall_status == "FAIL"
    with pytest.raises(CheckerEvidenceError, match="own-validator"):
        build_checker_evidence(
            result, frozen_allocation_sha256="c", phase22_freeze_manifest_sha256="d",
            python_version="python", own_validator_status=own_failed.overall_status,
            git_commit=None,
        )
