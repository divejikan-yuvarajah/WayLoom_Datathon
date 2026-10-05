"""Synthetic Phase 22 hard-rule model tests."""
from ortools.sat.python import cp_model
import pandas as pd

from src.task2b.compatibility import build_compatibility_matrix, order_compatibility_summary
from src.task2b.optimizer import build_optimizer_model
from src.task2b.priority import build_order_priority_metadata
from src.task2b.scenario import build_s1_scenario
from src.task2b.solver_data import build_solver_data
from tests.test_task2b_solver_data import _case
from tests.test_task2b_trip_time import _refs
from tests.test_task2b_scenario import _frames


def test_local_cp_sat_smoke_and_assignment_domain():
    model = cp_model.CpModel()
    x = model.NewBoolVar("x")
    model.Maximize(x)
    solver = cp_model.CpSolver()
    assert solver.Solve(model) == cp_model.OPTIMAL and solver.Value(x) == 1
    bundle = build_optimizer_model(build_solver_data(*_case()))
    assert set((o, v) for o, v, _ in bundle.x) == set(bundle.data.compatible_pairs)
    assert {t for _, _, t in bundle.x} == {1, 2}
    assert set(bundle.serve) == set(bundle.defer) == set(bundle.data.order_ids)


def test_whole_order_and_group_constraints():
    bundle = build_optimizer_model(build_solver_data(*_case()))
    bundle.model.Add(bundle.serve["o1"] == 1)
    bundle.model.Add(bundle.serve["o2"] == 1)
    solver = cp_model.CpSolver()
    assert solver.Solve(bundle.model) == cp_model.OPTIMAL
    assert sum(solver.Value(var) for (o, _, _), var in bundle.x.items() if o == "o1") == 1
    assert sum(solver.Value(var) for (o, _, _), var in bundle.x.items() if o == "o2") == 1
    assert solver.Value(bundle.use_trip["v1", 1]) == 1
    assert solver.Value(bundle.use_trip["v1", 2]) == 1
    assert solver.Value(bundle.trip_minutes["v1", 1]) >= 0


def _custom_bundle(order_specs, travel_rows, allowances, *, weight_cap=100, volume_cap=100):
    _, _, _, _, _, scenario_config = __import__("tests.test_task2b_scenario", fromlist=["_frames"])._frames()
    orders = pd.DataFrame([{
        "scenario": "S1", "order_ref": f"o{i}", "outlet_id": f"x{i // 2}", "brand": brand,
        "district": district, "depot": "Peliyagoda", "dock_type": dock,
        "parking_constraint": "normal", "temp_requirement": "ambient",
        "order_weight_kg": weight, "order_volume_m3": volume,
        "deferred_yesterday": 0, "days_since_last_served": 1,
    } for i, (brand, district, dock, weight, volume) in enumerate(order_specs)])
    fleet = pd.DataFrame([{"scenario": "S1", "vehicle_id": "v", "status": "available"}])
    vehicles = pd.DataFrame([{"vehicle_id": "v", "type": "truck", "temp": "ambient", "depot": "Peliyagoda",
                              "weight_cap_kg": weight_cap, "volume_cap_m3": volume_cap}])
    scenario = build_s1_scenario(orders, fleet, vehicles, pd.DataFrame(travel_rows), pd.DataFrame(allowances), scenario_config)
    matrix = build_compatibility_matrix(scenario["orders_s1"], scenario["usable_fleet_s1"])
    metadata = build_order_priority_metadata(scenario["orders_s1"], order_compatibility_summary(matrix), matrix)
    _, _, _, config, priority = _case()
    return build_optimizer_model(build_solver_data(scenario, matrix, metadata, config, priority))


def _force_all(bundle, *, one_trip=False):
    for var in bundle.serve.values():
        bundle.model.Add(var == 1)
    if one_trip:
        bundle.model.Add(bundle.use_trip["v", 2] == 0)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    return solver, solver.Solve(bundle.model)


def test_official_trip_time_examples_and_combined_fresh_budget():
    travel, allowance = _refs()
    specs = ([('Fresh', 'Gampaha', dock, 1, 1) for dock in ('rear_dock', 'rear_dock', 'street')]
             + [('Fresh', 'Colombo', 'street', 1, 1)] * 4)
    bundle = _custom_bundle(specs, travel.to_dict('records'), allowance.to_dict('records'))
    solver, status = _force_all(bundle)
    assert status == cp_model.OPTIMAL
    assert sorted(solver.Value(var) for var in bundle.trip_minutes.values()) == [101, 112]
    assert sum(solver.Value(var) for var in bundle.trip_minutes.values()) == 213


