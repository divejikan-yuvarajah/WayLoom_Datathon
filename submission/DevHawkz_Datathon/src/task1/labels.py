"""Task 1 training-population and eligibility helpers (Phase 04 Checkpoint A)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from pandas.errors import MergeError

DISPATCHED_STATUSES = {"attempted", "deferred"}
EXCLUDED_STATUS = "not_run"
ALLOWED_DISPATCH_STATUSES = DISPATCHED_STATUSES | {EXCLUDED_STATUS}

ELIGIBLE_DISPATCHED = "eligible_dispatched"
EXPECTED_EXCLUDED_NOT_RUN = "expected_excluded_not_run"
INVALID_DISPATCHED_MISSING_ASSIGNMENT = "invalid_dispatched_missing_assignment"
TASK1_FORBIDDEN_DIRECT_FEATURES = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
    "service_start_dt",
    "service_minutes",
    "late_flag",
}


@dataclass
class Task1EligibilityBlockerError(ValueError):
    """Raised when dispatched orders are missing route assignment keys."""

    message: str
    invalid_rows: pd.DataFrame

    def __str__(self) -> str:
        return self.message


class Task1JoinBlockerError(ValueError):
    """Raised when Task 1 dispatched-to-leg join cannot be executed safely."""


def assert_no_task1_direct_feature_leakage(feature_columns: list[str]) -> None:
    """Guard against direct prediction-time feature leakage for Task 1."""

    violating = sorted(set(feature_columns) & TASK1_FORBIDDEN_DIRECT_FEATURES)
    if violating:
        raise Task1JoinBlockerError(
            "Task 1 feature leakage detected: " + ", ".join(violating)
        )


def parse_clock(value: str) -> tuple[int, int]:
    """Parse strict HH:MM clock strings into hour/minute."""

    if value is None:
        raise Task1JoinBlockerError("Clock value is missing.")
    text = str(value).strip()
    parts = text.split(":")
    if len(parts) != 2 or len(parts[0]) != 2 or len(parts[1]) != 2:
        raise Task1JoinBlockerError(f"Invalid clock format: {value!r}. Expected HH:MM.")
    if not (parts[0].isdigit() and parts[1].isdigit()):
        raise Task1JoinBlockerError(f"Invalid clock format: {value!r}. Expected HH:MM.")

    hour = int(parts[0])
    minute = int(parts[1])
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise Task1JoinBlockerError(f"Invalid clock value: {value!r}. Expected 00:00-23:59.")
    return hour, minute


def combine_local_date_clock(
    date_value: object,
    clock_value: object,
    day_offset: int = 0,
) -> pd.Timestamp:
    """Combine local date + clock into timezone-naive local timestamp."""

    if pd.isna(date_value):
        raise Task1JoinBlockerError("Date value is missing.")
    if pd.isna(clock_value):
        raise Task1JoinBlockerError("Clock value is missing.")

    if isinstance(date_value, pd.Timestamp):
        base_date = date_value.date()
    elif isinstance(date_value, datetime):
        base_date = date_value.date()
    elif isinstance(date_value, date):
        base_date = date_value
    else:
        try:
            base_date = pd.to_datetime(date_value, errors="raise").date()
        except Exception as exc:
            raise Task1JoinBlockerError(
                f"Invalid date value: {date_value!r}."
            ) from exc

    hour, minute = parse_clock(str(clock_value))
    combined = datetime.combine(base_date, datetime.min.time()).replace(
        hour=hour, minute=minute
    ) + timedelta(days=int(day_offset))
    return pd.Timestamp(combined)


def _is_missing_assignment_value(series: pd.Series) -> pd.Series:
    if pd.api.types.is_string_dtype(series) or series.dtype == object:
        return series.isna() | series.astype("string").str.strip().eq("")
    return series.isna()


def _normalized_dispatch_status(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()


def _validate_dispatch_status_column(deliveries: pd.DataFrame) -> None:
    if "dispatch_status" not in deliveries.columns:
        raise ValueError("Missing required column: dispatch_status")

    normalized = _normalized_dispatch_status(deliveries["dispatch_status"])
    if normalized.isna().any():
        raise ValueError("dispatch_status contains missing values.")
    unknown_statuses = sorted(
        status for status in normalized.dropna().unique() if status not in ALLOWED_DISPATCH_STATUSES
    )
    if unknown_statuses:
        raise ValueError(
            "Unexpected dispatch_status values found: " + ", ".join(unknown_statuses)
        )


def select_dispatched_orders(deliveries: pd.DataFrame) -> pd.DataFrame:
    """Return attempted/deferred historical orders without mutating input."""

    _validate_dispatch_status_column(deliveries)
    dispatch_status = _normalized_dispatch_status(deliveries["dispatch_status"])
    dispatched_mask = dispatch_status.isin(DISPATCHED_STATUSES)
    dispatched = deliveries.loc[dispatched_mask].copy(deep=True)

    if dispatched.empty:
        raise ValueError(
            "No dispatched historical orders found. Expected at least one attempted/deferred row."
        )

    return dispatched


def classify_label_eligibility(deliveries: pd.DataFrame) -> pd.DataFrame:
    """Classify Task 1 label eligibility and fail on invalid dispatched rows."""

    _validate_dispatch_status_column(deliveries)
    required = {"route_id", "seq_in_route"}
    missing_required = sorted(required - set(deliveries.columns))
    if missing_required:
        raise ValueError("Missing required columns: " + ", ".join(missing_required))

    classified = deliveries.copy(deep=True)
    dispatch_status = _normalized_dispatch_status(classified["dispatch_status"])
    classified["dispatch_status"] = dispatch_status
    classified["task1_label_eligibility"] = EXPECTED_EXCLUDED_NOT_RUN

    dispatched_mask = dispatch_status.isin(DISPATCHED_STATUSES)
    missing_route = _is_missing_assignment_value(classified["route_id"])
    missing_seq = _is_missing_assignment_value(classified["seq_in_route"])
    invalid_dispatched_mask = dispatched_mask & (missing_route | missing_seq)
    eligible_dispatched_mask = dispatched_mask & ~invalid_dispatched_mask

    classified.loc[eligible_dispatched_mask, "task1_label_eligibility"] = ELIGIBLE_DISPATCHED
    classified.loc[
        invalid_dispatched_mask, "task1_label_eligibility"
    ] = INVALID_DISPATCHED_MISSING_ASSIGNMENT

    if invalid_dispatched_mask.any():
        invalid_rows = classified.loc[invalid_dispatched_mask].copy(deep=True)
        raise Task1EligibilityBlockerError(
            message=(
                "Dispatched rows are missing route assignment fields "
                "(route_id and/or seq_in_route)."
            ),
            invalid_rows=invalid_rows,
        )

    return classified


def join_orders_to_route_legs(
    dispatched_orders: pd.DataFrame,
    route_legs: pd.DataFrame,
) -> pd.DataFrame:
    """Left-join dispatched orders to route legs using the official composite key."""

    left_required = {"route_id", "seq_in_route"}
    right_required = {"route_id", "seq"}
    missing_left = sorted(left_required - set(dispatched_orders.columns))
    missing_right = sorted(right_required - set(route_legs.columns))
    if missing_left:
        raise Task1JoinBlockerError(
            "Dispatched orders missing required join columns: " + ", ".join(missing_left)
        )
    if missing_right:
        raise Task1JoinBlockerError(
            "Route legs missing required join columns: " + ", ".join(missing_right)
        )

    dispatched_with_trace = dispatched_orders.copy(deep=True)
    if "source_row_index" in dispatched_with_trace.columns:
        raise Task1JoinBlockerError(
            "Dispatched orders already include reserved trace column: source_row_index"
        )
    dispatched_with_trace["source_row_index"] = dispatched_orders.index

    try:
        joined = dispatched_with_trace.merge(
            route_legs.copy(deep=True),
            how="left",
            left_on=["route_id", "seq_in_route"],
            right_on=["route_id", "seq"],
            validate="one_to_one",
            indicator=True,
            suffixes=("_order", "_leg"),
            sort=False,
        )
    except MergeError as exc:
        raise Task1JoinBlockerError(
            "Official one-to-one join validation failed for (route_id, seq_in_route) -> (route_id, seq)."
        ) from exc
    return joined


def validate_task1_join_integrity(
    joined: pd.DataFrame,
    expected_dispatched_count: int,
) -> dict:
    """Validate DT-058 one-to-one join integrity requirements."""

    required_columns = {"delivery_id", "_merge"}
    missing_columns = sorted(required_columns - set(joined.columns))
    if missing_columns:
        raise Task1JoinBlockerError(
            "Joined table missing required columns: " + ", ".join(missing_columns)
        )

    violations: list[str] = []
    joined_row_count = int(len(joined))
    if joined_row_count != int(expected_dispatched_count):
        violations.append(
            "joined row count does not match dispatched row count "
            f"({joined_row_count} != {expected_dispatched_count})"
        )

    duplicate_delivery_count = int(joined["delivery_id"].duplicated(keep=False).sum())
    if duplicate_delivery_count > 0:
        violations.append("delivery_id is not unique after join")

    unmatched_count = int((joined["_merge"] != "both").sum())
    if unmatched_count > 0:
        violations.append("not all dispatched rows matched exactly one route leg")

    multiplied_rows_count = 0
    if "source_row_index" in joined.columns:
        multiplied_rows_count = int(joined["source_row_index"].duplicated(keep=False).sum())
        if multiplied_rows_count > 0:
            violations.append("source row traceability shows row multiplication")

    if violations:
        raise Task1JoinBlockerError("DT-058 join integrity failed: " + "; ".join(violations))

    return {
        "joined_row_count": joined_row_count,
        "expected_dispatched_count": int(expected_dispatched_count),
        "duplicate_delivery_count": duplicate_delivery_count,
        "unmatched_count": unmatched_count,
        "multiplied_rows_count": multiplied_rows_count,
    }


def detect_unmatched_dispatched_and_orphan_legs(
    joined: pd.DataFrame,
    route_legs: pd.DataFrame,
) -> dict:
    """DT-059 checks for unmatched dispatched rows and orphan route legs."""

    joined_required = {"_merge", "route_id", "seq"}
    route_required = {"route_id", "seq"}
    missing_joined = sorted(joined_required - set(joined.columns))
    missing_route = sorted(route_required - set(route_legs.columns))
    if missing_joined:
        raise Task1JoinBlockerError(
            "Joined table missing required DT-059 columns: " + ", ".join(missing_joined)
        )
    if missing_route:
        raise Task1JoinBlockerError(
            "Route legs table missing required DT-059 columns: " + ", ".join(missing_route)
        )

    unmatched_dispatched_count = int((joined["_merge"] == "left_only").sum())
    if unmatched_dispatched_count > 0:
        raise Task1JoinBlockerError(
            f"DT-059 unmatched dispatched orders detected (count={unmatched_dispatched_count})."
        )

    matched = joined.loc[joined["_merge"] == "both", ["route_id", "seq"]].dropna().copy(deep=True)
    matched["route_id"] = matched["route_id"].astype("string").str.strip()
    try:
        matched["seq"] = pd.to_numeric(matched["seq"], errors="raise")
    except Exception as exc:
        raise Task1JoinBlockerError("DT-059 matched leg seq contains non-numeric values.") from exc
    matched_leg_keys = set(zip(matched["route_id"], matched["seq"]))

    route_keys_df = route_legs.loc[
        route_legs["route_id"].notna() & route_legs["seq"].notna(), ["route_id", "seq"]
    ].copy(deep=True)
    route_keys_df["route_id"] = route_keys_df["route_id"].astype("string").str.strip()
    try:
        route_keys_df["seq"] = pd.to_numeric(route_keys_df["seq"], errors="raise")
    except Exception as exc:
        raise Task1JoinBlockerError("DT-059 route leg seq contains non-numeric values.") from exc
    route_leg_keys = set(zip(route_keys_df["route_id"], route_keys_df["seq"]))
    orphan_route_leg_count = len(route_leg_keys - matched_leg_keys)

    return {
        "unmatched_dispatched_count": unmatched_dispatched_count,
        "orphan_route_leg_count": orphan_route_leg_count,
    }


def detect_duplicate_join_matches(
    dispatched_orders: pd.DataFrame,
    route_legs: pd.DataFrame,
    joined: pd.DataFrame,
) -> dict:
    """DT-060 re-validates duplicate/ambiguous join conditions."""

    dispatched_required = {"route_id", "seq_in_route", "delivery_id"}
    route_required = {"route_id", "seq"}
    joined_required = {"delivery_id"}
    missing_dispatched = sorted(dispatched_required - set(dispatched_orders.columns))
    missing_route = sorted(route_required - set(route_legs.columns))
    missing_joined = sorted(joined_required - set(joined.columns))
    if missing_dispatched:
        raise Task1JoinBlockerError(
            "Dispatched table missing required DT-060 columns: " + ", ".join(missing_dispatched)
        )
    if missing_route:
        raise Task1JoinBlockerError(
            "Route legs table missing required DT-060 columns: " + ", ".join(missing_route)
        )
    if missing_joined:
        raise Task1JoinBlockerError(
            "Joined table missing required DT-060 columns: " + ", ".join(missing_joined)
        )

    duplicate_dispatched_key_count = int(
        dispatched_orders.duplicated(subset=["route_id", "seq_in_route"], keep=False).sum()
    )
    duplicate_route_key_count = int(
        route_legs.duplicated(subset=["route_id", "seq"], keep=False).sum()
    )
    duplicate_delivery_count = int(joined["delivery_id"].duplicated(keep=False).sum())
    multiplied_rows_count = 0
    if "source_row_index" in joined.columns:
        multiplied_rows_count = int(joined["source_row_index"].duplicated(keep=False).sum())

    violations: list[str] = []
    if duplicate_dispatched_key_count > 0:
        violations.append("duplicate dispatched (route_id, seq_in_route) keys detected")
    if duplicate_route_key_count > 0:
        violations.append("duplicate route leg (route_id, seq) keys detected")
    if duplicate_delivery_count > 0:
        violations.append("duplicate delivery_id detected after join")
    if multiplied_rows_count > 0:
        violations.append("row multiplication detected via source_row_index")

    if violations:
        raise Task1JoinBlockerError("DT-060 duplicate-join checks failed: " + "; ".join(violations))

    return {
        "duplicate_dispatched_key_count": duplicate_dispatched_key_count,
        "duplicate_route_key_count": duplicate_route_key_count,
        "duplicate_delivery_count": duplicate_delivery_count,
        "multiplied_rows_count": multiplied_rows_count,
    }


def validate_outlet_destination_consistency(joined: pd.DataFrame) -> dict:
    """DT-061 validates outlet_id == to_outlet for matched rows."""

    required_columns = {"_merge", "outlet_id", "to_outlet"}
    missing_columns = sorted(required_columns - set(joined.columns))
    if missing_columns:
        raise Task1JoinBlockerError(
            "Joined table missing required DT-061 columns: " + ", ".join(missing_columns)
        )

    matched = joined.loc[joined["_merge"] == "both", ["outlet_id", "to_outlet"]].copy(deep=True)
    if matched.empty:
        return {"matched_rows": 0, "destination_mismatch_count": 0}

    left = matched["outlet_id"].astype("string").str.strip()
    right = matched["to_outlet"].astype("string").str.strip()
    destination_mismatch_count = int((left != right).sum())

    if destination_mismatch_count > 0:
        raise Task1JoinBlockerError(
            f"DT-061 outlet destination mismatch detected (count={destination_mismatch_count})."
        )

    return {
        "matched_rows": int(len(matched)),
        "destination_mismatch_count": destination_mismatch_count,
    }


def resolve_local_datetime_columns(
    df: pd.DataFrame,
    *,
    date_column: str,
    clock_columns: list[str],
    required_clock_columns: list[str] | None = None,
) -> pd.DataFrame:
    """DT-062: Resolve HH:MM columns into timezone-naive local datetime columns."""

    required_clock_columns = required_clock_columns or []
    missing_required_columns = sorted(
        {date_column, *clock_columns} - set(df.columns)
    )
    if missing_required_columns:
        raise Task1JoinBlockerError(
            "Missing required DT-062 columns: " + ", ".join(missing_required_columns)
        )

    resolved = df.copy(deep=True)
    for clock_col in clock_columns:
        resolved_col = f"{clock_col}_dt"
        values: list[pd.Timestamp | pd.NaTType] = []
        for _, row in resolved.iterrows():
            clock_value = row[clock_col]
            if pd.isna(clock_value) or str(clock_value).strip() == "":
                if clock_col in required_clock_columns:
                    raise Task1JoinBlockerError(
                        f"DT-062 required clock column {clock_col} contains blank values."
                    )
                values.append(pd.NaT)
                continue
            values.append(
                combine_local_date_clock(
                    date_value=row[date_column],
                    clock_value=clock_value,
                    day_offset=0,
                )
            )
        resolved[resolved_col] = values

    return resolved


def resolve_route_actual_datetimes(
    route_legs: pd.DataFrame,
    *,
    date_column: str = "date",
    route_id_column: str = "route_id",
    seq_column: str = "seq",
    depart_column: str = "actual_depart_time",
    arrival_column: str = "arrival_time",
    leave_column: str = "leave_outlet_time",
    travel_duration_column: str = "actual_travel_duration_min",
    travel_tolerance_min: float = 5.0,
) -> pd.DataFrame:
    """DT-063: Resolve route actual chronology with deterministic midnight rollover."""

    required = {
        date_column,
        route_id_column,
        seq_column,
        depart_column,
        arrival_column,
        leave_column,
        travel_duration_column,
    }
    missing = sorted(required - set(route_legs.columns))
    if missing:
        raise Task1JoinBlockerError(
            "Missing required DT-063 route columns: " + ", ".join(missing)
        )
    if route_legs[route_id_column].isna().any():
        raise Task1JoinBlockerError("DT-063 route_id contains missing values.")
    if route_legs[seq_column].isna().any():
        raise Task1JoinBlockerError("DT-063 seq contains missing values.")

    resolved = route_legs.copy(deep=True)
    sequence_sort_column = "__task1_seq_sort"
    if sequence_sort_column in resolved.columns:
        raise Task1JoinBlockerError(
            f"DT-063 reserved helper column already exists: {sequence_sort_column}"
        )
    try:
        resolved[sequence_sort_column] = pd.to_numeric(
            resolved[seq_column], errors="raise"
        )
    except Exception as exc:
        raise Task1JoinBlockerError(
            "DT-063 seq must be numeric for route chronology ordering."
        ) from exc
    resolved = resolved.sort_values(
        [route_id_column, sequence_sort_column], kind="stable"
    ).copy(deep=True)

    depart_values: list[pd.Timestamp] = []
    arrival_values: list[pd.Timestamp] = []
    leave_values: list[pd.Timestamp] = []
    arrival_day_offsets: list[int] = []

    for _, group in resolved.groupby(route_id_column, sort=False):
        previous_event: pd.Timestamp | None = None
        current_day_offset = 0

        for _, row in group.iterrows():
            try:
                expected_travel = float(row[travel_duration_column])
            except Exception as exc:
                raise Task1JoinBlockerError(
                    "DT-063 actual_travel_duration_min must be numeric for chronology validation."
                ) from exc
            if pd.isna(expected_travel):
                raise Task1JoinBlockerError(
                    "DT-063 actual_travel_duration_min is missing for chronology validation."
                )

            row_results: dict[str, pd.Timestamp] = {}
            event_offsets: dict[str, int] = {}
            for event_col in (depart_column, arrival_column, leave_column):
                if pd.isna(row[event_col]) or str(row[event_col]).strip() == "":
                    raise Task1JoinBlockerError(
                        f"DT-063 required event time {event_col} is blank."
                    )

                candidate = combine_local_date_clock(
                    date_value=row[date_column],
                    clock_value=row[event_col],
                    day_offset=current_day_offset,
                )
                while previous_event is not None and candidate < previous_event:
                    current_day_offset += 1
                    candidate = combine_local_date_clock(
                        date_value=row[date_column],
                        clock_value=row[event_col],
                        day_offset=current_day_offset,
                    )

                row_results[event_col] = candidate
                event_offsets[event_col] = current_day_offset
                previous_event = candidate

            observed_travel = (
                row_results[arrival_column] - row_results[depart_column]
            ).total_seconds() / 60.0
            if observed_travel < 0:
                raise Task1JoinBlockerError(
                    "DT-063 resolved travel duration is negative after rollover."
                )
            if abs(observed_travel - expected_travel) > float(travel_tolerance_min):
                raise Task1JoinBlockerError(
                    "DT-063 chronology conflicts with actual_travel_duration_min beyond tolerance."
                )

            depart_values.append(row_results[depart_column])
            arrival_values.append(row_results[arrival_column])
            leave_values.append(row_results[leave_column])
            arrival_day_offsets.append(event_offsets[arrival_column])

    resolved[f"{depart_column}_dt"] = depart_values
    resolved[f"{arrival_column}_dt"] = arrival_values
    resolved[f"{leave_column}_dt"] = leave_values
    resolved["arrival_day_offset"] = arrival_day_offsets
    resolved = resolved.drop(columns=[sequence_sort_column])
    return resolved.sort_index(kind="stable")


def resolve_delivery_window_datetimes(
    joined_or_resolved: pd.DataFrame,
    *,
    route_date_column: str = "date",
    window_open_column: str = "window_open_time",
    window_close_column: str = "window_close_time",
    arrival_day_offset_column: str = "arrival_day_offset",
    arrival_datetime_column: str = "arrival_time_dt",
) -> pd.DataFrame:
    """DT-063: Anchor outlet windows to resolved service day and handle cross-midnight windows."""

    required = {
        route_date_column,
        window_open_column,
        window_close_column,
        arrival_day_offset_column,
        arrival_datetime_column,
    }
    missing = sorted(required - set(joined_or_resolved.columns))
    if missing:
        raise Task1JoinBlockerError(
            "Missing required DT-063 window columns: " + ", ".join(missing)
        )

    resolved = joined_or_resolved.copy(deep=True)
    open_values: list[pd.Timestamp] = []
    close_values: list[pd.Timestamp] = []
    for _, row in resolved.iterrows():
        if pd.isna(row[arrival_day_offset_column]):
            raise Task1JoinBlockerError("DT-063 arrival_day_offset is missing.")
        arrival_day_offset = int(row[arrival_day_offset_column])

        if pd.isna(row[window_open_column]) or str(row[window_open_column]).strip() == "":
            raise Task1JoinBlockerError("DT-063 window_open_time is required and cannot be blank.")
        if pd.isna(row[window_close_column]) or str(row[window_close_column]).strip() == "":
            raise Task1JoinBlockerError("DT-063 window_close_time is required and cannot be blank.")

        window_open_dt = combine_local_date_clock(
            date_value=row[route_date_column],
            clock_value=row[window_open_column],
            day_offset=arrival_day_offset,
        )
        window_close_dt = combine_local_date_clock(
            date_value=row[route_date_column],
            clock_value=row[window_close_column],
            day_offset=arrival_day_offset,
        )

        open_hour, open_min = parse_clock(str(row[window_open_column]))
        close_hour, close_min = parse_clock(str(row[window_close_column]))
        if (close_hour, close_min) < (open_hour, open_min):
            window_close_dt = window_close_dt + timedelta(days=1)
            # An arrival after midnight can belong to the window that opened
            # on the preceding route date (for example 23:00–01:00). Anchor
            # the valid cross-midnight interval around the resolved arrival,
            # rather than blindly shifting its opening to the arrival date.
            if row[arrival_datetime_column] < window_open_dt:
                window_open_dt = window_open_dt - timedelta(days=1)
                window_close_dt = window_close_dt - timedelta(days=1)

        open_values.append(window_open_dt)
        close_values.append(window_close_dt)

    resolved["window_open_dt"] = open_values
    resolved["window_close_dt"] = close_values
    return resolved


def compute_service_start(df: pd.DataFrame) -> pd.DataFrame:
    """DT-064: service_start_dt = max(arrival_dt, window_open_dt)."""

    required = {"arrival_time_dt", "window_open_dt"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1JoinBlockerError(
            "Missing required DT-064 columns: " + ", ".join(missing)
        )

    resolved = df.copy(deep=True)
    if resolved["arrival_time_dt"].isna().any():
        raise Task1JoinBlockerError("DT-064 arrival_time_dt contains missing values.")
    if resolved["window_open_dt"].isna().any():
        raise Task1JoinBlockerError("DT-064 window_open_dt contains missing values.")

    resolved["service_start_dt"] = resolved[["arrival_time_dt", "window_open_dt"]].max(axis=1)
    return resolved


def compute_service_minutes(df: pd.DataFrame) -> pd.DataFrame:
    """DT-065: service_minutes = (leave_outlet_dt - service_start_dt) / 60."""

    required = {"leave_outlet_time_dt", "service_start_dt"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1JoinBlockerError(
            "Missing required DT-065 columns: " + ", ".join(missing)
        )

    resolved = df.copy(deep=True)
    if resolved["leave_outlet_time_dt"].isna().any():
        raise Task1JoinBlockerError("DT-065 leave_outlet_time_dt contains missing values.")
    if resolved["service_start_dt"].isna().any():
        raise Task1JoinBlockerError("DT-065 service_start_dt contains missing values.")

    service_minutes = (
        resolved["leave_outlet_time_dt"] - resolved["service_start_dt"]
    ).dt.total_seconds() / 60.0
    if service_minutes.isna().any():
        raise Task1JoinBlockerError("DT-065 service_minutes contains missing values.")
    if ~np.isfinite(service_minutes.to_numpy(dtype=float)).all():
        raise Task1JoinBlockerError("DT-065 service_minutes contains non-finite values.")
    if (service_minutes < 0).any():
        raise Task1JoinBlockerError("DT-065 service_minutes cannot be negative.")

    resolved["service_minutes"] = service_minutes.astype(float)
    return resolved


def compute_late_flag(df: pd.DataFrame) -> pd.DataFrame:
    """DT-066: late_flag = 1 only when arrival_time_dt > window_close_dt."""

    required = {"arrival_time_dt", "window_close_dt"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1JoinBlockerError(
            "Missing required DT-066 columns: " + ", ".join(missing)
        )

    resolved = df.copy(deep=True)
    if resolved["arrival_time_dt"].isna().any():
        raise Task1JoinBlockerError("DT-066 arrival_time_dt contains missing values.")
    if resolved["window_close_dt"].isna().any():
        raise Task1JoinBlockerError("DT-066 window_close_dt contains missing values.")

    resolved["late_flag"] = (resolved["arrival_time_dt"] > resolved["window_close_dt"]).astype("int8")
    return resolved


def validate_task1_labels(df: pd.DataFrame) -> dict:
    """DT-067: Validate Task 1 label ranges and invariants."""

    required = {
        "delivery_id",
        "arrival_time_dt",
        "window_open_dt",
        "window_close_dt",
        "service_start_dt",
        "leave_outlet_time_dt",
        "service_minutes",
        "late_flag",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1JoinBlockerError("Missing required DT-067 columns: " + ", ".join(missing))

    if df["delivery_id"].duplicated().any():
        raise Task1JoinBlockerError("DT-067 delivery_id must be unique.")

    datetime_columns = [
        "arrival_time_dt",
        "window_open_dt",
        "window_close_dt",
        "service_start_dt",
        "leave_outlet_time_dt",
    ]
    for column in datetime_columns:
        if df[column].isna().any():
            raise Task1JoinBlockerError(f"DT-067 {column} contains missing values.")

    if df["service_minutes"].isna().any():
        raise Task1JoinBlockerError("DT-067 service_minutes contains missing values.")
    if ~np.isfinite(df["service_minutes"].to_numpy(dtype=float)).all():
        raise Task1JoinBlockerError("DT-067 service_minutes contains non-finite values.")
    if (df["service_minutes"] < 0).any():
        raise Task1JoinBlockerError("DT-067 service_minutes cannot be negative.")

    if df["late_flag"].isna().any():
        raise Task1JoinBlockerError("DT-067 late_flag contains missing values.")
    if not set(df["late_flag"].unique()).issubset({0, 1}):
        raise Task1JoinBlockerError("DT-067 late_flag must contain only 0/1 values.")

    if (df["service_start_dt"] < df["arrival_time_dt"]).any():
        raise Task1JoinBlockerError("DT-067 service_start_dt must be >= arrival_time_dt.")
    if (df["service_start_dt"] < df["window_open_dt"]).any():
        raise Task1JoinBlockerError("DT-067 service_start_dt must be >= window_open_dt.")
    if (df["leave_outlet_time_dt"] < df["service_start_dt"]).any():
        raise Task1JoinBlockerError("DT-067 leave_outlet_time_dt must be >= service_start_dt.")

    early_wait_mask = df["arrival_time_dt"] < df["window_open_dt"]
    if early_wait_mask.any():
        if not (df.loc[early_wait_mask, "service_start_dt"] == df.loc[early_wait_mask, "window_open_dt"]).all():
            raise Task1JoinBlockerError(
                "DT-067 early arrivals must start service at window_open_dt."
            )

    inside_or_late_mask = df["arrival_time_dt"] >= df["window_open_dt"]
    if inside_or_late_mask.any():
        if not (df.loc[inside_or_late_mask, "service_start_dt"] == df.loc[inside_or_late_mask, "arrival_time_dt"]).all():
            raise Task1JoinBlockerError(
                "DT-067 arrivals at/after opening must start service at arrival_time_dt."
            )

    before_close_mask = df["arrival_time_dt"] <= df["window_close_dt"]
    if before_close_mask.any():
        if (df.loc[before_close_mask, "late_flag"] != 0).any():
            raise Task1JoinBlockerError(
                "DT-067 arrivals at or before close must have late_flag = 0."
            )

    after_close_mask = df["arrival_time_dt"] > df["window_close_dt"]
    if after_close_mask.any():
        if (df.loc[after_close_mask, "late_flag"] != 1).any():
            raise Task1JoinBlockerError(
                "DT-067 arrivals after close must have late_flag = 1."
            )

    matched_dispatched_count = int((df["_merge"] == "both").sum()) if "_merge" in df.columns else len(df)
    if len(df) != matched_dispatched_count:
        raise Task1JoinBlockerError("DT-067 row count must equal matched dispatched count.")

    return {
        "row_count": int(len(df)),
        "matched_dispatched_count": matched_dispatched_count,
        "service_minutes_min": float(df["service_minutes"].min()),
        "service_minutes_max": float(df["service_minutes"].max()),
        "late_count": int((df["late_flag"] == 1).sum()),
        "on_time_count": int((df["late_flag"] == 0).sum()),
    }


def inspect_long_service_candidates(df: pd.DataFrame, threshold_minutes: float) -> pd.DataFrame:
    """DT-068: Identify suspicious long service durations without modifying data."""

    required = {"delivery_id", "service_minutes"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1JoinBlockerError("Missing required DT-068 columns: " + ", ".join(missing))
    if threshold_minutes < 0:
        raise Task1JoinBlockerError("DT-068 threshold_minutes must be non-negative.")

    candidate_mask = df["service_minutes"] >= float(threshold_minutes)
    candidates = df.loc[candidate_mask].copy(deep=True)
    return candidates


def summarize_task1_targets(df: pd.DataFrame) -> dict:
    """DT-069: Summarize Task 1 service-minute and lateness distributions."""

    required = {"service_minutes", "late_flag"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1JoinBlockerError("Missing required DT-069 columns: " + ", ".join(missing))

    service = pd.to_numeric(df["service_minutes"], errors="coerce")
    late = pd.to_numeric(df["late_flag"], errors="coerce")
    if service.isna().any():
        raise Task1JoinBlockerError("DT-069 service_minutes contains non-numeric values.")
    if late.isna().any():
        raise Task1JoinBlockerError("DT-069 late_flag contains non-numeric values.")

    late_unique = sorted(set(int(v) for v in late.dropna().unique()))
    if not set(late_unique).issubset({0, 1}):
        raise Task1JoinBlockerError("DT-069 late_flag must contain only 0/1 values.")

    service_summary = {
        "count": int(service.count()),
        "mean": float(service.mean()),
        "median": float(service.median()),
        "std": float(service.std(ddof=1)) if service.count() > 1 else 0.0,
        "min": float(service.min()),
        "max": float(service.max()),
        "p50": float(service.quantile(0.50)),
        "p75": float(service.quantile(0.75)),
        "p90": float(service.quantile(0.90)),
        "p95": float(service.quantile(0.95)),
        "p99": float(service.quantile(0.99)),
    }
    late_count = int((late == 1).sum())
    not_late_count = int((late == 0).sum())
    total = late_count + not_late_count

    return {
        "service_minutes": service_summary,
        "late_flag": {
            "late_count": late_count,
            "not_late_count": not_late_count,
            "late_rate": float(late_count / total) if total else 0.0,
        },
    }


def build_task1_training_labels(
    deliveries_train: pd.DataFrame,
    route_legs_train: pd.DataFrame,
    *,
    travel_tolerance_min: float = 5.0,
    long_service_threshold_minutes: float = 120.0,
) -> tuple[pd.DataFrame, dict]:
    """DT-071 canonical Task 1 training-label construction pipeline."""

    # Validate eligibility contract and isolate dispatched training population.
    _ = classify_label_eligibility(deliveries_train)
    dispatched_orders = select_dispatched_orders(deliveries_train)

    joined = join_orders_to_route_legs(dispatched_orders, route_legs_train)
    join_integrity = validate_task1_join_integrity(
        joined, expected_dispatched_count=len(dispatched_orders)
    )
    unmatched_and_orphans = detect_unmatched_dispatched_and_orphan_legs(
        joined, route_legs_train
    )
    duplicate_checks = detect_duplicate_join_matches(
        dispatched_orders, route_legs_train, joined
    )
    destination_checks = validate_outlet_destination_consistency(joined)

    resolved_actual = resolve_route_actual_datetimes(
        joined,
        travel_tolerance_min=travel_tolerance_min,
    )
    resolved_windows = resolve_delivery_window_datetimes(resolved_actual)
    with_service_start = compute_service_start(resolved_windows)
    with_service_minutes = compute_service_minutes(with_service_start)
    labeled = compute_late_flag(with_service_minutes)
    label_validation = validate_task1_labels(labeled)

    long_service_candidates = inspect_long_service_candidates(
        labeled, threshold_minutes=long_service_threshold_minutes
    )
    target_summary = summarize_task1_targets(labeled)

    diagnostics = {
        "join_integrity": join_integrity,
        "unmatched_and_orphans": unmatched_and_orphans,
        "duplicate_checks": duplicate_checks,
        "destination_checks": destination_checks,
        "label_validation": label_validation,
        "long_service_candidate_count": int(len(long_service_candidates)),
        "target_summary": target_summary,
    }
    return labeled.copy(deep=True), diagnostics
