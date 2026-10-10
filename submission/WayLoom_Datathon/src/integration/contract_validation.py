"""Canonical two-layer validation for exported Phase 28 payloads."""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel

from src.integration.models import (
    AllocationInsightResponse,
    DeferralExplanationResponse,
    DemandForecastResponse,
    Task1Response,
)
from src.integration.schemas import generated_schemas


CONTRACT_MODELS: dict[str, type[BaseModel]] = {
    "task1.schema.json": Task1Response,
    "demand_forecast.schema.json": DemandForecastResponse,
    "allocation_insight.schema.json": AllocationInsightResponse,
    "deferral_explanation.schema.json": DeferralExplanationResponse,
}


def _schema_filename(schema_name: str) -> str:
    filename = schema_name if schema_name.endswith(".schema.json") else f"{schema_name}.schema.json"
    if filename not in CONTRACT_MODELS:
        raise ValueError("Unknown integration schema.")
    return filename


def validate_json_schema(
    schema_name: str,
    payload: dict[str, Any],
    *,
    schema: dict[str, Any] | None = None,
) -> None:
    """Validate structure and all conditions expressible in standard JSON Schema."""
    filename = _schema_filename(schema_name)
    selected = schema if schema is not None else generated_schemas()[filename]
    Draft202012Validator.check_schema(selected)
    Draft202012Validator(selected).validate(payload)


def validate_semantics(schema_name: str, payload: dict[str, Any]) -> BaseModel:
    """Apply the canonical Pydantic/domain rules, including sibling arithmetic."""
    filename = _schema_filename(schema_name)
    return CONTRACT_MODELS[filename].model_validate(payload)


def validate_contract_payload(
    schema_name: str,
    payload: dict[str, Any],
    *,
    schema: dict[str, Any] | None = None,
) -> BaseModel:
    """Run standard JSON Schema first, then canonical semantic validation."""
    validate_json_schema(schema_name, payload, schema=schema)
    return validate_semantics(schema_name, payload)
