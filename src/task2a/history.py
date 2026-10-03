"""Canonical, leakage-safe Task 2A requested-demand history construction.

This module deliberately operates on order records only.  It does not use
route legs, Task 1 predictions, or dispatch outcomes to decide demand.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yaml

from src.common.data_inventory import load_manifest


class HistoryValidationError(ValueError):
    """Raised when a Task 2A demand-history contract is violated."""


REQUIRED_ORDER_COLUMNS = (
    "delivery_id",
    "order_date",
    "dispatch_date",
    "dispatch_status",
    "brand",
    "depot",
    "temp_requirement",
    "order_volume_m3",
)
REQUIRED_CALENDAR_COLUMNS = ("date", "iso_year", "iso_week", "is_operating")
STATUS_COLUMNS = ("attempted", "deferred", "not_run")
WEEKLY_KEYS = ["depot", "brand", "iso_year", "iso_week"]


def load_history_config(path: Path | str) -> dict[str, Any]:
    """Load the explicit Phase 11 policy configuration."""
    with Path(path).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise HistoryValidationError("Task 2A history configuration must be a mapping.")
    return value


def _require_columns(frame: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise HistoryValidationError(f"{label} missing required columns: {', '.join(missing)}")


def _parse_dates(series: pd.Series, label: str) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce").dt.normalize()
    if parsed.isna().any():
        raise HistoryValidationError(f"{label} contains missing or invalid dates.")
    return parsed


def validate_order_history_schema(
    orders: pd.DataFrame,
    *,
    source_file: str,
    required_statuses: Iterable[str] = STATUS_COLUMNS,
) -> pd.DataFrame:
    """Validate a source at one-order-per-row grain without route filtering."""
    _require_columns(orders, REQUIRED_ORDER_COLUMNS, source_file)
    result = orders.copy(deep=True)
    delivery_ids = result["delivery_id"]
    if delivery_ids.isna().any() or delivery_ids.astype("string").str.strip().eq("").any():
        raise HistoryValidationError(f"{source_file} has null or blank delivery_id values.")
    if delivery_ids.duplicated().any():
        raise HistoryValidationError(f"{source_file} has duplicate delivery_id values.")
    result["order_date"] = _parse_dates(result["order_date"], f"{source_file}.order_date")
    statuses = result["dispatch_status"].astype("string").str.strip()
    if statuses.isna().any() or statuses.eq("").any():
        raise HistoryValidationError(f"{source_file} has missing dispatch_status values.")
    allowed = set(required_statuses)
    invalid = ~statuses.isin(allowed)
    if invalid.any():
        raise HistoryValidationError(f"{source_file} contains unsupported dispatch_status values.")
    result["dispatch_status"] = statuses
    volumes = pd.to_numeric(result["order_volume_m3"], errors="coerce")
    if volumes.isna().any() or not np.isfinite(volumes).all() or (volumes < 0).any():
        raise HistoryValidationError(f"{source_file} has missing, non-finite, or negative order_volume_m3.")
    result["order_volume_m3"] = volumes.astype(float)
    result["source_file"] = source_file.removesuffix(".csv")
    return result


def _find_unique_artifact(raw_root: Path, filename: str) -> Path:
    matches = list(Path(raw_root).rglob(filename))
    if not matches:
        raise FileNotFoundError(f"Required artifact not found: {filename}")
    if len(matches) != 1:
        raise HistoryValidationError(f"Required artifact is duplicated: {filename}")
    return matches[0]


def load_task2a_demand_sources(
    raw_root: Path | str, manifest_path: Path | str, config: dict[str, Any]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load only the two official demand sources and calendar through manifest names."""
    manifest = load_manifest(Path(manifest_path))
    manifest_names = {item["filename"] for item in manifest["artifacts"]}
    names = config["official_sources"]
    requested = (names["deliveries_train"], names["task1_test_inputs"], names["calendar"])
    if not set(requested).issubset(manifest_names):
        raise HistoryValidationError("Phase 11 source names are absent from the dataset manifest.")
    train = pd.read_csv(_find_unique_artifact(Path(raw_root), names["deliveries_train"]))
    task1_test = pd.read_csv(_find_unique_artifact(Path(raw_root), names["task1_test_inputs"]))
    calendar = pd.read_csv(_find_unique_artifact(Path(raw_root), names["calendar"]))
    statuses = config["required_dispatch_statuses"]
    return (
        validate_order_history_schema(train, source_file="deliveries_train", required_statuses=statuses),
        validate_order_history_schema(task1_test, source_file="task1_test_inputs", required_statuses=statuses),
        validate_calendar(calendar),
    )


