import copy

import pytest
from jsonschema import ValidationError as JsonSchemaValidationError
from pydantic import ValidationError as PydanticValidationError

from src.integration.contract_validation import (
    validate_contract_payload,
    validate_json_schema,
)
from src.integration.schemas import generated_schemas
from src.integration.synthetic_data import tracked_examples


def _example(name):
    return copy.deepcopy(tracked_examples()[name])


@pytest.mark.parametrize("brand", ["Style", "Tech"])
def test_exported_demand_schema_rejects_nonfresh_chilled(brand):
    payload = _example("demand_forecast_style_response.synthetic.json")
    payload["brand"] = brand
    payload["pred_chilled_volume_m3"] = 1
    with pytest.raises(JsonSchemaValidationError):
        validate_json_schema("demand_forecast", payload)


def test_contract_validator_rejects_chilled_greater_than_total():
    payload = _example("demand_forecast_response.synthetic.json")
    payload["pred_total_volume_m3"] = 5
    payload["pred_chilled_volume_m3"] = 6
    with pytest.raises(PydanticValidationError):
        validate_contract_payload("demand_forecast", payload)


@pytest.mark.parametrize("chilled", [0, 5])
def test_contract_validator_accepts_fresh_boundary_values(chilled):
    payload = _example("demand_forecast_response.synthetic.json")
    payload["pred_total_volume_m3"] = 5
    payload["pred_chilled_volume_m3"] = chilled
    validate_contract_payload("demand_forecast", payload)


def test_contract_validator_rejects_unbalanced_allocation_counts():
    payload = _example("allocation_response.synthetic.json")
    payload["summary"].update(orders_total=10, orders_served=8, orders_deferred=1)
    with pytest.raises(PydanticValidationError):
        validate_contract_payload("allocation_insight", payload)


def test_contract_validator_accepts_balanced_allocation_counts():
    payload = _example("allocation_response.synthetic.json")
    payload["summary"].update(orders_total=10, orders_served=8, orders_deferred=2)
    validate_contract_payload("allocation_insight", payload)


@pytest.mark.parametrize("field", ["reason_class", "evidence"])
def test_exported_deferral_schema_rejects_not_available_with_evidence(field):
    payload = _example("deferral_explanation.synthetic.json")
    payload["availability"] = "not_available"
    if field == "reason_class":
        payload["evidence"] = None
        payload["primary_reason_code"] = None
        payload["secondary_reason_codes"] = []
    else:
        payload["reason_class"] = None
        payload["primary_reason_code"] = None
        payload["secondary_reason_codes"] = []
    with pytest.raises(JsonSchemaValidationError):
        validate_json_schema("deferral_explanation", payload)


@pytest.mark.parametrize("missing", ["reason_class", "primary_reason_code"])
def test_exported_deferral_schema_requires_reason_when_available(missing):
    payload = _example("deferral_explanation_policy.synthetic.json")
    payload["availability"] = "available"
    payload["source_mode"] = "private_local"
    payload[missing] = None
    with pytest.raises(JsonSchemaValidationError):
        validate_json_schema("deferral_explanation", payload)


def test_valid_deferral_modes_pass_full_contract_validation():
    synthetic = _example("deferral_explanation_policy.synthetic.json")
    validate_contract_payload("deferral_explanation", synthetic)
    available = copy.deepcopy(synthetic)
    available["availability"] = "available"
    available["source_mode"] = "private_local"
    validate_contract_payload("deferral_explanation", available)
    unavailable = copy.deepcopy(synthetic)
    unavailable.update(
        availability="not_available", reason_class=None,
        primary_reason_code=None, secondary_reason_codes=[], evidence=None,
        summary="A real explanation is not available in this mode.",
    )
    validate_contract_payload("deferral_explanation", unavailable)


def test_packaged_examples_pass_full_contract_validation():
    schemas = generated_schemas()
    mapping = {
        "task1_response.synthetic.json": "task1.schema.json",
        "demand_forecast_response.synthetic.json": "demand_forecast.schema.json",
        "demand_forecast_style_response.synthetic.json": "demand_forecast.schema.json",
        "allocation_response.synthetic.json": "allocation_insight.schema.json",
        "deferral_explanation.synthetic.json": "deferral_explanation.schema.json",
        "deferral_explanation_policy.synthetic.json": "deferral_explanation.schema.json",
    }
    for filename, payload in tracked_examples().items():
        schema_name = mapping[filename]
        validate_contract_payload(schema_name, payload, schema=schemas[schema_name])
