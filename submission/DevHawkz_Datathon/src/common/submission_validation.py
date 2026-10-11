"""Read-only, privacy-safe primitives for final submission validation."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


class SubmissionValidationError(ValueError):
    """A strict CSV or Phase 33 validation contract was violated."""


@dataclass(frozen=True)
class RawCSV:
    path: Path
    header: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    @property
    def frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows, columns=self.header, dtype="string")


@dataclass
class ValidationReport:
    checks: dict[str, str] = field(default_factory=dict)
    failures: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def record(self, task: str, passed: bool, check: str, failure_count: int = 0) -> None:
        self.checks[task] = "PASS" if passed else "FAIL"
        if not passed:
            self.failures.append({"task": task, "check": check, "failure_count": int(failure_count or 1)})

    @property
    def status(self) -> str:
        return "PASS" if self.checks and all(value == "PASS" for value in self.checks.values()) else "FAIL"

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "checks": dict(self.checks),
            "failures": list(self.failures),
            "warnings": list(self.warnings),
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_snapshot(paths: Iterable[Path]) -> dict[str, str]:
    return {Path(path).name: sha256_file(Path(path)) for path in paths}


def read_strict_csv(path: Path) -> RawCSV:
    """Parse a CSV without type coercion and reject malformed logical rows."""
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        raise SubmissionValidationError("CSV must be an existing, nonempty regular file.")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            parsed = list(csv.reader(stream, strict=True))
    except (UnicodeError, csv.Error, OSError) as exc:
        raise SubmissionValidationError("CSV is not valid UTF-8/standard CSV.") from exc
    if not parsed or not parsed[0]:
        raise SubmissionValidationError("CSV header is missing.")
    header = tuple(parsed[0])
    if any(value == "" for value in header) or len(set(header)) != len(header):
        raise SubmissionValidationError("CSV header contains blank or duplicate names.")
    if any(value.startswith("Unnamed:") for value in header):
        raise SubmissionValidationError("CSV contains an unexpected index column.")
    rows: list[tuple[str, ...]] = []
    for row in parsed[1:]:
        if len(row) != len(header):
            raise SubmissionValidationError("CSV logical row has the wrong field count.")
        if all(value == "" for value in row):
            raise SubmissionValidationError("CSV contains a blank logical data row.")
        rows.append(tuple(row))
    return RawCSV(path=path, header=header, rows=tuple(rows))


def numeric_series(raw: RawCSV, column: str) -> tuple[pd.Series, pd.Series]:
    if column not in raw.header:
        empty = pd.Series(dtype="float64")
        return empty, pd.Series(dtype="bool")
    text = raw.frame[column]
    values = pd.to_numeric(text, errors="coerce")
    valid = text.ne("") & values.notna()
    return values.astype("float64"), valid


def exact_sequence(left: pd.Series, right: pd.Series) -> bool:
    return left.astype("string").tolist() == right.astype("string").tolist()
