from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.common.data_quality import load_rules
from src.common.schema_assertions import (
    SchemaAssertionError,
    assert_required_columns,
    assert_required_files,
    assert_task1_leakage_guard,
    collect_hard_schema_results,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rules() -> dict:
    return load_rules(ROOT / "configs" / "data_quality_rules.yaml")


@pytest.fixture
def discovery() -> dict:
    return {"missing_required": [], "duplicate_required": {}}


@pytest.fixture
def valid_tables() -> dict[str, pd.DataFrame]:
    outlets = pd.DataFrame(
        [
            {
                "outlet_id": f"OUT{i:03d}",
                "brand": "Fresh" if i == 1 else "Style" if i == 2 else "Tech",
                "district": f"District{((i - 1) % 12) + 1}",
                "depot": "Peliyagoda" if i % 2 else "Kandy",
                "dock_type": "rear_dock" if i % 3 == 1 else ("street" if i % 3 == 2 else "mall_bay"),
                "parking_constraint": "normal" if i % 3 == 1 else ("van_only" if i % 3 == 2 else "mall_dock"),
                "mall_window": "" if i % 3 != 0 else "09:00-11:00",
                "window_open_time": "07:00",
                "window_close_time": "18:00",
            }
            for i in range(1, 121)
        ]
    )
    outlets.loc[outlets["outlet_id"] == "OUT001", ["brand", "district", "depot", "dock_type", "parking_constraint", "mall_window"]] = [
        "Fresh",
        "District1",
        "Peliyagoda",
        "rear_dock",
        "normal",
        "",
    ]
    outlets.loc[outlets["outlet_id"] == "OUT001", ["window_open_time", "window_close_time"]] = [
        "07:00",
        "10:00",
    ]
    outlets.loc[outlets["outlet_id"] == "OUT003", ["brand", "district", "depot", "dock_type", "parking_constraint", "mall_window"]] = [
        "Fresh",
        "District3",
        "Peliyagoda",
        "mall_bay",
        "mall_dock",
        "09:00-11:00",
    ]
    outlets.loc[outlets["outlet_id"] == "OUT003", ["window_open_time", "window_close_time"]] = [
        "07:00",
        "12:00",
    ]

    vehicles = pd.DataFrame(
        [
            {
                "vehicle_id": f"VEH{i:03d}",
                "type": "van" if i % 2 else "truck",
                "temp": "ambient" if i % 2 else "reefer",
                "weight_cap_kg": 1000 + i,
                "volume_cap_m3": 10 + i / 10,
                "fuel_type": "diesel",
                "km_per_l": 8.0,
                "weekly_fuel_quota_l": 200.0,
                "depot": "Peliyagoda" if i % 2 else "Kandy",
            }
            for i in range(1, 61)
        ]
    )
    vehicles.loc[vehicles["vehicle_id"] == "VEH001", ["type", "temp", "depot"]] = ["van", "ambient", "Peliyagoda"]
    vehicles.loc[vehicles["vehicle_id"] == "VEH002", ["type", "temp", "depot"]] = ["truck", "reefer", "Kandy"]

    calendar = []
    for date in pd.date_range("2026-01-05", "2026-01-18", freq="D"):
        iso = date.isocalendar()
        calendar.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "dow": date.weekday(),
                "is_weekend": 1 if date.weekday() in {5, 6} else 0,
                "iso_year": iso.year,
                "iso_week": iso.week,
                "is_payday": 0,
                "festival": "",
                "festival_ramp": 0.0,
                "is_holiday": 0,
                "monsoon": 0,
                "is_operating": 1,
            }
        )

    return {
        "deliveries_train.csv": pd.DataFrame(
            [
                {
                    "delivery_id": "DEL001",
                    "order_date": "2026-01-06",
                    "dispatch_date": "2026-01-06",
                    "dispatch_status": "attempted",
                    "outlet_id": "OUT001",
                    "brand": "Fresh",
                    "district": "District1",
                    "depot": "Peliyagoda",
                    "temp_requirement": "ambient",
                    "order_units": 3,
                    "order_weight_kg": 10.0,
                    "order_volume_m3": 1.0,
                    "route_id": "R001",
                    "seq_in_route": 0,
                    "vehicle_id": "VEH001",
                    "vehicle_type": "van",
                    "vehicle_temp": "ambient",
                    "planned_arrival_time": "08:00",
                    "window_open_time": "07:00",
                    "window_close_time": "10:00",
                }
            ]
        ),
        "task1_test_inputs.csv": pd.DataFrame(
            [
                {
                    "delivery_id": "TEST001",
                    "order_date": "2026-01-08",
                    "dispatch_date": "2026-01-08",
                    "dispatch_status": "attempted",
                    "outlet_id": "OUT003",
                    "brand": "Fresh",
                    "district": "District3",
                    "depot": "Peliyagoda",
                    "temp_requirement": "chilled",
                    "order_units": 2,
                    "order_weight_kg": 5.0,
                    "order_volume_m3": 0.5,
                    "route_id": "R002",
                    "seq_in_route": 0,
                    "vehicle_id": "VEH001",
                    "vehicle_type": "van",
                    "vehicle_temp": "ambient",
                    "planned_arrival_time": "09:00",
                    "window_open_time": "07:00",
                    "window_close_time": "12:00",
                }
            ]
        ),
        "route_legs_train.csv": pd.DataFrame(
            [
                {
                    "leg_id": "LEG001",
                    "date": "2026-01-06",
                    "route_id": "R001",
                    "seq": 0,
                    "depot": "Peliyagoda",
                    "vehicle_id": "VEH001",
                    "vehicle_type": "van",
                    "vehicle_temp": "ambient",
                    "brand": "Fresh",
                    "district": "District1",
                    "from_point": "DEPOT_P",
                    "to_outlet": "OUT001",
                    "distance_km": 10.0,
                    "planned_depart_time": "07:30",
                    "planned_travel_duration_min": 20.0,
                    "planned_arrival_time": "07:50",
                    "actual_depart_time": "07:35",
                    "actual_travel_duration_min": 25.0,
                    "arrival_time": "08:00",
                    "leave_outlet_time": "08:15",
                    "monsoon": 0,
                    "dow": 1,
                }
            ]
        ),
        "route_legs_test.csv": pd.DataFrame(
            [
                {
                    "leg_id": "LEG002",
                    "date": "2026-01-08",
                    "route_id": "R002",
                    "seq": 0,
                    "depot": "Peliyagoda",
                    "vehicle_id": "VEH001",
                    "vehicle_type": "van",
                    "vehicle_temp": "ambient",
                    "brand": "Fresh",
                    "district": "District3",
                    "from_point": "DEPOT_P",
                    "to_outlet": "OUT003",
                    "distance_km": 15.0,
                    "planned_depart_time": "08:30",
                    "planned_travel_duration_min": 30.0,
                    "planned_arrival_time": "09:00",
                    "monsoon": 0,
                    "dow": 3,
                }
            ]
        ),
        "task2a_test_inputs.csv": pd.DataFrame(
            [{"row_id": "ROW001", "depot": "Peliyagoda", "brand": "Fresh", "iso_year": 2026, "iso_week": 2}]
        ),
        "task2b_peak_day_scenarios.csv": pd.DataFrame(
            [
                {
                    "scenario": "S1",
                    "order_ref": "ORD001",
                    "outlet_id": "OUT003",
                    "brand": "Fresh",
                    "district": "District3",
                    "depot": "Peliyagoda",
                    "dock_type": "mall_bay",
                    "parking_constraint": "mall_dock",
                    "mall_window": "09:00-11:00",
                    "window_open_time": "07:00",
                    "window_close_time": "12:00",
                    "temp_requirement": "chilled",
                    "order_units": 4,
                    "order_weight_kg": 7.0,
                    "order_volume_m3": 0.7,
                    "deferred_yesterday": 0,
                    "days_since_last_served": 1,
                }
            ]
        ),
        "task2b_peak_day_fleet.csv": pd.DataFrame(
            [{"scenario": "S1", "vehicle_id": "VEH001", "status": "available"}]
        ),
        "outlets.csv": outlets,
        "vehicles.csv": vehicles,
        "calendar.csv": pd.DataFrame(calendar),
        "district_travel.csv": pd.DataFrame(
            [{"district": "District1", "depot": "Peliyagoda", "road_class": "urban", "free_flow_kmh": 30.0, "depot_to_district_km": 12.0, "depot_to_district_freeflow_min": 25.0, "inter_stop_km": 1.2, "inter_stop_freeflow_min": 5.0}]
        ),
        "service_allowance.csv": pd.DataFrame(
            [{"brand": "Fresh", "dock_type": "rear_dock", "service_allowance_min": 15.0}]
        ),
        "traffic_speed.csv": pd.DataFrame(
            [{"district": "District1", "monsoon": 0, "dow": 1, "speed_index": 90.0}]
        ),
        "road_conditions.csv": pd.DataFrame(
            [{"date": "2026-01-06", "district": "District1", "disruption_index": 100.0}]
        ),
    }


