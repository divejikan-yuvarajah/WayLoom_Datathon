import json

import pytest

from src.task2b.demo_example_selector import DemoSelectionError, select_demo_examples


def _record(order_ref, reason_class, position, changes=2, complete=True):
    return {
        "order_ref": order_ref, "reason_class": reason_class,
        "primary_reason_code": "LOWER_POLICY_PRIORITY" if reason_class == "POLICY_TRADEOFF" else "HARD_NO_COMPATIBLE_VEHICLE",
        "secondary_reason_codes": ["TRIP_SLOT_LIMIT"] if reason_class == "POLICY_TRADEOFF" else [],
        "counterfactual_complete": complete, "minimum_changed_orders": changes,
        "original_order_position": position, "brand": "Fresh", "district": "D",
        "temp_requirement": "chilled", "van_only": True,
        "compatible_vehicle_count": 1, "first_degraded_policy_tier": "LEVEL 3",
        "human_explanation": "Solver-grounded anonymous explanation.",
    }


def test_selector_is_deterministic_diverse_bounded_and_anonymized():
    records = [
        _record("secret-1", "POLICY_TRADEOFF", 2, 3),
        _record("secret-2", "UNAVOIDABLE_HARD", 1, None),
        _record("secret-3", "POLICY_TRADEOFF", 0, 1),
    ]
    first = select_demo_examples(records, max_examples=2)
    second = select_demo_examples(records, max_examples=2)
    assert first == second
    private, public = first
    assert len(public) == 2
    assert len({item["reason_class"] for item in public}) == 2
    assert [item["example_label"] for item in public] == ["DEFERRAL_EXAMPLE_A", "DEFERRAL_EXAMPLE_B"]
    serialized = json.dumps(public)
    assert "secret-" not in serialized and "order_ref" not in serialized
    assert any(item["order_ref"].startswith("secret-") for item in private)


def test_unresolved_examples_are_rejected_and_maximum_is_two():
    with pytest.raises(DemoSelectionError, match="No resolved"):
        select_demo_examples([_record("x", "POLICY_TRADEOFF", 0, complete=False)])
    with pytest.raises(DemoSelectionError, match="one or two"):
        select_demo_examples([_record("x", "POLICY_TRADEOFF", 0)], max_examples=3)

