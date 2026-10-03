from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.task1.features import (
    Task1FeatureBlockerError,
    add_calendar_features,
    add_cumulative_prior_planned_context,
    add_optional_context_features,
    add_outlet_reference_features,
    add_planned_time_and_window_features,
    add_ratio_features,
    add_route_aggregate_features,
    add_route_leg_plan_features,
    add_route_position_features,
    add_service_allowance_feature,
    add_vehicle_utilization_features,
    build_base_order_features,
    build_task1_feature_tables,
)


def _base_orders_train() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "delivery_id": "D1",
                "outlet_id": "O1",
                "brand": "Fresh",
                "district": "District1",
                "depot": "Peliyagoda",
                "temp_requirement": "ambient",
                "order_units": 10,
                "order_weight_kg": 50.0,
                "order_volume_m3": 2.0,
                "route_id": "R1",
                "seq_in_route": 0,
                "vehicle_id": "V1",
                "vehicle_type": "van",
                "vehicle_temp": "ambient",
                "planned_arrival_time": "08:00",
                "window_open_time": "07:00",
                "window_close_time": "09:00",
            },
            {
                "delivery_id": "D2",
                "outlet_id": "O2",
                "brand": "Style",
                "district": "District2",
                "depot": "Kandy",
                "temp_requirement": "chilled",
                "order_units": 20,
                "order_weight_kg": 80.0,
                "order_volume_m3": 4.0,
                "route_id": "R1",
                "seq_in_route": 1,
                "vehicle_id": "V2",
                "vehicle_type": "truck",
                "vehicle_temp": "reefer",
                "planned_arrival_time": "10:00",
                "window_open_time": "09:00",
                "window_close_time": "12:00",
            },
        ]
    )


def _base_orders_test() -> pd.DataFrame:
    out = _base_orders_train().copy(deep=True)
    out["delivery_id"] = ["T1", "T2"]
    return out


def _route_legs() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "route_id": "R1",
                "seq": 0,
                "date": "2026-01-05",
                "planned_depart_time": "07:30",
                "planned_arrival_time": "08:00",
                "distance_km": 10.0,
                "planned_travel_duration_min": 30.0,
            },
            {
                "route_id": "R1",
                "seq": 1,
                "date": "2026-01-05",
                "planned_depart_time": "09:30",
                "planned_arrival_time": "10:00",
                "distance_km": 15.0,
                "planned_travel_duration_min": 30.0,
            },
        ]
    )


def _refs() -> dict[str, pd.DataFrame]:
    outlets = pd.DataFrame(
        [
            {
                "outlet_id": "O1",
                "brand": "Fresh",
                "district": "District1",
                "depot": "Peliyagoda",
                "dock_type": "rear_dock",
                "parking_constraint": "normal",
                "mall_window": "",
                "window_open_time": "07:00",
                "window_close_time": "09:00",
            },
            {
                "outlet_id": "O2",
                "brand": "Style",
                "district": "District2",
                "depot": "Kandy",
                "dock_type": "street",
                "parking_constraint": "van_only",
                "mall_window": "",
                "window_open_time": "09:00",
                "window_close_time": "12:00",
            },
        ]
    )
    vehicles = pd.DataFrame(
        [
            {
                "vehicle_id": "V1",
                "type": "van",
                "temp": "ambient",
                "depot": "Peliyagoda",
                "weight_cap_kg": 100.0,
                "volume_cap_m3": 10.0,
                "fuel_type": "diesel",
                "km_per_l": 8.0,
                "weekly_fuel_quota_l": 200.0,
            },
            {
                "vehicle_id": "V2",
                "type": "truck",
                "temp": "reefer",
                "depot": "Kandy",
                "weight_cap_kg": 200.0,
                "volume_cap_m3": 20.0,
                "fuel_type": "diesel",
                "km_per_l": 6.0,
                "weekly_fuel_quota_l": 300.0,
            },
        ]
    )
    district_travel = pd.DataFrame(
        [
            {
                "district": "District1",
                "depot": "Peliyagoda",
                "road_class": "urban",
                "depot_to_district_km": 12.0,
                "depot_to_district_freeflow_min": 25.0,
                "inter_stop_km": 1.0,
                "inter_stop_freeflow_min": 5.0,
            },
            {
                "district": "District2",
                "depot": "Kandy",
                "road_class": "hilly",
                "depot_to_district_km": 8.0,
                "depot_to_district_freeflow_min": 20.0,
                "inter_stop_km": 1.5,
                "inter_stop_freeflow_min": 6.0,
            },
        ]
    )
    service_allowance = pd.DataFrame(
        [
            {"brand": "Fresh", "dock_type": "rear_dock", "service_allowance_min": 15.0},
            {"brand": "Style", "dock_type": "street", "service_allowance_min": 20.0},
        ]
    )
    calendar = pd.DataFrame(
        [
            {
                "date": "2026-01-05",
                "dow": 0,
                "is_weekend": 0,
                "iso_year": 2026,
                "iso_week": 2,
                "is_payday": 0,
                "festival": "",
                "festival_ramp": 0.0,
                "is_holiday": 0,
                "monsoon": 0,
                "is_operating": 1,
            }
        ]
    )
    return {
        "outlets": outlets,
        "vehicles": vehicles,
        "district_travel": district_travel,
        "service_allowance": service_allowance,
        "calendar": calendar,
    }


