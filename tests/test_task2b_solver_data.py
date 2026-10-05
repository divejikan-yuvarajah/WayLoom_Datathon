"""Synthetic-only numeric and upstream contract tests for Phase 22."""
from copy import deepcopy
from decimal import Decimal

import pytest
import yaml

from src.task2b.compatibility import build_compatibility_matrix, order_compatibility_summary
from src.task2b.cp_scaling import ScalingError, derive_exact_scale, from_scaled_int, to_scaled_int, validate_exact_scaling
from src.task2b.priority import build_order_priority_metadata
from src.task2b.scenario import build_s1_scenario
from src.task2b.solver_data import SolverDataError, build_solver_data
from tests.test_task2b_scenario import _frames


def _case():
    scenario = build_s1_scenario(*_frames())
    orders, vehicles = scenario["orders_s1"], scenario["usable_fleet_s1"]
    matrix = build_compatibility_matrix(orders, vehicles)
    metadata = build_order_priority_metadata(orders, order_compatibility_summary(matrix), matrix)
    with open("configs/task2b_optimizer.yaml", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    with open("configs/task2b_priority.yaml", encoding="utf-8") as stream:
        priority = yaml.safe_load(stream)
    return scenario, matrix, metadata, config, priority


def test_exact_decimal_scaling():
    values = ["0.125", "1.5", "10"]
    scale = derive_exact_scale(values)
    assert scale == 1000
    validate_exact_scaling(values, scale)
    assert to_scaled_int("0.125", scale) == 125
    assert from_scaled_int(125, scale) == Decimal("0.125")
    with pytest.raises(ScalingError):
        derive_exact_scale(["0.0000001"], 6)
    with pytest.raises(ScalingError):
        to_scaled_int("0.125", 100)


def test_solver_data_uses_only_exact_compatible_pairs():
    data = build_solver_data(*_case())
    assert data.order_ids == ("o1", "o2")
    assert data.vehicle_ids == ("v1",)
    assert data.compatible_pairs == (("o1", "v1"), ("o2", "v1"))
    scenario, matrix, metadata, config, priority = _case()
    matrix.loc[matrix.order_ref.eq("o2"), "is_compatible"] = False
    with pytest.raises(SolverDataError, match="disagrees"):
        build_solver_data(scenario, matrix, metadata, config, priority)
    scenario, matrix, metadata, config, priority = _case()
    priority["objective_levels"][0][1] = "minimize"
    with pytest.raises(SolverDataError, match="policy"):
        build_solver_data(scenario, matrix, metadata, config, priority)
    scenario, matrix, metadata, config, priority = _case()
    config["solver"]["stage_time_limits_seconds"] = [120, 60]
    with pytest.raises(SolverDataError, match="retry limits"):
        build_solver_data(scenario, matrix, metadata, config, priority)
    scenario, matrix, metadata, config, priority = _case()
    scenario["orders_s1"].loc[0, "brand"] = "Unknown"
    with pytest.raises(SolverDataError, match="brand"):
        build_solver_data(scenario, matrix, metadata, config, priority)


def test_impossible_order_has_no_assignment_and_ambient_can_use_reefer():
    from src.task2b.lexicographic_solver import solve_lexicographic
    from src.task2b.optimizer import build_optimizer_model
    from src.task2b.solution import extract_allocation

    orders, fleet, vehicles, travel, allowance, scenario_config = _frames()
    vehicles.loc[vehicles.vehicle_id.eq("v1"), ["type", "temp"]] = ["truck", "ambient"]
    scenario = build_s1_scenario(orders, fleet, vehicles, travel, allowance, scenario_config)
    matrix = build_compatibility_matrix(scenario["orders_s1"], scenario["usable_fleet_s1"])
    metadata = build_order_priority_metadata(scenario["orders_s1"], order_compatibility_summary(matrix), matrix)
    _, _, _, config, priority = _case()
    bundle = build_optimizer_model(build_solver_data(scenario, matrix, metadata, config, priority))
    assert not any(o == "o1" for o, _, _ in bundle.x)
    allocation = extract_allocation(bundle, solve_lexicographic(bundle, config))
    assert allocation.set_index("order_ref").loc["o1", "decision"] == "deferred"
    assert allocation.set_index("order_ref").loc["o2", "decision"] == "served"
    original = build_optimizer_model(build_solver_data(*_case()))
    assert any(o == "o2" and v == "v1" for o, v, _ in original.x)
