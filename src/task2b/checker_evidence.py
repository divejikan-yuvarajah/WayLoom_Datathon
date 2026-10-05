"""Immutable private evidence records for the Phase 23 official checker."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.task2b.checker_runner import CheckerRunResult


class CheckerEvidenceError(RuntimeError):
    """Checker evidence would be incomplete, misleading, or overwritten."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_checker_evidence(
    result: CheckerRunResult,
    *,
    frozen_allocation_sha256: str,
    phase22_freeze_manifest_sha256: str,
    python_version: str,
    own_validator_status: str,
    git_commit: str | None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    if own_validator_status != "PASS":
        raise CheckerEvidenceError("Official checker evidence requires own-validator PASS.")
    official_status = "PASS" if (
        result.status == "PASS" and result.pass_detected
        and result.exit_code == 0 and not result.timed_out
    ) else "FAIL"
    return {
        "phase": 23,
        "task": "DT-330",
        "checker": str(result.command[1]),
        "checker_sha256": result.checker_sha256,
        "checker_input_sha256": result.candidate_sha256,
        "frozen_allocation_sha256": frozen_allocation_sha256,
        "phase22_freeze_manifest_sha256": phase22_freeze_manifest_sha256,
        "python_version": python_version,
        "working_directory": result.working_directory,
        "invocation_mode": result.invocation_mode,
        "exit_code": result.exit_code,
        "timed_out": result.timed_out,
        "pass_detected": result.pass_detected,
        "stdout_sha256": sha256_text(result.stdout),
        "stderr_sha256": sha256_text(result.stderr),
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "own_validator_status": own_validator_status,
        "official_checker_status": official_status,
    }


def _validate_evidence_shape(evidence: dict[str, Any]) -> None:
    required = (
        "phase", "task", "checker", "checker_sha256", "checker_input_sha256",
        "frozen_allocation_sha256", "phase22_freeze_manifest_sha256",
        "python_version", "working_directory", "invocation_mode", "exit_code",
        "timed_out", "pass_detected", "stdout_sha256", "stderr_sha256",
        "timestamp", "own_validator_status", "official_checker_status",
    )
    if any(name not in evidence or evidence[name] is None for name in required):
        raise CheckerEvidenceError("Checker evidence is incomplete.")
    if evidence["phase"] != 23 or evidence["task"] != "DT-330":
        raise CheckerEvidenceError("Checker evidence phase/task identity is invalid.")
    if any(not isinstance(evidence[name], str) or not evidence[name]
           for name in ("checker", "python_version", "working_directory", "invocation_mode", "timestamp")):
        raise CheckerEvidenceError("Checker evidence identity fields are invalid.")
    for name in (
        "checker_sha256", "checker_input_sha256", "frozen_allocation_sha256",
        "phase22_freeze_manifest_sha256", "stdout_sha256", "stderr_sha256",
    ):
        value = evidence[name]
        if (not isinstance(value, str) or len(value) != 64
                or any(character not in "0123456789abcdef" for character in value.lower())):
            raise CheckerEvidenceError(f"Checker evidence hash is invalid: {name}.")


def require_successful_cross_validation(evidence: dict[str, Any]) -> None:
    _validate_evidence_shape(evidence)
    if (evidence.get("own_validator_status") != "PASS"
            or evidence.get("official_checker_status") != "PASS"
            or evidence.get("pass_detected") is not True
            or evidence.get("exit_code") != 0
            or evidence.get("timed_out") is not False):
        raise CheckerEvidenceError("Own validator and official checker must both PASS.")


def _write_text_atomically(path: Path, value: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix="phase23_evidence_", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(value)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_checker_evidence(run_dir: Path, evidence: dict[str, Any],
                          stdout: str, stderr: str) -> None:
    _validate_evidence_shape(evidence)
    run_dir = Path(run_dir)
    if run_dir.exists():
        raise CheckerEvidenceError("Checker evidence run directory already exists.")
    if evidence.get("stdout_sha256") != sha256_text(stdout) or evidence.get("stderr_sha256") != sha256_text(stderr):
        raise CheckerEvidenceError("Checker stream hashes do not match the evidence record.")
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_text_atomically(run_dir / "checker_stdout.txt", stdout)
    _write_text_atomically(run_dir / "checker_stderr.txt", stderr)
    _write_text_atomically(run_dir / "checker_input_sha256.txt", evidence["checker_input_sha256"] + "\n")
    _write_text_atomically(run_dir / "official_checker_sha256.txt", evidence["checker_sha256"] + "\n")
    _write_text_atomically(
        run_dir / "checker_evidence.json",
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
    )
