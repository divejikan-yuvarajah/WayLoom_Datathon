"""Targeted runtime-version metadata for frozen model artifacts."""

from __future__ import annotations

import importlib.metadata
import platform


RUNTIME_PACKAGES = (
    "numpy",
    "pandas",
    "scikit-learn",
    "catboost",
    "lightgbm",
    "joblib",
)


def current_model_runtime_versions() -> dict[str, str]:
    """Return only packages required by the final Task 1/Task 2A loaders."""
    versions = {"python": platform.python_version()}
    for package in RUNTIME_PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "NOT_INSTALLED"
    return versions
