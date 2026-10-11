"""Schema generation and validation helpers for the versioned contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from src.integration.models import (
    AllocationInsightResponse,
    DeferralExplanationResponse,
    DemandForecastResponse,
    Task1Response,
)


SCHEMA_MODELS = {
    "task1.schema.json": Task1Response,
    "demand_forecast.schema.json": DemandForecastResponse,
    "allocation_insight.schema.json": AllocationInsightResponse,
    "deferral_explanation.schema.json": DeferralExplanationResponse,
}

EXAMPLE_SCHEMA = {
    "task1_response.synthetic.json": "task1.schema.json",
    "demand_forecast_response.synthetic.json": "demand_forecast.schema.json",
    "demand_forecast_style_response.synthetic.json": "demand_forecast.schema.json",
    "allocation_response.synthetic.json": "allocation_insight.schema.json",
    "deferral_explanation.synthetic.json": "deferral_explanation.schema.json",
    "deferral_explanation_policy.synthetic.json": "deferral_explanation.schema.json",
}


def generated_schemas() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for filename, model in SCHEMA_MODELS.items():
        schema = model.model_json_schema(mode="validation")
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["$id"] = f"https://wayloom.local/integration/1.0/{filename}"
        result[filename] = schema
    return result


def validate_instance(instance: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate JSON-Schema-expressible rules only.

    Use ``validate_contract_payload`` for the complete public contract,
    including sibling arithmetic invariants.
    """
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError("Integration JSON document must be an object.")
    return value
