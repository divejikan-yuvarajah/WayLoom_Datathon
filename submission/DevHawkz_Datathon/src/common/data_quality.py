"""WayLoom Datathon - Phase 03 data-quality audit utilities.

This module implements privacy-safe audit checks only.
It never prints, samples, or serializes raw competition rows to console output.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
import yaml

from src.common.data_inventory import discover_dataset_files, load_manifest


PASS = "PASS"
EXPECTED = "EXPECTED"
WARNING = "WARNING"
BLOCKER = "BLOCKER"
NOT_APPLICABLE = "NOT_APPLICABLE"

VALID_STATUSES = {PASS, EXPECTED, WARNING, BLOCKER, NOT_APPLICABLE}

MISSING_TOKENS = {"", " ", "na", "n/a", "null", "none"}
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
TIME_RANGE_PATTERN = re.compile(
    r"^(?:[01]\d|2[0-3]):[0-5]\d-(?:[01]\d|2[0-3]):[0-5]\d$"
)


def make_result(
    rule_id: str,
    status: str,
    table: str,
    message: str,
    severity: Optional[str] = None,
    affected_count: int = 0,
    details: Optional[dict] = None,
) -> dict:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid audit status: {status}")
    return {
        "rule_id": rule_id,
        "status": status,
        "severity": severity or status,
        "table": table,
        "affected_count": int(affected_count),
        "message": message,
        "details": details or {},
    }


def load_rules(rules_path: Path) -> dict:
    with Path(rules_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def is_missing_value(value: Any) -> bool:
    if pd.isna(value):
        return True
    if isinstance(value, str):
        return value.strip().lower() in MISSING_TOKENS
    return False


def nonmissing_mask(series: pd.Series) -> pd.Series:
    return ~series.apply(is_missing_value)


def count_missing(series: pd.Series) -> int:
    return int(series.apply(is_missing_value).astype(int).sum())


def _safe_string_set(series: pd.Series) -> set[str]:
    mask = nonmissing_mask(series)
    return {str(v) for v in series[mask].tolist()}


def _column_present(df: pd.DataFrame, column: str) -> bool:
    return column in df.columns


def _series_numeric(series: pd.Series) -> pd.Series:
    cleaned = series.where(nonmissing_mask(series), pd.NA)
    return pd.to_numeric(cleaned, errors="coerce")


def _parse_dates(series: pd.Series) -> pd.Series:
    cleaned = series.where(nonmissing_mask(series), pd.NA)
    return pd.to_datetime(cleaned, format="%Y-%m-%d", errors="coerce")


def _is_integer_like(series: pd.Series) -> pd.Series:
    numeric = _series_numeric(series)
    return numeric.notna() & (numeric % 1 == 0)


def _allowed_values_for_column(column: str, table: str, rules: dict) -> Optional[set]:
    enums = rules.get("official_enums", {})
    if column == "brand":
        return set(enums.get("brand", []))
    if column == "dispatch_status":
        return set(enums.get("dispatch_status", []))
    if column == "temp_requirement":
        return set(enums.get("temp_requirement", []))
    if column == "depot":
        return set(enums.get("depot", []))
    if column == "dock_type":
        return set(enums.get("dock_type", []))
    if column == "parking_constraint":
        return set(enums.get("parking_constraint", []))
    if column in {"vehicle_type", "type"}:
        return set(enums.get("vehicle_type", []))
    if column in {"vehicle_temp", "temp"}:
        return set(enums.get("vehicle_temp", []))
    if column == "road_class":
        return set(enums.get("road_class", []))
    if column == "scenario":
        return set(enums.get("task2b_scenario", []))
    if column == "status":
        return set(enums.get("task2b_vehicle_status", []))
    return None


def _clock_time_valid(value: Any) -> bool:
    return isinstance(value, str) and bool(TIME_PATTERN.fullmatch(value))


def _time_range_valid(value: Any) -> bool:
    return isinstance(value, str) and bool(TIME_RANGE_PATTERN.fullmatch(value))


def load_tables_for_audit(raw_root: Path, manifest_path: Path) -> tuple[dict, dict]:
    """Discover and load audit tables locally.

    Only intended for local human-run CLI execution, not for agent data inspection.
    """
    manifest = load_manifest(manifest_path)
    discovered = discover_dataset_files(raw_root, manifest)
    tables: Dict[str, pd.DataFrame] = {}

    for filename, info in discovered.get("found_artifacts", {}).items():
        if info.get("format") != "csv":
            continue
        tables[filename] = pd.read_csv(
            info["path"],
            encoding="utf-8-sig",
            low_memory=False,
        )

    return discovered, tables


def audit_missing_values(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    row_keys_by_table = {
        "deliveries_train.csv": ["delivery_id"],
        "task1_test_inputs.csv": ["delivery_id"],
        "route_legs_train.csv": ["leg_id"],
        "route_legs_test.csv": ["leg_id"],
        "task2a_test_inputs.csv": ["row_id"],
        "task2b_peak_day_scenarios.csv": ["scenario", "order_ref"],
        "task2b_peak_day_fleet.csv": ["scenario", "vehicle_id"],
        "outlets.csv": ["outlet_id"],
        "vehicles.csv": ["vehicle_id"],
        "calendar.csv": ["date"],
    }

    for table_name, df in tables.items():
        for column in row_keys_by_table.get(table_name, []):
            if column not in df.columns:
                continue
            missing_count = count_missing(df[column])
            status = BLOCKER if missing_count else PASS
            results.append(
                make_result(
                    rule_id=f"DT-036.REQUIRED_IDENTIFIER.{column}",
                    status=status,
                    table=table_name,
                    message=f"{column} missing count: {missing_count}",
                    affected_count=missing_count,
                )
            )

    for table_name in ("deliveries_train.csv", "task1_test_inputs.csv"):
        if table_name not in tables:
            continue
        df = tables[table_name]
        if "dispatch_status" not in df.columns:
            continue

        not_run = df["dispatch_status"] == "not_run"
        for column in ("dispatch_date", "route_id"):
            if column in df.columns:
                expected_count = count_missing(df.loc[not_run, column])
                results.append(
                    make_result(
                        rule_id=f"DT-036.EXPECTED_NOT_RUN_BLANK.{column}",
                        status=EXPECTED if expected_count else PASS,
                        table=table_name,
                        message=f"{column} may be blank for not_run rows",
                        affected_count=expected_count,
                    )
                )

        if "mall_window" in df.columns:
            missing_count = count_missing(df["mall_window"])
            results.append(
                make_result(
                    rule_id="DT-036.MALL_WINDOW_CONDITIONAL",
                    status=EXPECTED if missing_count else PASS,
                    table=table_name,
                    message="mall_window may be blank outside mall outlets",
                    affected_count=missing_count,
                )
            )

        dispatched = df["dispatch_status"].isin(["attempted", "deferred"])
        blocker_cols = ("route_id", "seq_in_route")
        warning_cols = (
            "dispatch_date",
            "vehicle_id",
            "vehicle_type",
            "vehicle_temp",
            "planned_arrival_time",
        )

        for column in blocker_cols:
            if column not in df.columns:
                continue
            miss = count_missing(df.loc[dispatched, column])
            results.append(
                make_result(
                    rule_id=f"DT-036.DISPATCH_REQUIRED.{column}",
                    status=BLOCKER if miss else PASS,
                    table=table_name,
                    message=f"{column} required for attempted/deferred rows",
                    affected_count=miss,
                )
            )

        for column in warning_cols:
            if column not in df.columns:
                continue
            miss = count_missing(df.loc[dispatched, column])
            results.append(
                make_result(
                    rule_id=f"DT-036.DISPATCH_WARNING.{column}",
                    status=WARNING if miss else PASS,
                    table=table_name,
                    message=f"{column} should normally be present for attempted/deferred rows",
                    affected_count=miss,
                )
            )

    if "outlets.csv" in tables and "mall_window" in tables["outlets.csv"].columns:
        blank_count = count_missing(tables["outlets.csv"]["mall_window"])
        results.append(
            make_result(
                rule_id="DT-036.OUTLETS_MALL_WINDOW",
                status=EXPECTED if blank_count else PASS,
                table="outlets.csv",
                message="mall_window may be blank outside mall outlets",
                affected_count=blank_count,
            )
        )

    if "calendar.csv" in tables and "festival" in tables["calendar.csv"].columns:
        blank_count = count_missing(tables["calendar.csv"]["festival"])
        results.append(
            make_result(
                rule_id="DT-036.CALENDAR_FESTIVAL_BLANK",
                status=EXPECTED if blank_count else PASS,
                table="calendar.csv",
                message="festival may be blank when no festival applies",
                affected_count=blank_count,
            )
        )

    return results


def audit_complete_duplicates(tables: dict[str, pd.DataFrame]) -> list[dict]:
    results: list[dict] = []
    for table_name, df in tables.items():
        duplicate_count = int(df.duplicated(keep=False).sum())
        status = BLOCKER if duplicate_count else PASS
        results.append(
            make_result(
                rule_id="DT-037.COMPLETE_DUPLICATES",
                status=status,
                table=table_name,
                message="Exact duplicate row audit completed",
                affected_count=duplicate_count,
            )
        )
    return results


def audit_primary_keys(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    for table_name, key_sets in rules.get("official_keys", {}).items():
        if table_name not in tables:
            continue
        df = tables[table_name]
        for key_columns in key_sets:
            key_name = "+".join(key_columns)
            if any(col not in df.columns for col in key_columns):
                results.append(
                    make_result(
                        rule_id=f"DT-038.KEY_COLUMNS.{key_name}",
                        status=BLOCKER,
                        table=table_name,
                        message=f"Missing key columns for {key_name}",
                        affected_count=1,
                    )
                )
                continue
            duplicates = int(df.duplicated(subset=key_columns, keep=False).sum())
            status = BLOCKER if duplicates else PASS
            results.append(
                make_result(
                    rule_id=f"DT-038.KEY_UNIQUENESS.{key_name}",
                    status=status,
                    table=table_name,
                    message=f"Duplicate key audit for {key_name}",
                    affected_count=duplicates,
                )
            )
    return results


def audit_semantic_types(tables: dict[str, pd.DataFrame]) -> list[dict]:
    results: list[dict] = []
    from src.common.data_inventory import classify_column_semantic_type

    for table_name, df in tables.items():
        for column in df.columns:
            semantic_type = classify_column_semantic_type(column, table_name)
            if semantic_type == "unknown":
                continue
            series = df[column]
            mask = nonmissing_mask(series)
            invalid_count = 0

            if semantic_type == "numeric_count":
                numeric = _series_numeric(series)
                invalid_count = int(mask.sum() - (_is_integer_like(series)).sum())
            elif semantic_type in {"numeric_continuous", "numeric_duration"}:
                numeric = _series_numeric(series)
                invalid_count = int(mask.sum() - numeric.notna().sum())
            elif semantic_type == "binary_indicator":
                numeric = _series_numeric(series)
                valid = numeric.isin([0, 1])
                invalid_count = int((mask & ~valid).sum())
            elif semantic_type == "date":
                parsed = _parse_dates(series)
                invalid_count = int(mask.sum() - parsed.notna().sum())
            elif semantic_type == "clock_time":
                invalid_count = int(mask.sum() - series[mask].apply(_clock_time_valid).sum())
            elif semantic_type == "time_range":
                invalid_count = int(mask.sum() - series[mask].apply(_time_range_valid).sum())

            results.append(
                make_result(
                    rule_id=f"DT-039.SEMANTIC_TYPE.{column}",
                    status=BLOCKER if invalid_count else PASS,
                    table=table_name,
                    message=f"{column} semantic type validated as {semantic_type}",
                    affected_count=invalid_count,
                    details={"semantic_type": semantic_type},
                )
            )
    return results


def audit_dates(tables: dict[str, pd.DataFrame]) -> list[dict]:
    results: list[dict] = []
    date_columns = {"order_date", "dispatch_date", "date"}

    for table_name, df in tables.items():
        for column in [c for c in df.columns if c in date_columns]:
            parsed = _parse_dates(df[column])
            mask = nonmissing_mask(df[column])
            invalid = int(mask.sum() - parsed.notna().sum())
            results.append(
                make_result(
                    rule_id=f"DT-040.DATE_PARSE.{column}",
                    status=BLOCKER if invalid else PASS,
                    table=table_name,
                    message=f"Date parse audit for {column}",
                    affected_count=invalid,
                )
            )

    for table_name in ("deliveries_train.csv", "task1_test_inputs.csv"):
        if table_name not in tables:
            continue
        df = tables[table_name]
        if not {"order_date", "dispatch_date", "dispatch_status"}.issubset(df.columns):
            continue
        order_date = _parse_dates(df["order_date"])
        dispatch_date = _parse_dates(df["dispatch_date"])

        attempted = df["dispatch_status"] == "attempted"
        deferred = df["dispatch_status"] == "deferred"
        not_run = df["dispatch_status"] == "not_run"

        attempted_mismatch = int(((dispatch_date != order_date) & attempted & dispatch_date.notna() & order_date.notna()).sum())
        deferred_mismatch = int(((dispatch_date <= order_date) & deferred & dispatch_date.notna() & order_date.notna()).sum())
        not_run_blank_ok = int((not_run & df["dispatch_date"].apply(is_missing_value)).sum())

        results.extend(
            [
                make_result(
                    rule_id="DT-040.ATTEMPTED_SAME_DAY",
                    status=WARNING if attempted_mismatch else PASS,
                    table=table_name,
                    message="attempted rows should normally dispatch on requested order date",
                    affected_count=attempted_mismatch,
                ),
                make_result(
                    rule_id="DT-040.DEFERRED_LATER",
                    status=WARNING if deferred_mismatch else PASS,
                    table=table_name,
                    message="deferred rows should normally dispatch later than requested order date",
                    affected_count=deferred_mismatch,
                ),
                make_result(
                    rule_id="DT-040.NOT_RUN_BLANK_DISPATCH_DATE",
                    status=EXPECTED if not_run_blank_ok else PASS,
                    table=table_name,
                    message="not_run rows may have blank dispatch_date",
                    affected_count=not_run_blank_ok,
                ),
            ]
        )

    return results


def audit_times(tables: dict[str, pd.DataFrame]) -> list[dict]:
    results: list[dict] = []
    time_columns = {
        "planned_arrival_time",
        "window_open_time",
        "window_close_time",
        "planned_depart_time",
        "actual_depart_time",
        "arrival_time",
        "leave_outlet_time",
    }
    for table_name, df in tables.items():
        for column in [c for c in df.columns if c in time_columns]:
            mask = nonmissing_mask(df[column])
            invalid = int(mask.sum() - df.loc[mask, column].apply(_clock_time_valid).sum())
            results.append(
                make_result(
                    rule_id=f"DT-041.CLOCK_TIME.{column}",
                    status=BLOCKER if invalid else PASS,
                    table=table_name,
                    message=f"Clock time format validated for {column}",
                    affected_count=invalid,
                )
            )
        if "mall_window" in df.columns:
            mask = nonmissing_mask(df["mall_window"])
            invalid = int(mask.sum() - df.loc[mask, "mall_window"].apply(_time_range_valid).sum())
            results.append(
                make_result(
                    rule_id="DT-041.MALL_WINDOW_FORMAT",
                    status=BLOCKER if invalid else PASS,
                    table=table_name,
                    message="mall_window format validated as HH:MM-HH:MM when populated",
                    affected_count=invalid,
                )
            )
    return results


def audit_categories(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    binary_columns = set(rules.get("binary_columns", []))
    for table_name, df in tables.items():
        for column in df.columns:
            if column in binary_columns:
                numeric = _series_numeric(df[column])
                mask = nonmissing_mask(df[column])
                invalid = int((mask & ~numeric.isin([0, 1])).sum())
                results.append(
                    make_result(
                        rule_id=f"DT-042.BINARY_ENUM.{column}",
                        status=BLOCKER if invalid else PASS,
                        table=table_name,
                        message=f"Binary column {column} restricted to 0/1",
                        affected_count=invalid,
                    )
                )
                continue

            allowed = _allowed_values_for_column(column, table_name, rules)
            if allowed is None:
                continue
            mask = nonmissing_mask(df[column])
            invalid = int((mask & ~df[column].isin(allowed)).sum())
            results.append(
                make_result(
                    rule_id=f"DT-042.ENUM.{column}",
                    status=BLOCKER if invalid else PASS,
                    table=table_name,
                    message=f"{column} validated against official categories",
                    affected_count=invalid,
                    details={"allowed_values": sorted(allowed)},
                )
            )
    return results


def audit_numeric_ranges(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    nonnegative = set(rules.get("nonnegative_numeric_columns", []))
    positive = set(rules.get("strictly_positive_when_present", []))
    bounded = rules.get("bounded_numeric", {})
    binary_columns = set(rules.get("binary_columns", []))

    for table_name, df in tables.items():
        for column in df.columns:
            if column in nonnegative:
                numeric = _series_numeric(df[column])
                invalid = int((numeric < 0).fillna(False).sum())
                status = BLOCKER if invalid else PASS
                results.append(
                    make_result(
                        rule_id=f"DT-043.NONNEGATIVE.{column}",
                        status=status,
                        table=table_name,
                        message=f"{column} must be nonnegative",
                        affected_count=invalid,
                    )
                )
                if column in {"order_units", "order_weight_kg", "order_volume_m3"}:
                    zero_count = int((numeric == 0).fillna(False).sum())
                    results.append(
                        make_result(
                            rule_id=f"DT-043.ZERO_WARNING.{column}",
                            status=WARNING if zero_count else PASS,
                            table=table_name,
                            message=f"{column} equal to zero is suspicious but not automatically invalid",
                            affected_count=zero_count,
                        )
                    )

            if column in positive:
                numeric = _series_numeric(df[column])
                mask = numeric.notna()
                invalid = int((mask & (numeric <= 0)).sum())
                results.append(
                    make_result(
                        rule_id=f"DT-043.POSITIVE.{column}",
                        status=BLOCKER if invalid else PASS,
                        table=table_name,
                        message=f"{column} must be > 0 when present",
                        affected_count=invalid,
                    )
                )

            if column in bounded:
                numeric = _series_numeric(df[column])
                limits = bounded[column]
                mask = numeric.notna()
                invalid = int(
                    (mask & ((numeric < limits["min"]) | (numeric > limits["max"]))).sum()
                )
                results.append(
                    make_result(
                        rule_id=f"DT-043.BOUNDED.{column}",
                        status=BLOCKER if invalid else PASS,
                        table=table_name,
                        message=f"{column} must stay within [{limits['min']}, {limits['max']}]",
                        affected_count=invalid,
                    )
                )

            if column in binary_columns:
                numeric = _series_numeric(df[column])
                mask = numeric.notna()
                invalid = int((mask & ~numeric.isin([0, 1])).sum())
                results.append(
                    make_result(
                        rule_id=f"DT-043.BINARY_RANGE.{column}",
                        status=BLOCKER if invalid else PASS,
                        table=table_name,
                        message=f"{column} must be binary 0/1",
                        affected_count=invalid,
                    )
                )
    return results


def audit_outliers(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    candidate_columns = set(rules.get("nonnegative_numeric_columns", [])) | set(
        rules.get("strictly_positive_when_present", [])
    )

    for table_name, df in tables.items():
        for column in [c for c in df.columns if c in candidate_columns]:
            numeric = _series_numeric(df[column]).dropna()
            if len(numeric) < 4:
                results.append(
                    make_result(
                        rule_id=f"DT-044.OUTLIER.{column}",
                        status=NOT_APPLICABLE,
                        table=table_name,
                        message="Insufficient values for robust outlier review",
                    )
                )
                continue
            q1 = numeric.quantile(0.25)
            q3 = numeric.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                outlier_count = 0
            else:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                outlier_count = int(((numeric < lower) | (numeric > upper)).sum())
            results.append(
                make_result(
                    rule_id=f"DT-044.OUTLIER.{column}",
                    status=WARNING if outlier_count else PASS,
                    table=table_name,
                    message=f"Robust outlier review for {column}",
                    affected_count=outlier_count,
                )
            )
    return results


def audit_order_ids(tables: dict[str, pd.DataFrame]) -> list[dict]:
    results: list[dict] = []
    for table_name in ("deliveries_train.csv", "task1_test_inputs.csv"):
        if table_name not in tables or "delivery_id" not in tables[table_name].columns:
            continue
        df = tables[table_name]
        missing = count_missing(df["delivery_id"])
        duplicates = int(df.duplicated(subset=["delivery_id"], keep=False).sum())
        results.extend(
            [
                make_result(
                    rule_id="DT-045.DELIVERY_ID_PRESENT",
                    status=BLOCKER if missing else PASS,
                    table=table_name,
                    message="delivery_id must be nonblank",
                    affected_count=missing,
                ),
                make_result(
                    rule_id="DT-045.DELIVERY_ID_UNIQUE",
                    status=BLOCKER if duplicates else PASS,
                    table=table_name,
                    message="delivery_id must be unique",
                    affected_count=duplicates,
                ),
            ]
        )

    if {"deliveries_train.csv", "task1_test_inputs.csv"}.issubset(tables):
        left = _safe_string_set(tables["deliveries_train.csv"]["delivery_id"])
        right = _safe_string_set(tables["task1_test_inputs.csv"]["delivery_id"])
        overlap = left & right
        results.append(
            make_result(
                rule_id="DT-045.DELIVERY_ID_TRAIN_TEST_OVERLAP",
                status=WARNING if overlap else PASS,
                table="deliveries_train.csv|task1_test_inputs.csv",
                message="Cross-file delivery_id overlap should be understood before Task 2A demand construction",
                affected_count=len(overlap),
            )
        )

    if "task2b_peak_day_scenarios.csv" in tables:
        df = tables["task2b_peak_day_scenarios.csv"]
        if {"scenario", "order_ref"}.issubset(df.columns):
            composite_dupes = int(
                df.duplicated(subset=["scenario", "order_ref"], keep=False).sum()
            )
            results.append(
                make_result(
                    rule_id="DT-045.ORDER_REF_UNIQUE_WITHIN_SCENARIO",
                    status=BLOCKER if composite_dupes else PASS,
                    table="task2b_peak_day_scenarios.csv",
                    message="order_ref must be unique within scenario S1",
                    affected_count=composite_dupes,
                )
            )
    return results


def audit_route_leg_keys(tables: dict[str, pd.DataFrame]) -> list[dict]:
    results: list[dict] = []
    for table_name in ("route_legs_train.csv", "route_legs_test.csv"):
        if table_name not in tables:
            continue
        df = tables[table_name]
        if "leg_id" in df.columns:
            leg_dupes = int(df.duplicated(subset=["leg_id"], keep=False).sum())
            results.append(
                make_result(
                    rule_id="DT-046.LEG_ID_UNIQUE",
                    status=BLOCKER if leg_dupes else PASS,
                    table=table_name,
                    message="leg_id must be unique",
                    affected_count=leg_dupes,
                )
            )
        if {"route_id", "seq"}.issubset(df.columns):
            route_dupes = int(df.duplicated(subset=["route_id", "seq"], keep=False).sum())
            results.append(
                make_result(
                    rule_id="DT-046.ROUTE_KEY_UNIQUE",
                    status=BLOCKER if route_dupes else PASS,
                    table=table_name,
                    message="route_id + seq must be unique within route legs",
                    affected_count=route_dupes,
                )
            )

    for table_name in ("deliveries_train.csv", "task1_test_inputs.csv"):
        if table_name not in tables:
            continue
        df = tables[table_name]
        if not {"dispatch_status", "route_id", "seq_in_route"}.issubset(df.columns):
            continue
        dispatched = df["dispatch_status"].isin(["attempted", "deferred"])
        route_missing = count_missing(df.loc[dispatched, "route_id"])
        seq_missing = count_missing(df.loc[dispatched, "seq_in_route"])
        seq_numeric = _series_numeric(df["seq_in_route"])
        seq_negative = int(((seq_numeric < 0) & dispatched).fillna(False).sum())
        results.extend(
            [
                make_result(
                    rule_id="DT-046.ORDER_ROUTE_ID_PRESENT",
                    status=BLOCKER if route_missing else PASS,
                    table=table_name,
                    message="Dispatched rows must have route_id",
                    affected_count=route_missing,
                ),
                make_result(
                    rule_id="DT-046.ORDER_SEQ_PRESENT",
                    status=BLOCKER if seq_missing else PASS,
                    table=table_name,
                    message="Dispatched rows must have seq_in_route",
                    affected_count=seq_missing,
                ),
                make_result(
                    rule_id="DT-046.ORDER_SEQ_NONNEGATIVE",
                    status=BLOCKER if seq_negative else PASS,
                    table=table_name,
                    message="seq_in_route must be >= 0 for dispatched rows",
                    affected_count=seq_negative,
                ),
            ]
        )
    return results


def audit_outlet_references(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    if "outlets.csv" not in tables:
        return [
            make_result(
                rule_id="DT-047.OUTLETS_PRESENT",
                status=BLOCKER,
                table="outlets.csv",
                message="outlets.csv must be available for outlet integrity checks",
                affected_count=1,
            )
        ]

    outlets = tables["outlets.csv"].copy()
    if "outlet_id" not in outlets.columns:
        return [
            make_result(
                rule_id="DT-047.OUTLETS_KEY",
                status=BLOCKER,
                table="outlets.csv",
                message="outlets.csv missing outlet_id",
                affected_count=1,
            )
        ]

    unique_outlets = outlets["outlet_id"].nunique(dropna=True)
    expected_count = int(rules.get("official_counts", {}).get("outlets", 120))
    results.append(
        make_result(
            rule_id="DT-047.OUTLET_COUNT",
            status=BLOCKER if unique_outlets != expected_count else PASS,
            table="outlets.csv",
            message=f"Unique outlets should equal {expected_count}",
            affected_count=abs(unique_outlets - expected_count),
            details={"observed_unique_outlets": int(unique_outlets)},
        )
    )

    outlet_ids = _safe_string_set(outlets["outlet_id"])
    mappings = rules.get("reference_mappings", {}).get("outlet_references", {})
    for table_name, column in mappings.items():
        if table_name not in tables or column not in tables[table_name].columns:
            continue
        df = tables[table_name]
        referenced = {
            str(v)
            for v in df[column][nonmissing_mask(df[column])].tolist()
        }
        missing_refs = referenced - outlet_ids
        results.append(
            make_result(
                rule_id="DT-047.OUTLET_REFERENCE_RESOLVE",
                status=BLOCKER if missing_refs else PASS,
                table=table_name,
                message=f"{column} references must resolve in outlets.csv",
                affected_count=len(missing_refs),
            )
        )

    attrs = rules.get("reference_attribute_checks", {}).get("outlets", [])
    for table_name in ("deliveries_train.csv", "task1_test_inputs.csv", "task2b_peak_day_scenarios.csv"):
        if table_name not in tables or "outlet_id" not in tables[table_name].columns:
            continue
        df = tables[table_name]
        merged = df.merge(outlets, on="outlet_id", how="left", suffixes=("", "__ref"))
        for attr in attrs:
            if attr not in df.columns or f"{attr}__ref" not in merged.columns:
                continue
            mask = nonmissing_mask(merged[attr]) & nonmissing_mask(merged[f"{attr}__ref"])
            mismatch = int((mask & (merged[attr] != merged[f"{attr}__ref"])).sum())
            results.append(
                make_result(
                    rule_id=f"DT-047.OUTLET_ATTR_MATCH.{attr}",
                    status=BLOCKER if mismatch else PASS,
                    table=table_name,
                    message=f"{attr} should match outlet reference when copied",
                    affected_count=mismatch,
                )
            )
    return results


def audit_vehicle_references(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    if "vehicles.csv" not in tables:
        return [
            make_result(
                rule_id="DT-048.VEHICLES_PRESENT",
                status=BLOCKER,
                table="vehicles.csv",
                message="vehicles.csv must be available for vehicle integrity checks",
                affected_count=1,
            )
        ]

    vehicles = tables["vehicles.csv"].copy()
    if "vehicle_id" not in vehicles.columns:
        return [
            make_result(
                rule_id="DT-048.VEHICLES_KEY",
                status=BLOCKER,
                table="vehicles.csv",
                message="vehicles.csv missing vehicle_id",
                affected_count=1,
            )
        ]

    unique_vehicles = vehicles["vehicle_id"].nunique(dropna=True)
    expected_count = int(rules.get("official_counts", {}).get("vehicles", 60))
    results.append(
        make_result(
            rule_id="DT-048.VEHICLE_COUNT",
            status=BLOCKER if unique_vehicles != expected_count else PASS,
            table="vehicles.csv",
            message=f"Unique vehicles should equal {expected_count}",
            affected_count=abs(unique_vehicles - expected_count),
            details={"observed_unique_vehicles": int(unique_vehicles)},
        )
    )

    vehicle_ids = _safe_string_set(vehicles["vehicle_id"])
    mappings = rules.get("reference_mappings", {}).get("vehicle_references", {})
    for table_name, column in mappings.items():
        if table_name not in tables or column not in tables[table_name].columns:
            continue
        df = tables[table_name]
        mask = nonmissing_mask(df[column])
        if table_name in {"deliveries_train.csv", "task1_test_inputs.csv"} and "dispatch_status" in df.columns:
            mask = mask & (df["dispatch_status"] != "not_run")
        referenced = {str(v) for v in df.loc[mask, column].tolist()}
        missing_refs = referenced - vehicle_ids
        results.append(
            make_result(
                rule_id="DT-048.VEHICLE_REFERENCE_RESOLVE",
                status=BLOCKER if missing_refs else PASS,
                table=table_name,
                message=f"{column} references must resolve in vehicles.csv when assigned",
                affected_count=len(missing_refs),
            )
        )

    for table_name in ("deliveries_train.csv", "task1_test_inputs.csv", "route_legs_train.csv", "route_legs_test.csv"):
        if table_name not in tables or "vehicle_id" not in tables[table_name].columns:
            continue
        df = tables[table_name]
        merged = df.merge(vehicles, on="vehicle_id", how="left", suffixes=("", "__ref"))
        mapping = {"vehicle_type": "type", "vehicle_temp": "temp", "depot": "depot"}
        for left, right in mapping.items():
            if left not in df.columns or right not in vehicles.columns:
                continue
            mask = nonmissing_mask(merged[left]) & nonmissing_mask(merged[right])
            mismatch = int((mask & (merged[left] != merged[right])).sum())
            results.append(
                make_result(
                    rule_id=f"DT-048.VEHICLE_ATTR_MATCH.{left}",
                    status=BLOCKER if mismatch else PASS,
                    table=table_name,
                    message=f"{left} should match vehicles.{right} when copied",
                    affected_count=mismatch,
                )
            )
    return results


def audit_calendar_coverage(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    if "calendar.csv" not in tables:
        return [
            make_result(
                rule_id="DT-049.CALENDAR_PRESENT",
                status=BLOCKER,
                table="calendar.csv",
                message="calendar.csv must exist for date/week coverage checks",
                affected_count=1,
            )
        ]

    cal = tables["calendar.csv"].copy()
    if "date" not in cal.columns:
        return [
            make_result(
                rule_id="DT-049.CALENDAR_DATE_COLUMN",
                status=BLOCKER,
                table="calendar.csv",
                message="calendar.csv missing date column",
                affected_count=1,
            )
        ]

    parsed = _parse_dates(cal["date"])
    invalid_dates = int(nonmissing_mask(cal["date"]).sum() - parsed.notna().sum())
    results.append(
        make_result(
            rule_id="DT-049.CALENDAR_DATE_PARSE",
            status=BLOCKER if invalid_dates else PASS,
            table="calendar.csv",
            message="calendar date values must parse",
            affected_count=invalid_dates,
        )
    )

    date_dupes = int(cal.duplicated(subset=["date"], keep=False).sum())
    results.append(
        make_result(
            rule_id="DT-049.CALENDAR_DATE_UNIQUE",
            status=BLOCKER if date_dupes else PASS,
            table="calendar.csv",
            message="calendar.date must be unique",
            affected_count=date_dupes,
        )
    )

    if {"dow", "iso_year", "iso_week", "is_weekend"}.issubset(cal.columns):
        valid_rows = parsed.notna()
        actual_dow = parsed.dt.weekday
        actual_iso = parsed.dt.isocalendar()
        numeric_dow = pd.to_numeric(cal["dow"], errors="coerce")
        numeric_weekend = pd.to_numeric(cal["is_weekend"], errors="coerce")
        dow_mismatch = int((valid_rows & (numeric_dow != actual_dow)).sum())
        iso_year_mismatch = int((valid_rows & (pd.to_numeric(cal["iso_year"], errors="coerce") != actual_iso.year)).sum())
        iso_week_mismatch = int((valid_rows & (pd.to_numeric(cal["iso_week"], errors="coerce") != actual_iso.week)).sum())

        # Hard rule: a given dow should not map inconsistently to is_weekend.
        consistent_weekend_groups = (
            pd.DataFrame({"dow": numeric_dow, "is_weekend": numeric_weekend})
            .dropna()
            .groupby("dow")["is_weekend"]
            .nunique()
        )
        weekend_inconsistency = int((consistent_weekend_groups > 1).sum())

        # Soft rule: standard Saturday/Sunday weekend assumption may not be universal.
        weekend_expected = actual_dow.isin([5, 6]).astype(int)
        weekend_standard_mismatch = int(
            (valid_rows & (numeric_weekend != weekend_expected)).sum()
        )
        results.extend(
            [
                make_result("DT-049.CALENDAR_DOW", BLOCKER if dow_mismatch else PASS, "calendar.csv", "dow must match actual date with Monday=0", dow_mismatch),
                make_result("DT-049.CALENDAR_ISO_YEAR", BLOCKER if iso_year_mismatch else PASS, "calendar.csv", "iso_year must match actual ISO year", iso_year_mismatch),
                make_result("DT-049.CALENDAR_ISO_WEEK", BLOCKER if iso_week_mismatch else PASS, "calendar.csv", "iso_week must match actual ISO week", iso_week_mismatch),
                make_result("DT-049.CALENDAR_WEEKEND", BLOCKER if weekend_inconsistency else PASS, "calendar.csv", "is_weekend must be internally consistent for each dow", weekend_inconsistency),
                make_result("DT-049.CALENDAR_WEEKEND_STANDARD", WARNING if weekend_standard_mismatch else PASS, "calendar.csv", "is_weekend differs from standard Saturday/Sunday assumption", weekend_standard_mismatch),
            ]
        )

    calendar_dates = {
        d.strftime("%Y-%m-%d")
        for d in parsed.dropna().tolist()
    }

    required_dates: set[str] = set()
    for table_name, column in [
        ("deliveries_train.csv", "order_date"),
        ("deliveries_train.csv", "dispatch_date"),
        ("task1_test_inputs.csv", "order_date"),
        ("task1_test_inputs.csv", "dispatch_date"),
        ("route_legs_train.csv", "date"),
        ("route_legs_test.csv", "date"),
    ]:
        if table_name in tables and column in tables[table_name].columns:
            series = tables[table_name][column]
            required_dates |= _safe_string_set(series)
    missing_dates = {d for d in required_dates if d not in calendar_dates}
    results.append(
        make_result(
            rule_id="DT-049.CALENDAR_DATE_COVERAGE",
            status=BLOCKER if missing_dates else PASS,
            table="calendar.csv",
            message="calendar.csv must cover required Task 1 / history dates",
            affected_count=len(missing_dates),
        )
    )

    if "task2a_test_inputs.csv" in tables and {"iso_year", "iso_week"}.issubset(tables["task2a_test_inputs.csv"].columns):
        forecast_pairs = {
            (int(y), int(w))
            for y, w in zip(
                pd.to_numeric(tables["task2a_test_inputs.csv"]["iso_year"], errors="coerce").dropna().astype(int),
                pd.to_numeric(tables["task2a_test_inputs.csv"]["iso_week"], errors="coerce").dropna().astype(int),
            )
        }
        calendar_pairs = {
            (int(y), int(w))
            for y, w in zip(
                pd.to_numeric(cal["iso_year"], errors="coerce").dropna().astype(int),
                pd.to_numeric(cal["iso_week"], errors="coerce").dropna().astype(int),
            )
        }
        missing_weeks = forecast_pairs - calendar_pairs
        results.append(
            make_result(
                rule_id="DT-049.CALENDAR_FORECAST_WEEK_COVERAGE",
                status=BLOCKER if missing_weeks else PASS,
                table="calendar.csv",
                message="calendar.csv must cover all Task 2A forecast iso_year + iso_week pairs",
                affected_count=len(missing_weeks),
            )
        )

    return results


def audit_optional_reference_coverage(
    tables: dict[str, pd.DataFrame],
    reference_table: str,
    target_tables: Sequence[str],
    preferred_columns: Sequence[str],
    rule_id_prefix: str,
) -> list[dict]:
    results: list[dict] = []
    if reference_table not in tables:
        return [
            make_result(
                rule_id=f"{rule_id_prefix}.TABLE_PRESENT",
                status=WARNING,
                table=reference_table,
                message=f"{reference_table} is unavailable; optional feature should remain disabled",
                affected_count=1,
            )
        ]

    ref = tables[reference_table]
    join_cols = [col for col in preferred_columns if col in ref.columns]
    if len(join_cols) < 2:
        return [
            make_result(
                rule_id=f"{rule_id_prefix}.JOIN_UNRESOLVED",
                status=WARNING,
                table=reference_table,
                message="Join mapping unresolved; optional feature should remain disabled until clarified",
                affected_count=1,
            )
        ]

    ref_keys = set(tuple(values) for values in ref[join_cols].dropna().itertuples(index=False, name=None))
    target_keys: set[tuple] = set()
    for table_name in target_tables:
        if table_name not in tables:
            continue
        df = tables[table_name]
        if not set(join_cols).issubset(df.columns):
            continue
        target_keys |= set(tuple(values) for values in df[join_cols].dropna().itertuples(index=False, name=None))

    if not target_keys:
        return [
            make_result(
                rule_id=f"{rule_id_prefix}.NO_TARGET_KEYS",
                status=NOT_APPLICABLE,
                table=reference_table,
                message="No auditable target keys available for optional coverage check",
            )
        ]

    missing = target_keys - ref_keys
    if not missing:
        status = PASS
    else:
        status = WARNING
    return [
        make_result(
            rule_id=f"{rule_id_prefix}.COVERAGE",
            status=status,
            table=reference_table,
            message="Optional reference coverage measured against available join keys",
            affected_count=len(missing),
            details={"join_columns": join_cols},
        )
    ]


def audit_road_coverage(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    join_cols = rules.get("coverage", {}).get("road_conditions", {}).get("preferred_join_columns", ["date", "district"])
    return audit_optional_reference_coverage(
        tables,
        reference_table="road_conditions.csv",
        target_tables=[
            "route_legs_train.csv",
            "route_legs_test.csv",
            "deliveries_train.csv",
            "task1_test_inputs.csv",
        ],
        preferred_columns=join_cols,
        rule_id_prefix="DT-050.ROAD_COVERAGE",
    )


def audit_traffic_coverage(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    join_cols = rules.get("coverage", {}).get("traffic_speed", {}).get("candidate_join_columns", ["district", "monsoon", "dow"])
    return audit_optional_reference_coverage(
        tables,
        reference_table="traffic_speed.csv",
        target_tables=["route_legs_train.csv", "route_legs_test.csv"],
        preferred_columns=join_cols,
        rule_id_prefix="DT-051.TRAFFIC_COVERAGE",
    )


def audit_train_test_compatibility(tables: dict[str, pd.DataFrame], rules: dict) -> list[dict]:
    results: list[dict] = []
    compare_pairs = [
        ("deliveries_train.csv", "task1_test_inputs.csv", ["brand", "district", "depot", "temp_requirement", "vehicle_type", "vehicle_temp"]),
        ("route_legs_train.csv", "route_legs_test.csv", ["brand", "district", "depot", "vehicle_type", "vehicle_temp"]),
    ]

    for train_table, test_table, columns in compare_pairs:
        if train_table not in tables or test_table not in tables:
            continue
        train_df = tables[train_table]
        test_df = tables[test_table]
        for column in columns:
            if column not in train_df.columns or column not in test_df.columns:
                continue
            train_values = _safe_string_set(train_df[column])
            test_values = _safe_string_set(test_df[column])
            unseen = test_values - train_values
            invalid = set()
            allowed = _allowed_values_for_column(column, test_table, rules)
            if allowed is not None:
                invalid = {value for value in unseen if value not in allowed}
                unseen = unseen - invalid
            results.append(
                make_result(
                    rule_id=f"DT-052.CATEGORY_COMPAT.{column}",
                    status=BLOCKER if invalid else (WARNING if unseen else PASS),
                    table=f"{train_table}|{test_table}",
                    message=f"Train/test compatibility evaluated for {column}",
                    affected_count=len(invalid) + len(unseen),
                )
            )

    if {"deliveries_train.csv", "task1_test_inputs.csv", "task2a_test_inputs.csv"}.issubset(tables):
        history = pd.concat(
            [
                tables["deliveries_train.csv"][["depot", "brand"]],
                tables["task1_test_inputs.csv"][["depot", "brand"]],
            ],
            ignore_index=True,
        )
        hist_pairs = set(tuple(values) for values in history.dropna().itertuples(index=False, name=None))
        future = tables["task2a_test_inputs.csv"][["depot", "brand"]]
        future_pairs = set(tuple(values) for values in future.dropna().itertuples(index=False, name=None))
        unseen_pairs = future_pairs - hist_pairs
        results.append(
            make_result(
                rule_id="DT-052.TASK2A_DEPOT_BRAND_SUPPORT",
                status=WARNING if unseen_pairs else PASS,
                table="task2a_test_inputs.csv",
                message="Task 2A depot + brand support checked against combined history source",
                affected_count=len(unseen_pairs),
            )
        )
    return results


def build_audit_summary(audit_sections: dict[str, list[dict]]) -> dict:
    all_results = [item for items in audit_sections.values() for item in items]
    blockers = [r for r in all_results if r["status"] == BLOCKER]
    warnings = [r for r in all_results if r["status"] == WARNING]
    expected = [r for r in all_results if r["status"] == EXPECTED]
    passes = [r for r in all_results if r["status"] == PASS]

    return {
        "phase": "03_data_quality_audit",
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "expected_count": len(expected),
        "pass_count": len(passes),
        "blocker_rule_codes": sorted({r["rule_id"] for r in blockers}),
        "warning_rule_codes": sorted({r["rule_id"] for r in warnings}),
        "sections": audit_sections,
    }


def render_phase03_report(summary: dict) -> str:
    blockers = summary.get("blocker_rule_codes", [])
    warnings = summary.get("warning_rule_codes", [])
    blocker_lines = [f"- {code}" for code in blockers] if blockers else ["- None"]
    warning_lines = [f"- {code}" for code in warnings] if warnings else ["- None"]
    return "\n".join(
        [
            "# Phase 03 Audit Report",
            "",
            "## Phase Verdict",
            f"- PHASE 03 STATUS: {summary.get('status', 'FAIL')}",
            f"- BLOCKERS: {summary.get('blocker_count', 0)}",
            f"- WARNINGS DOCUMENTED: {'YES' if summary.get('warning_count', 0) else 'NO'}",
            f"- READY FOR PHASE 04: {'YES' if summary.get('status') == 'PASS' else 'NO'}",
            "",
            "## Blocking Issues",
            *blocker_lines,
            "",
            "## Non-Blocking Warnings",
            *warning_lines,
            "",
            "## Downstream Treatment",
            "- BLOCKER results must be resolved before Phase 04.",
            "- WARNING results may proceed only with documented downstream handling.",
            "- Optional road/traffic features remain disabled until join coverage is trustworthy.",
        ]
    )


def write_phase03_private_reports(output_dir: Path, audit_sections: dict[str, list[dict]], summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_map = {
        "missingness.json": audit_sections.get("missingness", []),
        "duplicate_rows.json": audit_sections.get("duplicate_rows", []),
        "key_integrity.json": audit_sections.get("key_integrity", []),
        "type_validation.json": audit_sections.get("type_validation", []),
        "date_validation.json": audit_sections.get("date_validation", []),
        "time_validation.json": audit_sections.get("time_validation", []),
        "category_validation.json": audit_sections.get("category_validation", []),
        "numeric_validation.json": audit_sections.get("numeric_validation", []),
        "outlier_review.json": audit_sections.get("outlier_review", []),
        "reference_integrity.json": audit_sections.get("reference_integrity", []),
        "coverage.json": audit_sections.get("coverage", []),
        "train_test_compatibility.json": audit_sections.get("train_test_compatibility", []),
        "audit_summary.json": summary,
    }
    for filename, payload in file_map.items():
        with (output_dir / filename).open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    with (output_dir / "phase03_audit_report.md").open("w", encoding="utf-8") as handle:
        handle.write(render_phase03_report(summary))
