"""Explicit allowlisted adapters; never serialize arbitrary internal objects."""

from __future__ import annotations

from collections.abc import Mapping

from src.integration.models import DeferralExplanationResponse
from src.integration.synthetic_data import LIMITATION


PHASE26_ALLOWED_FIELDS = {
    "example_ref", "availability", "reason_class", "primary_reason_code",
    "secondary_reason_codes", "summary", "evidence", "limitations",
}


def adapt_sanitized_phase26_example(payload: Mapping[str, object]) -> DeferralExplanationResponse:
    """Adapt an already-sanitized Phase 26 demo object through a strict allowlist."""
    clean = {key: payload[key] for key in PHASE26_ALLOWED_FIELDS if key in payload}
    clean.setdefault("availability", "available")
    clean.setdefault("limitations", LIMITATION)
    return DeferralExplanationResponse(source_mode="private_local", **clean)


def public_model_dict(model: object) -> dict:
    """Serialize only a validated Pydantic public response model."""
    model_dump = getattr(model, "model_dump", None)
    if model_dump is None:
        raise TypeError("Public response must be a validated integration model.")
    return model_dump(mode="json")
