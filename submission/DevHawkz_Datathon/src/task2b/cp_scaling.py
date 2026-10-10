"""Exact decimal-to-integer conversion for the local CP-SAT model."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Iterable


class ScalingError(ValueError):
    """A source number cannot be represented under the configured precision."""


def _decimal(value: object) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ScalingError("Invalid numeric source value.") from exc
    if not result.is_finite():
        raise ScalingError("Numeric source values must be finite.")
    return result


def derive_exact_scale(values: Iterable[object], max_decimal_places: int = 6) -> int:
    if not isinstance(max_decimal_places, int) or max_decimal_places < 0 or max_decimal_places > 12:
        raise ScalingError("Unsupported decimal precision limit.")
    required = 0
    for value in values:
        number = _decimal(value)
        places = max(0, -number.normalize().as_tuple().exponent) if number else 0
        if places > max_decimal_places:
            raise ScalingError("Source value exceeds exact decimal precision limit.")
        required = max(required, places)
    return 10 ** required


def to_scaled_int(value: object, scale: int) -> int:
    if not isinstance(scale, int) or scale < 1:
        raise ScalingError("Scale must be a positive integer.")
    scaled = _decimal(value) * scale
    if scaled != scaled.to_integral_value():
        raise ScalingError("Scaling would round a source value.")
    integer = int(scaled)
    if abs(integer) > (2**63 - 1):
        raise ScalingError("Scaled value exceeds signed 64-bit range.")
    return integer


def from_scaled_int(value: int, scale: int) -> Decimal:
    if not isinstance(value, int) or not isinstance(scale, int) or scale < 1:
        raise ScalingError("Invalid scaled integer or scale.")
    return Decimal(value) / Decimal(scale)


def validate_exact_scaling(values: Iterable[object], scale: int) -> None:
    for value in values:
        if from_scaled_int(to_scaled_int(value, scale), scale) != _decimal(value):
            raise ScalingError("Numeric round-trip failed.")
