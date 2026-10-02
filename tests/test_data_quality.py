from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.common.data_quality import (
    BLOCKER,
    EXPECTED,
    NOT_APPLICABLE,
    PASS,
    WARNING,
    audit_calendar_coverage,
    audit_categories,
    audit_complete_duplicates,
    audit_dates,
    audit_missing_values,
    audit_numeric_ranges,
    audit_order_ids,
    audit_outliers,
    audit_primary_keys,
    audit_road_coverage,
    audit_route_leg_keys,
    audit_semantic_types,
    audit_times,
    audit_train_test_compatibility,
    audit_traffic_coverage,
    audit_outlet_references,
    audit_vehicle_references,
    build_audit_summary,
    load_rules,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rules() -> dict:
    return load_rules(ROOT / "configs" / "data_quality_rules.yaml")


@pytest.fixture
def valid_tables() -> dict[str, pd.DataFrame]:
    outlets = []
    for idx in range(1, 121):
        outlet_id = f"OUT{idx:03d}"
        brand = ["Fresh", "Style", "Tech"][(idx - 1) % 3]
        depot = "Peliyagoda" if idx % 2 else "Kandy"
        district = f"District{((idx - 1) % 12) + 1}"
        dock_type = "rear_dock" if idx % 3 == 1 else ("street" if idx % 3 == 2 else "mall_bay")
        parking = "normal" if dock_type == "rear_dock" else ("van_only" if dock_type == "street" else "mall_dock")
        mall_window = "" if dock_type != "mall_bay" else "09:00-11:00"
        outlets.append(
            {
                "outlet_id": outlet_id,
                "brand": brand,
                "district": district,
                "depot": depot,
                "dock_type": dock_type,
                "parking_constraint": parking,
                "mall_window": mall_window,
                "window_open_time": "07:00",
                "window_close_time": "18:00",
            }
        )
    outlets_df = pd.DataFrame(outlets)
    outlets_df.loc[outlets_df["outlet_id"] == "OUT001", ["brand", "district", "depot", "dock_type", "parking_constraint", "mall_window"]] = [
        "Fresh",
        "District1",
        "Peliyagoda",
        "rear_dock",
        "normal",
        "",
    ]
    outlets_df.loc[outlets_df["outlet_id"] == "OUT001", ["window_open_time", "window_close_time"]] = ["07:00", "10:00"]
    outlets_df.loc[outlets_df["outlet_id"] == "OUT002", ["brand", "district", "depot", "dock_type", "parking_constraint", "mall_window"]] = [
        "Tech",
        "District2",
        "Kandy",
        "street",
        "van_only",
        "",
    ]
    outlets_df.loc[outlets_df["outlet_id"] == "OUT002", ["window_open_time", "window_close_time"]] = ["08:00", "11:00"]
    outlets_df.loc[outlets_df["outlet_id"] == "OUT003", ["brand", "district", "depot", "dock_type", "parking_constraint", "mall_window"]] = [
        "Fresh",
        "District3",
        "Peliyagoda",
        "mall_bay",
        "mall_dock",
        "09:00-11:00",
    ]
    outlets_df.loc[outlets_df["outlet_id"] == "OUT003", ["window_open_time", "window_close_time"]] = ["07:00", "12:00"]

    vehicles = []
    for idx in range(1, 61):
        vehicle_id = f"VEH{idx:03d}"
        vehicle_type = "van" if idx % 2 else "truck"
        vehicle_temp = "ambient" if idx % 2 else "reefer"
        depot = "Peliyagoda" if idx % 2 else "Kandy"
        vehicles.append(
            {
                "vehicle_id": vehicle_id,
                "type": vehicle_type,
                "temp": vehicle_temp,
                "weight_cap_kg": 1000 + idx,
                "volume_cap_m3": 10 + idx / 10,
                "fuel_type": "diesel",
                "km_per_l": 8.0,
                "weekly_fuel_quota_l": 200.0,
                "depot": depot,
            }
        )
    vehicles_df = pd.DataFrame(vehicles)
    vehicles_df.loc[vehicles_df["vehicle_id"] == "VEH001", ["type", "temp", "depot"]] = ["van", "ambient", "Peliyagoda"]
    vehicles_df.loc[vehicles_df["vehicle_id"] == "VEH002", ["type", "temp", "depot"]] = ["truck", "reefer", "Kandy"]

    calendar_rows = []
    for date in pd.date_range("2026-01-05", "2026-01-18", freq="D"):
        weekday = date.weekday()
        iso = date.isocalendar()
        calendar_rows.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "dow": weekday,
                "is_weekend": 1 if weekday in {5, 6} else 0,
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
                    "order_weight_kg": 10.5,
                    "order_volume_m3": 1.0,
                    "route_id": "R001",
                    "seq_in_route": 0,
                    "vehicle_id": "VEH001",
                    "vehicle_type": "van",
                    "vehicle_temp": "ambient",
                    "planned_arrival_time": "08:00",
                    "window_open_time": "07:00",
                    "window_close_time": "10:00",
                },
                {
                    "delivery_id": "DEL002",
                    "order_date": "2026-01-07",
                    "dispatch_date": "",
                    "dispatch_status": "not_run",
                    "outlet_id": "OUT002",
                    "brand": "Tech",
                    "district": "District2",
                    "depot": "Kandy",
                    "temp_requirement": "ambient",
                    "order_units": 0,
                    "order_weight_kg": 0.0,
                    "order_volume_m3": 0.0,
                    "route_id": "",
                    "seq_in_route": pd.NA,
                    "vehicle_id": "",
                    "vehicle_type": "",
                    "vehicle_temp": "",
                    "planned_arrival_time": "",
                    "window_open_time": "08:00",
                    "window_close_time": "11:00",
                },
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
                },
                {
                    "scenario": "S1",
                    "order_ref": "ORD002",
                    "outlet_id": "OUT003",
                    "brand": "Fresh",
                    "district": "District3",
                    "depot": "Peliyagoda",
                    "dock_type": "mall_bay",
                    "parking_constraint": "mall_dock",
                    "mall_window": "09:00-11:00",
                    "window_open_time": "07:00",
                    "window_close_time": "12:00",
                    "temp_requirement": "ambient",
                    "order_units": 6,
                    "order_weight_kg": 9.0,
                    "order_volume_m3": 0.9,
                    "deferred_yesterday": 0,
                    "days_since_last_served": 2,
                },
            ]
        ),
        "task2b_peak_day_fleet.csv": pd.DataFrame(
            [
                {"scenario": "S1", "vehicle_id": "VEH001", "status": "available"},
                {"scenario": "S1", "vehicle_id": "VEH002", "status": "in_workshop"},
            ]
        ),
        "outlets.csv": outlets_df,
        "vehicles.csv": vehicles_df,
        "calendar.csv": pd.DataFrame(calendar_rows),
        "district_travel.csv": pd.DataFrame(
            [
                {
                    "district": "District1",
                    "depot": "Peliyagoda",
                    "road_class": "urban",
                    "free_flow_kmh": 30.0,
                    "depot_to_district_km": 12.0,
                    "depot_to_district_freeflow_min": 25.0,
                    "inter_stop_km": 1.2,
                    "inter_stop_freeflow_min": 5.0,
                },
                {
                    "district": "District3",
                    "depot": "Peliyagoda",
                    "road_class": "urban",
                    "free_flow_kmh": 28.0,
                    "depot_to_district_km": 18.0,
                    "depot_to_district_freeflow_min": 35.0,
                    "inter_stop_km": 1.5,
                    "inter_stop_freeflow_min": 6.0,
                },
            ]
        ),
        "service_allowance.csv": pd.DataFrame(
            [
                {"brand": "Fresh", "dock_type": "rear_dock", "service_allowance_min": 15.0},
                {"brand": "Fresh", "dock_type": "mall_bay", "service_allowance_min": 20.0},
                {"brand": "Tech", "dock_type": "street", "service_allowance_min": 12.0},
            ]
        ),
        "traffic_speed.csv": pd.DataFrame(
            [
                {"district": "District1", "monsoon": 0, "dow": 1, "speed_index": 90.0},
                {"district": "District3", "monsoon": 0, "dow": 3, "speed_index": 92.0},
            ]
        ),
        "road_conditions.csv": pd.DataFrame(
            [
                {"date": "2026-01-06", "district": "District1", "disruption_index": 100.0},
                {"date": "2026-01-08", "district": "District3", "disruption_index": 95.0},
            ]
        ),
    }


