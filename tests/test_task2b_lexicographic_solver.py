"""Synthetic Phase 22 sequential-objective and status tests."""
import pytest
from ortools.sat.python import cp_model
import src.task2b.lexicographic_solver as lexicographic_solver

from src.task2b.lexicographic_solver import SolverStatusError, assert_deterministic, check_solver_status, solve_lexicographic
from src.task2b.optimizer import build_optimizer_model
from src.task2b.priority import OBJECTIVE_LEVELS
from src.task2b.solution import extract_allocation
from src.task2b.solver_data import build_solver_data
from tests.test_task2b_solver_data import _case


def test_all_stages_proven_and_deterministic():
    scenario, matrix, metadata, config, priority = _case()
    first = build_optimizer_model(build_solver_data(scenario, matrix, metadata, config, priority))
    progress = []
    a = solve_lexicographic(first, config, on_progress=progress.append)
    allocation_a = extract_allocation(first, a)
    second = build_optimizer_model(build_solver_data(scenario, matrix, metadata, config, priority))
    b = solve_lexicographic(second, config)
    allocation_b = extract_allocation(second, b)
    assert_deterministic((a, allocation_a), (b, allocation_b))
    assert tuple(a.objective_vector) == OBJECTIVE_LEVELS
    assert all(stage["status"] == "OPTIMAL" for stage in a.stage_records)
    assert progress[0] == "FEASIBILITY SMOKE: START"
    assert all("objective_value" not in message for message in progress)
    assert a.objective_vector["served_order_count"] == 2
    assert len(first.model.Proto().constraints) >= 9


@pytest.mark.parametrize("status", [cp_model.FEASIBLE, cp_model.INFEASIBLE, cp_model.MODEL_INVALID, cp_model.UNKNOWN])
def test_final_stage_rejects_nonoptimal_status(status):
    with pytest.raises(SolverStatusError):
        check_solver_status(status, final_stage=True)


def test_smoke_accepts_feasible_but_rejects_invalid():
    check_solver_status(cp_model.FEASIBLE, final_stage=False)
    with pytest.raises(SolverStatusError):
        check_solver_status(cp_model.UNKNOWN, final_stage=False)


def test_feasible_stage_retries_and_still_requires_proof(monkeypatch):
    scenario, matrix, metadata, config, priority = _case()
    config["solver"]["max_time_seconds_per_objective_stage"] = 1
    config["solver"]["stage_time_limits_seconds"] = [1, 2, 3]
    original_factory = lexicographic_solver._solver

    class FirstAttemptFeasible:
        def __init__(self, real):
            self.real = real
            self.calls = 0
            self.parameters = real.parameters

        def Solve(self, model):
            self.calls += 1
            actual = self.real.Solve(model)
            return cp_model.FEASIBLE if self.calls == 2 and actual == cp_model.OPTIMAL else actual

        def __getattr__(self, name):
            return getattr(self.real, name)

    monkeypatch.setattr(lexicographic_solver, "_solver", lambda cfg: FirstAttemptFeasible(original_factory(cfg)))
    bundle = build_optimizer_model(build_solver_data(scenario, matrix, metadata, config, priority))
    result = solve_lexicographic(bundle, config)
    assert [attempt["status"] for attempt in result.stage_records[0]["attempts"]] == ["FEASIBLE", "OPTIMAL"]
    assert all(stage["status"] == "OPTIMAL" for stage in result.stage_records)


def test_retry_exhaustion_names_stage_without_freezing(monkeypatch):
    scenario, matrix, metadata, config, priority = _case()
    config["solver"]["max_time_seconds_per_objective_stage"] = 1
    config["solver"]["stage_time_limits_seconds"] = [1, 2]
    original_factory = lexicographic_solver._solver

    class NoProof:
        def __init__(self, real):
            self.real = real
            self.calls = 0
            self.parameters = real.parameters

        def Solve(self, model):
            self.calls += 1
            self.real.Solve(model)
            return cp_model.OPTIMAL if self.calls == 1 else cp_model.FEASIBLE

        def __getattr__(self, name):
            return getattr(self.real, name)

    monkeypatch.setattr(lexicographic_solver, "_solver", lambda cfg: NoProof(original_factory(cfg)))
    bundle = build_optimizer_model(build_solver_data(scenario, matrix, metadata, config, priority))
    with pytest.raises(SolverStatusError, match="served_order_count remained FEASIBLE"):
        solve_lexicographic(bundle, config)
