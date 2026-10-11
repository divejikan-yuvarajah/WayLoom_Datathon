"""Independent hard-rule audit on extracted ordinary tables, not CP-SAT vars."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from src.task2b.solution import ALLOCATION_COLUMNS, AUDIT_CHECK_NAMES
from src.task2b.priority import OBJECTIVE_LEVELS
from src.task2b.solver_data import SolverData
from src.task2b.trip_time import calculate_trip_time


class AuditError(ValueError):
    """A candidate allocation violates an official rule or extraction contract."""


@dataclass
class AuditResult:
    status: str
    checks: dict[str, bool]
    trip_summary: pd.DataFrame


TRIP_SUMMARY_COLUMNS = ("vehicle_id", "trip_id", "brand", "district", "order_count", "weight_kg",
                        "volume_m3", "weight_cap_kg", "volume_cap_m3", "outbound_minutes",
                        "inter_stop_minutes", "handling_minutes", "trip_minutes", "budget_category")


def audit_objective_vector(allocation: pd.DataFrame, data: SolverData,
                           expected: dict[str, int]) -> dict[str, int]:
    """Recount the frozen Phase 21 hierarchy from exported decisions."""
    if tuple(expected) != OBJECTIVE_LEVELS:
        raise AuditError("Objective tier order differs from Phase 21.")
    served = allocation.loc[allocation.decision.eq("served")]
    counts = {name: 0 for name in OBJECTIVE_LEVELS}
    for row in served.to_dict("records"):
        o, v = str(row["order_ref"]), str(row["vehicle_id"])
        meta, vehicle = data.metadata_rows[o], data.vehicle_rows[v]
        counts["served_order_count"] += 1
        counts["served_previous_deferred_count"] += int(meta["deferred_yesterday"])
        counts["served_waiting_days_sum"] += int(meta["days_since_last_served"])
        counts["served_low_flexibility_count"] += int(str(meta["is_low_flexibility"]) == "True")
        counts["served_fresh_chilled_count"] += int(str(meta["is_fresh_chilled"]) == "True")
        counts["served_fresh_count"] += int(str(meta["is_fresh"]) == "True")
        if vehicle["type"] == "van" and vehicle["temp"] == "reefer" and str(meta["has_non_reefer_van_alternative"]) == "True":
            counts["avoidable_reefer_van_assignment_count"] += 1
        if vehicle["temp"] == "reefer" and str(meta["has_non_reefer_alternative"]) == "True":
            counts["avoidable_reefer_assignment_count"] += 1
        if vehicle["type"] == "van" and str(meta["has_non_van_alternative"]) == "True":
            counts["avoidable_van_assignment_count"] += 1
    if counts != expected:
        raise AuditError("Extracted allocation disagrees with CP-SAT objective values.")
    return counts


def _number(value: object) -> Decimal:
    number = Decimal(str(value))
    if not number.is_finite():
        raise AuditError("Nonfinite numeric value in allocation audit.")
    return number


def audit_allocation(allocation: pd.DataFrame, data: SolverData,
                     solver_minutes: dict[tuple[str, int], Decimal] | None = None) -> AuditResult:
    if set(allocation.columns) != set(ALLOCATION_COLUMNS) or allocation.order_ref.isna().any():
        raise AuditError("Allocation schema or order keys are invalid.")
    if allocation.order_ref.duplicated().any() or set(allocation.order_ref.astype(str)) != set(data.order_ids):
        raise AuditError("Every S1 order must have exactly one decision.")
    checks = {key: True for key in AUDIT_CHECK_NAMES}
    joined = allocation.copy(deep=True)
    if not joined.scenario.eq("S1").all() or not joined.decision.isin(["served", "deferred"]).all():
        raise AuditError("Scenario or decision domain is invalid.")
    for row in joined.to_dict("records"):
        source = data.order_rows[str(row["order_ref"])]
        if str(row["outlet_id"]) != str(source["outlet_id"]):
            raise AuditError("Order-to-outlet mapping changed.")
        if row["decision"] == "deferred":
            if pd.notna(row["vehicle_id"]) or pd.notna(row["trip_id"]):
                raise AuditError("Deferred orders must not have assignments.")
            continue
        if pd.isna(row["vehicle_id"]) or pd.isna(row["trip_id"]):
            raise AuditError("Served order is missing vehicle or trip.")
        v, o = str(row["vehicle_id"]), str(row["order_ref"])
        if v not in data.vehicle_rows or int(row["trip_id"]) not in (1, 2) or row["trip_id"] != int(row["trip_id"]):
            raise AuditError("Served order uses unavailable vehicle or invalid trip.")
        vehicle = data.vehicle_rows[v]
        if vehicle["status"] != "available" or vehicle["depot"] != "Peliyagoda":
            raise AuditError("Workshop/unavailable fleet entered the allocation.")
        if source["temp_requirement"] == "chilled" and vehicle["temp"] != "reefer":
            raise AuditError("Chilled order assigned to non-reefer.")
        if source["parking_constraint"] == "van_only" and vehicle["type"] != "van":
            raise AuditError("Van-only order assigned to non-van.")
        if source["depot"] != vehicle["depot"]:
            raise AuditError("Vehicle home depot does not match order depot.")
        if (o, v) not in data.compatible_pairs:
            raise AuditError("Served assignment was not Phase 19 compatible.")
    served = joined.loc[joined.decision.eq("served")].copy()
    trip_rows = []
    budgets = {v: {"Fresh": Decimal(0), "StyleTech": Decimal(0)} for v in data.vehicle_ids}
    for (vehicle_id, trip_id), group in served.groupby(["vehicle_id", "trip_id"], sort=True):
        if group.empty:
            continue
        source_orders = data.orders.loc[data.orders.order_ref.isin(group.order_ref)].copy()
        if len(source_orders) != len(group) or source_orders.brand.nunique() != 1 or source_orders.district.nunique() != 1:
            raise AuditError("Trip mixes brands/districts or loses a whole order.")
        vehicle = data.vehicle_rows[str(vehicle_id)]
        weight = sum(_number(value) for value in source_orders.order_weight_kg)
        volume = sum(_number(value) for value in source_orders.order_volume_m3)
        if weight > _number(vehicle["weight_cap_kg"]) or volume > _number(vehicle["volume_cap_m3"]):
            raise AuditError("Trip exceeds weight or volume capacity.")
        breakdown = calculate_trip_time(source_orders, data.travel, data.allowance)
        travel = data.travel.loc[(data.travel.depot == "Peliyagoda") & (data.travel.district == breakdown.district)].iloc[0]
        exact_outbound = _number(travel["depot_to_district_freeflow_min"])
        exact_inter = _number(travel["inter_stop_freeflow_min"]) * (len(source_orders) - 1)
        handling = Decimal(0)
        for order in source_orders.to_dict("records"):
            ref = data.allowance.loc[(data.allowance.brand == order["brand"]) &
                                     (data.allowance.dock_type == order["dock_type"])]
            if len(ref) != 1:
                raise AuditError("Brand+dock service reference is missing or duplicated.")
            handling += _number(ref.service_allowance_min.iloc[0])
        exact_minutes = exact_outbound + exact_inter + handling
        tolerance = Decimal("0.00000001")
        if breakdown.return_minutes_added != 0:
            raise AuditError("Phase 20 trip-time calculator added a forbidden return leg.")
        if abs(_number(breakdown.trip_minutes) - exact_minutes) > tolerance:
            component = next((name for name, actual, expected in (
                ("outbound", breakdown.outbound_minutes, exact_outbound),
                ("inter-stop", breakdown.inter_stop_minutes, exact_inter),
                ("handling", breakdown.handling_minutes, handling),
            ) if abs(_number(actual) - expected) > tolerance), "total")
            raise AuditError(f"Phase 20 {component} trip-time calculation disagrees with exact arithmetic.")
        if solver_minutes is not None and solver_minutes.get((str(vehicle_id), int(trip_id))) != exact_minutes:
            raise AuditError("CP-SAT trip time disagrees with Phase 20 recomputation.")
        category = "Fresh" if breakdown.brand == "Fresh" else "StyleTech"
        budgets[str(vehicle_id)][category] += exact_minutes
        trip_rows.append({"vehicle_id": vehicle_id, "trip_id": int(trip_id), "brand": breakdown.brand,
                          "district": breakdown.district, "order_count": len(group), "weight_kg": str(weight),
                          "volume_m3": str(volume), "weight_cap_kg": str(vehicle["weight_cap_kg"]),
                          "volume_cap_m3": str(vehicle["volume_cap_m3"]), "outbound_minutes": str(exact_outbound),
                          "inter_stop_minutes": str(exact_inter), "handling_minutes": str(handling),
                          "trip_minutes": str(exact_minutes), "budget_category": category})
    if served.groupby("vehicle_id").trip_id.nunique().gt(2).any():
        raise AuditError("Vehicle uses more than two trips.")
    if any(totals["Fresh"] > 270 or totals["StyleTech"] > 480 for totals in budgets.values()):
        raise AuditError("Vehicle exceeds Fresh or Style+Tech daily budget.")
    if solver_minutes is not None:
        used = {(str(r["vehicle_id"]), int(r["trip_id"])) for r in trip_rows}
        if any(minutes != 0 for key, minutes in solver_minutes.items() if key not in used):
            raise AuditError("Unused CP-SAT trip has nonzero minutes.")
    return AuditResult("PASS", checks, pd.DataFrame(trip_rows, columns=TRIP_SUMMARY_COLUMNS))
