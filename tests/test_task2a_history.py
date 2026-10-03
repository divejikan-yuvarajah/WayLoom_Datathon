"""Synthetic tests for the Phase 11 Task 2A demand-history contract."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.task2a.history import (
    HistoryValidationError,
    build_complete_weekly_panel,
    build_task2a_history,
    classify_missing_weeks,
    combine_weekly_targets,
    join_official_calendar,
    load_history_config,
    load_task2a_demand_sources,
    validate_calendar,
    validate_order_history_schema,
    validate_weekly_panel,
)


CONFIG = load_history_config(Path("configs/task2a_history.yaml"))


def _calendar(start: str = "2024-01-01", periods: int = 21) -> pd.DataFrame:
    dates = pd.date_range(start, periods=periods, freq="D")
    iso = dates.isocalendar()
    return pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "iso_year": iso.year.astype(int),
        "iso_week": iso.week.astype(int),
        "is_operating": 1,
    })


def _orders(rows: list[dict]) -> pd.DataFrame:
    defaults = {
        "dispatch_date": "2024-01-01",
        "dispatch_status": "attempted",
        "brand": "Fresh",
        "depot": "Peliyagoda",
        "temp_requirement": "ambient",
        "order_volume_m3": 1.0,
    }
    return pd.DataFrame([{**defaults, **row} for row in rows])


def _valid_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = _orders([
        {"delivery_id": "train-1", "order_date": "2024-01-01", "temp_requirement": "chilled", "order_volume_m3": 2.0},
        {"delivery_id": "train-2", "order_date": "2024-01-03", "dispatch_status": "deferred", "dispatch_date": "2024-01-09", "order_volume_m3": 3.0},
    ])
    test = _orders([
        {"delivery_id": "test-1", "order_date": "2024-01-10", "dispatch_status": "not_run", "dispatch_date": None, "order_volume_m3": 4.0, "brand": "Style"},
        {"delivery_id": "test-2", "order_date": "2024-01-14", "order_volume_m3": 1.5, "brand": "Tech"},
    ])
    return train, test, _calendar()


def test_build_history_retains_both_sources_statuses_and_requested_dates() -> None:
    train, test, calendar = _valid_sources()
    result = build_task2a_history(train, test, calendar, CONFIG)
    orders = result["demand_orders"]
    observed = result["weekly_observed"]
    assert len(orders) == 4
    assert set(orders["source_file"]) == {"deliveries_train", "task1_test_inputs"}
    assert result["diagnostics"]["dispatch_status_retention"] == {
        "attempted_order_count": 2, "deferred_order_count": 1, "not_run_order_count": 1,
    }
    deferred = observed.loc[(observed["brand"] == "Fresh") & (observed["iso_week"] == 1)]
    assert deferred["total_volume_m3"].iloc[0] == 5.0
    assert observed.loc[observed["brand"] == "Style", "chilled_volume_m3"].eq(0.0).all()
    assert observed.loc[observed["brand"] == "Tech", "chilled_volume_m3"].eq(0.0).all()
    assert result["diagnostics"]["weekly_reconciliation"]["volume_reconciled"] is True


@pytest.mark.parametrize("column", ["delivery_id", "order_date", "dispatch_date", "order_volume_m3"])
def test_required_order_schema_is_enforced(column: str) -> None:
    frame = _orders([{"delivery_id": "x", "order_date": "2024-01-01"}]).drop(columns=column)
    with pytest.raises(HistoryValidationError):
        validate_order_history_schema(frame, source_file="synthetic")


@pytest.mark.parametrize("mutator", [
    lambda x: x.assign(delivery_id=None),
    lambda x: x.assign(delivery_id=" "),
    lambda x: pd.concat([x, x], ignore_index=True),
])
def test_source_delivery_ids_cannot_be_null_blank_or_duplicate(mutator) -> None:
    frame = _orders([{"delivery_id": "x", "order_date": "2024-01-01"}])
    with pytest.raises(HistoryValidationError):
        validate_order_history_schema(mutator(frame), source_file="synthetic")


def test_duplicate_ids_across_sources_are_a_hard_blocker() -> None:
    train, test, calendar = _valid_sources()
    test.loc[0, "delivery_id"] = train.loc[0, "delivery_id"]
    with pytest.raises(HistoryValidationError, match="duplicate delivery_id"):
        build_task2a_history(train, test, calendar, CONFIG)


def test_not_run_with_blank_operational_fields_is_demand() -> None:
    train = _orders([{ "delivery_id": "n", "order_date": "2024-01-01", "dispatch_status": "not_run", "dispatch_date": None, "route_id": None, "vehicle_id": None, "order_volume_m3": 7.0 }])
    test = _orders([{ "delivery_id": "t", "order_date": "2024-01-14" }])
    result = build_task2a_history(train, test, _calendar(), CONFIG)
    assert result["weekly_observed"]["total_volume_m3"].sum() == 8.0


@pytest.mark.parametrize("value", [None, "not-a-date"])
def test_invalid_requested_date_is_rejected(value: object) -> None:
    frame = _orders([{ "delivery_id": "x", "order_date": value }])
    with pytest.raises(HistoryValidationError):
        validate_order_history_schema(frame, source_file="synthetic")


@pytest.mark.parametrize("value", [-0.1, np.nan, np.inf])
def test_invalid_volume_is_rejected(value: float) -> None:
    frame = _orders([{ "delivery_id": "x", "order_date": "2024-01-01", "order_volume_m3": value }])
    with pytest.raises(HistoryValidationError):
        validate_order_history_schema(frame, source_file="synthetic")


def test_calendar_is_left_joined_and_official_iso_fields_are_preserved() -> None:
    train, _, calendar = _valid_sources()
    joined = join_official_calendar(validate_order_history_schema(train, source_file="deliveries_train"), calendar)
    assert len(joined) == len(train)
    assert set(joined["iso_year"]) == {2024}
    assert set(joined["iso_week"]) == {1}


def test_calendar_duplicate_or_unmatched_date_is_a_blocker() -> None:
    calendar = _calendar()
    with pytest.raises(HistoryValidationError, match="unique"):
        validate_calendar(pd.concat([calendar, calendar.iloc[[0]]], ignore_index=True))
    orders = validate_order_history_schema(_orders([{ "delivery_id": "x", "order_date": "2025-01-01" }]), source_file="synthetic")
    with pytest.raises(HistoryValidationError, match="absent"):
        join_official_calendar(orders, calendar)


def test_iso_year_week_53_and_same_week_number_across_years_use_calendar() -> None:
    calendar = pd.DataFrame({
        "date": ["2020-12-31", "2021-01-01", "2021-01-04", "2022-01-03"],
        "iso_year": [2020, 2020, 2021, 2022], "iso_week": [53, 53, 1, 1], "is_operating": [1, 1, 1, 1],
    })
    train = _orders([{ "delivery_id": "a", "order_date": "2020-12-31" }, { "delivery_id": "b", "order_date": "2021-01-04" }])
    test = _orders([{ "delivery_id": "c", "order_date": "2022-01-03" }])
    # Test aggregation before the complete-panel step, which correctly requires complete calendar weeks.
    joined = join_official_calendar(pd.concat([
        validate_order_history_schema(train, source_file="deliveries_train"),
        validate_order_history_schema(test, source_file="task1_test_inputs"),
    ], ignore_index=True), calendar)
    weekly = combine_weekly_targets(
        __import__("src.task2a.history", fromlist=["aggregate_weekly_total_demand"]).aggregate_weekly_total_demand(joined),
        __import__("src.task2a.history", fromlist=["aggregate_weekly_chilled_demand"]).aggregate_weekly_chilled_demand(joined, CONFIG),
    )
    assert set(map(tuple, weekly[["iso_year", "iso_week"]].to_numpy())) == {(2020, 53), (2021, 1), (2022, 1)}


def test_fresh_chilled_and_ambient_are_separated_and_nonfresh_contradictions_block() -> None:
    train, test, calendar = _valid_sources()
    result = build_task2a_history(train, test, calendar, CONFIG)
    fresh = result["weekly_observed"].loc[result["weekly_observed"]["brand"].eq("Fresh")]
    assert fresh["chilled_volume_m3"].sum() == 2.0
    bad = test.copy()
    bad.loc[0, "temp_requirement"] = "chilled"
    with pytest.raises(HistoryValidationError, match="Style/Tech chilled"):
        build_task2a_history(train, bad, calendar, CONFIG)


def test_confirmed_zero_interior_week_is_filled_but_boundary_is_not() -> None:
    calendar = _calendar(periods=21)
    train = _orders([{ "delivery_id": "a", "order_date": "2024-01-01" }])
    test = _orders([{ "delivery_id": "b", "order_date": "2024-01-21" }])
    result = build_task2a_history(train, test, calendar, CONFIG)
    panel = result["weekly_panel"]
    middle = panel.loc[panel["iso_week"].eq(2)].iloc[0]
    assert middle["panel_status"] == "CONFIRMED_ZERO"
    assert middle["total_volume_m3"] == 0.0


def test_calendar_incomplete_and_unresolved_gaps_block_validation() -> None:
    calendar = _calendar(periods=21)
    calendar = calendar.drop(index=calendar.index[8]).reset_index(drop=True)  # interior week, not an order date
    train = _orders([{ "delivery_id": "a", "order_date": "2024-01-01" }])
    test = _orders([{ "delivery_id": "b", "order_date": "2024-01-21" }])
    with pytest.raises(HistoryValidationError, match="unresolved or incomplete"):
        build_task2a_history(train, test, calendar, CONFIG)

    panel = pd.DataFrame({
        "panel_status": ["UNRESOLVED_GAP"], "depot": ["P"], "brand": ["Fresh"], "iso_year": [2024], "iso_week": [1],
        "total_volume_m3": [np.nan], "chilled_volume_m3": [np.nan], "order_count": [np.nan],
    })
    assert classify_missing_weeks(panel.assign(_observed=False, week_start_date=pd.Timestamp("2024-01-01"), week_end_date=pd.Timestamp("2024-01-07"), coverage_start_date=pd.Timestamp("2024-01-01"), coverage_end_date=pd.Timestamp("2024-01-07"), calendar_days=np.nan, is_complete_calendar_week=False)).iloc[0]["panel_status"] == "UNRESOLVED_GAP"


def test_loader_uses_manifest_names_without_reading_routes(tmp_path: Path) -> None:
    train, test, calendar = _valid_sources()
    train.to_csv(tmp_path / "deliveries_train.csv", index=False)
    test.to_csv(tmp_path / "task1_test_inputs.csv", index=False)
    calendar.to_csv(tmp_path / "calendar.csv", index=False)
    manifest = {"artifacts": [{"filename": name} for name in ("deliveries_train.csv", "task1_test_inputs.csv", "calendar.csv")]}
    manifest_path = tmp_path / "manifest.yaml"
    import yaml
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    loaded = load_task2a_demand_sources(tmp_path, manifest_path, CONFIG)
    assert [len(frame) for frame in loaded] == [2, 2, 21]
