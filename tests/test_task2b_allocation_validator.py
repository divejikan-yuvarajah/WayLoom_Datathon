"""Synthetic-only independent Phase 23 allocation-validator tests."""

from copy import deepcopy
import subprocess
import sys

import pandas as pd
import pytest
import yaml

from src.task2b.allocation_validator import (
    AllocationValidationError,
    build_official_checker_candidate,
    validate_frozen_task2b_allocation,
    verify_frozen_integrity,
)
from src.task2b.artifact_integrity import ALLOCATION_COLUMNS, sha256_file


def _config():
    with open("configs/task2b_validation.yaml", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _case():
    orders = pd.DataFrame([
        {"scenario": "S1", "order_ref": "o1", "outlet_id": "shared", "brand": "Fresh",
         "district": "Gampaha", "depot": "Peliyagoda", "dock_type": "rear_dock",
         "parking_constraint": "van_only", "temp_requirement": "chilled",
         "order_weight_kg": 4, "order_volume_m3": 4},
        {"scenario": "S1", "order_ref": "o2", "outlet_id": "shared", "brand": "Fresh",
         "district": "Gampaha", "depot": "Peliyagoda", "dock_type": "street",
         "parking_constraint": "normal", "temp_requirement": "ambient",
         "order_weight_kg": 4, "order_volume_m3": 4},
        {"scenario": "S1", "order_ref": "o3", "outlet_id": "other", "brand": "Style",
         "district": "Colombo", "depot": "Peliyagoda", "dock_type": "street",
         "parking_constraint": "normal", "temp_requirement": "ambient",
         "order_weight_kg": 2, "order_volume_m3": 2},
    ])
    fleet = pd.DataFrame([
        {"scenario": "S1", "vehicle_id": "v1", "status": "available"},
        {"scenario": "S1", "vehicle_id": "v2", "status": "available"},
    ])
    vehicles = pd.DataFrame([
        {"vehicle_id": "v1", "type": "van", "temp": "reefer", "depot": "Peliyagoda",
         "weight_cap_kg": 8, "volume_cap_m3": 8},
        {"vehicle_id": "v2", "type": "truck", "temp": "ambient", "depot": "Peliyagoda",
         "weight_cap_kg": 10, "volume_cap_m3": 10},
    ])
    travel = pd.DataFrame([
        {"depot": "Peliyagoda", "district": "Gampaha",
         "depot_to_district_freeflow_min": 37, "inter_stop_freeflow_min": 9},
        {"depot": "Peliyagoda", "district": "Colombo",
         "depot_to_district_freeflow_min": 24, "inter_stop_freeflow_min": 8},
    ])
    allowance = pd.DataFrame([
        {"brand": "Fresh", "dock_type": "rear_dock", "service_allowance_min": 15},
        {"brand": "Fresh", "dock_type": "street", "service_allowance_min": 16},
        {"brand": "Style", "dock_type": "street", "service_allowance_min": 10},
    ])
    allocation = pd.DataFrame([
        {"scenario": "S1", "order_ref": "o1", "outlet_id": "shared", "decision": "served", "vehicle_id": "v1", "trip_id": "1"},
        {"scenario": "S1", "order_ref": "o2", "outlet_id": "shared", "decision": "served", "vehicle_id": "v1", "trip_id": "1"},
        {"scenario": "S1", "order_ref": "o3", "outlet_id": "other", "decision": "served", "vehicle_id": "v2", "trip_id": "2"},
    ])
    allocation["trip_id"] = allocation["trip_id"].astype(object)
    return allocation, orders, fleet, vehicles, travel, allowance, _config()


def _validate(case):
    return validate_frozen_task2b_allocation(*case)


def test_validator_import_is_solver_neutral():
    code = r'''
import builtins
import sys

blocked = (
    "ortools",
    "src.task2b.solution",
    "src.task2b.optimizer",
    "src.task2b.lexicographic_solver",
    "src.task2b.solver_data",
)
real_import = builtins.__import__

def guarded_import(name, *args, **kwargs):
    if any(name == module or name.startswith(module + ".") for module in blocked):
        raise ImportError(f"blocked solver dependency: {name}")
    return real_import(name, *args, **kwargs)

builtins.__import__ = guarded_import
import src.task2b.allocation_validator  # noqa: F401

loaded = [name for name in sys.modules if any(
    name == module or name.startswith(module + ".") for module in blocked
)]
if loaded:
    raise SystemExit(f"solver modules imported: {loaded}")
'''
    completed = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout


def test_valid_allocation_is_deterministic_read_only_and_allows_repeated_outlet_and_trip2_only():
    case = _case()
    originals = [frame.copy(deep=True) for frame in case[:-1]]
    first = _validate(case)
    second = _validate(case)
    assert first.overall_status == "PASS"
    assert first.summary() == second.summary()
    assert first.checked_trip_count == 2
    for original, current in zip(originals, case[:-1]):
        pd.testing.assert_frame_equal(original, current)


def test_extended_internal_allocation_is_valid_and_diagnostics_do_not_leak():
    case = list(_case())
    expected_candidate = build_official_checker_candidate(case[0], case[1])
    case[0]["diagnostic_score"] = [0.1, 0.2, 0.3]
    case[0]["brand"] = ["wrong", "wrong", "wrong"]
    case[0]["district"] = ["wrong", "wrong", "wrong"]
    case[0]["audit_note"] = ["internal-a", "internal-b", "internal-c"]

    report = _validate(tuple(case))
    candidate = build_official_checker_candidate(case[0], case[1])

    assert report.overall_status == "PASS"
    assert tuple(candidate.columns) == ALLOCATION_COLUMNS
    assert not {"diagnostic_score", "brand", "district", "audit_note"}.intersection(candidate.columns)
    pd.testing.assert_frame_equal(candidate, expected_candidate)


def test_same_trip_id_may_be_reused_by_different_vehicles():
    case = list(_case())
    case[0].loc[case[0].vehicle_id.eq("v2"), "trip_id"] = "1"
    assert _validate(tuple(case)).overall_status == "PASS"


def test_mixed_dock_types_are_valid_and_only_change_handling_allowance():
    report = _validate(_case())
    trip = report.trip_time_audit.loc[
        report.trip_time_audit.vehicle_id.eq("v1")
        & report.trip_time_audit.trip_id.eq(1)
    ].iloc[0]
    assert report.overall_status == "PASS"
    assert trip.order_count == 2
    assert trip.handling_minutes == "31"


@pytest.mark.parametrize(("mutation", "rule"), [
    (lambda a, o, f, v: a.__setitem__("scenario", ["S2", "S1", "S1"]), "scenario_values"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "outlet_id"), "wrong"), "scenario_values"),
    (lambda a, o, f, v: a.loc.__setitem__((1, "order_ref"), "o1"), "order_ref_coverage"),
    (lambda a, o, f, v: a.drop(index=2, inplace=True), "order_ref_coverage"),
    (lambda a, o, f, v: a.loc.__setitem__((2, "order_ref"), "extra"), "order_ref_coverage"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "order_ref"), ""), "order_ref_coverage"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "decision"), "Served"), "decision_domain"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "decision"), "pending"), "decision_domain"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "decision"), ""), "decision_domain"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "vehicle_id"), ""), "served_fields"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "trip_id"), ""), "served_fields"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "vehicle_id"), "unknown"), "served_fields"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "trip_id"), 0), "trip_id_domain"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "trip_id"), 3), "trip_id_domain"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "trip_id"), -1), "trip_id_domain"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "trip_id"), 1.5), "trip_id_domain"),
    (lambda a, o, f, v: a.loc.__setitem__((0, "trip_id"), "trip1"), "trip_id_domain"),
])
def test_identity_decision_and_served_field_mutations_fail(mutation, rule):
    case = list(_case())
    mutation(case[0], case[1], case[2], case[3])
    assert _validate(tuple(case)).rules[rule].status == "FAIL"