def append_demand_sources(deliveries_train: pd.DataFrame, task1_test_inputs: pd.DataFrame) -> pd.DataFrame:
    """Append source orders row-wise; intentionally never deduplicates records."""
    combined = pd.concat([deliveries_train, task1_test_inputs], axis=0, ignore_index=True, sort=False)
    if len(combined) != len(deliveries_train) + len(task1_test_inputs):
        raise HistoryValidationError("Source append did not preserve the exact source row count.")
    return combined


def validate_combined_delivery_ids(combined: pd.DataFrame) -> dict[str, int]:
    """Prove the appended demand universe contains each order exactly once."""
    _require_columns(combined, ["delivery_id", "source_file"], "combined demand history")
    ids = combined["delivery_id"]
    if ids.isna().any() or ids.astype("string").str.strip().eq("").any():
        raise HistoryValidationError("Combined demand history has null or blank delivery_id values.")
    if ids.duplicated().any():
        raise HistoryValidationError("Combined demand history has duplicate delivery_id values; no auto-dedupe is allowed.")
    return {"combined_row_count": int(len(combined)), "unique_delivery_id_count": int(ids.nunique())}


def validate_dispatch_status_retention(combined: pd.DataFrame, required_statuses: Iterable[str]) -> dict[str, int]:
    """Confirm all official statuses are retained rather than filtered operationally."""
    _require_columns(combined, ["dispatch_status"], "combined demand history")
    statuses = combined["dispatch_status"].astype("string").str.strip()
    allowed = set(required_statuses)
    if (~statuses.isin(allowed)).any():
        raise HistoryValidationError("Combined demand history contains an unsupported dispatch status.")
    return {f"{status}_order_count": int(statuses.eq(status).sum()) for status in required_statuses}


