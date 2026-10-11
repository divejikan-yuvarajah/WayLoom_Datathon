"""Leakage-safe direct multi-horizon Task 2A training-table assembly."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.task2a.calendar_features import build_target_week_calendar_features, validate_target_calendar_coverage
from src.task2a.eda import EDAValidationError, SERIES_KEYS
from src.task2a.features import (
    METADATA_COLUMNS,
    TARGET_COLUMNS,
    build_feature_registry,
    build_origin_demand_features,
    feature_coverage_summary,
    get_task2a_feature_columns,
    audit_future_demand_leakage,
    validate_feature_config,
)


ELIGIBLE_TARGET_STATUSES = {"OBSERVED_DEMAND", "CONFIRMED_ZERO"}


class MultiHorizonValidationError(EDAValidationError):
    """Raised when direct multi-horizon labels or calendar joins are unsafe."""


def _max_horizon(config: dict[str, Any] | None) -> int:
    if config is None:
        return 10
    validate_feature_config(config)
    return int(config.get("multihorizon", {}).get("max_horizon", config.get("horizon", {}).get("max_weeks", 10)))


def _eligible_target_statuses(config: dict[str, Any] | None) -> set[str]:
    if config is None:
        return ELIGIBLE_TARGET_STATUSES
    validate_feature_config(config)
    configured = config.get("target_eligibility", {}).get("allowed_panel_statuses", sorted(ELIGIBLE_TARGET_STATUSES))
    statuses = {str(value).strip().upper() for value in configured}
    if statuses != ELIGIBLE_TARGET_STATUSES:
        raise MultiHorizonValidationError("Only OBSERVED_DEMAND and CONFIRMED_ZERO may be training targets.")
    return statuses


def build_direct_multihorizon_table(panel: pd.DataFrame, calendar: pd.DataFrame,
                                    config: dict[str, Any] | None = None) -> pd.DataFrame:
    """Create rows ``(series, origin t, horizon h)`` with labels at ``t+h``.

    The only demand-derived predictors are constructed once at the origin.  A
    future panel lookup contributes labels only; it never overwrites or joins
    future demand values into the predictor set.
    """
    try:
        origins = build_origin_demand_features(panel, config)
    except EDAValidationError as error:
        raise MultiHorizonValidationError(str(error)) from error
    max_horizon = _max_horizon(config)
    try:
        calendar_features = validate_target_calendar_coverage(build_target_week_calendar_features(calendar))
    except EDAValidationError as error:
        raise MultiHorizonValidationError(str(error)) from error
    calendar_features = calendar_features.rename(columns={
        "iso_year": "target_iso_year", "iso_week": "target_iso_week",
    })
    base = origins.rename(columns={
        "iso_year": "origin_iso_year", "iso_week": "origin_iso_week",
        "week_start_date": "origin_week_start_date", "week_status": "origin_panel_status",
        "demand_feature_max_source_week": "origin_demand_feature_max_source_week",
    }).copy()
    horizons = pd.DataFrame({"horizon_weeks": range(1, max_horizon + 1)})
    base["_join_key"] = 1
    horizons["_join_key"] = 1
    candidates = base.merge(horizons, on="_join_key", how="inner", validate="many_to_many").drop(columns="_join_key")
    candidates["target_week_start_date"] = candidates["origin_week_start_date"] + pd.to_timedelta(candidates["horizon_weeks"], unit="W")

    labels = origins[[*SERIES_KEYS, "week_start_date", "iso_year", "iso_week", "total_volume_m3", "chilled_volume_m3", "week_status"]].rename(columns={
        "week_start_date": "target_week_start_date", "iso_year": "target_iso_year", "iso_week": "target_iso_week",
        "total_volume_m3": TARGET_COLUMNS[0], "chilled_volume_m3": TARGET_COLUMNS[1], "week_status": "target_panel_status",
    })
    result = candidates.merge(labels, on=[*SERIES_KEYS, "target_week_start_date"], how="inner", validate="many_to_one")
    result = result.loc[result.target_panel_status.isin(_eligible_target_statuses(config))].copy()
    result = result.merge(calendar_features, on=["target_iso_year", "target_iso_week"], how="left", validate="many_to_one")
    if result.empty:
        raise MultiHorizonValidationError("No eligible observed or confirmed-zero direct-horizon targets were assembled.")
    target_calendar_columns = [column for column in calendar_features if column.startswith("target_")]
    if result[target_calendar_columns].isna().any().any() or not result.target_calendar_days.eq(7).all():
        raise MultiHorizonValidationError("Official target-week calendar coverage is incomplete for an eligible label.")
    validate_multihorizon_table(result, config)
    return result.sort_values([*SERIES_KEYS, "origin_week_start_date", "horizon_weeks"], kind="stable").reset_index(drop=True)


def validate_multihorizon_table(table: pd.DataFrame, config: dict[str, Any] | None = None) -> None:
    max_horizon = _max_horizon(config)
    required = [*METADATA_COLUMNS, *TARGET_COLUMNS, *get_task2a_feature_columns(config)]
    missing = [column for column in required if column not in table]
    if missing:
        raise MultiHorizonValidationError(f"multi-horizon table missing columns: {', '.join(missing)}")
    key = [*SERIES_KEYS, "origin_week_start_date", "horizon_weeks"]
    if table.duplicated(key).any():
        raise MultiHorizonValidationError("multi-horizon table has duplicate series/origin/horizon keys.")
    if not table.horizon_weeks.between(1, max_horizon).all():
        raise MultiHorizonValidationError("multi-horizon table includes a horizon outside the configured range.")
    origin = pd.to_datetime(table.origin_week_start_date)
    target = pd.to_datetime(table.target_week_start_date)
    source_max = pd.to_datetime(table.origin_demand_feature_max_source_week)
    if not source_max.le(origin).all():
        raise MultiHorizonValidationError("A demand-derived feature references a week after its forecast origin.")
    if not (target.sub(origin).dt.days.eq(table.horizon_weeks.astype(int) * 7)).all():
        raise MultiHorizonValidationError("target week does not equal origin week plus horizon weeks.")
    if not table.target_panel_status.isin(_eligible_target_statuses(config)).all():
        raise MultiHorizonValidationError("multi-horizon training labels include a non-eligible target status.")
    predictors = get_task2a_feature_columns(config)
    forbidden = set(TARGET_COLUMNS) | set(METADATA_COLUMNS)
    if forbidden.intersection(predictors):
        raise MultiHorizonValidationError("Target or metadata entered the predictor registry.")
    for _, group in table.groupby([*SERIES_KEYS, "origin_week_start_date"], sort=False):
        changing = [
            column for column in predictors
            if column != "horizon_weeks" and not column.startswith("target_")
            and group[column].nunique(dropna=False) > 1
        ]
        if changing:
            raise MultiHorizonValidationError("Origin-derived predictors vary across horizons: " + ", ".join(changing))


def assemble_phase13_artifacts(panel: pd.DataFrame, calendar: pd.DataFrame,
                               config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build tables plus privacy-safe metadata for the local operator report."""
    origins = build_origin_demand_features(panel, config)
    table = build_direct_multihorizon_table(panel, calendar, config)
    registry = build_feature_registry(config)
    return {
        "origin_features": origins,
        "multihorizon_train": table,
        "registry": registry,
        "summary": {
            "status": "PASS",
            "n_origin_rows": int(len(origins)),
            "n_multihorizon_rows": int(len(table)),
            "max_horizon_weeks": _max_horizon(config),
            "feature_coverage": feature_coverage_summary(table, config),
            "leakage_audit": audit_future_demand_leakage(panel, table, config),
        },
    }