@pytest.mark.parametrize(("vehicle", "trip"), [("v1", ""), ("", 1), ("N/A", ""), ("", 0), ("-", "-")])
def test_deferred_assignment_must_be_truly_blank(vehicle, trip):
    case = list(_case())
    case[0].loc[0, ["decision", "vehicle_id", "trip_id"]] = ["deferred", vehicle, trip]
    report = _validate(tuple(case))
    assert report.rules["deferred_fields"].status == "FAIL"


def test_deferred_blank_passes_and_candidate_serializes_empty_fields():
    case = list(_case())
    case[0].loc[0, ["decision", "vehicle_id", "trip_id"]] = ["deferred", "", ""]
    report = _validate(tuple(case))
    assert report.overall_status == "PASS"
    candidate = build_official_checker_candidate(case[0], case[1])
    row = candidate.set_index("order_ref").loc["o1"]
    assert row.vehicle_id == "" and row.trip_id == ""
    assert tuple(candidate.columns) == ("scenario", "order_ref", "outlet_id", "decision", "vehicle_id", "trip_id")


def test_missing_schema_and_blank_scenario_fail_without_mutation_or_crash():
    case = list(_case())
    case[0] = case[0].drop(columns=["scenario"])
    report = _validate(tuple(case))
    assert report.rules["allocation_schema"].status == "FAIL"
    assert report.rules["scenario_values"].status == "FAIL"
    with pytest.raises(AllocationValidationError, match="missing required official columns"):
        build_official_checker_candidate(case[0], case[1])


