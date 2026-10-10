"""Checksum-first I/O for trusted, registry-owned local model artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

import joblib


class ArtifactIOError(ValueError):
    """A registered artifact failed path, integrity, or load validation."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def resolve_model_artifact(
    project_root: Path,
    relative_path: str,
    *,
    require_exists: bool = True,
) -> Path:
    """Resolve one package-relative artifact and keep it under ``models/``."""
    root = Path(project_root).resolve()
    models_root = (root / "models").resolve()
    raw = str(relative_path).strip().replace("\\", "/")
    parsed = urlparse(raw)
    pure = PurePosixPath(raw)
    if (
        not raw
        or parsed.scheme
        or raw.startswith(("/", "//"))
        or pure.is_absolute()
        or ".." in pure.parts
        or pure.parts[0:1] != ("models",)
    ):
        raise ArtifactIOError("Artifact path must be package-relative and remain under models/.")
    resolved = (root / Path(*pure.parts)).resolve()
    if not _inside(resolved, models_root):
        raise ArtifactIOError("Artifact path escapes the approved models root.")
    if require_exists and not resolved.is_file():
        raise ArtifactIOError("A required registered artifact is missing.")
    return resolved


def verify_registered_file(project_root: Path, entry: dict[str, Any]) -> Path:
    """Verify size and SHA256 before any parser or deserializer sees the file."""
    path = resolve_model_artifact(project_root, str(entry.get("relative_path", "")))
    expected_hash = str(entry.get("sha256", ""))
    expected_size = entry.get("size_bytes")
    if len(expected_hash) != 64 or any(char not in "0123456789abcdef" for char in expected_hash):
        raise ArtifactIOError("Registered artifact SHA256 is invalid.")
    if type(expected_size) is not int or expected_size < 1:
        raise ArtifactIOError("Registered artifact size is invalid.")
    if path.stat().st_size != expected_size:
        raise ArtifactIOError("Registered artifact size mismatch.")
    if sha256_file(path) != expected_hash:
        raise ArtifactIOError("Registered artifact checksum mismatch.")
    return path


def load_verified_joblib(project_root: Path, entry: dict[str, Any]) -> Any:
    """Load one allowlisted joblib artifact after its integrity check passes."""
    if entry.get("serializer") != "joblib" or entry.get("format") != "joblib":
        raise ArtifactIOError("Artifact is not registered with the supported joblib serializer.")
    path = verify_registered_file(project_root, entry)
    try:
        return joblib.load(path)
    except Exception as exc:
        raise ArtifactIOError("Registered joblib artifact could not be loaded safely.") from exc


def load_verified_json(project_root: Path, entry: dict[str, Any]) -> dict[str, Any]:
    """Load one registered JSON metadata artifact after integrity verification."""
    if entry.get("serializer") != "json" or entry.get("format") != "json":
        raise ArtifactIOError("Artifact is not registered as JSON.")
    path = verify_registered_file(project_root, entry)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ArtifactIOError("Registered JSON artifact could not be parsed.") from exc
    if not isinstance(value, dict):
        raise ArtifactIOError("Registered JSON artifact must contain an object.")
    return value
