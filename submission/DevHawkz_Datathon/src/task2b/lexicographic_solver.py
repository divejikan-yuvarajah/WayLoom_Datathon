"""Sequential Phase 21 objectives with proof of every preceding optimum."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ortools.sat.python import cp_model

from src.task2b.priority import OBJECTIVE_LEVELS
from src.task2b.optimizer import ModelBundle


class SolverStatusError(RuntimeError):
    """The candidate cannot be frozen under the required solver status."""


@dataclass
class SolveResult:
    solver: cp_model.CpSolver
    smoke_status: str
    stage_records: list[dict]
    objective_vector: dict[str, int]


def check_solver_status(status: int, *, final_stage: bool) -> None:
    accepted = {cp_model.OPTIMAL} if final_stage else {cp_model.OPTIMAL, cp_model.FEASIBLE}
    if status not in accepted:
        name = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE",
                cp_model.INFEASIBLE: "INFEASIBLE", cp_model.MODEL_INVALID: "MODEL_INVALID",
                cp_model.UNKNOWN: "UNKNOWN"}.get(status, f"UNRECOGNIZED({status})")
        raise SolverStatusError(f"Solver status {name} cannot continue/freeze.")


def _solver(config: dict) -> cp_model.CpSolver:
    params = config["solver"]
    solver = cp_model.CpSolver()
    solver.parameters.random_seed = int(params["random_seed"])
    solver.parameters.num_search_workers = int(params["num_search_workers"])
    solver.parameters.max_time_in_seconds = float(params["max_time_seconds_per_objective_stage"])
    solver.parameters.log_search_progress = bool(params["log_search_progress"])
    solver.parameters.linearization_level = int(params["linearization_level"])
    return solver


def _hint_solution(bundle: ModelBundle, solver: cp_model.CpSolver) -> None:
    """Offer the last feasible assignment to the next proof attempt."""
    bundle.model.ClearHints()
    for family in (bundle.serve, bundle.defer, bundle.x, bundle.use_trip,
                   bundle.use_group, bundle.trip_minutes):
        for variable in family.values():
            bundle.model.AddHint(variable, solver.Value(variable))


def solve_lexicographic(bundle: ModelBundle, config: dict,
                        on_progress: Callable[[str], None] | None = None) -> SolveResult:
    progress = on_progress or (lambda _message: None)
    solver = _solver(config)
    progress("FEASIBILITY SMOKE: START")
    smoke = solver.Solve(bundle.model)
    check_solver_status(smoke, final_stage=False)
    smoke_name = solver.StatusName(smoke)
    progress(f"FEASIBILITY SMOKE: {smoke_name}")
    records = []
    values = {}
    for name in OBJECTIVE_LEVELS:
        expression = bundle.objectives[name]
        direction = "maximize" if name.startswith("served_") else "minimize"
        if direction == "maximize":
            bundle.model.Maximize(expression)
        else:
            bundle.model.Minimize(expression)
        attempts = []
        for attempt_number, seconds in enumerate(config["solver"]["stage_time_limits_seconds"], start=1):
            solver.parameters.max_time_in_seconds = float(seconds)
            progress(f"{name}: ATTEMPT {attempt_number} START")
            status = solver.Solve(bundle.model)
            progress(f"{name}: ATTEMPT {attempt_number} {solver.StatusName(status)}")
            attempts.append({"status": solver.StatusName(status), "time_limit_seconds": seconds,
                             "wall_time_seconds": solver.WallTime()})
            if status == cp_model.OPTIMAL:
                break
            if status == cp_model.FEASIBLE:
                _hint_solution(bundle, solver)
                continue
            check_solver_status(status, final_stage=True)
        if status != cp_model.OPTIMAL:
            raise SolverStatusError(
                f"Phase 22 objective stage {name} remained FEASIBLE after {len(attempts)} bounded attempts; "
                "no allocation was frozen. Increase only the solver time limits and rerun."
            )
        optimum = int(solver.Value(expression)) if not isinstance(expression, int) else expression
        records.append({"level": name, "direction": direction, "status": solver.StatusName(status),
                        "objective_value": optimum, "best_bound": solver.BestObjectiveBound(),
                        "wall_time_seconds": solver.WallTime(), "branches": solver.NumBranches(),
                        "conflicts": solver.NumConflicts(), "fixed_for_next_stage": True,
                        "attempts": attempts})
        values[name] = optimum
        bundle.model.Add(expression == optimum)
        _hint_solution(bundle, solver)
    return SolveResult(solver, smoke_name, records, values)


def assert_deterministic(first: tuple[SolveResult, object], second: tuple[SolveResult, object]) -> None:
    result_a, allocation_a = first
    result_b, allocation_b = second
    if result_a.objective_vector != result_b.objective_vector or not allocation_a.equals(allocation_b):
        raise SolverStatusError("Two stable-seed final solves disagree.")
