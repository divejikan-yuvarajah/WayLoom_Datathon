from dataclasses import replace

import pytest

from src.task2b.individual_feasibility import (
    IndividualFeasibilityError,
    evaluate_individual_feasibility,
)
from tests.test_task2b_optimizer_constraints import _custom_bundle


def _one(brand: str, minutes: int):
    travel = [{"depot": "Peliyagoda", "district": "A",
               "depot_to_district_freeflow_min": 0, "inter_stop_freeflow_min": 0}]
    allowance = [{"brand": brand, "dock_type": "dock", "service_allowance_min": minutes}]
    return _custom_bundle([(brand, "A", "dock", 1, 1)], travel, allowance).data


@pytest.mark.parametrize("brand,minutes,expected", [
    ("Fresh", 270, True), ("Fresh", 271, False),
    ("Style", 480, True), ("Style", 481, False),
    ("Tech", 480, True), ("Tech", 481, False),
])
def test_exact_single_order_time_boundaries(brand, minutes, expected):
    result = evaluate_individual_feasibility(_one(brand, minutes), "o0")
    assert result.individually_feasible is expected
    if not expected:
        assert result.time_blocker_code == (
            "FRESH_TIME_BUDGET" if brand == "Fresh" else "STYLE_TECH_TIME_BUDGET"
        )


def test_zero_compatible_vehicles_is_hard_individual_infeasibility():
    data = _one("Fresh", 1)
    result = evaluate_individual_feasibility(replace(data, compatible_pairs=()), "o0")
    assert result.compatible_vehicle_count == 0
    assert result.individually_feasible is False
    assert result.time_blocker_code is None


def test_phase19_compatible_pair_is_defensively_rechecked():
    data = _one("Fresh", 1)
    bad_vehicle = {**data.vehicle_rows["v"], "weight_cap_kg": 0}
    bad = replace(data, vehicle_rows={"v": bad_vehicle}, weight_cap={"v": 0})
    with pytest.raises(IndividualFeasibilityError, match="defensive"):
        evaluate_individual_feasibility(bad, "o0")

