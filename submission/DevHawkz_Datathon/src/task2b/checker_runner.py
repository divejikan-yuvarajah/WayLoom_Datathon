"""Immutable organizer-checker discovery and subprocess execution for Phase 23."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from src.task2b.artifact_integrity import sha256_file


class CheckerRunnerError(RuntimeError):
    """The official checker interface or execution is unsafe/invalid."""


@dataclass(frozen=True)
class OfficialCheckerInterface:
    checker_path: Path
    invocation_kind: str
    candidate_argument_mode: str
    working_directory: Path
    success_exit_codes: tuple[int, ...]
    pass_marker: str
    fail_markers: tuple[str, ...]
    timeout_seconds: float
    checker_sha256: str


@dataclass(frozen=True)
class CheckerRunResult:
    status: str
    pass_detected: bool
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool
    command: tuple[str, ...]
    working_directory: str
    checker_sha256: str
    candidate_sha256: str
    invocation_mode: str


def locate_official_checker(repository_root: Path, raw_root: Path, manifest: dict,
                            configured_path: str) -> Path:
    """Locate the manifest-declared checker without inspecting competition rows."""
    expected = {
        entry.get("filename") for entry in manifest.get("artifacts", [])
        if entry.get("category") == "validation"
    }
    if "check_allocation.py" not in expected:
        raise CheckerRunnerError("Dataset manifest does not declare the official checker.")
    configured = (Path(repository_root) / configured_path).resolve()
    if configured.is_file() and configured.name == "check_allocation.py":
        return configured
    matches = sorted(Path(raw_root).rglob("check_allocation.py")) if Path(raw_root).is_dir() else []
    if len(matches) != 1:
        raise CheckerRunnerError("Official check_allocation.py could not be located uniquely.")
    return matches[0].resolve()


def discover_official_checker_interface(checker_path: Path, config: dict) -> OfficialCheckerInterface:
    """Confirm the supplied checker's actual single-positional-file interface."""
    checker_path = Path(checker_path).resolve()
    if not checker_path.is_file():
        raise CheckerRunnerError("Official checker file is missing.")
    checker = config.get("official_checker", {})
    interface = checker.get("interface", {})
    expected = {
        "invocation_kind": "python_script",
        "candidate_argument_mode": "single_positional",
        "working_directory": "checker_parent",
        "success_exit_codes": [0],
        "pass_marker": "FEASIBILITY: PASSED - every rule satisfied.",
        "fail_markers": ["FAIL:", "FEASIBILITY: FAILED"],
    }
    if any(interface.get(key) != value for key, value in expected.items()):
        raise CheckerRunnerError("Configured official checker interface is not the inspected interface.")
    timeout = checker.get("timeout_seconds")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise CheckerRunnerError("Official checker timeout must be positive.")
    source = checker_path.read_text(encoding="utf-8")
    required_source_evidence = (
        "if len(args) != 1:",
        "sys.exit(check(args[0], example))",
        expected["pass_marker"],
        'os.path.dirname(os.path.abspath(__file__)), "data"',
    )
    if any(token not in source for token in required_source_evidence):
        raise CheckerRunnerError("Official checker source no longer matches the discovered interface.")
    return OfficialCheckerInterface(
        checker_path=checker_path,
        invocation_kind="python_script",
        candidate_argument_mode="single_positional",
        working_directory=checker_path.parent,
        success_exit_codes=(0,),
        pass_marker=expected["pass_marker"],
        fail_markers=tuple(expected["fail_markers"]),
        timeout_seconds=float(timeout),
        checker_sha256=sha256_file(checker_path),
    )


def run_official_checker(interface: OfficialCheckerInterface,
                         candidate_path: Path) -> CheckerRunResult:
    candidate_path = Path(candidate_path).resolve()
    if not candidate_path.is_file():
        raise CheckerRunnerError("Official checker candidate is missing.")
    if not interface.checker_path.is_file():
        raise CheckerRunnerError("Official checker disappeared before execution.")
    if sha256_file(interface.checker_path) != interface.checker_sha256:
        raise CheckerRunnerError("Official checker changed after interface discovery.")
    candidate_sha256 = sha256_file(candidate_path)
    command = (sys.executable, str(interface.checker_path), str(candidate_path))
    try:
        completed = subprocess.run(
            command,
            cwd=interface.working_directory,
            capture_output=True,
            text=True,
            timeout=interface.timeout_seconds,
            check=False,
        )
        if (not interface.checker_path.is_file()
                or sha256_file(interface.checker_path) != interface.checker_sha256):
            raise CheckerRunnerError("Official checker changed during execution.")
        if not candidate_path.is_file() or sha256_file(candidate_path) != candidate_sha256:
            raise CheckerRunnerError("Checker candidate changed during execution.")
        stdout, stderr = completed.stdout, completed.stderr
        marker_ok = any(line.strip() == interface.pass_marker for line in stdout.splitlines())
        fail_marker_found = any(marker in stdout or marker in stderr for marker in interface.fail_markers)
        passed = completed.returncode in interface.success_exit_codes and marker_ok and not fail_marker_found
        return CheckerRunResult(
            status="PASS" if passed else "FAIL", pass_detected=passed,
            exit_code=completed.returncode, stdout=stdout, stderr=stderr,
            timed_out=False, command=command,
            working_directory=str(interface.working_directory),
            checker_sha256=interface.checker_sha256,
            candidate_sha256=candidate_sha256,
            invocation_mode="python_script_single_positional_candidate",
        )
    except subprocess.TimeoutExpired as exc:
        if (not interface.checker_path.is_file()
                or sha256_file(interface.checker_path) != interface.checker_sha256):
            raise CheckerRunnerError("Official checker changed during execution.") from exc
        if not candidate_path.is_file() or sha256_file(candidate_path) != candidate_sha256:
            raise CheckerRunnerError("Checker candidate changed during execution.") from exc
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return CheckerRunResult(
            status="FAIL", pass_detected=False, exit_code=None,
            stdout=stdout, stderr=stderr, timed_out=True, command=command,
            working_directory=str(interface.working_directory),
            checker_sha256=interface.checker_sha256,
            candidate_sha256=candidate_sha256,
            invocation_mode="python_script_single_positional_candidate",
        )
