from dataclasses import replace

from ortools.sat.python import cp_model

from src.task2b.counterfactual_reasoner import (
    changed_expression,
    forced_hard_status,
    solve_forced_counterfactual,
)
from src.task2b.individual_feasibility import (
    IndividualFeasibilityResult,
    evaluate_individual_feasibility,
)
from src.task2b.lexicographic_solver import solve_lexicographic
from src.task2b.optimizer import build_optimizer_model
from src.task2b.solution import extract_allocation
from src.task2b.solver_data import build_solver_data
from tests.test_task2b_solver_data import _case


def _reasoner():
    return {
        "counterfactual": {"random_seed": 42, "num_search_workers": 1,
                           "max_time_seconds_per_stage": 10},
        "minimal_change": {"require_optimal": True},
    }


def test_individually_feasible_target_has_forced_hard_solution_and_nine_optimal_stages():
    scenario, matrix, metadata, optimizer, priority = _case()
    data = build_solver_data(scenario, matrix, metadata, optimizer, priority)
    baseline_bundle = build_optimizer_model(data)
    baseline_result = solve_lexicographic(baseline_bundle, optimizer)
    baseline = extract_allocation(baseline_bundle, baseline_result)
    individual = evaluate_individual_feasibility(data, "o1")
    result = solve_forced_counterfactual(
        data, baseline, baseline_result.objective_vector, "o1", individual,
        optimizer, _reasoner(),
    )
    assert result.hard_status == "OPTIMAL"
    assert result.forced_solve_status == "OPTIMAL"
    assert len(result.stage_records) == 9
    assert all(stage["status"] == "OPTIMAL" for stage in result.stage_records)
    assert result.vector_relation == "EQUAL"
    assert result.minimal_change_status == "OPTIMAL"


def test_hard_infeasible_forced_target_reports_infeasible():
    scenario, matrix, metadata, optimizer, priority = _case()
    data = build_solver_data(scenario, matrix, metadata, optimizer, priority)
    impossible = replace(data, compatible_pairs=tuple(
        pair for pair in data.compatible_pairs if pair[0] != "o1"
    ))
    config = {**optimizer, "solver": {**optimizer["solver"],
              "max_time_seconds_per_objective_stage": 10,
              "stage_time_limits_seconds": [10]}}
    assert forced_hard_status(impossible, "o1", config) == "INFEASIBLE"


def test_changed_expression_matches_deferred_to_served_and_exact_assignment():
    scenario, matrix, metadata, optimizer, priority = _case()
    data = build_solver_data(scenario, matrix, metadata, optimizer, priority)
    bundle = build_optimizer_model(data)
    frozen = __import__("pandas").DataFrame([
        ["S1", "o1", "shared", "deferred", "", ""],
        ["S1", "o2", "shared", "served", "v1", 2],
    ], columns=["scenario", "order_ref", "outlet_id", "decision", "vehicle_id", "trip_id"])
    expression = changed_expression(bundle, frozen)
    bundle.model.Add(bundle.serve["o1"] == 1)
    bundle.model.Add(bundle.x["o2", "v1", 2] == 1)
    bundle.model.Minimize(expression)
    solver = cp_model.CpSolver()
    assert solver.Solve(bundle.model) == cp_model.OPTIMAL
    assert solver.Value(expression) == 1
