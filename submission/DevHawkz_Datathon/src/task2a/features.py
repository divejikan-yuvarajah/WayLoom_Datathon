"""Origin-safe demand features for Phase 13 Task 2A forecasting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.task2a.eda import EDAValidationError, SERIES_KEYS, validate_task2a_eda_input


LAG_WEEKS = (1, 2, 4, 13, 52)
ROLLING_WINDOWS = (4, 8, 13)
TARGET_COLUMNS = ("target_total_volume_m3", "target_chilled_volume_m3")
METADATA_COLUMNS = (
    "origin_iso_year", "origin_iso_week", "origin_week_start_date",
    "origin_demand_feature_max_source_week",
    "target_iso_year", "target_iso_week", "target_week_start_date",
    "origin_panel_status", "target_panel_status",
)


class FeatureValidationError(EDAValidationError):
    """Raised when Phase 13 feature inputs or settings violate their contract."""


def load_feature_config(path: str | Path) -> dict[str, Any]:
    """Load the explicit Phase 13 feature policy configuration."""
    with Path(path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise FeatureValidationError("Task 2A feature configuration must be a mapping.")
    validate_feature_config(config)
    return config


def validate_feature_config(config: dict[str, Any]) -> None:
    horizon = config.get("multihorizon", {}).get("max_horizon", config.get("horizon", {}).get("max_weeks", 10))
    if not isinstance(horizon, int) or not 1 <= horizon <= 10:
        raise FeatureValidationError("configured maximum horizon must be an integer in 1..10.")
    minimum = config.get("multihorizon", {}).get("min_horizon", 1)
    if minimum != 1:
        raise FeatureValidationError("multihorizon.min_horizon must be exactly 1.")
    for field, defaults in (("lags", LAG_WEEKS), ("rolling_means", ROLLING_WINDOWS)):
        legacy = "rolling" if field == "rolling_means" else field
        values = config.get(field, {}).get("values" if field == "lags" else "windows", config.get(legacy, {}).get("weeks", list(defaults)))
        if not isinstance(values, list) or not values or any(not isinstance(value, int) or value < 1 for value in values):
            raise FeatureValidationError(f"{field}.weeks must contain positive integer weeks.")


def _configured_weeks(config: dict[str, Any] | None, section: str, defaults: tuple[int, ...]) -> tuple[int, ...]:
    if config is None:
        return defaults
    validate_feature_config(config)
    canonical = "rolling_means" if section == "rolling" else section
    values = config.get(canonical, {}).get("values" if canonical == "lags" else "windows", config.get(section, {}).get("weeks", list(defaults)))
    return tuple(sorted(set(int(value) for value in values)))


def build_origin_demand_features(panel: pd.DataFrame, config: dict[str, Any] | None = None) -> pd.DataFrame:
    """Build predictors at each origin using demand available on or before that origin.

    Lag ``k`` intentionally means ``y[t-(k-1)]``: lag-1 is the known current
    origin demand, while lag-2 is the preceding week.  Rolling windows end at
    the origin and require complete history, so they never silently borrow a
    later value or fill a missing historical value.
    """
    try:
        frame = validate_task2a_eda_input(panel)
    except EDAValidationError as error:
        raise FeatureValidationError(str(error)) from error
    lags = _configured_weeks(config, "lags", LAG_WEEKS)
    windows = _configured_weeks(config, "rolling", ROLLING_WINDOWS)
    frame = frame.sort_values([*SERIES_KEYS, "week_start_date"], kind="stable").reset_index(drop=True)
    group = frame.groupby(SERIES_KEYS, sort=False)
    frame["history_weeks_available"] = group.cumcount() + 1
    # All demand-derived transforms below are trailing/inclusive, so this
    # auditable lineage bound is the origin itself, never a future week.
    frame["demand_feature_max_source_week"] = frame["week_start_date"]

    for source, prefix in (("total_volume_m3", "total"), ("chilled_volume_m3", "chilled")):
        for lag in lags:
            frame[f"{prefix}_lag_{lag}"] = group[source].shift(lag - 1)
        for window in windows:
            frame[f"{prefix}_rolling_mean_{window}"] = group[source].transform(
                lambda values, width=window: values.rolling(width, min_periods=width).mean()
            )

        # These explicit trend features compare two non-overlapping trailing
        # windows, both ending no later than the origin.
        if 4 in windows and 13 in windows:
            short = frame[f"{prefix}_rolling_mean_4"]
            long = frame[f"{prefix}_rolling_mean_13"]
            frame[f"{prefix}_trend_4_vs_13"] = short - long
            frame[f"{prefix}_trend_ratio_4_vs_13"] = np.divide(
                short.to_numpy(dtype=float), long.to_numpy(dtype=float),
                out=np.full(len(frame), np.nan), where=long.to_numpy(dtype=float) > 0,
            )
    return frame


def _registry_row(name: str, group: str, source: str, available_at: str, transform: str,
                  null_policy: str, dtype: str, role: str = "feature") -> dict[str, str]:
    return {
        "feature_name": name,
        "feature_group": group,
        "source": source,
        "available_at": available_at,
        "transform": transform,
        "missing_value_policy": null_policy,
        "data_type": dtype,
        "role": role,
        "selection_status": "enabled" if role == "feature" else "excluded",
        "leakage_risk": "none" if role == "feature" else "target_or_metadata",
        "rationale": "Phase 13 origin-safe direct multi-horizon feature contract.",
    }


def build_feature_registry(config: dict[str, Any] | None = None) -> pd.DataFrame:
    """Return the versioned feature registry; labels are deliberately excluded."""
    lags = _configured_weeks(config, "lags", LAG_WEEKS)
    windows = _configured_weeks(config, "rolling", ROLLING_WINDOWS)
    rows: list[dict[str, str]] = [
        _registry_row("depot", "series", "Phase 11 panel", "origin", "identity", "not_null", "category"),
        _registry_row("brand", "series", "Phase 11 panel", "origin", "identity", "not_null", "category"),
        _registry_row("horizon_weeks", "horizon", "direct forecast design", "origin", "1..H", "not_null", "integer"),
        _registry_row("history_weeks_available", "history", "Phase 11 panel", "origin", "trailing count", "not_null", "integer"),
    ]
    for prefix in ("total", "chilled"):
        for lag in lags:
            rows.append(_registry_row(f"{prefix}_lag_{lag}", "lag", "Phase 11 panel", "origin", f"y[t-{lag - 1}]", "keep_null", "float"))
        for window in windows:
            rows.append(_registry_row(f"{prefix}_rolling_mean_{window}", "rolling", "Phase 11 panel", "origin", f"trailing mean t-{window - 1}:t", "keep_null", "float"))
        if 4 in windows and 13 in windows:
            rows += [
                _registry_row(f"{prefix}_trend_4_vs_13", "trend", "Phase 11 panel", "origin", "rolling_4 - rolling_13", "keep_null", "float"),
                _registry_row(f"{prefix}_trend_ratio_4_vs_13", "trend", "Phase 11 panel", "origin", "rolling_4 / rolling_13", "null when denominator <= 0", "float"),
            ]
    calendar_names = (
        "target_operating_days", "target_weekend_days", "target_payday_days", "target_has_payday",
        "target_holiday_days", "target_has_holiday", "target_festival_days", "target_has_festival",
        "target_festival_names", "target_max_festival_ramp", "target_mean_festival_ramp",
        "target_monsoon_days", "target_monsoon_day_fraction", "target_has_monsoon_day",
    )
    for name in calendar_names:
        dtype = "category" if name == "target_festival_names" else "float"
        rows.append(_registry_row(name, "target_calendar", "official daily calendar", "target week", "Phase 12 weekly aggregation", "not_null", dtype))
    for name in (*METADATA_COLUMNS, *TARGET_COLUMNS):
        rows.append(_registry_row(name, "metadata" if name not in TARGET_COLUMNS else "label", "assembled table", "not a predictor", "identity", "not_applicable", "metadata", "excluded"))
    registry = pd.DataFrame(rows)
    availability = {
        "series": "STATIC_SERIES", "horizon": "FORECAST_HORIZON", "target_calendar": "TARGET_WEEK_CALENDAR",
        "lag": "PAST_DEMAND", "rolling": "PAST_DEMAND", "trend": "PAST_DEMAND", "history": "PAST_DEMAND",
    }
    registry["source_columns"] = registry["source"]
    registry["formula"] = registry["transform"]
    registry["availability_type"] = registry["feature_group"].map(availability).fillna("NOT_A_PREDICTOR")
    registry["prediction_time_safe"] = registry["role"].eq("feature")
    registry["uses_future_actual_demand"] = registry["feature_name"].isin(TARGET_COLUMNS)
    registry["requires_history_weeks"] = registry["feature_name"].str.extract(r"(?:lag_|mean_)(\d+)", expand=False).fillna(0).astype(int)
    registry["categorical"] = registry["data_type"].eq("category")
    registry["nullable"] = registry["missing_value_policy"].isin(["keep_null", "null when denominator <= 0"])
    registry["status"] = registry["selection_status"]
    return registry


def get_task2a_feature_columns(config: dict[str, Any] | None = None) -> list[str]:
    registry = build_feature_registry(config)
    columns = registry.loc[registry.role.eq("feature"), "feature_name"].tolist()
    forbidden = set(TARGET_COLUMNS) | set(METADATA_COLUMNS)
    if forbidden.intersection(columns):
        raise AssertionError("Target or metadata column entered the Task 2A feature matrix.")
    return columns


def get_task2a_metadata_columns() -> list[str]:
    return list(METADATA_COLUMNS)


def get_task2a_target_columns() -> list[str]:
    return list(TARGET_COLUMNS)


def feature_coverage_summary(table: pd.DataFrame, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return privacy-safe coverage counts without serializing observations."""
    predictors = get_task2a_feature_columns(config)
    available = [column for column in predictors if column in table]
    return {
        "n_rows": int(len(table)),
        "n_predictors": int(len(available)),
        "missing_predictor_cells": int(table[available].isna().sum().sum()) if available else 0,
        "all_predictors_present": bool(len(available) == len(predictors)),
    }


