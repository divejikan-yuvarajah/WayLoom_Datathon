import pandas as pd
import pytest

from src.task2b.direct_insertion import (
    DirectInsertionError,
    analyze_direct_insertion,
    require_no_direct_insertion,
)
from tests.test_task2b_optimizer_constraints import _custom_bundle


def _allocation(rows):
    return pd.DataFrame(rows, columns=["scenario", "order_ref", "outlet_id", "decision", "vehicle_id", "trip_id"])


def _data(specs, *, cap=10, allowance_minutes=1):
    districts = sorted({item[1] for item in specs})
    travel = [{"depot": "Peliyagoda", "district": district,
               "depot_to_district_freeflow_min": 0, "inter_stop_freeflow_min": 0}
              for district in districts]
    brands = sorted({item[0] for item in specs})
    allowance = [{"brand": brand, "dock_type": "dock",
                  "service_allowance_min": allowance_minutes}
                 for brand in brands]
    return _custom_bundle(specs, travel, allowance, weight_cap=cap, volume_cap=cap).data


def test_same_group_spare_capacity_and_time_is_directly_insertable_and_contradicts_freeze():
    data = _data([("Fresh", "A", "dock", 2, 2)] * 2)
    frozen = _allocation([
        ["S1", "o0", "x", "served", "v", 1],
        ["S1", "o1", "x", "deferred", "", ""],
    ])
    result = analyze_direct_insertion(data, frozen, "o1")
    assert result.direct_insert_possible
    assert any(item.path_type == "EXISTING_SAME_GROUP" and item.feasible for item in result.attempts)
    with pytest.raises(DirectInsertionError, match="contradicts"):
        require_no_direct_insertion(result)


@pytest.mark.parametrize("cap,specs,blocker", [
    (9, [("Fresh", "A", "dock", 5, 1)] * 2, "WEIGHT_CAPACITY"),
    (9, [("Fresh", "A", "dock", 1, 5)] * 2, "VOLUME_CAPACITY"),
])
def test_existing_trip_capacity_blockers_are_recorded(cap, specs, blocker):
    data = _data(specs, cap=cap)
    frozen = _allocation([
        ["S1", "o0", "x", "served", "v", 1],
        ["S1", "o1", "x", "deferred", "", ""],
    ])
    result = analyze_direct_insertion(data, frozen, "o1")
    existing = next(item for item in result.attempts if item.path_type == "EXISTING_SAME_GROUP")
    assert blocker in existing.blockers


def test_different_group_uses_free_slot_or_reports_two_trip_pressure():
    specs = [("Fresh", district, "dock", 1, 1) for district in ("A", "B", "C")]
    data = _data(specs)
    one_trip = _allocation([
        ["S1", "o0", "x", "served", "v", 1],
        ["S1", "o1", "x", "deferred", "", ""],
        ["S1", "o2", "x", "deferred", "", ""],
    ])
    free = analyze_direct_insertion(data, one_trip, "o1")
    assert any(item.path_type == "NEW_TRIP" and item.feasible for item in free.attempts)
    two_trips = _allocation([
        ["S1", "o0", "x", "served", "v", 1],
        ["S1", "o1", "x", "served", "v", 2],
        ["S1", "o2", "x", "deferred", "", ""],
    ])
    blocked = analyze_direct_insertion(data, two_trips, "o2")
    assert not blocked.direct_insert_possible
    assert "NO_FREE_TRIP_SLOT" in blocked.blocker_codes


@pytest.mark.parametrize("brand,minutes,blocker", [
    ("Fresh", 136, "FRESH_TIME_BUDGET"),
    ("Style", 241, "STYLE_TECH_TIME_BUDGET"),
])
def test_combined_vehicle_time_budget_blocker(brand, minutes, blocker):
    data = _data([(brand, "A", "dock", 1, 1)] * 2, allowance_minutes=minutes)
    frozen = _allocation([
        ["S1", "o0", "x", "served", "v", 1],
        ["S1", "o1", "x", "deferred", "", ""],
    ])
    result = analyze_direct_insertion(data, frozen, "o1")
    assert blocker in result.blocker_codes
