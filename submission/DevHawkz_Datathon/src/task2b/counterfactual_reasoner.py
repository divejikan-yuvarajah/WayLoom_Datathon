"""Solver-grounded force-serve diagnostics over the frozen Phase 22 model."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable

import pandas as pd
from ortools.sat.python import cp_model

from src.task2b.counterfactual_delta import (
    allocation_change_rows,
    compare_objective_vectors,
    first_degraded_policy_tier,
    objective_deltas,
    summarize_allocation_changes,
)
from src.task2b.individual_feasibility import IndividualFeasibilityResult
from src.task2b.lexicographic_solver import SolveResult, solve_lexicographic
from src.task2b.optimizer import ModelBundle, build_optimizer_model
from src.task2b.priority import OBJECTIVE_LEVELS
from src.task2b.solution import extract_allocation
from src.task2b.solver_data import SolverData


class CounterfactualReasonerError(RuntimeError):
    """A forced counterfactual is unresolved or contradicts frozen evidence."""


@dataclass(frozen=True)
class ForcedCounterfactualResult:
    order_ref: str
    hard_status: str
    forced_solve_status: str
    stage_records: tuple[dict, ...]
    objective_vector: dict[str, int] | None
    vector_relation: str | None
    first_degraded_tier: str | None
    minimal_change_status: str | None
    minimum_changed_orders: int | None
    allocation: pd.DataFrame | None
    changes: pd.DataFrame | None
    change_summary: dict[str, int] | None
    objective_delta: dict[str, int] | None


def counterfactual_solver_config(optimizer_config: dict, reasoner_config: dict) -> dict:
    """Keep model/policy mechanics frozen while applying diagnostic solve limits."""
    config = deepcopy(optimizer_config)
    requested = reasoner_config.get("counterfactual") or {}
    seconds = float(requested.get("max_time_seconds_per_stage", 120))
    workers = int(requested.get("num_search_workers", 1))
    seed = int(requested.get("random_seed", 42))
    if seconds <= 0 or workers != 1:
        raise CounterfactualReasonerError("Counterfactual solves require positive time and one worker.")
    config["solver"]["random_seed"] = seed
    config["solver"]["num_search_workers"] = workers
    config["solver"]["max_time_seconds_per_objective_stage"] = seconds
    config["solver"]["stage_time_limits_seconds"] = list(
        requested.get("stage_time_limits_seconds") or [seconds]
    )
    if any(float(value) <= 0 for value in config["solver"]["stage_time_limits_seconds"]):
        raise CounterfactualReasonerError("Counterfactual stage limits must be positive.")
    return config


def _new_solver(config: dict, seconds: float | None = None) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    params = config["solver"]
    solver.parameters.random_seed = int(params["random_seed"])
    solver.parameters.num_search_workers = int(params["num_search_workers"])
    solver.parameters.max_time_in_seconds = float(
        seconds if seconds is not None else params["max_time_seconds_per_objective_stage"]
    )
    solver.parameters.log_search_progress = bool(params.get("log_search_progress", False))
    solver.parameters.linearization_level = int(params.get("linearization_level", 2))
    return solver


def forced_hard_status(data: SolverData, order_ref: str, config: dict) -> str:
    bundle = build_optimizer_model(data)
    if order_ref not in bundle.serve:
        raise CounterfactualReasonerError("Unknown forced target.")
    bundle.model.Add(bundle.serve[order_ref] == 1)
    solver = _new_solver(config)
    return solver.StatusName(solver.Solve(bundle.model))


def changed_expression(bundle: ModelBundle, frozen_allocation: pd.DataFrame):
    """Exact Phase 26 row-change metric as a CP-SAT linear expression."""
    rows = frozen_allocation.set_index(frozen_allocation["order_ref"].astype(str), drop=False)
    if rows.index.duplicated().any() or set(rows.index) != set(bundle.data.order_ids):
        raise CounterfactualReasonerError("Frozen allocation does not match solver order grain.")
    terms = []
    for order_ref in bundle.data.order_ids:
        row = rows.loc[order_ref]
        if row["decision"] == "deferred":
            terms.append(bundle.serve[order_ref])
            continue
        if row["decision"] != "served" or pd.isna(row["vehicle_id"]) or pd.isna(row["trip_id"]):
            raise CounterfactualReasonerError("Frozen allocation decision/assignment is invalid.")
        key = (order_ref, str(row["vehicle_id"]), int(row["trip_id"]))
        if key not in bundle.x:
            raise CounterfactualReasonerError("Frozen served assignment is absent from the approved model.")
        terms.append(1 - bundle.x[key])
    return sum(terms)


def _solve_minimal_change(bundle: ModelBundle, frozen_allocation: pd.DataFrame,
                          objective_vector: dict[str, int], config: dict) -> tuple[str, int | None, object | None]:
    if tuple(objective_vector) != OBJECTIVE_LEVELS:
        raise CounterfactualReasonerError("Forced objective vector is incomplete.")
    expression = changed_expression(bundle, frozen_allocation)
    bundle.model.Minimize(expression)
    last_status = "UNKNOWN"
    for seconds in config["solver"]["stage_time_limits_seconds"]:
        solver = _new_solver(config, float(seconds))
        status = solver.Solve(bundle.model)
        last_status = solver.StatusName(status)
        if status == cp_model.OPTIMAL:
            return last_status, int(solver.Value(expression)), solver
        if status not in (cp_model.FEASIBLE, cp_model.UNKNOWN):
            break
    return last_status, None, None


def solve_forced_counterfactual(
    data: SolverData,
    frozen_allocation: pd.DataFrame,
    baseline_vector: dict[str, int],
    order_ref: str,
    individual: IndividualFeasibilityResult,
    optimizer_config: dict,
    reasoner_config: dict,
    on_progress: Callable[[str], None] | None = None,
) -> ForcedCounterfactualResult:
    """Force one deferred order, prove policy stages, then find the nearest witness."""
    config = counterfactual_solver_config(optimizer_config, reasoner_config)
    hard_status = forced_hard_status(data, order_ref, config)
    hard_feasible = hard_status in {"OPTIMAL", "FEASIBLE"}
    if individual.individually_feasible != hard_feasible:
        raise CounterfactualReasonerError(
            "Individual feasibility and forced-target hard model disagree."
        )
    if not hard_feasible:
        if hard_status != "INFEASIBLE":
            raise CounterfactualReasonerError(f"Forced hard solve is unresolved: {hard_status}.")
        return ForcedCounterfactualResult(
            order_ref, hard_status, "INFEASIBLE", (), None, None, None,
            None, None, None, None, None, None,
        )

    bundle = build_optimizer_model(data)
    bundle.model.Add(bundle.serve[order_ref] == 1)
    result = solve_lexicographic(bundle, config, on_progress=on_progress)
    if len(result.stage_records) != len(OBJECTIVE_LEVELS) or any(
        record["status"] != "OPTIMAL" for record in result.stage_records
    ):
        raise CounterfactualReasonerError("Every forced policy stage must be OPTIMAL.")
    relation = compare_objective_vectors(result.objective_vector, baseline_vector)
    if relation == "BETTER":
        raise CounterfactualReasonerError(
            "Forced target improves the frozen objective vector; Phase 22 evidence is contradicted."
        )
    minimal_status, minimum, diagnostic_solver = _solve_minimal_change(
        bundle, frozen_allocation, result.objective_vector, config
    )
    require_minimum = bool((reasoner_config.get("minimal_change") or {}).get("require_optimal", True))
    if require_minimum and minimal_status != "OPTIMAL":
        raise CounterfactualReasonerError(
            f"Minimal-change diagnostic is unresolved: {minimal_status}."
        )
    if diagnostic_solver is None:
        raise CounterfactualReasonerError("No publishable minimal-change witness exists.")
    diagnostic = SolveResult(diagnostic_solver, hard_status, result.stage_records, result.objective_vector)
    allocation = extract_allocation(bundle, diagnostic)
    changes = allocation_change_rows(frozen_allocation, allocation)
    summary = summarize_allocation_changes(changes)
    if minimum != summary["changed_order_count"]:
        raise CounterfactualReasonerError("CP-SAT change objective and extracted allocation disagree.")
    return ForcedCounterfactualResult(
        order_ref=order_ref,
        hard_status=hard_status,
        forced_solve_status="OPTIMAL",
        stage_records=tuple(result.stage_records),
        objective_vector=result.objective_vector,
        vector_relation=relation,
        first_degraded_tier=first_degraded_policy_tier(result.objective_vector, baseline_vector),
        minimal_change_status=minimal_status,
        minimum_changed_orders=minimum,
        allocation=allocation,
        changes=changes,
        change_summary=summary,
        objective_delta=objective_deltas(result.objective_vector, baseline_vector),
    )