def audit_future_demand_leakage(panel: pd.DataFrame, table: pd.DataFrame,
                                config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Independently reconcile every demand feature to its canonical origin history.

    The comparison uses the Phase 11 panel and the direct table's origin keys;
    it does not rely on the table's self-reported source-date metadata.  Thus a
    future value accidentally substituted into a lag, rolling mean, or trend
    predictor is rejected before any private output is written.
    """
    registry = build_feature_registry(config)
    enabled = registry.loc[registry.status.eq("enabled")].copy()
    if not enabled.prediction_time_safe.all() or enabled.uses_future_actual_demand.any():
        raise FeatureValidationError("Enabled feature registry contains an unsafe future-demand feature.")
    predictors = get_task2a_feature_columns(config)
    if set(TARGET_COLUMNS).intersection(predictors):
        raise FeatureValidationError("Target labels appear in the predictor registry.")
    missing = [name for name in predictors if name not in table]
    if missing:
        raise FeatureValidationError("Feature table is missing registry predictors: " + ", ".join(missing))
    if "origin_demand_feature_max_source_week" not in table or not pd.to_datetime(
        table["origin_demand_feature_max_source_week"]
    ).le(pd.to_datetime(table["origin_week_start_date"])).all():
        raise FeatureValidationError("A demand feature has source lineage after its origin week.")
    # Deliberately recompute the contract formulas here instead of calling the
    # feature builder.  This keeps the audit independent of the production
    # transform implementation it is meant to check.
    try:
        expected = validate_task2a_eda_input(panel)
    except EDAValidationError as error:
        raise FeatureValidationError(str(error)) from error
    expected = expected.sort_values([*SERIES_KEYS, "week_start_date"], kind="stable").reset_index(drop=True)
    expected_group = expected.groupby(SERIES_KEYS, sort=False)
    expected["history_weeks_available"] = expected_group.cumcount() + 1
    lags = _configured_weeks(config, "lags", LAG_WEEKS)
    windows = _configured_weeks(config, "rolling", ROLLING_WINDOWS)
    for source, prefix in (("total_volume_m3", "total"), ("chilled_volume_m3", "chilled")):
        for lag in lags:
            expected[f"{prefix}_lag_{lag}"] = expected_group[source].shift(lag - 1)
        for window in windows:
            expected[f"{prefix}_rolling_mean_{window}"] = expected_group[source].transform(
                lambda values, width=window: values.rolling(width, min_periods=width).mean()
            )
        if 4 in windows and 13 in windows:
            short = expected[f"{prefix}_rolling_mean_4"]
            long = expected[f"{prefix}_rolling_mean_13"]
            expected[f"{prefix}_trend_4_vs_13"] = short - long
            expected[f"{prefix}_trend_ratio_4_vs_13"] = np.divide(
                short.to_numpy(dtype=float), long.to_numpy(dtype=float), out=np.full(len(expected), np.nan),
                where=long.to_numpy(dtype=float) > 0,
            )
    demand_features = registry.loc[
        registry.feature_group.isin(["history", "lag", "rolling", "trend"]) & registry.status.eq("enabled"),
        "feature_name",
    ].tolist()
    origin_rows = table.drop_duplicates([*SERIES_KEYS, "origin_week_start_date"])[
        [*SERIES_KEYS, "origin_week_start_date", *demand_features]
    ].rename(columns={"origin_week_start_date": "week_start_date"})
    expected_rows = expected[[*SERIES_KEYS, "week_start_date", *demand_features]]
    joined = expected_rows.merge(
        origin_rows, on=[*SERIES_KEYS, "week_start_date"], how="inner", suffixes=("_expected", "_actual"),
        validate="one_to_one",
    )
    if len(joined) != len(origin_rows):
        raise FeatureValidationError("A direct-table origin is absent from the canonical Phase 11 panel.")
    for name in demand_features:
        expected_values = joined[f"{name}_expected"].to_numpy(dtype=float)
        actual_values = joined[f"{name}_actual"].to_numpy(dtype=float)
        if not np.isclose(expected_values, actual_values, equal_nan=True).all():
            raise FeatureValidationError(f"Demand feature lineage mismatch: {name}.")
    return {
        "status": "PASS",
        "enabled_feature_count": int(len(enabled)),
        "future_actual_demand_features": int(enabled.uses_future_actual_demand.sum()),
        "target_columns_in_predictors": int(len(set(TARGET_COLUMNS).intersection(predictors))),
        "reconciled_demand_feature_count": int(len(demand_features)),
    }