def validate_calendar(calendar: pd.DataFrame) -> pd.DataFrame:
    """Validate the official calendar mapping used as the only ISO source of truth."""
    _require_columns(calendar, REQUIRED_CALENDAR_COLUMNS, "calendar")
    result = calendar.copy(deep=True)
    result["date"] = _parse_dates(result["date"], "calendar.date")
    if result["date"].duplicated().any():
        raise HistoryValidationError("calendar.date must be unique for a many-to-one demand join.")
    for column in ("iso_year", "iso_week", "is_operating"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if result[column].isna().any() or not np.isfinite(result[column]).all():
            raise HistoryValidationError(f"calendar.{column} must be finite numeric values.")
    if ((result["iso_week"] < 1) | (result["iso_week"] > 53)).any():
        raise HistoryValidationError("calendar.iso_week must be between 1 and 53.")
    if not result["is_operating"].isin([0, 1]).all():
        raise HistoryValidationError("calendar.is_operating must contain only 0 or 1.")
    result[["iso_year", "iso_week", "is_operating"]] = result[["iso_year", "iso_week", "is_operating"]].astype(int)
    return result


def assign_requested_demand_date(combined: pd.DataFrame) -> pd.DataFrame:
    """Normalize and retain order_date as the sole Task 2A demand date."""
    result = combined.copy(deep=True)
    result["order_date"] = _parse_dates(result["order_date"], "combined.order_date")
    return result


def join_official_calendar(combined: pd.DataFrame, calendar: pd.DataFrame) -> pd.DataFrame:
    """Left join order_date to official calendar date, rejecting any hidden loss/multiplication."""
    orders = assign_requested_demand_date(combined)
    cal = validate_calendar(calendar)
    joined = orders.merge(
        cal,
        how="left",
        left_on="order_date",
        right_on="date",
        validate="many_to_one",
        indicator=True,
        suffixes=("", "_calendar"),
    )
    if len(joined) != len(orders):
        raise HistoryValidationError("Calendar join changed the order row count.")
    if joined["_merge"].ne("both").any():
        raise HistoryValidationError("One or more requested order_date values are absent from calendar.")
    return joined.drop(columns=["_merge"])


def aggregate_weekly_total_demand(joined: pd.DataFrame) -> pd.DataFrame:
    """Aggregate requested volume and status counts at official weekly series grain."""
    _require_columns(joined, WEEKLY_KEYS + ["order_volume_m3", "dispatch_status"], "calendar-joined orders")
    grouped = joined.groupby(WEEKLY_KEYS, as_index=False, sort=True)
    totals = grouped.agg(total_volume_m3=("order_volume_m3", "sum"), order_count=("delivery_id", "size"))
    for status in STATUS_COLUMNS:
        values = joined.assign(_status=joined["dispatch_status"].eq(status).astype(int)).groupby(WEEKLY_KEYS, as_index=False)["_status"].sum()
        totals = totals.merge(values.rename(columns={"_status": f"{status}_order_count"}), on=WEEKLY_KEYS, validate="one_to_one")
    return totals


def aggregate_weekly_chilled_demand(joined: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Calculate Fresh chilled demand and enforce exact zero semantics for Style/Tech."""
    chilled = config["chilled"]
    _require_columns(joined, WEEKLY_KEYS + ["brand", "temp_requirement", "order_volume_m3"], "calendar-joined orders")
    strict = bool(chilled.get("strict_nonfresh_chilled_input_check", True))
    nonfresh = set(chilled["nonfresh_brands"])
    contradiction = joined["brand"].isin(nonfresh) & joined["temp_requirement"].astype("string").str.strip().eq(chilled["chilled_temp_value"])
    if strict and contradiction.any():
        raise HistoryValidationError("Style/Tech chilled source records violate the strict Phase 11 policy.")
    fresh_chilled = joined.loc[
        joined["brand"].eq(chilled["eligible_brand"])
        & joined["temp_requirement"].astype("string").str.strip().eq(chilled["chilled_temp_value"])
    ]
    result = fresh_chilled.groupby(WEEKLY_KEYS, as_index=False, sort=True).agg(
        chilled_volume_m3=("order_volume_m3", "sum"), chilled_order_count=("delivery_id", "size")
    )
    return result


def combine_weekly_targets(totals: pd.DataFrame, chilled: pd.DataFrame) -> pd.DataFrame:
    """Attach chilled targets to observed weekly totals with exact non-Fresh zeros."""
    result = totals.merge(chilled, on=WEEKLY_KEYS, how="left", validate="one_to_one")
    result["chilled_volume_m3"] = result["chilled_volume_m3"].fillna(0.0).astype(float)
    result["chilled_order_count"] = result["chilled_order_count"].fillna(0).astype(int)
    nonfresh = result["brand"].isin(["Style", "Tech"])
    result.loc[nonfresh, "chilled_volume_m3"] = 0.0
    result.loc[nonfresh, "chilled_order_count"] = 0
    if (result["chilled_volume_m3"] > result["total_volume_m3"]).any() or (result["chilled_volume_m3"] < 0).any():
        raise HistoryValidationError("Fresh chilled volume must be within [0, total_volume_m3].")
    if not result.loc[result["brand"].eq("Style"), "chilled_volume_m3"].eq(0.0).all():
        raise HistoryValidationError("Style chilled volume must be exactly zero.")
    if not result.loc[result["brand"].eq("Tech"), "chilled_volume_m3"].eq(0.0).all():
        raise HistoryValidationError("Tech chilled volume must be exactly zero.")
    return result.sort_values(WEEKLY_KEYS, kind="stable").reset_index(drop=True)


def build_calendar_week_spine(calendar: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    """Build the official calendar week spine limited to the observed source coverage interval."""
    cal = validate_calendar(calendar)
    start, end = orders["order_date"].min(), orders["order_date"].max()
    scoped = cal.loc[cal["date"].between(start, end)].copy()
    if scoped.empty:
        raise HistoryValidationError("No calendar weeks overlap the requested-order date coverage.")
    spine = scoped.groupby(["iso_year", "iso_week"], as_index=False, sort=True).agg(
        week_start_date=("date", "min"),
        week_end_date=("date", "max"),
        calendar_days=("date", "size"),
        operating_days=("is_operating", "sum"),
    )
    spine["is_complete_calendar_week"] = spine["calendar_days"].eq(7)
    spine["coverage_start_date"] = start
    spine["coverage_end_date"] = end
    return spine


def classify_missing_weeks(panel: pd.DataFrame) -> pd.DataFrame:
    """Classify gaps explicitly; only complete interior weeks are confirmed zeros."""
    result = panel.copy(deep=True)
    observed = result["_observed"].fillna(False).astype(bool)
    boundary = (result["week_start_date"] < result["coverage_start_date"]) | (result["week_end_date"] > result["coverage_end_date"])
    result["panel_status"] = np.select(
        [observed, ~observed & boundary, ~observed & result["calendar_days"].isna(), ~observed & ~result["is_complete_calendar_week"]],
        ["OBSERVED_DEMAND", "BOUNDARY_PARTIAL", "UNRESOLVED_GAP", "CALENDAR_INCOMPLETE"],
        default="CONFIRMED_ZERO",
    )
    zero = result["panel_status"].eq("CONFIRMED_ZERO")
    numeric_columns = ["total_volume_m3", "chilled_volume_m3", "order_count", "chilled_order_count", *[f"{s}_order_count" for s in STATUS_COLUMNS]]
    result.loc[zero, numeric_columns] = 0.0
    result["is_confirmed_zero_demand"] = zero
    return result


def build_complete_weekly_panel(observed: pd.DataFrame, calendar: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    """Cross each observed series with the official weekly spine and audit absent weeks."""
    if observed.empty:
        raise HistoryValidationError("Cannot build a weekly panel from an empty demand history.")
    spine = build_calendar_week_spine(calendar, orders)
    series = observed[["depot", "brand"]].drop_duplicates().sort_values(["depot", "brand"], kind="stable")
    series["_join"] = 1
    spine["_join"] = 1
    panel = series.merge(spine, on="_join", how="inner").drop(columns="_join")
    panel = panel.merge(observed.assign(_observed=True), on=WEEKLY_KEYS, how="left", validate="one_to_one")
    panel = classify_missing_weeks(panel)
    if panel.duplicated(WEEKLY_KEYS).any():
        raise HistoryValidationError("Complete weekly panel has duplicate series/week keys.")
    return panel.sort_values(WEEKLY_KEYS, kind="stable").reset_index(drop=True)


def validate_weekly_panel(orders: pd.DataFrame, observed: pd.DataFrame, panel: pd.DataFrame) -> dict[str, Any]:
    """Enforce Phase 11 volume/count/chilled/gap reconciliation without rounding."""
    if panel.duplicated(WEEKLY_KEYS).any():
        raise HistoryValidationError("Weekly panel contains duplicate keys.")
    blockers = panel["panel_status"].isin(["UNRESOLVED_GAP", "CALENDAR_INCOMPLETE"])
    if blockers.any():
        raise HistoryValidationError("Weekly panel contains unresolved or incomplete calendar gaps.")
    for frame, label in ((observed, "observed"), (panel, "panel")):
        numeric = frame[["total_volume_m3", "chilled_volume_m3"]].to_numpy(dtype=float)
        if not np.isfinite(numeric).all() or (numeric < 0).any():
            raise HistoryValidationError(f"{label} weekly targets must be finite and nonnegative.")
        if (frame["chilled_volume_m3"] > frame["total_volume_m3"]).any():
            raise HistoryValidationError(f"{label} chilled volume exceeds total volume.")
        if not frame.loc[frame["brand"].eq("Style"), "chilled_volume_m3"].eq(0.0).all():
            raise HistoryValidationError("Style chilled volume must be exactly zero.")
        if not frame.loc[frame["brand"].eq("Tech"), "chilled_volume_m3"].eq(0.0).all():
            raise HistoryValidationError("Tech chilled volume must be exactly zero.")
    source_volume = float(orders["order_volume_m3"].sum())
    weekly_volume = float(observed["total_volume_m3"].sum())
    if not np.isclose(source_volume, weekly_volume, rtol=1e-12, atol=1e-12):
        raise HistoryValidationError("Order-level and weekly total volumes do not reconcile.")
    if len(orders) != int(observed["order_count"].sum()):
        raise HistoryValidationError("Order-level and weekly order counts do not reconcile.")
    return {
        "order_count_reconciled": True,
        "volume_reconciled": True,
        "unresolved_gap_count": int(panel["panel_status"].eq("UNRESOLVED_GAP").sum()),
        "calendar_incomplete_count": int(panel["panel_status"].eq("CALENDAR_INCOMPLETE").sum()),
        "boundary_partial_count": int(panel["panel_status"].eq("BOUNDARY_PARTIAL").sum()),
    }


def build_task2a_history(
    deliveries_train: pd.DataFrame,
    task1_test_inputs: pd.DataFrame,
    calendar: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Build all Phase 11 in-memory artifacts from synthetic or operator-local frames."""
    statuses = config["required_dispatch_statuses"]
    train = validate_order_history_schema(deliveries_train, source_file="deliveries_train", required_statuses=statuses)
    test = validate_order_history_schema(task1_test_inputs, source_file="task1_test_inputs", required_statuses=statuses)
    combined = append_demand_sources(train, test)
    uniqueness = validate_combined_delivery_ids(combined)
    retention = validate_dispatch_status_retention(combined, statuses)
    joined = join_official_calendar(combined, calendar)
    totals = aggregate_weekly_total_demand(joined)
    chilled = aggregate_weekly_chilled_demand(joined, config)
    observed = combine_weekly_targets(totals, chilled)
    panel = build_complete_weekly_panel(observed, calendar, joined)
    reconciliation = validate_weekly_panel(joined, observed, panel)
    return {
        "demand_orders": joined.sort_values(["order_date", "delivery_id"], kind="stable").reset_index(drop=True),
        "weekly_observed": observed,
        "weekly_panel": panel.drop(columns="_observed"),
        "diagnostics": {"source_reconciliation": uniqueness, "dispatch_status_retention": retention, "weekly_reconciliation": reconciliation},
    }
