"""Private artifact, hash, schema, and aggregate reporting controls."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


class ReportingError(ValueError):
    """A Phase 27 privacy, schema, or frozen-artifact control failed."""


TASK1_SCHEMA = ["delivery_id", "pred_service_min", "pred_late_prob"]
TASK2A_SCHEMA = ["row_id", "pred_total_volume_m3", "pred_chilled_volume_m3"]


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_path(path: str | Path) -> str:
    target = Path(path)
    if target.is_file():
        return sha256_file(target)
    if not target.is_dir():
        raise ReportingError(f"Frozen artifact is missing: {target}")
    digest = hashlib.sha256()
    for child in sorted(item for item in target.rglob("*") if item.is_file()):
        digest.update(child.relative_to(target).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(child).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def hash_artifacts(paths: Iterable[str | Path]) -> dict[str, str]:
    return {Path(path).as_posix(): sha256_path(path) for path in paths}


def guard_official_schema(frame: pd.DataFrame, task: str) -> None:
    expected = TASK1_SCHEMA if task == "task1" else TASK2A_SCHEMA if task == "task2a" else None
    if expected is None or list(frame.columns) != expected:
        raise ReportingError(f"{task} official schema is not exact.")


def official_schema_guard(task1_path: Path, task2a_path: Path) -> dict[str, Any]:
    task1 = pd.read_csv(task1_path)
    task2a = pd.read_csv(task2a_path)
    guard_official_schema(task1, "task1")
    guard_official_schema(task2a, "task2a")
    return {"status": "PASS", "task1_schema": list(task1.columns), "task2a_schema": list(task2a.columns),
            "task1_sha256": sha256_file(task1_path), "task2a_sha256": sha256_file(task2a_path)}


def require_private_path(path: Path, *, repository_root: Path) -> Path:
    allowed = (repository_root / "reports" / "private").resolve()
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise ReportingError("Uncertainty artifacts must remain below reports/private/.") from exc
    return resolved


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_csv_atomic(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            # Seventeen significant digits preserve IEEE-754 float values on
            # CSV parse, which lets the validator enforce zero-tolerance point
            # parity with the frozen official submissions.
            frame.to_csv(stream, index=False, float_format="%.17g")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def assert_points_unchanged(private: pd.DataFrame, official: pd.DataFrame, *, task: str) -> None:
    if task == "task1":
        key, points = "delivery_id", ["pred_service_min"]
    elif task == "task2a":
        key, points = "row_id", ["pred_total_volume_m3", "pred_chilled_volume_m3"]
    else:
        raise ReportingError("Unknown point-prediction task.")
    if private[key].astype(str).tolist() != official[key].astype(str).tolist():
        raise ReportingError("Private uncertainty artifact changed identifier coverage/order.")
    for column in points:
        private_values = pd.to_numeric(private[column], errors="raise").to_numpy(dtype=float)
        official_values = pd.to_numeric(official[column], errors="raise").to_numpy(dtype=float)
        if (not np.isfinite(private_values).all() or not np.isfinite(official_values).all()
                or not np.array_equal(private_values, official_values)):
            raise ReportingError("Private uncertainty artifact changed a frozen point prediction.")