def test_duplicate_served_order_fails_coverage_and_whole_order_audits():
    case = list(_case())
    duplicate = case[0].iloc[[0]].copy()
    duplicate.loc[:, "vehicle_id"] = "v2"
    duplicate.loc[:, "trip_id"] = "2"
    case[0] = pd.concat([case[0], duplicate], ignore_index=True)
    report = _validate(tuple(case))
    assert report.rules["order_ref_coverage"].status == "FAIL"
    assert report.rules["whole_order"].status == "FAIL"


def test_multiple_independent_violations_are_all_reported():
    case = list(_case())
    case[0].loc[0, "scenario"] = ""
    case[0].loc[1, "decision"] = "pending"
    case[3].loc[case[3].vehicle_id.eq("v1"), "temp"] = "ambient"
    report = _validate(tuple(case))
    assert report.overall_status == "FAIL"
    assert report.rules["scenario_values"].status == "FAIL"
    assert report.rules["decision_domain"].status == "FAIL"
    assert report.rules["refrigeration"].status == "FAIL"


@pytest.mark.parametrize(("mutation", "rule"), [
    (lambda a, o, f, v: a.loc.__setitem__((2, ["vehicle_id", "trip_id"]), ["v1", 1]), "same_brand_district"),
    (lambda a, o, f, v: o.loc.__setitem__((1, "district"), "Colombo"), "same_brand_district"),
    (lambda a, o, f, v: v.loc.__setitem__((v.vehicle_id.eq("v1"), "temp"), "ambient"), "refrigeration"),
    (lambda a, o, f, v: v.loc.__setitem__((v.vehicle_id.eq("v1"), "type"), "truck"), "van_only"),
    (lambda a, o, f, v: v.loc.__setitem__((v.vehicle_id.eq("v1"), "depot"), "Other"), "home_depot_availability"),
    (lambda a, o, f, v: f.loc.__setitem__((f.vehicle_id.eq("v1"), "status"), "in_workshop"), "home_depot_availability"),
    (lambda a, o, f, v: v.loc.__setitem__((v.vehicle_id.eq("v1"), "weight_cap_kg"), 7), "capacity"),
    (lambda a, o, f, v: v.loc.__setitem__((v.vehicle_id.eq("v1"), "volume_cap_m3"), 7), "capacity"),
])
def test_each_official_hard_rule_mutation_fails(mutation, rule):
    case = list(_case())
    mutation(case[0], case[1], case[2], case[3])
    assert _validate(tuple(case)).rules[rule].status == "FAIL"