def _statuses(results: list[dict], prefix: str) -> list[str]:
    return [r["status"] for r in results if r["rule_id"].startswith(prefix)]


def test_dt036_missing_values_expected_and_blocker(valid_tables: dict, rules: dict):
    results = audit_missing_values(valid_tables, rules)
    assert EXPECTED in _statuses(results, "DT-036.EXPECTED_NOT_RUN_BLANK.dispatch_date")
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["deliveries_train.csv"].loc[0, "delivery_id"] = ""
    broken_results = audit_missing_values(broken, rules)
    assert any(r["rule_id"] == "DT-036.REQUIRED_IDENTIFIER.delivery_id" and r["status"] == BLOCKER for r in broken_results)


def test_dt037_complete_duplicates(valid_tables: dict):
    duped = {name: df.copy() for name, df in valid_tables.items()}
    duped["deliveries_train.csv"] = pd.concat(
        [duped["deliveries_train.csv"], duped["deliveries_train.csv"].iloc[[0]]],
        ignore_index=True,
    )
    results = audit_complete_duplicates(duped)
    assert any(r["table"] == "deliveries_train.csv" and r["status"] == BLOCKER for r in results)


def test_dt038_primary_key_duplicates(valid_tables: dict, rules: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["service_allowance.csv"] = pd.concat(
        [broken["service_allowance.csv"], broken["service_allowance.csv"].iloc[[0]]],
        ignore_index=True,
    )
    results = audit_primary_keys(broken, rules)
    assert any(r["rule_id"] == "DT-038.KEY_UNIQUENESS.brand+dock_type" and r["status"] == BLOCKER for r in results)


def test_dt039_semantic_type_validation(valid_tables: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["deliveries_train.csv"]["order_units"] = broken["deliveries_train.csv"]["order_units"].astype(object)
    broken["deliveries_train.csv"].loc[0, "order_units"] = "three"
    results = audit_semantic_types(broken)
    assert any(r["rule_id"] == "DT-039.SEMANTIC_TYPE.order_units" and r["status"] == BLOCKER for r in results)


def test_dt040_date_validation(valid_tables: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["deliveries_train.csv"].loc[0, "dispatch_date"] = "2026-13-40"
    results = audit_dates(broken)
    assert any(r["rule_id"] == "DT-040.DATE_PARSE.dispatch_date" and r["status"] == BLOCKER for r in results)


def test_dt041_time_validation(valid_tables: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["route_legs_train.csv"].loc[0, "arrival_time"] = "7:30"
    results = audit_times(broken)
    assert any(r["rule_id"] == "DT-041.CLOCK_TIME.arrival_time" and r["status"] == BLOCKER for r in results)


def test_dt042_category_validation(valid_tables: dict, rules: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["deliveries_train.csv"].loc[0, "brand"] = "fresh"
    results = audit_categories(broken, rules)
    assert any(r["rule_id"] == "DT-042.ENUM.brand" and r["status"] == BLOCKER for r in results)


def test_dt043_numeric_ranges(valid_tables: dict, rules: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["deliveries_train.csv"].loc[0, "order_weight_kg"] = -1
    results = audit_numeric_ranges(broken, rules)
    assert any(r["rule_id"] == "DT-043.NONNEGATIVE.order_weight_kg" and r["status"] == BLOCKER for r in results)
    assert any(r["rule_id"] == "DT-043.ZERO_WARNING.order_units" and r["status"] == WARNING for r in audit_numeric_ranges(valid_tables, rules))


def test_dt044_outliers_warning(valid_tables: dict, rules: dict):
    outlier_tables = {name: df.copy() for name, df in valid_tables.items()}
    outlier_tables["deliveries_train.csv"] = pd.DataFrame(
        [
            {**valid_tables["deliveries_train.csv"].iloc[0].to_dict(), "order_weight_kg": 1.0, "delivery_id": "A1"},
            {**valid_tables["deliveries_train.csv"].iloc[0].to_dict(), "order_weight_kg": 1.0, "delivery_id": "A2"},
            {**valid_tables["deliveries_train.csv"].iloc[0].to_dict(), "order_weight_kg": 1.0, "delivery_id": "A3"},
            {**valid_tables["deliveries_train.csv"].iloc[0].to_dict(), "order_weight_kg": 1000.0, "delivery_id": "A4"},
        ]
    )
    results = audit_outliers(outlier_tables, rules)
    assert any(r["rule_id"] == "DT-044.OUTLIER.order_weight_kg" and r["status"] == WARNING for r in results)


def test_dt045_order_id_integrity(valid_tables: dict):
    results = audit_order_ids(valid_tables)
    assert any(r["rule_id"] == "DT-045.ORDER_REF_UNIQUE_WITHIN_SCENARIO" and r["status"] == PASS for r in results)

    overlap = {name: df.copy() for name, df in valid_tables.items()}
    overlap["task1_test_inputs.csv"].loc[0, "delivery_id"] = "DEL001"
    overlap_results = audit_order_ids(overlap)
    assert any(r["rule_id"] == "DT-045.DELIVERY_ID_TRAIN_TEST_OVERLAP" and r["status"] == WARNING for r in overlap_results)


def test_dt046_route_leg_key_integrity(valid_tables: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["route_legs_train.csv"] = pd.concat(
        [broken["route_legs_train.csv"], broken["route_legs_train.csv"].assign(leg_id="LEG002")],
        ignore_index=True,
    )
    results = audit_route_leg_keys(broken)
    assert any(r["rule_id"] == "DT-046.ROUTE_KEY_UNIQUE" and r["status"] == BLOCKER for r in results)


def test_dt047_outlet_reference_integrity(valid_tables: dict, rules: dict):
    results = audit_outlet_references(valid_tables, rules)
    assert any(r["rule_id"] == "DT-047.OUTLET_COUNT" and r["status"] == PASS for r in results)
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["task2b_peak_day_scenarios.csv"].loc[0, "outlet_id"] = "OUT999"
    broken_results = audit_outlet_references(broken, rules)
    assert any(r["rule_id"] == "DT-047.OUTLET_REFERENCE_RESOLVE" and r["status"] == BLOCKER for r in broken_results)


def test_dt048_vehicle_reference_integrity(valid_tables: dict, rules: dict):
    results = audit_vehicle_references(valid_tables, rules)
    assert any(r["rule_id"] == "DT-048.VEHICLE_COUNT" and r["status"] == PASS for r in results)
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["route_legs_train.csv"].loc[0, "vehicle_id"] = "VEH999"
    broken_results = audit_vehicle_references(broken, rules)
    assert any(r["rule_id"] == "DT-048.VEHICLE_REFERENCE_RESOLVE" and r["status"] == BLOCKER for r in broken_results)


def test_dt049_calendar_coverage(valid_tables: dict, rules: dict):
    results = audit_calendar_coverage(valid_tables, rules)
    assert any(r["rule_id"] == "DT-049.CALENDAR_DATE_COVERAGE" and r["status"] == PASS for r in results)
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["calendar.csv"] = broken["calendar.csv"][broken["calendar.csv"]["date"] != "2026-01-08"]
    broken_results = audit_calendar_coverage(broken, rules)
    assert any(r["rule_id"] == "DT-049.CALENDAR_DATE_COVERAGE" and r["status"] == BLOCKER for r in broken_results)


def test_dt049_calendar_weekend_internal_consistency(valid_tables: dict, rules: dict):
    warning_case = {name: df.copy() for name, df in valid_tables.items()}
    warning_case["calendar.csv"]["is_weekend"] = 0
    warning_results = audit_calendar_coverage(warning_case, rules)
    assert any(r["rule_id"] == "DT-049.CALENDAR_WEEKEND" and r["status"] == PASS for r in warning_results)
    assert any(r["rule_id"] == "DT-049.CALENDAR_WEEKEND_STANDARD" and r["status"] == WARNING for r in warning_results)

    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["calendar.csv"].loc[broken["calendar.csv"]["dow"] == 0, "is_weekend"] = [0, 1]
    broken_results = audit_calendar_coverage(broken, rules)
    assert any(r["rule_id"] == "DT-049.CALENDAR_WEEKEND" and r["status"] == BLOCKER for r in broken_results)


def test_dt050_road_coverage(valid_tables: dict, rules: dict):
    results = audit_road_coverage(valid_tables, rules)
    assert any(r["rule_id"] == "DT-050.ROAD_COVERAGE.COVERAGE" and r["status"] == PASS for r in results)


def test_dt051_traffic_coverage_warning(valid_tables: dict, rules: dict):
    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["traffic_speed.csv"] = pd.DataFrame([{"speed_index": 100.0}])
    results = audit_traffic_coverage(broken, rules)
    assert any(r["rule_id"] == "DT-051.TRAFFIC_COVERAGE.JOIN_UNRESOLVED" and r["status"] == WARNING for r in results)


def test_dt052_train_test_compatibility(valid_tables: dict, rules: dict):
    warning_tables = {name: df.copy() for name, df in valid_tables.items()}
    warning_tables["task1_test_inputs.csv"].loc[0, "brand"] = "Style"
    results = audit_train_test_compatibility(warning_tables, rules)
    assert any(r["rule_id"] == "DT-052.CATEGORY_COMPAT.brand" and r["status"] == WARNING for r in results)

    broken = {name: df.copy() for name, df in valid_tables.items()}
    broken["task1_test_inputs.csv"].loc[0, "brand"] = "InvalidBrand"
    broken_results = audit_train_test_compatibility(broken, rules)
    assert any(r["rule_id"] == "DT-052.CATEGORY_COMPAT.brand" and r["status"] == BLOCKER for r in broken_results)


def test_build_audit_summary(valid_tables: dict, rules: dict):
    sections = {
        "missingness": audit_missing_values(valid_tables, rules),
        "duplicate_rows": audit_complete_duplicates(valid_tables),
    }
    summary = build_audit_summary(sections)
    assert summary["status"] == "PASS"
    assert summary["blocker_count"] == 0
