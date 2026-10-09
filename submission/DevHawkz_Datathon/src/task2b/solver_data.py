"""Validated, deterministic Phase 22 inputs; contains no solver decisions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from src.task2b.cp_scaling import derive_exact_scale, to_scaled_int, validate_exact_scaling
from src.task2b.priority import OBJECTIVE_LEVELS


class SolverDataError(ValueError):
    """An upstream scenario, compatibility, or policy contract is inconsistent."""


@dataclass(frozen=True)
class SolverData:
    orders: pd.DataFrame
    vehicles: pd.DataFrame
    travel: pd.DataFrame
    allowance: pd.DataFrame
    matrix: pd.DataFrame
    metadata: pd.DataFrame
    order_ids: tuple[str, ...]
    vehicle_ids: tuple[str, ...]
    groups: tuple[tuple[str, str], ...]
    compatible_pairs: tuple[tuple[str, str], ...]
    order_rows: dict[str, dict]
    vehicle_rows: dict[str, dict]
    metadata_rows: dict[str, dict]
    order_group: dict[str, tuple[str, str]]
    weight: dict[str, int]
    volume: dict[str, int]
    weight_cap: dict[str, int]
    volume_cap: dict[str, int]
    outbound: dict[tuple[str, str], int]
    inter_stop: dict[tuple[str, str], int]
    service: dict[str, int]
    scales: dict[str, int]


def _require(frame: pd.DataFrame, names: set[str], label: str) -> None:
    if names.difference(frame.columns):
        raise SolverDataError(f"{label} is missing required columns.")


def _flag(value: object) -> bool:
    if value is True or str(value) == "True":
        return True
    if value is False or str(value) == "False":
        return False
    raise SolverDataError("Compatibility/policy flags must be Boolean.")


def validate_optimizer_config(config: dict, priority_config: dict) -> None:
    if config.get("version") != 1 or config.get("solver", {}).get("engine") != "ortools_cp_sat":
        raise SolverDataError("Invalid local CP-SAT configuration.")
    model, time, objective, scaling = (config.get(k, {}) for k in ("model", "time", "objective", "scaling"))
    if model.get("trip_ids") != [1, 2] or any(model.get(k) is not True for k in (
        "enforce_trip_2_requires_trip_1", "assignment_variables_only_for_compatible_pairs",
        "independently_recheck_compatibility_contract")):
        raise SolverDataError("Official two-trip/compatibility model is not enabled.")
    if time.get("fresh_budget_min") != 270 or time.get("style_tech_budget_min") != 480 or time.get("include_return_leg") is not False:
        raise SolverDataError("Official time budgets or return-leg rule changed.")
    if scaling.get("strategy") != "exact_decimal" or scaling.get("reject_rounding") is not True:
        raise SolverDataError("Exact scaling is mandatory.")
    if objective.get("strategy") != "lexicographic" or priority_config.get("strategy") != "lexicographic":
        raise SolverDataError("The Phase 21 lexicographic policy is frozen.")
    levels = priority_config.get("objective_levels")
    expected = [[name, "maximize" if name.startswith("served_") else "minimize"] for name in OBJECTIVE_LEVELS]
    if levels != expected or priority_config.get("hard_rule_override") is not False or priority_config.get("low_flexibility_threshold") != 2:
        raise SolverDataError("The Phase 21 objective or low-flexibility policy changed.")
    solver = config["solver"]
    if solver.get("require_optimal_objective_stages_for_freeze") is not True or solver.get("allow_feasible_only_final_freeze") is not False:
        raise SolverDataError("Final freeze must require all stages OPTIMAL.")
    if not isinstance(solver.get("max_time_seconds_per_objective_stage"), (int, float)) or solver["max_time_seconds_per_objective_stage"] <= 0:
        raise SolverDataError("A positive solve time is required.")
    limits = solver.get("stage_time_limits_seconds")
    if (not isinstance(limits, list) or not limits or
        any(not isinstance(value, (int, float)) or value <= 0 for value in limits) or
        limits[0] != solver["max_time_seconds_per_objective_stage"] or
        any(later <= earlier for earlier, later in zip(limits, limits[1:]))):
        raise SolverDataError("Objective retry limits must increase from the base solve time.")
    if not isinstance(solver.get("num_search_workers"), int) or solver["num_search_workers"] != 1:
        raise SolverDataError("Deterministic single-worker solve is required.")
    if solver.get("linearization_level") not in (0, 1, 2):
        raise SolverDataError("CP-SAT linearization level must be a supported mechanical setting.")


def build_solver_data(scenario: dict, matrix: pd.DataFrame, metadata: pd.DataFrame,
                      config: dict, priority_config: dict) -> SolverData:
    validate_optimizer_config(config, priority_config)
    orders = scenario["orders_s1"].copy(deep=True)
    vehicles = scenario["usable_fleet_s1"].copy(deep=True)
    travel = scenario["district_travel_ref"].copy(deep=True)
    allowance = scenario["service_allowance_ref"].copy(deep=True)
    matrix = matrix.copy(deep=True)
    metadata = metadata.copy(deep=True)
    _require(orders, {"order_ref", "outlet_id", "scenario", "brand", "district", "depot", "dock_type", "temp_requirement",
                      "parking_constraint", "order_weight_kg", "order_volume_m3"}, "orders")
    _require(vehicles, {"vehicle_id", "status", "type", "temp", "depot", "weight_cap_kg", "volume_cap_m3"}, "vehicles")
    _require(matrix, {"order_ref", "vehicle_id", "is_compatible"}, "compatibility matrix")
    _require(metadata, {"order_ref", "deferred_yesterday", "days_since_last_served", "is_fresh", "is_fresh_chilled",
                        "compatible_vehicle_count", "is_individually_impossible", "is_singleton", "is_low_flexibility",
                        "has_non_reefer_alternative", "has_non_van_alternative", "has_non_reefer_van_alternative"}, "priority metadata")
    if orders.order_ref.isna().any() or orders.order_ref.duplicated().any() or vehicles.vehicle_id.isna().any() or vehicles.vehicle_id.duplicated().any():
        raise SolverDataError("Order and vehicle IDs must be unique and nonnull.")
    if not orders.scenario.eq("S1").all() or not orders.depot.eq("Peliyagoda").all() or not vehicles.status.eq("available").all() or not vehicles.depot.eq("Peliyagoda").all():
        raise SolverDataError("Only S1 orders and available Peliyagoda vehicles may enter the model.")
    if not set(orders.brand).issubset({"Fresh", "Style", "Tech"}) or not set(orders.temp_requirement).issubset({"ambient", "chilled"}):
        raise SolverDataError("Unsupported brand or temperature domain in S1 orders.")
    if matrix.duplicated(["order_ref", "vehicle_id"]).any() or metadata.order_ref.duplicated().any():
        raise SolverDataError("Compatibility/priority keys must be unique.")
    order_ids = tuple(sorted(orders.order_ref.astype(str)))
    vehicle_ids = tuple(sorted(vehicles.vehicle_id.astype(str)))
    if set(metadata.order_ref.astype(str)) != set(order_ids):
        raise SolverDataError("Every S1 order needs one priority row.")
    if set(map(tuple, matrix[["order_ref", "vehicle_id"]].astype(str).itertuples(index=False, name=None))) != {(o, v) for o in order_ids for v in vehicle_ids}:
        raise SolverDataError("The Phase 19 matrix must cover the complete usable cross product.")
    order_rows = {str(r["order_ref"]): r for r in orders.to_dict("records")}
    vehicle_rows = {str(r["vehicle_id"]): r for r in vehicles.to_dict("records")}
    metadata_rows = {str(r["order_ref"]): r for r in metadata.to_dict("records")}
    compatible_pairs = []
    for pair in matrix.to_dict("records"):
        o, v = str(pair["order_ref"]), str(pair["vehicle_id"])
        order, vehicle = order_rows[o], vehicle_rows[v]
        independently_compatible = (
            (order["temp_requirement"] != "chilled" or vehicle["temp"] == "reefer")
            and (order["parking_constraint"] != "van_only" or vehicle["type"] == "van")
            and order["depot"] == vehicle["depot"]
            and Decimal(str(order["order_weight_kg"])) <= Decimal(str(vehicle["weight_cap_kg"]))
            and Decimal(str(order["order_volume_m3"])) <= Decimal(str(vehicle["volume_cap_m3"]))
        )
        if _flag(pair["is_compatible"]) != independently_compatible:
            raise SolverDataError("Phase 19 compatibility disagrees with independent exact hard-rule checks.")
        if independently_compatible:
            compatible_pairs.append((o, v))
    compatible_pairs = tuple(sorted(compatible_pairs))
    options = {o: [vehicle_rows[v] for oo, v in compatible_pairs if oo == o] for o in order_ids}
    for o in order_ids:
        order, meta, choices = order_rows[o], metadata_rows[o], options[o]
        expected = {
            "deferred_yesterday": int(order["deferred_yesterday"]),
            "days_since_last_served": int(order["days_since_last_served"]),
            "compatible_vehicle_count": len(choices),
        }
        if any(int(meta[k]) != value for k, value in expected.items()):
            raise SolverDataError("Priority metadata disagrees with scenario/compatibility inputs.")
        flags = {
            "is_fresh": order["brand"] == "Fresh",
            "is_fresh_chilled": order["brand"] == "Fresh" and order["temp_requirement"] == "chilled",
            "is_individually_impossible": len(choices) == 0,
            "is_singleton": len(choices) == 1,
            "is_low_flexibility": 1 <= len(choices) <= 2,
            "has_non_reefer_alternative": any(v["temp"] != "reefer" for v in choices),
            "has_non_van_alternative": any(v["type"] != "van" for v in choices),
            "has_non_reefer_van_alternative": any(v["temp"] != "reefer" or v["type"] != "van" for v in choices),
        }
        if any(_flag(meta[k]) != value for k, value in flags.items()):
            raise SolverDataError("Priority metadata flags disagree with Phase 19 inputs.")
    groups = tuple(sorted({(str(r["brand"]), str(r["district"])) for r in order_rows.values()}))
    order_group = {o: (str(order_rows[o]["brand"]), str(order_rows[o]["district"])) for o in order_ids}
    travel_map = {(str(r["depot"]), str(r["district"])): r for r in travel.to_dict("records")}
    service_map = {(str(r["brand"]), str(r["dock_type"])): r for r in allowance.to_dict("records")}
    if travel.duplicated(["depot", "district"]).any() or allowance.duplicated(["brand", "dock_type"]).any():
        raise SolverDataError("Trip-time reference keys must be unique.")
    if any((order_rows[o]["depot"], order_rows[o]["district"]) not in travel_map or
           (order_rows[o]["brand"], order_rows[o]["dock_type"]) not in service_map for o in order_ids):
        raise SolverDataError("Trip-time reference coverage is incomplete.")
    weight_values = [r["order_weight_kg"] for r in order_rows.values()] + [r["weight_cap_kg"] for r in vehicle_rows.values()]
    volume_values = [r["order_volume_m3"] for r in order_rows.values()] + [r["volume_cap_m3"] for r in vehicle_rows.values()]
    time_values = ([r["depot_to_district_freeflow_min"] for r in travel_map.values()] +
                   [r["inter_stop_freeflow_min"] for r in travel_map.values()] +
                   [r["service_allowance_min"] for r in service_map.values()] + [270, 480])
    maximum = config["scaling"]["max_decimal_places"]
    scales = {"weight": derive_exact_scale(weight_values, maximum),
              "volume": derive_exact_scale(volume_values, maximum),
              "time": derive_exact_scale(time_values, maximum)}
    for family, values in (("weight", weight_values), ("volume", volume_values), ("time", time_values)):
        validate_exact_scaling(values, scales[family])
    weight = {o: to_scaled_int(order_rows[o]["order_weight_kg"], scales["weight"]) for o in order_ids}
    volume = {o: to_scaled_int(order_rows[o]["order_volume_m3"], scales["volume"]) for o in order_ids}
    weight_cap = {v: to_scaled_int(vehicle_rows[v]["weight_cap_kg"], scales["weight"]) for v in vehicle_ids}
    volume_cap = {v: to_scaled_int(vehicle_rows[v]["volume_cap_m3"], scales["volume"]) for v in vehicle_ids}
    outbound = {(r["depot"], r["district"]): to_scaled_int(r["depot_to_district_freeflow_min"], scales["time"]) for r in travel_map.values()}
    inter_stop = {(r["depot"], r["district"]): to_scaled_int(r["inter_stop_freeflow_min"], scales["time"]) for r in travel_map.values()}
    service = {o: to_scaled_int(service_map[(order_rows[o]["brand"], order_rows[o]["dock_type"])]["service_allowance_min"], scales["time"]) for o in order_ids}
    return SolverData(orders, vehicles, travel, allowance, matrix, metadata, order_ids, vehicle_ids,
                      groups, compatible_pairs, order_rows, vehicle_rows, metadata_rows, order_group,
                      weight, volume, weight_cap, volume_cap, outbound, inter_stop, service, scales)
