"""Synthetic checker-process tests; never invoke the real organizer checker."""

import sys
from pathlib import Path

import pytest

from src.task2b.artifact_integrity import sha256_file
from src.task2b.checker_runner import (
    CheckerRunnerError,
    OfficialCheckerInterface,
    discover_official_checker_interface,
    locate_official_checker,
    run_official_checker,
)


PASS_MARKER = "FEASIBILITY: PASSED - every rule satisfied."


def _interface(script: Path, *, timeout=2):
    return OfficialCheckerInterface(
        checker_path=script.resolve(), invocation_kind="python_script",
        candidate_argument_mode="single_positional", working_directory=script.parent.resolve(),
        success_exit_codes=(0,), pass_marker=PASS_MARKER,
        fail_markers=("FAIL:", "FEASIBILITY: FAILED"), timeout_seconds=timeout,
        checker_sha256=sha256_file(script),
    )


def _candidate(tmp_path):
    path = tmp_path / "candidate with spaces.csv"
    path.write_text("scenario,order_ref,decision,vehicle_id,trip_id\n", encoding="utf-8")
    return path


def test_runner_requires_exit_zero_pass_marker_and_no_fail_marker(tmp_path):
    candidate = _candidate(tmp_path)
    success = tmp_path / "success.py"
    success.write_text(f"import os,sys\nprint(os.getcwd())\nprint({PASS_MARKER!r})\n", encoding="utf-8")
    result = run_official_checker(_interface(success), candidate)
    assert result.status == "PASS" and result.pass_detected and result.exit_code == 0
    assert str(success.parent.resolve()) in result.stdout
    assert result.candidate_sha256 == sha256_file(candidate)

    no_marker = tmp_path / "no_marker.py"
    no_marker.write_text("print('done')\n", encoding="utf-8")
    assert run_official_checker(_interface(no_marker), candidate).status == "FAIL"

    embellished_marker = tmp_path / "embellished_marker.py"
    embellished_marker.write_text(f"print('prefix ' + {PASS_MARKER!r})\n", encoding="utf-8")
    assert run_official_checker(_interface(embellished_marker), candidate).status == "FAIL"

    nonzero = tmp_path / "nonzero.py"
    nonzero.write_text(f"import sys\nprint({PASS_MARKER!r})\nsys.exit(1)\n", encoding="utf-8")
    assert run_official_checker(_interface(nonzero), candidate).status == "FAIL"

    fail_marker = tmp_path / "fail_marker.py"
    fail_marker.write_text(f"print({PASS_MARKER!r})\nprint('FAIL: synthetic')\n", encoding="utf-8")
    assert run_official_checker(_interface(fail_marker), candidate).status == "FAIL"


def test_runner_captures_stderr_and_timeout(tmp_path):
    candidate = _candidate(tmp_path)
    stderr_script = tmp_path / "stderr.py"
    stderr_script.write_text(f"import sys\nprint('diagnostic', file=sys.stderr)\nprint({PASS_MARKER!r})\n", encoding="utf-8")
    result = run_official_checker(_interface(stderr_script), candidate)
    assert result.status == "PASS" and "diagnostic" in result.stderr

    timeout_script = tmp_path / "timeout.py"
    timeout_script.write_text("import time\ntime.sleep(5)\n", encoding="utf-8")
    result = run_official_checker(_interface(timeout_script, timeout=0.05), candidate)
    assert result.status == "FAIL" and result.timed_out and result.exit_code is None


def test_runner_rejects_missing_candidate_or_changed_checker(tmp_path):
    script = tmp_path / "checker.py"
    script.write_text(f"print({PASS_MARKER!r})\n", encoding="utf-8")
    interface = _interface(script)
    with pytest.raises(CheckerRunnerError, match="candidate"):
        run_official_checker(interface, tmp_path / "missing.csv")
    candidate = _candidate(tmp_path)
    script.write_text("print('changed')\n", encoding="utf-8")
    with pytest.raises(CheckerRunnerError, match="changed"):
        run_official_checker(interface, candidate)


def test_runner_rejects_checker_or_candidate_mutation_during_execution(tmp_path):
    candidate = _candidate(tmp_path)
    candidate_mutator = tmp_path / "candidate_mutator.py"
    candidate_mutator.write_text(
        f"from pathlib import Path\nimport sys\nPath(sys.argv[1]).write_text('changed')\nprint({PASS_MARKER!r})\n",
        encoding="utf-8",
    )
    with pytest.raises(CheckerRunnerError, match="candidate changed"):
        run_official_checker(_interface(candidate_mutator), candidate)

    candidate = _candidate(tmp_path)
    self_mutator = tmp_path / "self_mutator.py"
    self_mutator.write_text(
        f"from pathlib import Path\nPath(__file__).write_text('changed')\nprint({PASS_MARKER!r})\n",
        encoding="utf-8",
    )
    with pytest.raises(CheckerRunnerError, match="checker changed"):
        run_official_checker(_interface(self_mutator), candidate)


def test_discovery_confirms_actual_interface_and_rejects_invalid_source(tmp_path):
    source = '''import os, sys\nPASS = "FEASIBILITY: PASSED - every rule satisfied."\nroot = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")\nargs=[]\nif len(args) != 1:\n    pass\nexample=False\ndef check(path, example): return 0\nsys.exit(check(args[0], example))\n'''
    checker = tmp_path / "check_allocation.py"
    checker.write_text(source, encoding="utf-8")
    config = {"official_checker": {"timeout_seconds": 10, "interface": {
        "invocation_kind": "python_script", "candidate_argument_mode": "single_positional",
        "working_directory": "checker_parent", "success_exit_codes": [0],
        "pass_marker": PASS_MARKER, "fail_markers": ["FAIL:", "FEASIBILITY: FAILED"],
    }}}
    assert discover_official_checker_interface(checker, config).checker_sha256 == sha256_file(checker)
    checker.write_text("print('not official')\n", encoding="utf-8")
    with pytest.raises(CheckerRunnerError, match="interface"):
        discover_official_checker_interface(checker, config)


def test_locator_requires_manifest_declaration_and_unique_file(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    configured = repository / "DataSet" / "check_allocation.py"
    configured.parent.mkdir()
    configured.write_text("# checker\n", encoding="utf-8")
    manifest = {"artifacts": [{"filename": "check_allocation.py", "category": "validation"}]}
    assert locate_official_checker(repository, tmp_path / "raw", manifest, "DataSet/check_allocation.py") == configured.resolve()
    with pytest.raises(CheckerRunnerError, match="manifest"):
        locate_official_checker(repository, tmp_path / "raw", {"artifacts": []}, "DataSet/check_allocation.py")
