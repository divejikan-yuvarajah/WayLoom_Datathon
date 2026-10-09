from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.task1.feature_registry import (
    FORBIDDEN_DIRECT_TASK1_FEATURES,
    build_feature_registry,
    validate_feature_registry,
)
from src.task1.historical_features import Task1HistoricalFeatureTransformer
from src.task1.labels import combine_local_date_clock, parse_clock


class Task1FeatureBlockerError(ValueError):
    """Raised when feature engineering violates Phase 06 contracts."""


TASK1_FORBIDDEN_SOURCE_COLUMNS = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
    "service_start_dt",
    "service_minutes",
    "late_flag",
}

HISTORICAL_FEATURE_COLUMNS = {
    "outlet_prior_service_median",
    "outlet_prior_late_rate",
    "brand_dock_prior_service_median",
    "brand_dock_prior_late_rate",
    "brand_prior_service_median",
    "brand_prior_late_rate",
}


def load_task1_features_config(config_path: Path | str) -> dict[str, Any]:
    with Path(config_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _assert_unique_delivery_ids(df: pd.DataFrame) -> None:
    if "delivery_id" not in df.columns:
        raise Task1FeatureBlockerError("Missing required column: delivery_id")
    if df["delivery_id"].duplicated().any():
        raise Task1FeatureBlockerError("delivery_id must be unique (one row per delivery).")


def _assert_required(df: pd.DataFrame, required: set[str], where: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1FeatureBlockerError(
            f"Missing required columns in {where}: " + ", ".join(missing)
        )


def _parse_time_range_mall(value: object) -> tuple[float, float, bool]:
    if pd.isna(value) or str(value).strip() == "":
        return np.nan, np.nan, False
    text = str(value).strip()
    if "-" not in text:
        raise Task1FeatureBlockerError(f"Invalid mall_window format: {value!r}")
    start_s, end_s = [x.strip() for x in text.split("-", 1)]
    sh, sm = parse_clock(start_s)
    eh, em = parse_clock(end_s)
    start = sh * 60 + sm
    end = eh * 60 + em
    crosses = end < start
    return float(start), float(end), bool(crosses)


def build_base_order_features(orders: pd.DataFrame) -> pd.DataFrame:
    _assert_unique_delivery_ids(orders)
    required = {
        "delivery_id",
        "outlet_id",
        "brand",
        "district",
        "depot",
        "temp_requirement",
        "order_units",
        "order_weight_kg",
        "order_volume_m3",
        "route_id",
        "seq_in_route",
        "vehicle_id",
        "vehicle_type",
        "vehicle_temp",
        "planned_arrival_time",
        "window_open_time",
        "window_close_time",
    }
    _assert_required(orders, required, "orders")

    if {"service_minutes", "late_flag"} & set(orders.columns):
        raise Task1FeatureBlockerError("Targets must remain outside base feature table.")
    return orders.copy(deep=True)


def add_outlet_reference_features(base: pd.DataFrame, outlets: pd.DataFrame) -> pd.DataFrame:
    _assert_required(outlets, {"outlet_id", "dock_type", "parking_constraint", "mall_window"}, "outlets")
    if outlets["outlet_id"].duplicated().any():
        raise Task1FeatureBlockerError("outlets reference has duplicate outlet_id.")

    left = base.copy(deep=True)
    right = outlets.copy(deep=True)
    left["outlet_id"] = left["outlet_id"].astype("string").str.strip()
    right["outlet_id"] = right["outlet_id"].astype("string").str.strip()

    merged = left.merge(
        right[
            [
                "outlet_id",
                "brand",
                "district",
                "depot",
                "dock_type",
                "parking_constraint",
                "mall_window",
                "window_open_time",
                "window_close_time",
            ]
        ],
        on="outlet_id",
        how="left",
        suffixes=("", "_outlet"),
        validate="many_to_one",
    )
    if merged["dock_type"].isna().any():
        raise Task1FeatureBlockerError("Unknown outlet_id encountered in orders.")

    for col in ("brand", "district", "depot", "window_open_time", "window_close_time"):
        o_col = f"{col}_outlet"
        left = merged[col].astype("string").str.strip()
        right = merged[o_col].astype("string").str.strip()
        mismatch = left.notna() & right.notna() & (left != right)
        if mismatch.any():
            raise Task1FeatureBlockerError(
                f"Order/reference conflict for {col} on outlet join."
            )
        merged[col] = left.fillna(right)
        merged = merged.drop(columns=[o_col])

    starts: list[float] = []
    ends: list[float] = []
    crosses: list[bool] = []
    has_window: list[int] = []
    for val in merged["mall_window"]:
        s, e, c = _parse_time_range_mall(val)
        starts.append(s)
        ends.append(e)
        crosses.append(c)
        has_window.append(0 if np.isnan(s) else 1)
    merged["has_mall_window"] = np.array(has_window, dtype="int8")
    merged["mall_window_start_minute"] = np.array(starts, dtype=float)
    merged["mall_window_end_minute"] = np.array(ends, dtype=float)
    merged["mall_window_crosses_midnight"] = np.array(crosses, dtype=bool)
    return merged


def add_geography_features(df: pd.DataFrame, district_travel: pd.DataFrame) -> pd.DataFrame:
    required = {
        "district",
        "depot",
        "road_class",
        "depot_to_district_km",
        "depot_to_district_freeflow_min",
        "inter_stop_km",
        "inter_stop_freeflow_min",
    }
    _assert_required(district_travel, required, "district_travel")
    if district_travel.duplicated(subset=["district", "depot"]).any():
        raise Task1FeatureBlockerError("district_travel key (district,depot) must be unique.")
    return df.merge(
        district_travel[list(required)],
        on=["district", "depot"],
        how="left",
        validate="many_to_one",
    )


def add_vehicle_features(df: pd.DataFrame, vehicles: pd.DataFrame) -> pd.DataFrame:
    required = {
        "vehicle_id",
        "type",
        "temp",
        "depot",
        "weight_cap_kg",
        "volume_cap_m3",
        "fuel_type",
        "km_per_l",
        "weekly_fuel_quota_l",
    }
    _assert_required(vehicles, required, "vehicles")
    if vehicles["vehicle_id"].duplicated().any():
        raise Task1FeatureBlockerError("vehicles reference has duplicate vehicle_id.")

    left = df.copy(deep=True)
    right = vehicles.copy(deep=True)
    left["vehicle_id"] = left["vehicle_id"].astype("string").str.strip()
    right["vehicle_id"] = right["vehicle_id"].astype("string").str.strip()

    merged = left.merge(
        right[
            [
                "vehicle_id",
                "type",
                "temp",
                "depot",
                "weight_cap_kg",
                "volume_cap_m3",
                "fuel_type",
                "km_per_l",
                "weekly_fuel_quota_l",
            ]
        ],
        on="vehicle_id",
        how="left",
        suffixes=("", "_veh"),
        validate="many_to_one",
    )
    if merged["type"].isna().any():
        raise Task1FeatureBlockerError("Unknown vehicle_id encountered in orders.")

    if (merged["vehicle_type"].astype("string").str.strip() != merged["type"].astype("string").str.strip()).any():
        raise Task1FeatureBlockerError("vehicle_type mismatch between order and vehicle reference.")
    if (merged["vehicle_temp"].astype("string").str.strip() != merged["temp"].astype("string").str.strip()).any():
        raise Task1FeatureBlockerError("vehicle_temp mismatch between order and vehicle reference.")

    merged = merged.rename(
        columns={
            "type": "vehicle_type_ref",
            "temp": "vehicle_temp_ref",
            "depot_veh": "vehicle_home_depot",
        }
    )
    merged["vehicle_home_depot"] = merged["vehicle_home_depot"].astype("string")
    return merged


def add_route_leg_plan_features(df: pd.DataFrame, route_legs: pd.DataFrame) -> pd.DataFrame:
    required = {
        "route_id",
        "seq",
        "date",
        "planned_depart_time",
        "planned_arrival_time",
        "distance_km",
        "planned_travel_duration_min",
    }
    _assert_required(route_legs, required, "route_legs")
    if route_legs.duplicated(subset=["route_id", "seq"]).any():
        raise Task1FeatureBlockerError("route_legs (route_id,seq) must be unique.")

    joined = df.merge(
        route_legs[list(required)],
        how="left",
        left_on=["route_id", "seq_in_route"],
        right_on=["route_id", "seq"],
        validate="one_to_one",
        suffixes=("", "_leg"),
    )
    if joined["seq"].isna().any():
        raise Task1FeatureBlockerError("Orders missing planned route-leg match.")
    joined = joined.drop(columns=["seq"])
    # Route-leg planned arrival is canonical for DT-100 if order value mismatches.
    pa_order = joined["planned_arrival_time"].astype("string").str.strip()
    pa_leg = joined["planned_arrival_time_leg"].astype("string").str.strip()
    mismatch = pa_order.notna() & pa_leg.notna() & (pa_order != pa_leg)
    if mismatch.any():
        raise Task1FeatureBlockerError("planned_arrival_time mismatch between orders and route legs.")
    joined["planned_arrival_time"] = pa_order.fillna(pa_leg)
    joined = joined.drop(columns=["planned_arrival_time_leg"])
    return joined


def add_route_position_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(deep=True)
    out["route_seq"] = pd.to_numeric(out["seq_in_route"], errors="raise").astype(int)
    if (out["route_seq"] < 0).any():
        raise Task1FeatureBlockerError("seq_in_route must be non-negative.")
    out["route_stop_count"] = out.groupby("route_id")["delivery_id"].transform("count").astype(int)
    denom = (out["route_stop_count"] - 1).astype(float)
    out["route_seq_fraction"] = np.where(
        denom <= 0,
        0.0,
        out["route_seq"].astype(float) / denom,
    )
    if ((out["route_seq_fraction"] < 0) | (out["route_seq_fraction"] > 1)).any():
        raise Task1FeatureBlockerError("route_seq_fraction must be in [0,1].")
    out["is_first_stop"] = (out["route_seq"] == 0).astype("int8")
    return out


def _resolve_planned_times(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(deep=True)
    required = {"date", "planned_arrival_time", "planned_depart_time", "window_open_time", "window_close_time"}
    _assert_required(out, required, "planned-time resolution input")
    arr_dt: list[pd.Timestamp] = []
    dep_dt: list[pd.Timestamp] = []
    open_dt: list[pd.Timestamp] = []
    close_dt: list[pd.Timestamp] = []
    for _, row in out.iterrows():
        base_date = row["date"]
        arr = combine_local_date_clock(base_date, row["planned_arrival_time"], 0)
        dep = combine_local_date_clock(base_date, row["planned_depart_time"], 0)
        o_dt = combine_local_date_clock(base_date, row["window_open_time"], 0)
        c_dt = combine_local_date_clock(base_date, row["window_close_time"], 0)
        o_hm = parse_clock(str(row["window_open_time"]).strip())
        c_hm = parse_clock(str(row["window_close_time"]).strip())
        crosses = c_hm < o_hm
        if crosses:
            c_dt = c_dt + timedelta(days=1)
            a_hm = parse_clock(str(row["planned_arrival_time"]).strip())
            d_hm = parse_clock(str(row["planned_depart_time"]).strip())
            if a_hm < o_hm:
                arr = arr + timedelta(days=1)
            if d_hm < o_hm:
                dep = dep + timedelta(days=1)
        arr_dt.append(arr)
        dep_dt.append(dep)
        open_dt.append(o_dt)
        close_dt.append(c_dt)
    out["resolved_planned_arrival_dt"] = arr_dt
    out["resolved_planned_depart_dt"] = dep_dt
    out["resolved_window_open_dt"] = open_dt
    out["resolved_window_close_dt"] = close_dt
    return out


def add_planned_time_and_window_features(df: pd.DataFrame, *, add_cyclical: bool = True) -> pd.DataFrame:
    out = _resolve_planned_times(df)
    arr_mins: list[int] = []
    dep_mins: list[int] = []
    for a, d in zip(out["planned_arrival_time"], out["planned_depart_time"]):
        ah, am = parse_clock(str(a).strip())
        dh, dm = parse_clock(str(d).strip())
        arr_mins.append(ah * 60 + am)
        dep_mins.append(dh * 60 + dm)
    out["planned_arrival_minute_of_day"] = np.array(arr_mins, dtype=int)
    out["planned_depart_minute_of_day"] = np.array(dep_mins, dtype=int)
    out["planned_arrival_hour"] = (out["planned_arrival_minute_of_day"] // 60).astype(int)
    out["planned_depart_hour"] = (out["planned_depart_minute_of_day"] // 60).astype(int)
    if add_cyclical:
        out["planned_arrival_sin"] = np.sin(2 * np.pi * out["planned_arrival_minute_of_day"] / 1440.0)
        out["planned_arrival_cos"] = np.cos(2 * np.pi * out["planned_arrival_minute_of_day"] / 1440.0)
        out["planned_depart_sin"] = np.sin(2 * np.pi * out["planned_depart_minute_of_day"] / 1440.0)
        out["planned_depart_cos"] = np.cos(2 * np.pi * out["planned_depart_minute_of_day"] / 1440.0)

    out["planned_slack_to_close_min"] = (
        out["resolved_window_close_dt"] - out["resolved_planned_arrival_dt"]
    ).dt.total_seconds() / 60.0
    out["planned_early_wait_min"] = np.maximum(
        0.0,
        (
            out["resolved_window_open_dt"] - out["resolved_planned_arrival_dt"]
        ).dt.total_seconds()
        / 60.0,
    )
    out["leg_distance_km"] = pd.to_numeric(out["distance_km"], errors="raise").astype(float)
    out["planned_travel_duration_min_feature"] = pd.to_numeric(
        out["planned_travel_duration_min"], errors="raise"
    ).astype(float)
    out["planned_leg_speed_kmh"] = np.where(
        out["planned_travel_duration_min_feature"] > 0,
        out["leg_distance_km"] / (out["planned_travel_duration_min_feature"] / 60.0),
        np.nan,
    )
    return out


def add_calendar_features(df: pd.DataFrame, calendar: pd.DataFrame) -> pd.DataFrame:
    required = {
        "date",
        "dow",
        "is_weekend",
        "iso_year",
        "iso_week",
        "is_payday",
        "festival",
        "festival_ramp",
        "is_holiday",
        "monsoon",
        "is_operating",
    }
    _assert_required(calendar, required, "calendar")
    if calendar["date"].duplicated().any():
        raise Task1FeatureBlockerError("calendar.date must be unique.")
    out = df.merge(calendar[list(required)], on="date", how="left", validate="many_to_one")
    if out["dow"].isna().any():
        raise Task1FeatureBlockerError("Calendar join missing required dates.")
    ramp = pd.to_numeric(out["festival_ramp"], errors="raise")
    if ((ramp < 0) | (ramp > 1)).any():
        raise Task1FeatureBlockerError("festival_ramp must be in [0,1].")
    return out


def add_optional_context_features(
    df: pd.DataFrame,
    *,
    road_conditions: pd.DataFrame | None,
    traffic_speed: pd.DataFrame | None,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, str]]:
    out = df.copy(deep=True)
    status = {"road": "DISABLED", "traffic": "DISABLED"}
    opt = config.get("optional_context", {})

    if bool(opt.get("road_enabled")):
        if road_conditions is None:
            raise Task1FeatureBlockerError("Road context enabled but road_conditions table missing.")
        keys = opt.get("road_join_keys", ["date", "district"])
        _assert_required(out, set(keys), "road join left")
        _assert_required(road_conditions, set(keys) | {"disruption_index"}, "road_conditions")
        if road_conditions.duplicated(subset=keys).any():
            raise Task1FeatureBlockerError("road_conditions join key duplicated.")
        out = out.merge(
            road_conditions[keys + ["disruption_index"]],
            how="left",
            on=keys,
            validate="many_to_one",
        )
        status["road"] = "READY"

    if bool(opt.get("traffic_enabled")):
        if traffic_speed is None:
            raise Task1FeatureBlockerError("Traffic context enabled but traffic_speed table missing.")
        traffic_keys = opt.get("traffic_join_keys", ["district", "dow", "monsoon", "planned_arrival_hour"])
        ref_hour_col = opt.get("traffic_hour_column", "hour")
        left_keys = [k for k in traffic_keys if k != "planned_arrival_hour"] + ["planned_arrival_hour"]
        right_keys = [k for k in traffic_keys if k != "planned_arrival_hour"] + [ref_hour_col]
        _assert_required(out, set(left_keys), "traffic join left")
        _assert_required(traffic_speed, set(right_keys) | {"speed_index"}, "traffic_speed")
        if traffic_speed.duplicated(subset=right_keys).any():
            raise Task1FeatureBlockerError("traffic_speed join key duplicated.")
        out = out.merge(
            traffic_speed[right_keys + ["speed_index"]],
            how="left",
            left_on=left_keys,
            right_on=right_keys,
            validate="many_to_one",
        )
        if ref_hour_col != "planned_arrival_hour":
            out = out.drop(columns=[ref_hour_col])
        status["traffic"] = "READY"

    return out, status


def add_service_allowance_feature(df: pd.DataFrame, service_allowance: pd.DataFrame) -> pd.DataFrame:
    _assert_required(service_allowance, {"brand", "dock_type", "service_allowance_min"}, "service_allowance")
    if service_allowance.duplicated(subset=["brand", "dock_type"]).any():
        raise Task1FeatureBlockerError("service_allowance (brand,dock_type) must be unique.")
    out = df.merge(
        service_allowance[["brand", "dock_type", "service_allowance_min"]],
        on=["brand", "dock_type"],
        how="left",
        validate="many_to_one",
    )
    if out["service_allowance_min"].isna().any():
        raise Task1FeatureBlockerError("Missing service_allowance_min after brand+dock_type join.")
    return out


def add_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(deep=True)
    units = pd.to_numeric(out["order_units"], errors="coerce")
    weight = pd.to_numeric(out["order_weight_kg"], errors="coerce")
    volume = pd.to_numeric(out["order_volume_m3"], errors="coerce")

    out["weight_per_unit_kg"] = np.where(units > 0, weight / units, np.nan)
    out["volume_per_unit_m3"] = np.where(units > 0, volume / units, np.nan)
    out["cargo_density_kg_per_m3"] = np.where(volume > 0, weight / volume, np.nan)
    for col in ("weight_per_unit_kg", "volume_per_unit_m3", "cargo_density_kg_per_m3"):
        vals = pd.to_numeric(out[col], errors="coerce").to_numpy(dtype=float)
        if np.isinf(vals).any():
            raise Task1FeatureBlockerError(f"Infinite value detected in ratio feature {col}.")
    return out


def add_route_aggregate_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(deep=True)
    group = out.groupby("route_id", dropna=False)
    out["route_total_units"] = group["order_units"].transform("sum")
    out["route_total_weight_kg"] = group["order_weight_kg"].transform("sum")
    out["route_total_volume_m3"] = group["order_volume_m3"].transform("sum")
    out["route_total_distance_km"] = group["leg_distance_km"].transform("sum")
    out["route_total_planned_travel_min"] = group["planned_travel_duration_min_feature"].transform("sum")
    out["route_total_service_allowance_min"] = group["service_allowance_min"].transform("sum")
    out["route_stop_count"] = group["delivery_id"].transform("count").astype(int)
    return out


def add_vehicle_utilization_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(deep=True)
    weight_cap = pd.to_numeric(out["weight_cap_kg"], errors="coerce")
    volume_cap = pd.to_numeric(out["volume_cap_m3"], errors="coerce")
    if (weight_cap <= 0).any() or (volume_cap <= 0).any():
        raise Task1FeatureBlockerError("Vehicle capacities must be strictly positive.")
    out["route_weight_utilization"] = out["route_total_weight_kg"] / weight_cap
    out["route_volume_utilization"] = out["route_total_volume_m3"] / volume_cap
    out["route_max_utilization"] = out[["route_weight_utilization", "route_volume_utilization"]].max(axis=1)
    return out


def add_cumulative_prior_planned_context(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(deep=True)
    out = out.sort_values(["route_id", "seq_in_route"], kind="stable").copy(deep=True)
    g = out.groupby("route_id", sort=False)
    out["prior_stop_count"] = g.cumcount().astype(int)
    for src, dst in [
        ("order_units", "prior_planned_units"),
        ("order_weight_kg", "prior_planned_weight_kg"),
        ("order_volume_m3", "prior_planned_volume_m3"),
        ("leg_distance_km", "prior_leg_distance_km"),
        ("planned_travel_duration_min_feature", "prior_planned_travel_min"),
        ("service_allowance_min", "prior_service_allowance_min"),
    ]:
        out[dst] = g[src].cumsum() - out[src]
    return out.sort_index(kind="stable")


def _default_feature_allow_list(df: pd.DataFrame) -> list[str]:
    blocked = {
        "delivery_id",
        "service_minutes",
        "late_flag",
        "service_start_dt",
        "actual_depart_time",
        "actual_travel_duration_min",
        "arrival_time",
        "leave_outlet_time",
        "route_id",
        "vehicle_id",
        "mall_window",
        "planned_arrival_time",
        "planned_depart_time",
        "window_open_time",
        "window_close_time",
        "resolved_planned_arrival_dt",
        "resolved_planned_depart_dt",
        "resolved_window_open_dt",
        "resolved_window_close_dt",
    }
    return [c for c in df.columns if c not in blocked]


def audit_feature_leakage(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    registry: pd.DataFrame,
) -> dict[str, Any]:
    # Layer 1: direct forbidden names
    forbidden_in_train = sorted(set(X_train.columns) & FORBIDDEN_DIRECT_TASK1_FEATURES)
    forbidden_in_test = sorted(set(X_test.columns) & FORBIDDEN_DIRECT_TASK1_FEATURES)
    if forbidden_in_train or forbidden_in_test:
        raise Task1FeatureBlockerError(
            f"Forbidden direct feature(s) in final matrices. train={forbidden_in_train}, test={forbidden_in_test}"
        )

    # Layer 2: source lineage (registry source_columns should not include forbidden actuals)
    bad_lineage: list[str] = []
    for _, row in registry.iterrows():
        if row["status"] == "DISABLED":
            continue
        cols = row["source_columns"]
        cols_set = set(cols if isinstance(cols, list) else [cols])
        if cols_set & TASK1_FORBIDDEN_SOURCE_COLUMNS:
            bad_lineage.append(str(row["feature_name"]))
    if bad_lineage:
        raise Task1FeatureBlockerError(
            "Enabled feature has forbidden lineage: " + ", ".join(sorted(bad_lineage))
        )

    # Layer 3 & 6: train/test parity and deterministic ordering
    if list(X_train.columns) != list(X_test.columns):
        raise Task1FeatureBlockerError("Train/test feature columns must match exactly in name/order.")

    # Layer 5: explicit target separation
    target_alias = {"service_minutes", "late_flag"}
    if target_alias & set(X_train.columns):
        raise Task1FeatureBlockerError("Target fields leaked into X_train.")

    return {
        "forbidden_direct_count": len(forbidden_in_train) + len(forbidden_in_test),
        "lineage_violations": sorted(bad_lineage),
        "train_test_parity": True,
    }


def build_task1_feature_tables(
    *,
    orders_train: pd.DataFrame,
    orders_test: pd.DataFrame,
    route_legs_train: pd.DataFrame,
    route_legs_test: pd.DataFrame,
    outlets: pd.DataFrame,
    vehicles: pd.DataFrame,
    district_travel: pd.DataFrame,
    service_allowance: pd.DataFrame,
    calendar: pd.DataFrame,
    labels_train: pd.DataFrame,
    config: dict[str, Any],
    road_conditions: pd.DataFrame | None = None,
    traffic_speed: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Canonical Phase 06 feature-builder for Task 1 train/test matrices."""
    _assert_required(labels_train, {"delivery_id", "service_minutes", "late_flag"}, "labels_train")

    # Feature engineering for training must be aligned to the canonical labeled population
    # from Phase 04, avoiding unlabeled/non-run rows that do not belong in Task 1 training.
    label_ids = labels_train[["delivery_id"]].drop_duplicates().copy(deep=True)
    if label_ids["delivery_id"].duplicated().any():
        raise Task1FeatureBlockerError("labels_train delivery_id must be unique.")
    orders_train = label_ids.merge(
        orders_train,
        on="delivery_id",
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    missing_mask = orders_train["_merge"] != "both"
    if missing_mask.any():
        missing_count = int(missing_mask.sum())
        raise Task1FeatureBlockerError(
            f"Training orders are missing for canonical label population (count={missing_count})."
        )
    orders_train = orders_train.drop(columns=["_merge"])

    def _run_pipeline(base_orders: pd.DataFrame, route_legs: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
        x = build_base_order_features(base_orders)
        x = add_outlet_reference_features(x, outlets)
        x = add_geography_features(x, district_travel)
        x = add_vehicle_features(x, vehicles)
        x = add_route_leg_plan_features(x, route_legs)
        x = add_route_position_features(x)
        x = add_planned_time_and_window_features(
            x, add_cyclical=bool(config.get("planned_time", {}).get("add_cyclical_features", True))
        )
        x = add_calendar_features(x, calendar)
        x, env_status = add_optional_context_features(
            x,
            road_conditions=road_conditions,
            traffic_speed=traffic_speed,
            config=config,
        )
        x = add_service_allowance_feature(x, service_allowance)
        x = add_ratio_features(x)
        x = add_route_aggregate_features(x)
        x = add_vehicle_utilization_features(x)
        x = add_cumulative_prior_planned_context(x)
        return x, env_status

    train_full, env_status_train = _run_pipeline(orders_train, route_legs_train)
    test_full, env_status_test = _run_pipeline(orders_test, route_legs_test)

    # DT-119 historical features
    hist_date_col = str(config.get("history", {}).get("date_column", "date"))
    hist_transformer = Task1HistoricalFeatureTransformer(date_col=hist_date_col)

    train_for_hist = train_full[["delivery_id", "outlet_id", "brand", "dock_type", hist_date_col]].copy(deep=True)
    hist_targets = labels_train[["delivery_id", "service_minutes", "late_flag"]].copy(deep=True)
    train_hist_join = train_for_hist.merge(hist_targets, on="delivery_id", how="left", validate="one_to_one")
    if train_hist_join["service_minutes"].isna().any() or train_hist_join["late_flag"].isna().any():
        raise Task1FeatureBlockerError("Training labels missing for historical feature construction.")

    hist_train_features = hist_transformer.fit_transform_training_chronological(
        train_hist_join[["outlet_id", "brand", "dock_type", hist_date_col]],
        train_hist_join["service_minutes"],
        train_hist_join["late_flag"],
    )
    hist_transformer.fit(
        train_hist_join[["outlet_id", "brand", "dock_type", hist_date_col]],
        train_hist_join["service_minutes"],
        train_hist_join["late_flag"],
    )
    hist_test_features = hist_transformer.transform(
        test_full[["outlet_id", "brand", "dock_type"]]
    )
    train_full = pd.concat([train_full, hist_train_features], axis=1)
    test_full = pd.concat([test_full, hist_test_features], axis=1)

    feature_allow_list = _default_feature_allow_list(train_full)
    X_train = train_full[feature_allow_list].copy(deep=True)
    X_test = test_full[feature_allow_list].copy(deep=True)

    registry = build_feature_registry(
        feature_allow_list, historical_columns=HISTORICAL_FEATURE_COLUMNS
    )
    validate_feature_registry(registry, expected_features=feature_allow_list)
    leakage = audit_feature_leakage(X_train, X_test, registry)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "trace_train": train_full[["delivery_id"]].copy(deep=True),
        "trace_test": test_full[["delivery_id"]].copy(deep=True),
        "feature_registry": registry,
        "leakage_audit": leakage,
        "env_status": {"train": env_status_train, "test": env_status_test},
    }