def test_assert_required_files_pass(discovery: dict):
    result = assert_required_files(discovery)
    assert result["status"] == "PASS"


def test_assert_required_files_fail():
    with pytest.raises(SchemaAssertionError):
        assert_required_files({"missing_required": ["deliveries_train.csv"], "duplicate_required": {}})


def test_assert_required_columns_pass(valid_tables: dict, rules: dict):
    result = assert_required_columns(valid_tables, rules)
    assert result["status"] == "PASS"


def test_assert_required_columns_fail(valid_tables: dict, rules: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["deliveries_train.csv"] = broken["deliveries_train.csv"].drop(columns=["delivery_id"])
    with pytest.raises(SchemaAssertionError):
        assert_required_columns(broken, rules)


def test_task1_leakage_guard_pass(rules: dict):
    result = assert_task1_leakage_guard(
        ["order_units", "order_weight_kg", "planned_arrival_time"],
        rules["task1_direct_feature_deny_list"],
    )
    assert result["status"] == "PASS"


def test_task1_leakage_guard_fail(rules: dict):
    with pytest.raises(SchemaAssertionError):
        assert_task1_leakage_guard(
            ["order_units", "arrival_time"],
            rules["task1_direct_feature_deny_list"],
        )


def test_collect_hard_schema_results_pass(valid_tables: dict, rules: dict, discovery: dict):
    results = collect_hard_schema_results(
        tables=valid_tables,
        discovery=discovery,
        rules=rules,
        feature_columns=["order_units", "order_weight_kg"],
    )
    assert results
    assert all(result["status"] == "PASS" for result in results if result["severity"] == "PASS")


def test_collect_hard_schema_results_fail_on_route_key(valid_tables: dict, rules: dict, discovery: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["route_legs_train.csv"] = pd.concat(
        [broken["route_legs_train.csv"], broken["route_legs_train.csv"].assign(leg_id="LEG003")],
        ignore_index=True,
    )
    with pytest.raises(SchemaAssertionError):
        collect_hard_schema_results(
            tables=broken,
            discovery=discovery,
            rules=rules,
            feature_columns=["order_units"],
        )
