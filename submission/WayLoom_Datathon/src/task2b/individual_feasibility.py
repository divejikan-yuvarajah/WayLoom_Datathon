"""Exact one-order feasibility diagnostics over approved Phase 22 data."""

from __future__ import annotations

from dataclasses import dataclass

from src.task2b.cp_scaling import from_scaled_int
from src.task2b.solver_data import SolverData


@dataclass(frozen=True)
class IndividualFeasibilityResult:
    order_ref: str
    compatible_vehicle_count: int
    individually_feasible: bool
    feasible_vehicle_count: int
    time_blocker_code: str | None
    minimum_single_order_minutes: str | None


class IndividualFeasibilityError(ValueError):
    """Static compatibility and exact one-order feasibility disagree."""


def single_order_minutes(data: SolverData, order_ref: str) -> int:
    """Official one-order trip time in Phase 22 scaled integer units."""
    order = data.order_rows[order_ref]
    return data.outbound[(str(order["depot"]), str(order["district"]))] + data.service[order_ref]


def _defensive_static_check(data: SolverData, order_ref: str, vehicle_id: str) -> None:
    order, vehicle = data.order_rows[order_ref], data.vehicle_rows[vehicle_id]
    valid = (
        (order["temp_requirement"] != "chilled" or vehicle["temp"] == "reefer")
        and (order["parking_constraint"] != "van_only" or vehicle["type"] == "van")
        and order["depot"] == vehicle["depot"]
        and data.weight[order_ref] <= data.weight_cap[vehicle_id]
        and data.volume[order_ref] <= data.volume_cap[vehicle_id]
    )
    if not valid:
        raise IndividualFeasibilityError(
            "Phase 19 compatible pair fails a defensive official-rule recheck."
        )


def evaluate_individual_feasibility(data: SolverData,
                                    order_ref: str) -> IndividualFeasibilityResult:
    if order_ref not in data.order_rows:
        raise IndividualFeasibilityError("Unknown order_ref for individual feasibility.")
    vehicles = [v for o, v in data.compatible_pairs if o == order_ref]
    for vehicle_id in vehicles:
        _defensive_static_check(data, order_ref, vehicle_id)
    if not vehicles:
        return IndividualFeasibilityResult(order_ref, 0, False, 0, None, None)
    minutes = single_order_minutes(data, order_ref)
    order = data.order_rows[order_ref]
    limit = (270 if order["brand"] == "Fresh" else 480) * data.scales["time"]
    feasible = [vehicle_id for vehicle_id in vehicles if minutes <= limit]
    blocker = None
    if not feasible:
        blocker = "FRESH_TIME_BUDGET" if order["brand"] == "Fresh" else "STYLE_TECH_TIME_BUDGET"
    return IndividualFeasibilityResult(
        order_ref=order_ref,
        compatible_vehicle_count=len(vehicles),
        individually_feasible=bool(feasible),
        feasible_vehicle_count=len(feasible),
        time_blocker_code=blocker,
        minimum_single_order_minutes=str(from_scaled_int(minutes, data.scales["time"])),
    )