def _budget_case(brands, minutes):
    orders = pd.DataFrame([
        {"scenario": "S1", "order_ref": f"o{i}", "outlet_id": f"x{i}", "brand": brand,
         "district": f"D{i}", "depot": "Peliyagoda", "dock_type": "dock",
         "parking_constraint": "normal", "temp_requirement": "ambient",
         "order_weight_kg": 1, "order_volume_m3": 1}
        for i, brand in enumerate(brands)
    ])
    fleet = pd.DataFrame([{"scenario": "S1", "vehicle_id": "v", "status": "available"}])
    vehicles = pd.DataFrame([{"vehicle_id": "v", "type": "truck", "temp": "ambient",
                              "depot": "Peliyagoda", "weight_cap_kg": 10, "volume_cap_m3": 10}])
    travel = pd.DataFrame([{"depot": "Peliyagoda", "district": f"D{i}",
                            "depot_to_district_freeflow_min": 0, "inter_stop_freeflow_min": 0}
                           for i in range(len(brands))])
    allowance_values = {}
    for brand, minute in zip(brands, minutes):
        if brand in allowance_values and allowance_values[brand] != minute:
            raise ValueError("Synthetic orders of one brand require one allowance value.")
        allowance_values[brand] = minute
    allowance = pd.DataFrame([{"brand": brand, "dock_type": "dock", "service_allowance_min": minute}
                              for brand, minute in allowance_values.items()])
    allocation = pd.DataFrame([{"scenario": "S1", "order_ref": f"o{i}", "outlet_id": f"x{i}",
                                "decision": "served", "vehicle_id": "v", "trip_id": i + 1}
                               for i in range(len(brands))])
    return allocation, orders, fleet, vehicles, travel, allowance, _config()


@pytest.mark.parametrize(("case", "expected"), [
    (_budget_case(["Fresh", "Fresh"], [135, 135]), "PASS"),
    (_budget_case(["Fresh", "Fresh"], [135.5, 135.5]), "FAIL"),
    (_budget_case(["Style", "Tech"], [240, 240]), "PASS"),
    (_budget_case(["Style", "Tech"], [240, 241]), "FAIL"),
])
def test_exact_fresh_and_style_tech_budget_boundaries(case, expected):
    assert _validate(case).rules["trip_count_time_budget"].status == expected


def test_official_101_and_112_examples_and_no_return():
    docks = ["rear_dock", "rear_dock", "street"] + ["street"] * 4
    districts = ["Gampaha"] * 3 + ["Colombo"] * 4
    orders = pd.DataFrame([
        {"scenario": "S1", "order_ref": f"o{i}", "outlet_id": "duplicate-outlet",
         "brand": "Fresh", "district": district, "depot": "Peliyagoda", "dock_type": dock,
         "parking_constraint": "normal", "temp_requirement": "ambient",
         "order_weight_kg": 1, "order_volume_m3": 1}
        for i, (district, dock) in enumerate(zip(districts, docks))
    ])
    fleet = pd.DataFrame([{"scenario": "S1", "vehicle_id": "v", "status": "available"}])
    vehicles = pd.DataFrame([{"vehicle_id": "v", "type": "truck", "temp": "ambient",
                              "depot": "Peliyagoda", "weight_cap_kg": 20, "volume_cap_m3": 20}])
    travel = pd.DataFrame([
        {"depot": "Peliyagoda", "district": "Gampaha", "depot_to_district_freeflow_min": 37, "inter_stop_freeflow_min": 9},
        {"depot": "Peliyagoda", "district": "Colombo", "depot_to_district_freeflow_min": 24, "inter_stop_freeflow_min": 8},
    ])
    allowance = pd.DataFrame([
        {"brand": "Fresh", "dock_type": "rear_dock", "service_allowance_min": 15},
        {"brand": "Fresh", "dock_type": "street", "service_allowance_min": 16},
    ])
    allocation = pd.DataFrame([
        {"scenario": "S1", "order_ref": f"o{i}", "outlet_id": "duplicate-outlet",
         "decision": "served", "vehicle_id": "v", "trip_id": 1 if i < 3 else 2}
        for i in range(7)
    ])
    report = _validate((allocation, orders, fleet, vehicles, travel, allowance, _config()))
    assert report.overall_status == "PASS"
    assert sorted(report.trip_time_audit.trip_minutes.tolist()) == ["101", "112"]
    assert report.trip_time_audit.return_minutes_added.eq("0.0").all()