def _labels() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"delivery_id": "D1", "service_minutes": 12.0, "late_flag": 0},
            {"delivery_id": "D2", "service_minutes": 25.0, "late_flag": 1},
        ]
    )


def test_dt091_base_one_row_per_delivery() -> None:
    base = build_base_order_features(_base_orders_train())
    assert base["delivery_id"].nunique() == len(base)


def test_dt092_outlet_reference_join_allows_many_deliveries_per_outlet() -> None:
    orders = _base_orders_train().copy(deep=True)
    # Make both deliveries map to the same outlet to assert many-to-one cardinality.
    orders.loc[1, "outlet_id"] = "O1"
    orders.loc[1, "brand"] = "Fresh"
    orders.loc[1, "district"] = "District1"
    orders.loc[1, "depot"] = "Peliyagoda"
    orders.loc[1, "window_open_time"] = "07:00"
    orders.loc[1, "window_close_time"] = "09:00"
    base = build_base_order_features(orders)
    joined = add_outlet_reference_features(base, _refs()["outlets"])
    assert len(joined) == len(base)
    assert joined["dock_type"].notna().all()


def test_dt091_duplicate_delivery_fails() -> None:
    dup = pd.concat([_base_orders_train(), _base_orders_train().iloc[[0]]], ignore_index=True)
    with pytest.raises(Task1FeatureBlockerError, match="delivery_id must be unique"):
        build_base_order_features(dup)


def test_dt096_to_dt104_route_time_features() -> None:
    base = build_base_order_features(_base_orders_train())
    joined = add_route_leg_plan_features(base, _route_legs())
    pos = add_route_position_features(joined)
    assert list(pos["route_seq"]) == [0, 1]
    assert list(pos["route_stop_count"]) == [2, 2]
    assert list(pos["route_seq_fraction"]) == [0.0, 1.0]
    assert list(pos["is_first_stop"]) == [1, 0]

    timef = add_planned_time_and_window_features(pos)
    assert "planned_arrival_minute_of_day" in timef.columns
    assert timef.loc[0, "planned_slack_to_close_min"] == 60.0
    assert timef.loc[0, "planned_early_wait_min"] == 0.0
    assert timef.loc[0, "leg_distance_km"] == 10.0
    assert timef.loc[0, "planned_travel_duration_min_feature"] == 30.0


def test_dt101_dt102_cross_midnight_slack_and_wait() -> None:
    df = pd.DataFrame(
        [
            {
                "delivery_id": "D1",
                "outlet_id": "O1",
                "brand": "Fresh",
                "district": "District1",
                "depot": "Peliyagoda",
                "temp_requirement": "ambient",
                "order_units": 1,
                "order_weight_kg": 1.0,
                "order_volume_m3": 1.0,
                "route_id": "R1",
                "seq_in_route": 0,
                "vehicle_id": "V1",
                "vehicle_type": "van",
                "vehicle_temp": "ambient",
                "planned_arrival_time": "00:30",
                "window_open_time": "23:00",
                "window_close_time": "01:00",
                "date": "2026-01-05",
                "planned_depart_time": "23:30",
                "distance_km": 10.0,
                "planned_travel_duration_min": 60.0,
            }
        ]
    )
    out = add_planned_time_and_window_features(df)
    assert out.loc[0, "planned_slack_to_close_min"] == 30.0
    assert out.loc[0, "planned_early_wait_min"] == 0.0


def test_dt113_to_dt117_ratios_totals_utilization_and_no_inf() -> None:
    base = build_base_order_features(_base_orders_train())
    route = add_route_leg_plan_features(base, _route_legs())
    route = add_route_position_features(route)
    route = add_planned_time_and_window_features(route)
    refs = _refs()
    geo = route.merge(refs["district_travel"], on=["district", "depot"], how="left")
    veh = route.merge(
        refs["vehicles"][["vehicle_id", "weight_cap_kg", "volume_cap_m3"]],
        on="vehicle_id",
        how="left",
    )
    with_allow = route.merge(
        refs["service_allowance"], on=["brand"], how="left", suffixes=("", "_x")
    )
    with_allow["service_allowance_min"] = [15.0, 20.0]
    ratios = add_ratio_features(with_allow)
    assert np.isfinite(ratios["weight_per_unit_kg"].to_numpy(dtype=float)).all()

    totals = add_route_aggregate_features(ratios)
    assert totals.loc[0, "route_total_units"] == 30
    util_base = totals.merge(
        refs["vehicles"][["vehicle_id", "weight_cap_kg", "volume_cap_m3"]],
        on="vehicle_id",
        how="left",
    )
    util = add_vehicle_utilization_features(util_base)
    assert (util["route_weight_utilization"] > 0).all()


