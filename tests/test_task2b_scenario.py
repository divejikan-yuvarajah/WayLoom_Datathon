"""Synthetic-only Phase 18 scenario/reference contract tests."""

from __future__ import annotations

from copy import deepcopy

import pandas as pd
import pytest

from src.task2b.scenario import (ScenarioValidationError, build_s1_scenario, validate_district_travel,
                                  validate_fleet, validate_orders, validate_service_allowance, validate_vehicles)


def _frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    orders = pd.DataFrame([
        {"scenario": "S1", "order_ref": "o1", "outlet_id": "shared", "brand": "Fresh", "district": "D1", "depot": "Peliyagoda", "dock_type": "dock", "parking_constraint": "van_only", "temp_requirement": "chilled", "order_weight_kg": 1.0, "order_volume_m3": 2.0, "deferred_yesterday": 1, "days_since_last_served": 4},
        {"scenario": "S1", "order_ref": "o2", "outlet_id": "shared", "brand": "Style", "district": "D2", "depot": "Peliyagoda", "dock_type": "dock", "parking_constraint": "standard", "temp_requirement": "ambient", "order_weight_kg": 3.0, "order_volume_m3": 4.0, "deferred_yesterday": 0, "days_since_last_served": 1},
        {"scenario": "S2", "order_ref": "other", "outlet_id": "x", "brand": "Tech", "district": "D1", "depot": "Other", "dock_type": "dock", "parking_constraint": "standard", "temp_requirement": "ambient", "order_weight_kg": 2.0, "order_volume_m3": 1.0, "deferred_yesterday": 0, "days_since_last_served": 0},
    ])
    fleet = pd.DataFrame([{"scenario": "S1", "vehicle_id": "v1", "status": "available"}, {"scenario": "S1", "vehicle_id": "v2", "status": "in_workshop"}, {"scenario": "S2", "vehicle_id": "v3", "status": "available"}])
    vehicles = pd.DataFrame([{"vehicle_id": "v1", "type": "van", "temp": "reefer", "weight_cap_kg": 10, "volume_cap_m3": 10, "depot": "Peliyagoda"}, {"vehicle_id": "v2", "type": "truck", "temp": "ambient", "weight_cap_kg": 10, "volume_cap_m3": 10, "depot": "Peliyagoda"}, {"vehicle_id": "v3", "type": "van", "temp": "ambient", "weight_cap_kg": 10, "volume_cap_m3": 10, "depot": "Other"}])
    travel = pd.DataFrame([{"depot": "Peliyagoda", "district": "D1", "depot_to_district_freeflow_min": 1, "inter_stop_freeflow_min": 1}, {"depot": "Peliyagoda", "district": "D2", "depot_to_district_freeflow_min": 1, "inter_stop_freeflow_min": 1}])
    allowance = pd.DataFrame([{"brand": brand, "dock_type": "dock", "service_allowance_min": 1} for brand in ("Fresh", "Style")])
    config = {"version": 1, "scenario": {"expected_id": "S1", "expected_depot": "Peliyagoda"}, "fleet": {"available_status": "available", "workshop_status": "in_workshop"}}
    return orders, fleet, vehicles, travel, allowance, config


def test_orders_use_order_ref_and_allow_duplicate_outlet() -> None:
    orders, *_ = _frames()
    assert len(validate_orders(orders)) == len(orders)
    duplicate = orders.copy(); duplicate.loc[1, "order_ref"] = "o1"
    with pytest.raises(ScenarioValidationError, match="order_ref"):
        validate_orders(duplicate)
    for column, value in (("deferred_yesterday", 2), ("order_weight_kg", -1), ("order_volume_m3", float("inf")), ("days_since_last_served", 1.5)):
        bad = orders.copy()
        if column == "days_since_last_served":
            bad[column] = bad[column].astype(float)
        bad.loc[0, column] = value
        with pytest.raises(ScenarioValidationError):
            validate_orders(bad)


def test_fleet_references_and_s1_availability_are_fail_closed() -> None:
    frames = _frames()
    result = build_s1_scenario(*frames)
    assert result["available_fleet_s1"].status.eq("available").all()
    assert result["usable_fleet_s1"].vehicle_id.tolist() == ["v1"]
    assert not set(result["available_fleet_s1"].vehicle_id).intersection(result["workshop_vehicle_ids"])
    assert result["depot_fleet_diagnostics"] == {"s1_non_peliyagoda_order_count": 0,
        "available_vehicle_count": 1, "available_peliyagoda_home_vehicle_count": 1,
        "available_non_peliyagoda_home_vehicle_count": 0, "workshop_vehicle_count": 1}
    orders, fleet, vehicles, travel, allowance, config = _frames()
    fleet.loc[0, "status"] = "unknown"
    with pytest.raises(ScenarioValidationError, match="unsupported"):
        build_s1_scenario(orders, fleet, vehicles, travel, allowance, config)
    orders.loc[0, "depot"] = "Other"
    with pytest.raises(ScenarioValidationError, match="Peliyagoda"):
        build_s1_scenario(orders, _frames()[1], vehicles, travel, allowance, config)
    duplicate = _frames()[1]
    duplicate.loc[1, "vehicle_id"] = "v1"
    with pytest.raises(ScenarioValidationError, match="vehicle_id"):
        validate_fleet(duplicate)


def test_reference_validation_and_coverage_fail_closed() -> None:
    orders, fleet, vehicles, travel, allowance, config = _frames()
    bad = vehicles.copy(); bad.loc[0, "weight_cap_kg"] = 0
    with pytest.raises(ScenarioValidationError): validate_vehicles(bad)
    bad = vehicles.copy(); bad.loc[0, "type"] = "car"
    with pytest.raises(ScenarioValidationError, match="type"): validate_vehicles(bad)
    bad = vehicles.copy(); bad.loc[0, "temp"] = "frozen"
    with pytest.raises(ScenarioValidationError, match="temperature"): validate_vehicles(bad)
    bad = travel.copy(); bad.loc[0, "depot_to_district_freeflow_min"] = -1
    with pytest.raises(ScenarioValidationError): validate_district_travel(bad)
    bad = allowance.copy(); bad.loc[0, "service_allowance_min"] = float("nan")
    with pytest.raises(ScenarioValidationError): validate_service_allowance(bad)
    with pytest.raises(ScenarioValidationError, match="district travel"):
        build_s1_scenario(orders, fleet, vehicles, travel.iloc[:1], allowance, config)
    with pytest.raises(ScenarioValidationError, match="vehicle"):
        build_s1_scenario(orders, fleet, vehicles.iloc[1:], travel, allowance, config)
    with pytest.raises(ScenarioValidationError, match="service allowance"):
        build_s1_scenario(orders, fleet, vehicles, travel, allowance.iloc[:1], config)
    with pytest.raises(ScenarioValidationError, match="unique"):
        validate_district_travel(pd.concat([travel, travel.iloc[[0]]], ignore_index=True))
    with pytest.raises(ScenarioValidationError, match="unique"):
        validate_service_allowance(pd.concat([allowance, allowance.iloc[[0]]], ignore_index=True))