def test_fresh_exact_budget_boundary_and_separate_style_tech_budget():
    travel = [{"depot": "Peliyagoda", "district": district,
               "depot_to_district_freeflow_min": 0, "inter_stop_freeflow_min": 0}
              for district in ("A", "B", "C")]
    allowance = [{"brand": brand, "dock_type": "dock", "service_allowance_min": minutes}
                 for brand, minutes in (("Fresh", 270), ("Style", 240), ("Tech", 240))]
    one = [('Fresh', 'A', 'dock', 1, 1)]
    assert _force_all(_custom_bundle(one, travel, allowance))[1] == cp_model.OPTIMAL
    over = [dict(row) for row in allowance]
    over[0]["service_allowance_min"] = 271
    assert _force_all(_custom_bundle(one, travel, over))[1] == cp_model.INFEASIBLE
    two = [('Style', 'A', 'dock', 1, 1), ('Tech', 'B', 'dock', 1, 1)]
    assert _force_all(_custom_bundle(two, travel, allowance))[1] == cp_model.OPTIMAL
    over[0]["service_allowance_min"] = 270
    over[2]["service_allowance_min"] = 241
    assert _force_all(_custom_bundle(two, travel, over))[1] == cp_model.INFEASIBLE
    mixed = [('Fresh', 'A', 'dock', 1, 1), ('Style', 'B', 'dock', 1, 1)]
    assert _force_all(_custom_bundle(mixed, travel, allowance))[1] == cp_model.OPTIMAL
    two_fresh = [('Fresh', 'A', 'dock', 1, 1), ('Fresh', 'B', 'dock', 1, 1)]
    fresh_135 = [dict(row) for row in allowance]
    fresh_135[0]["service_allowance_min"] = 135
    assert _force_all(_custom_bundle(two_fresh, travel, fresh_135))[1] == cp_model.OPTIMAL
    fresh_135[0]["service_allowance_min"] = 136
    assert _force_all(_custom_bundle(two_fresh, travel, fresh_135))[1] == cp_model.INFEASIBLE


def test_combined_weight_and_volume_and_group_separation():
    travel = [{"depot": "Peliyagoda", "district": "A", "depot_to_district_freeflow_min": 1,
               "inter_stop_freeflow_min": 1}]
    allowance = [{"brand": "Fresh", "dock_type": "dock", "service_allowance_min": 1}]
    two = [('Fresh', 'A', 'dock', 5, 5)] * 2
    assert _force_all(_custom_bundle(two, travel, allowance, weight_cap=10, volume_cap=10), one_trip=True)[1] == cp_model.OPTIMAL
    assert _force_all(_custom_bundle(two, travel, allowance, weight_cap=9, volume_cap=10), one_trip=True)[1] == cp_model.INFEASIBLE
    assert _force_all(_custom_bundle(two, travel, allowance, weight_cap=10, volume_cap=9), one_trip=True)[1] == cp_model.INFEASIBLE
    other_brand = allowance + [{"brand": "Style", "dock_type": "dock", "service_allowance_min": 1}]
    mixed_brand = [('Fresh', 'A', 'dock', 1, 1), ('Style', 'A', 'dock', 1, 1)]
    assert _force_all(_custom_bundle(mixed_brand, travel, other_brand), one_trip=True)[1] == cp_model.INFEASIBLE
    other_district = travel + [{"depot": "Peliyagoda", "district": "B", "depot_to_district_freeflow_min": 1,
                                "inter_stop_freeflow_min": 1}]
    mixed_district = [('Fresh', 'A', 'dock', 1, 1), ('Fresh', 'B', 'dock', 1, 1)]
    assert _force_all(_custom_bundle(mixed_district, other_district, allowance), one_trip=True)[1] == cp_model.INFEASIBLE


def test_identical_vehicle_symmetry_keeps_feasible_service():
    orders, fleet, vehicles, travel, allowance, scenario_config = _frames()
    fleet.loc[fleet.vehicle_id.eq("v2"), "status"] = "available"
    vehicles.loc[vehicles.vehicle_id.eq("v2"), ["type", "temp", "weight_cap_kg", "volume_cap_m3"]] = ["van", "reefer", 10, 10]
    scenario = build_s1_scenario(orders, fleet, vehicles, travel, allowance, scenario_config)
    matrix = build_compatibility_matrix(scenario["orders_s1"], scenario["usable_fleet_s1"])
    metadata = build_order_priority_metadata(scenario["orders_s1"], order_compatibility_summary(matrix), matrix)
    _, _, _, config, priority = _case()
    bundle = build_optimizer_model(build_solver_data(scenario, matrix, metadata, config, priority))
    for variable in bundle.serve.values():
        bundle.model.Add(variable == 1)
    solver = cp_model.CpSolver()
    assert solver.Solve(bundle.model) == cp_model.OPTIMAL
    assert sum(solver.Value(bundle.use_trip["v1", t]) for t in (1, 2)) >= sum(
        solver.Value(bundle.use_trip["v2", t]) for t in (1, 2))