def test_dt118_prior_cumulative_context() -> None:
    df = _base_orders_train().copy(deep=True)
    df["leg_distance_km"] = [10.0, 20.0]
    df["planned_travel_duration_min_feature"] = [30.0, 40.0]
    df["service_allowance_min"] = [15.0, 20.0]
    out = add_cumulative_prior_planned_context(df)
    assert out.loc[0, "prior_stop_count"] == 0
    assert out.loc[1, "prior_stop_count"] == 1
    assert out.loc[1, "prior_planned_units"] == 10
    assert out.loc[1, "prior_leg_distance_km"] == 10.0


def test_dt105_to_dt112_calendar_optional_allowance() -> None:
    base = build_base_order_features(_base_orders_train())
    route = add_route_leg_plan_features(base, _route_legs())
    route = add_route_position_features(route)
    route = add_planned_time_and_window_features(route)
    cal = add_calendar_features(route, _refs()["calendar"])
    assert set(["is_payday", "festival", "festival_ramp", "monsoon"]).issubset(set(cal.columns))

    cfg = {"optional_context": {"road_enabled": False, "traffic_enabled": False}}
    optional, status = add_optional_context_features(
        cal, road_conditions=None, traffic_speed=None, config=cfg
    )
    assert status["road"] == "DISABLED"
    assert status["traffic"] == "DISABLED"

    out = add_service_allowance_feature(
        optional.merge(_refs()["outlets"][["outlet_id", "dock_type"]], on="outlet_id", how="left"),
        _refs()["service_allowance"],
    )
    assert "service_allowance_min" in out.columns


def test_full_build_train_test_parity_and_forbidden_excluded() -> None:
    refs = _refs()
    built = build_task1_feature_tables(
        orders_train=_base_orders_train(),
        orders_test=_base_orders_test(),
        route_legs_train=_route_legs(),
        route_legs_test=_route_legs(),
        outlets=refs["outlets"],
        vehicles=refs["vehicles"],
        district_travel=refs["district_travel"],
        service_allowance=refs["service_allowance"],
        calendar=refs["calendar"],
        labels_train=_labels(),
        config={
            "planned_time": {"add_cyclical_features": True},
            "history": {"date_column": "date"},
            "optional_context": {"road_enabled": False, "traffic_enabled": False},
        },
    )
    X_train = built["X_train"]
    X_test = built["X_test"]
    assert list(X_train.columns) == list(X_test.columns)
    forbidden = {
        "actual_depart_time",
        "actual_travel_duration_min",
        "arrival_time",
        "leave_outlet_time",
        "service_start_dt",
        "service_minutes",
        "late_flag",
    }
    assert len(set(X_train.columns) & forbidden) == 0


def test_build_uses_only_labeled_training_population_for_features() -> None:
    refs = _refs()
    orders_train = _base_orders_train().copy(deep=True)
    # Extra unlabeled training row with unknown vehicle should be ignored
    # because Phase 06 train features are built for canonical labeled rows only.
    orders_train = pd.concat(
        [
            orders_train,
            pd.DataFrame(
                [
                    {
                        "delivery_id": "UNLABELED_BAD",
                        "outlet_id": "O1",
                        "brand": "Fresh",
                        "district": "District1",
                        "depot": "Peliyagoda",
                        "temp_requirement": "ambient",
                        "order_units": 1,
                        "order_weight_kg": 1.0,
                        "order_volume_m3": 0.1,
                        "route_id": "R1",
                        "seq_in_route": 0,
                        "vehicle_id": "UNKNOWN_VEHICLE",
                        "vehicle_type": "van",
                        "vehicle_temp": "ambient",
                        "planned_arrival_time": "08:00",
                        "window_open_time": "07:00",
                        "window_close_time": "09:00",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    built = build_task1_feature_tables(
        orders_train=orders_train,
        orders_test=_base_orders_test(),
        route_legs_train=_route_legs(),
        route_legs_test=_route_legs(),
        outlets=refs["outlets"],
        vehicles=refs["vehicles"],
        district_travel=refs["district_travel"],
        service_allowance=refs["service_allowance"],
        calendar=refs["calendar"],
        labels_train=_labels(),  # contains only D1, D2
        config={
            "planned_time": {"add_cyclical_features": True},
            "history": {"date_column": "date"},
            "optional_context": {"road_enabled": False, "traffic_enabled": False},
        },
    )
    assert built["trace_train"]["delivery_id"].tolist() == ["D1", "D2"]
    assert built["X_train"].shape[0] == 2
