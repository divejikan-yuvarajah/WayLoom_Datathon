"""Solver-neutral Task 2B artifact schema and file-integrity helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path


ALLOCATION_COLUMNS = (
    "scenario",
    "order_ref",
    "outlet_id",
    "decision",
    "vehicle_id",
    "trip_id",
)


def sha256_file(path: Path) -> str:
    """Return the SHA256 digest of a file without interpreting its contents."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
