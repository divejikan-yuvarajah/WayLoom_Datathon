"""Phase 18 validated Task 2B S1 inputs; deliberately no allocation logic."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import yaml


class ScenarioValidationError(ValueError):
    """An official Task 2B scenario contract is not satisfied."""


ORDER_COLUMNS = {
    "scenario", "order_ref", "outlet_id", "brand", "district", "depot", "dock_type",
    "parking_constraint", "temp_requirement", "order_weight_kg", "order_volume_m3",
    "deferred_yesterday", "days_since_last_served",
}
FLEET_COLUMNS = {"scenario", "vehicle_id", "status"}
VEHICLE_COLUMNS = {"vehicle_id", "type", "temp", "weight_cap_kg", "volume_cap_m3", "depot"}
TRAVEL_COLUMNS = {"depot", "district", "depot_to_district_freeflow_min", "inter_stop_freeflow_min"}
ALLOWANCE_COLUMNS = {"brand", "dock_type", "service_allowance_min"}
VEHICLE_TYPES = {"truck", "van"}
VEHICLE_TEMPS = {"reefer", "ambient"}


def load_scenario_config(path: str) -> dict[str, Any]:
    config = yaml.safe_load(open(path, encoding="utf-8"))
    if not isinstance(config, dict) or config.get("version") != 1:
        raise ScenarioValidationError("Task 2B scenario configuration is invalid.")
    if config.get("scenario", {}).get("expected_id") != "S1" or config["scenario"].get("expected_depot") != "Peliyagoda":
        raise ScenarioValidationError("Phase 18 is frozen to Scenario S1 at Peliyagoda.")
    return config


def _require(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        raise ScenarioValidationError(f"{label} missing required columns: {', '.join(sorted(missing))}")


def _nonblank(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    for column in columns:
        values = frame[column].astype("string").str.strip()
        if values.isna().any() or values.eq("").any():
            raise ScenarioValidationError(f"{label}.{column} must be nonblank.")


def _finite_nonnegative(frame: pd.DataFrame, columns: list[str], label: str, *, positive: bool = False) -> None:
    for column in columns:
        values = pd.to_numeric(frame[column], errors="raise").to_numpy(dtype=float)
        invalid = not np.isfinite(values).all() or ((values <= 0).any() if positive else (values < 0).any())
        if invalid:
            bound = "positive" if positive else "nonnegative"
            raise ScenarioValidationError(f"{label}.{column} must be finite and {bound}.")


def filter_s1(frame: pd.DataFrame, label: str, scenario: str = "S1") -> pd.DataFrame:
    _require(frame, {"scenario"}, label)
    result = frame.loc[frame.scenario.eq(scenario)].copy()
    if result.empty or not result.scenario.eq(scenario).all():
        raise ScenarioValidationError(f"{label} has no valid Scenario {scenario} rows.")
    return result.reset_index(drop=True)


def validate_orders(orders: pd.DataFrame) -> pd.DataFrame:
    _require(orders, ORDER_COLUMNS, "orders")
    result = orders.copy(deep=True)
    _nonblank(result, ["scenario", "order_ref", "outlet_id", "brand", "district", "depot", "dock_type", "parking_constraint", "temp_requirement"], "orders")
    if result.duplicated(["scenario", "order_ref"]).any():
        raise ScenarioValidationError("order_ref must be unique within a scenario; outlet_id is not the allocation key.")
    _finite_nonnegative(result, ["order_weight_kg", "order_volume_m3"], "orders")
    deferred = pd.to_numeric(result.deferred_yesterday, errors="raise")
    if not deferred.isin([0, 1]).all():
        raise ScenarioValidationError("orders.deferred_yesterday must be 0 or 1.")
    days = pd.to_numeric(result.days_since_last_served, errors="raise")
    if not np.isfinite(days.to_numpy(dtype=float)).all() or (days < 0).any() or not np.equal(days, np.floor(days)).all():
        raise ScenarioValidationError("orders.days_since_last_served must be a nonnegative integer.")
    result["deferred_yesterday"] = deferred.astype(int)
    result["days_since_last_served"] = days.astype(int)
    return result


def validate_fleet(fleet: pd.DataFrame) -> pd.DataFrame:
    _require(fleet, FLEET_COLUMNS, "fleet")
    result = fleet.copy(deep=True)
    _nonblank(result, ["scenario", "vehicle_id", "status"], "fleet")
    if result.duplicated(["scenario", "vehicle_id"]).any():
        raise ScenarioValidationError("vehicle_id must be unique within a scenario.")
    statuses = set(result.status.astype(str))
    if not statuses.issubset({"available", "in_workshop"}):
        raise ScenarioValidationError("Fleet has an unsupported status.")
    return result


def validate_vehicles(vehicles: pd.DataFrame) -> pd.DataFrame:
    _require(vehicles, VEHICLE_COLUMNS, "vehicles")
    result = vehicles.copy(deep=True)
    _nonblank(result, ["vehicle_id", "type", "temp", "depot"], "vehicles")
    if result.vehicle_id.duplicated().any():
        raise ScenarioValidationError("vehicles.vehicle_id must be unique.")
    if not result["type"].isin(VEHICLE_TYPES).all():
        raise ScenarioValidationError("vehicles.type must be an official vehicle type.")
    if not result.temp.isin(VEHICLE_TEMPS).all():
        raise ScenarioValidationError("vehicles.temp must be an official vehicle temperature capability.")
    _finite_nonnegative(result, ["weight_cap_kg", "volume_cap_m3"], "vehicles", positive=True)
    return result


def validate_district_travel(travel: pd.DataFrame) -> pd.DataFrame:
    _require(travel, TRAVEL_COLUMNS, "district travel")
    result = travel.copy(deep=True)
    _nonblank(result, ["depot", "district"], "district travel")
    if result.duplicated(["depot", "district"]).any():
        raise ScenarioValidationError("district travel requires unique depot + district keys.")
    _finite_nonnegative(result, ["depot_to_district_freeflow_min", "inter_stop_freeflow_min"], "district travel")
    return result


def validate_service_allowance(allowance: pd.DataFrame) -> pd.DataFrame:
    _require(allowance, ALLOWANCE_COLUMNS, "service allowance")
    result = allowance.copy(deep=True)
    _nonblank(result, ["brand", "dock_type"], "service allowance")
    if result.duplicated(["brand", "dock_type"]).any():
        raise ScenarioValidationError("service allowance requires unique brand + dock_type keys.")
    _finite_nonnegative(result, ["service_allowance_min"], "service allowance")
    return result


def _assert_coverage(left: pd.DataFrame, keys: list[str], right: pd.DataFrame, label: str) -> None:
    probe = left[keys].drop_duplicates().merge(right[keys].drop_duplicates(), on=keys, how="left", indicator=True, validate="one_to_one")
    if not probe._merge.eq("both").all():
        raise ScenarioValidationError(f"Missing {label} reference coverage.")


def build_s1_scenario(orders: pd.DataFrame, fleet: pd.DataFrame, vehicles: pd.DataFrame,
                      travel: pd.DataFrame, allowance: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    """Create validated Phase-18-only scenario views without compatibility/allocation decisions."""
    expected = config["scenario"]
    orders_s1 = filter_s1(validate_orders(orders), "orders", expected["expected_id"])
    fleet_s1 = filter_s1(validate_fleet(fleet), "fleet", expected["expected_id"])
    vehicles_ref = validate_vehicles(vehicles)
    travel_ref = validate_district_travel(travel)
    allowance_ref = validate_service_allowance(allowance)
    if not orders_s1.depot.eq(expected["expected_depot"]).all():
        raise ScenarioValidationError("S1 order depot contradicts Peliyagoda.")
    _assert_coverage(fleet_s1, ["vehicle_id"], vehicles_ref, "vehicle")
    _assert_coverage(orders_s1, ["depot", "district"], travel_ref, "district travel")
    _assert_coverage(orders_s1, ["brand", "dock_type"], allowance_ref, "service allowance")
    available = fleet_s1.loc[fleet_s1.status.eq(config["fleet"]["available_status"])].copy()
    workshop = fleet_s1.loc[fleet_s1.status.eq(config["fleet"]["workshop_status"]), "vehicle_id"].astype(str)
    if set(available.vehicle_id.astype(str)).intersection(workshop):
        raise ScenarioValidationError("A workshop vehicle entered the available fleet.")
    available_with_ref = available.merge(vehicles_ref, on="vehicle_id", how="left", validate="one_to_one")
    usable = available_with_ref.loc[available_with_ref.depot.eq(expected["expected_depot"])].copy()
    if not usable.status.eq(config["fleet"]["available_status"]).all() or not usable.depot.eq(expected["expected_depot"]).all():
        raise ScenarioValidationError("Usable fleet violates the available Peliyagoda-home contract.")
    diagnostics = {"s1_non_peliyagoda_order_count": int((~orders_s1.depot.eq(expected["expected_depot"])).sum()),
                   "available_vehicle_count": int(len(available)),
                   "available_peliyagoda_home_vehicle_count": int(len(usable)),
                   "available_non_peliyagoda_home_vehicle_count": int(len(available) - len(usable)),
                   "workshop_vehicle_count": int(len(workshop))}
    return {"orders_s1": orders_s1, "fleet_s1": fleet_s1, "available_fleet_s1": available,
            "usable_fleet_s1": usable, "vehicles_ref": vehicles_ref, "district_travel_ref": travel_ref,
            "service_allowance_ref": allowance_ref, "workshop_vehicle_ids": set(workshop),
            "depot_fleet_diagnostics": diagnostics}
