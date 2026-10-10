"""Deterministic finite-sample higher-order-statistic quantiles."""

from __future__ import annotations

from math import ceil
from typing import Iterable

import numpy as np


class QuantileError(ValueError):
    """A calibration score or requested coverage level is invalid."""


def validate_coverage_level(coverage: float) -> float:
    try:
        value = float(coverage)
    except (TypeError, ValueError) as exc:
        raise QuantileError("Coverage must be numeric.") from exc
    if not np.isfinite(value) or not 0.0 < value < 1.0:
        raise QuantileError("Coverage must be strictly between zero and one.")
    return value


def validate_coverage_levels(levels: Iterable[float]) -> tuple[float, ...]:
    values = tuple(validate_coverage_level(level) for level in levels)
    if not values or len(values) != len(set(values)) or tuple(sorted(values)) != values:
        raise QuantileError("Coverage levels must be nonempty, unique, and increasing.")
    return values


def validate_scores(scores: Iterable[float]) -> np.ndarray:
    values = np.asarray(list(scores), dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise QuantileError("At least one one-dimensional calibration score is required.")
    if not np.isfinite(values).all():
        raise QuantileError("Calibration scores must be finite.")
    if (values < 0).any():
        raise QuantileError("Absolute-residual scores cannot be negative.")
    return values


def finite_sample_rank(sample_count: int, coverage: float) -> int:
    """Return the one-based conformal-style rank, clipped to ``[1, n]``."""
    if type(sample_count) is not int or sample_count < 1:
        raise QuantileError("Sample count must be a positive integer.")
    level = validate_coverage_level(coverage)
    return min(sample_count, max(1, ceil((sample_count + 1) * level)))


def finite_sample_quantile(scores: Iterable[float], coverage: float) -> float:
    """Return the kth sorted score without interpolation.

    ``k = clip(ceil((n + 1) * coverage), 1, n)`` is one-based.
    """
    values = np.sort(validate_scores(scores), kind="stable")
    return float(values[finite_sample_rank(len(values), coverage) - 1])
