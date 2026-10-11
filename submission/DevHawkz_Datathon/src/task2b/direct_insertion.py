"""Direct insertion analysis against the frozen Task 2B allocation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.task2b.solver_data import SolverData


BLOCKER_CODES = (
    "GROUP_MISMATCH_REQUIRES_NEW_TRIP",
    "NO_FREE_TRIP_SLOT",
    "WEIGHT_CAPACITY",
    "VOLUME_CAPACITY",
    "FRESH_TIME_BUDGET",
    "STYLE_TECH_TIME_BUDGET",
    "STATIC_COMPATIBILITY",
)


class DirectInsertionError(ValueError):
    """The insertion diagnostic is invalid or contradicts Phase 22 optimality."""


@dataclass(frozen=True)
class InsertionAttempt:
    vehicle_id: str
    trip_id: int | None
    path_type: str
    feasible: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class DirectInsertionResult:
    order_ref: str
    direct_insert_possible: bool
    attempts: tuple[InsertionAttempt, ...]

    @property
    def blocker_codes(self) -> tuple[str, ...]:
        return tuple(sorted({code for attempt in self.attempts for code in attempt.blockers}))


def _trip_minutes(data: SolverData, order_ids: list[str]) -> int:
    if not order_ids:
        return 0
    group = data.order_group[order_ids[0]]
    if any(data.order_group[o] != group for o in order_ids):
        raise DirectInsertionError("Insertion time requested for a mixed trip group.")
    outbound = data.outbound[("Peliyagoda", group[1])]
    inter = data.inter_stop[("Peliyagoda", group[1])]
    return outbound + inter * (len(order_ids) - 1) + sum(data.service[o] for o in order_ids)


def _vehicle_budget_minutes(data: SolverData, allocation: pd.DataFrame,
                            vehicle_id: str, category: str,
                            replacement: tuple[int, list[str]] | None = None,
                            addition: tuple[int, list[str]] | None = None) -> int:
    served = allocation.loc[
        allocation["decision"].eq("served") & allocation["vehicle_id"].astype(str).eq(vehicle_id)
    ]
    trips = {int(t): group["order_ref"].astype(str).tolist()
             for t, group in served.groupby("trip_id", sort=True)}
    if replacement is not None:
        trips[replacement[0]] = replacement[1]
    if addition is not None:
        trips[addition[0]] = addition[1]
    total = 0
    for order_ids in trips.values():
        brand = data.order_group[order_ids[0]][0]
        selected = brand == "Fresh" if category == "Fresh" else brand in {"Style", "Tech"}
        if selected:
            total += _trip_minutes(data, order_ids)
    return total


def _capacity_blockers(data: SolverData, vehicle_id: str,
                       order_ids: list[str]) -> list[str]:
    blockers = []
    if sum(data.weight[o] for o in order_ids) > data.weight_cap[vehicle_id]:
        blockers.append("WEIGHT_CAPACITY")
    if sum(data.volume[o] for o in order_ids) > data.volume_cap[vehicle_id]:
        blockers.append("VOLUME_CAPACITY")
    return blockers


def _time_blocker(data: SolverData, allocation: pd.DataFrame, vehicle_id: str,
                  order_ref: str, *, replacement: tuple[int, list[str]] | None = None,
                  addition: tuple[int, list[str]] | None = None) -> str | None:
    brand = data.order_group[order_ref][0]
    category, limit = ("Fresh", 270) if brand == "Fresh" else ("StyleTech", 480)
    total = _vehicle_budget_minutes(
        data, allocation, vehicle_id, category, replacement=replacement, addition=addition
    )
    if total > limit * data.scales["time"]:
        return "FRESH_TIME_BUDGET" if category == "Fresh" else "STYLE_TECH_TIME_BUDGET"
    return None


def analyze_direct_insertion(data: SolverData, frozen_allocation: pd.DataFrame,
                             order_ref: str) -> DirectInsertionResult:
    required = {"order_ref", "decision", "vehicle_id", "trip_id"}
    if required.difference(frozen_allocation.columns) or frozen_allocation.order_ref.duplicated().any():
        raise DirectInsertionError("Frozen allocation is not one-row-per-order.")
    target_rows = frozen_allocation.loc[frozen_allocation.order_ref.astype(str).eq(order_ref)]
    if len(target_rows) != 1 or target_rows.iloc[0]["decision"] != "deferred":
        raise DirectInsertionError("Direct insertion target must be frozen deferred.")
    compatible = [v for o, v in data.compatible_pairs if o == order_ref]
    attempts: list[InsertionAttempt] = []
    target_group = data.order_group[order_ref]
    for vehicle_id in data.vehicle_ids:
        if vehicle_id not in compatible:
            continue
        assigned = frozen_allocation.loc[
            frozen_allocation["decision"].eq("served")
            & frozen_allocation["vehicle_id"].astype(str).eq(vehicle_id)
        ]
        used_trips = sorted(int(value) for value in assigned["trip_id"].dropna().unique())
        same_group_found = False
        for trip_id, rows in assigned.groupby("trip_id", sort=True):
            order_ids = rows["order_ref"].astype(str).tolist()
            if data.order_group[order_ids[0]] != target_group:
                continue
            same_group_found = True
            candidate = order_ids + [order_ref]
            blockers = _capacity_blockers(data, vehicle_id, candidate)
            time = _time_blocker(
                data, frozen_allocation, vehicle_id, order_ref,
                replacement=(int(trip_id), candidate),
            )
            if time:
                blockers.append(time)
            attempts.append(InsertionAttempt(vehicle_id, int(trip_id), "EXISTING_SAME_GROUP",
                                             not blockers, tuple(blockers)))
        if not same_group_found:
            group_marker = ["GROUP_MISMATCH_REQUIRES_NEW_TRIP"] if used_trips else []
        else:
            group_marker = []
        if len(used_trips) < 2:
            new_trip = next(value for value in (1, 2) if value not in used_trips)
            blockers = _capacity_blockers(data, vehicle_id, [order_ref])
            time = _time_blocker(
                data, frozen_allocation, vehicle_id, order_ref,
                addition=(new_trip, [order_ref]),
            )
            if time:
                blockers.append(time)
            feasible = not blockers
            attempts.append(InsertionAttempt(vehicle_id, new_trip, "NEW_TRIP",
                                             feasible, tuple(group_marker + blockers)))
        else:
            blockers = (["GROUP_MISMATCH_REQUIRES_NEW_TRIP"] if not same_group_found else [])
            blockers.append("NO_FREE_TRIP_SLOT")
            attempts.append(InsertionAttempt(
                vehicle_id, None, "NEW_TRIP", False, tuple(blockers),
            ))
    return DirectInsertionResult(order_ref, any(item.feasible for item in attempts), tuple(attempts))


def require_no_direct_insertion(result: DirectInsertionResult) -> None:
    if result.direct_insert_possible:
        raise DirectInsertionError(
            "A frozen deferred order can be inserted without changing another assignment; "
            "this contradicts the frozen Level 1 optimum."
        )
