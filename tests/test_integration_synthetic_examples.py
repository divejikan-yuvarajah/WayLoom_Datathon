import json
from pathlib import Path

from src.integration.privacy import assert_public_payload, validate_synthetic_identifier
from src.integration.schemas import EXAMPLE_SCHEMA, generated_schemas, validate_instance
from src.integration.synthetic_data import tracked_examples


ROOT = Path(__file__).resolve().parents[1]


def test_generated_examples_are_deterministic_and_validate():
    first = tracked_examples(42)
    second = tracked_examples(42)
    assert first == second
    schemas = generated_schemas()
    for filename, payload in first.items():
        validate_instance(payload, schemas[EXAMPLE_SCHEMA[filename]])
        assert_public_payload(payload)


def test_all_tracked_examples_and_schemas_match_generated_contract():
    schemas = generated_schemas()
    examples = tracked_examples(42)
    for filename, schema in schemas.items():
        tracked = json.loads((ROOT / "schemas" / "integration" / filename).read_text(encoding="utf-8"))
        assert tracked == schema
    for filename, payload in examples.items():
        tracked = json.loads((ROOT / "examples" / "integration" / filename).read_text(encoding="utf-8"))
        assert tracked == payload
        validate_instance(tracked, schemas[EXAMPLE_SCHEMA[filename]])


def test_synthetic_identifiers_and_required_scenarios():
    examples = tracked_examples()
    assert validate_synthetic_identifier(examples["task1_response.synthetic.json"]["delivery_ref"])
    assert validate_synthetic_identifier(examples["demand_forecast_response.synthetic.json"]["forecast_ref"])
    assert validate_synthetic_identifier(examples["allocation_response.synthetic.json"]["scenario_ref"])
    assert examples["demand_forecast_style_response.synthetic.json"]["pred_chilled_volume_m3"] == 0
    assert examples["deferral_explanation.synthetic.json"]["reason_class"] == "UNAVOIDABLE_HARD"
    assert examples["deferral_explanation_policy.synthetic.json"]["reason_class"] == "POLICY_TRADEOFF"


def test_generation_has_no_filesystem_dependency(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("synthetic generation attempted filesystem access")
    monkeypatch.setattr("pathlib.Path.open", forbidden)
    monkeypatch.setattr("pathlib.Path.read_text", forbidden)
    monkeypatch.setattr("pathlib.Path.read_bytes", forbidden)
    assert json.dumps(tracked_examples(42), sort_keys=True)
