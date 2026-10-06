import pandas as pd
import pytest
import json

from src.task2b.counterfactual_delta import (
    CounterfactualDeltaError,
    allocation_change_rows,
    canonical_objective_vector,
    compare_objective_vectors,
    first_degraded_policy_tier,
    summarize_allocation_changes,
)
from src.task2b.priority import OBJECTIVE_LEVELS


def _vector(**updates):
    value = {name: 0 for name in OBJECTIVE_LEVELS}
    value.update(updates)
    return value


def test_direction_aware_max_min_and_first_degraded_tier():
    base = _vector(served_order_count=10, avoidable_reefer_assignment_count=2)
    assert compare_objective_vectors(_vector(served_order_count=11, avoidable_reefer_assignment_count=99), base) == "BETTER"
    worse_max = _vector(served_order_count=9, avoidable_reefer_assignment_count=0)
    assert compare_objective_vectors(worse_max, base) == "WORSE"
    assert first_degraded_policy_tier(worse_max, base).startswith("LEVEL 1")
    worse_min = _vector(served_order_count=10, avoidable_reefer_assignment_count=3)
    assert compare_objective_vectors(worse_min, base) == "WORSE"
    assert first_degraded_policy_tier(worse_min, base).startswith("LEVEL 7B")
    assert compare_objective_vectors(base, base) == "EQUAL"


def test_no_naive_tuple_or_wrong_key_order_is_accepted():
    base = _vector()
    wrong = dict(reversed(list(base.items())))
    with pytest.raises(CounterfactualDeltaError, match="keys/order"):
        compare_objective_vectors(wrong, base)


def test_manifest_vector_is_canonicalized_after_sorted_json_serialization():
    original = {name: index for index, name in enumerate(OBJECTIVE_LEVELS)}
    sorted_json = json.loads(json.dumps(original, sort_keys=True))
    assert tuple(sorted_json) != OBJECTIVE_LEVELS
    restored = canonical_objective_vector(sorted_json)
    assert tuple(restored) == OBJECTIVE_LEVELS
    assert restored == original


def test_changed_metric_distinguishes_same_assignment_moves_and_decisions():
    columns = ["order_ref", "decision", "vehicle_id", "trip_id"]
    before = pd.DataFrame([
        ["a", "served", "v1", 1], ["b", "served", "v1", 1],
        ["c", "served", "v2", 2], ["d", "deferred", "", ""],
    ], columns=columns)
    after = pd.DataFrame([
        ["a", "served", "v1", 1], ["b", "served", "v1", 2],
        ["c", "deferred", "", ""], ["d", "served", "v2", 2],
    ], columns=columns)
    changes = allocation_change_rows(before, after).set_index("order_ref")
    assert not changes.loc["a", "changed"]
    assert changes.loc["b", "served_reassigned"]
    assert changes.loc["c", "served_to_deferred"]
    assert changes.loc["d", "deferred_to_served"]
    summary = summarize_allocation_changes(changes.reset_index())
    assert summary["changed_order_count"] == 3
    assert summary["served_reassigned_count"] == 1