@pytest.mark.parametrize(("docks", "expected_outbound", "expected_inter", "expected_handling", "expected_total"), [
    (["rear_dock"], "37", "0", "15", "52"),
    (["rear_dock", "street"], "37", "9", "31", "77"),
    (["rear_dock", "rear_dock", "street"], "37", "18", "46", "101"),
])
def test_exact_time_components_for_one_two_and_three_orders(
    docks, expected_outbound, expected_inter, expected_handling, expected_total
):
    orders = pd.DataFrame([
        {"scenario": "S1", "order_ref": f"o{i}", "outlet_id": "same-outlet",
         "brand": "Fresh", "district": "Gampaha", "depot": "Peliyagoda",
         "dock_type": dock, "parking_constraint": "normal", "temp_requirement": "ambient",
         "order_weight_kg": 1, "order_volume_m3": 1}
        for i, dock in enumerate(docks)
    ])
    allocation = pd.DataFrame([
        {"scenario": "S1", "order_ref": f"o{i}", "outlet_id": "same-outlet",
         "decision": "served", "vehicle_id": "v", "trip_id": 1}
        for i in range(len(docks))
    ])
    fleet = pd.DataFrame([{"scenario": "S1", "vehicle_id": "v", "status": "available"}])
    vehicles = pd.DataFrame([{"vehicle_id": "v", "type": "truck", "temp": "ambient",
                              "depot": "Peliyagoda", "weight_cap_kg": 10, "volume_cap_m3": 10}])
    travel = pd.DataFrame([{"depot": "Peliyagoda", "district": "Gampaha",
                            "depot_to_district_freeflow_min": 37, "inter_stop_freeflow_min": 9}])
    allowance = pd.DataFrame([
        {"brand": "Fresh", "dock_type": "rear_dock", "service_allowance_min": 15},
        {"brand": "Fresh", "dock_type": "street", "service_allowance_min": 16},
    ])
    report = validate_frozen_task2b_allocation(
        allocation, orders, fleet, vehicles, travel, allowance, _config()
    )
    row = report.trip_time_audit.iloc[0]
    assert report.overall_status == "PASS"
    assert (row.outbound_minutes, row.inter_stop_minutes, row.handling_minutes, row.trip_minutes) == (
        expected_outbound, expected_inter, expected_handling, expected_total
    )


def test_frozen_trip_summary_minutes_must_match_independent_recomputation():
    case = _case()
    initial = _validate(case)
    stored = initial.trip_time_audit[["vehicle_id", "trip_id", "trip_minutes"]].copy()
    matched = validate_frozen_task2b_allocation(*case, frozen_trip_summary=stored)
    assert matched.rules["trip_time_exact"].status == "PASS"
    stored.loc[0, "trip_minutes"] = "999"
    mismatched = validate_frozen_task2b_allocation(*case, frozen_trip_summary=stored)
    assert mismatched.rules["trip_time_exact"].status == "FAIL"


def test_frozen_hash_integrity_fails_closed(tmp_path):
    allocation = tmp_path / "allocation.csv"
    summary = tmp_path / "trips.csv"
    manifest = tmp_path / "freeze.json"
    allocation.write_text("a\n", encoding="utf-8")
    summary.write_text("b\n", encoding="utf-8")
    manifest.write_text(pd.Series({"phase": 22, "state": "FROZEN",
                                   "allocation_sha256": sha256_file(allocation),
                                   "trip_summary_sha256": sha256_file(summary)}).to_json(), encoding="utf-8")
    assert verify_frozen_integrity(allocation, manifest, summary)["status"] == "PASS"
    allocation.write_text("changed\n", encoding="utf-8")
    with pytest.raises(AllocationValidationError, match="SHA256"):
        verify_frozen_integrity(allocation, manifest, summary)
