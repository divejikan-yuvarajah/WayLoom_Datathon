import shutil
import sys
from pathlib import Path

import pytest

from src.task2b.artifact_integrity import sha256_file
from src.task2b.checker_runner import CheckerRunnerError, OfficialCheckerInterface
from src.task2b.final_submission_validation import (
    require_byte_identical_staged_copy,
    run_final_official_checker,
)


PASS_MARKER = "FEASIBILITY: PASSED - every rule satisfied."


def _candidate(tmp_path):
    path = tmp_path / "submission_task2b.csv"
    path.write_text("scenario,order_ref,outlet_id,decision,vehicle_id,trip_id\n", encoding="utf-8")
    return path


def _interface(script, timeout=2):
    return OfficialCheckerInterface(
        checker_path=script.resolve(), invocation_kind="python_script",
        candidate_argument_mode="single_positional", working_directory=script.parent.resolve(),
        success_exit_codes=(0,), pass_marker=PASS_MARKER,
        fail_markers=("FAIL:", "FEASIBILITY: FAILED"), timeout_seconds=timeout,
        checker_sha256=sha256_file(script),
    )


def test_actual_checker_adapter_is_invoked_on_exact_final_file(tmp_path):
    candidate = _candidate(tmp_path)
    script = tmp_path / "checker.py"
    script.write_text(f"import sys\nassert sys.argv[1].endswith('submission_task2b.csv')\nprint({PASS_MARKER!r})\n", encoding="utf-8")
    before = sha256_file(candidate)
    result = run_final_official_checker(_interface(script), candidate, "PASS")
    assert result.status == "PASS" and result.candidate_sha256 == before
    assert sha256_file(candidate) == before


@pytest.mark.parametrize(("source", "expected"), [
    ("print('FEASIBILITY: FAILED')\n", "FAIL"),
    ("raise RuntimeError('crash')\n", "FAIL"),
])
def test_checker_failure_and_crash_are_not_pass(source, expected, tmp_path):
    candidate = _candidate(tmp_path)
    script = tmp_path / "checker.py"
    script.write_text(source, encoding="utf-8")
    assert run_final_official_checker(_interface(script), candidate, "PASS").status == expected


def test_missing_checker_is_blocking(tmp_path):
    candidate = _candidate(tmp_path)
    missing = tmp_path / "missing.py"
    interface = OfficialCheckerInterface(
        missing, "python_script", "single_positional", tmp_path, (0,), PASS_MARKER,
        ("FAIL:",), 1, "0" * 64,
    )
    with pytest.raises(CheckerRunnerError, match="disappeared"):
        run_final_official_checker(interface, candidate, "PASS")


def test_independent_validator_disagreement_blocks_checker(tmp_path):
    candidate = _candidate(tmp_path)
    script = tmp_path / "checker.py"
    script.write_text(f"print({PASS_MARKER!r})\n", encoding="utf-8")
    with pytest.raises(ValueError, match="independent"):
        run_final_official_checker(_interface(script), candidate, "FAIL")


def test_staged_copy_must_be_byte_identical(tmp_path):
    final = _candidate(tmp_path)
    staged = tmp_path / "staged.csv"
    shutil.copyfile(final, staged)
    assert require_byte_identical_staged_copy(final, staged) == sha256_file(final)
    staged.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="byte-identical"):
        require_byte_identical_staged_copy(final, staged)


def test_checker_source_is_not_modified_and_no_optimality_claim(tmp_path):
    candidate = _candidate(tmp_path)
    script = tmp_path / "checker.py"
    script.write_text(f"print({PASS_MARKER!r})\n", encoding="utf-8")
    checker_hash = sha256_file(script)
    run_final_official_checker(_interface(script), candidate, "PASS")
    assert sha256_file(script) == checker_hash
    source = Path("scripts/validate_final_submissions.py").read_text(encoding="utf-8")
    assert "FEASIBILITY ONLY" in source and "OPTIMALITY: PASS" not in source
