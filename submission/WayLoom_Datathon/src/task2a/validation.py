"""Frozen rolling-origin validation plan for Task 2A forecasts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.task2a.eda import EDAValidationError, validate_task2a_eda_input
from src.task2a.features import audit_future_demand_leakage as audit_phase13_feature_lineage
from src.task2a.features import build_feature_registry, get_task2a_feature_columns
from src.task2a.multihorizon import validate_multihorizon_table


SERIES = ("depot", "brand")
ORIGIN = "origin_week_start_date"
TARGET = "target_week_start_date"
HORIZON = "horizon_weeks"
EXPECTED_HORIZONS = tuple(range(1, 11))


class ForecastValidationError(ValueError):
    """A frozen backtest rule or source-coverage requirement was violated."""


@dataclass(frozen=True)
class ForecastBacktestSplit:
    backtest_id: str
    origin_week_start_date: pd.Timestamp
    train_indices: np.ndarray
    validation_indices: np.ndarray
    validation_target_start_date: pd.Timestamp
    validation_target_end_date: pd.Timestamp


def load_validation_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    validate_validation_config(config)
    return config


def validate_validation_config(config: dict[str, Any]) -> None:
    if not isinstance(config, dict):
        raise ForecastValidationError("Validation configuration must be a mapping.")
    if config.get("version") != 1:
        raise ForecastValidationError("Validation configuration version must be 1.")
    settings = config.get("backtesting", {})
    required = {"validation_horizon_weeks": 10, "require_full_horizon": True,
                "require_same_origins_across_series": True, "choose_origins_from_date_coverage_only": True}
    for key, expected in required.items():
        if settings.get(key) != expected:
            raise ForecastValidationError(f"backtesting.{key} must be {expected!r}.")
    if settings.get("strategy") != "rolling_origin":
        raise ForecastValidationError("backtesting.strategy must be rolling_origin.")
    for key in ("n_backtests", "step_weeks", "minimum_training_weeks"):
        value = settings.get(key)
        if type(value) is not int or value < 1:
            raise ForecastValidationError(f"backtesting.{key} must be a positive integer.")
    if config.get("series_key") != list(SERIES) or config.get("origin_column") != ORIGIN or config.get("target_week_column") != TARGET or config.get("horizon_column") != HORIZON:
        raise ForecastValidationError("Validation keys must match the canonical Phase 13 table.")
    eligibility = config.get("training_eligibility", {})
    if eligibility.get("require_target_week_on_or_before_origin") is not True or eligibility.get("require_feature_source_week_on_or_before_origin") is not True:
        raise ForecastValidationError("Training target and feature-source availability rules must be enabled.")
    metrics = config.get("metrics", {})
    if metrics.get("total_volume", {}).get("primary") != "mae" or metrics.get("chilled_volume", {}).get("primary") != "mae" or metrics.get("chilled_volume", {}).get("primary_population") != "Fresh":
        raise ForecastValidationError("Frozen primary metric contract is total MAE and Fresh chilled MAE.")
    secondary = {"rmse", "wape", "mean_bias_m3", "p90_absolute_error"}
    if any(set(metrics.get(target, {}).get("secondary", [])) != secondary for target in ("total_volume", "chilled_volume")):
        raise ForecastValidationError("Frozen secondary metrics must be RMSE, WAPE, bias and P90 absolute error.")
    structural = metrics.get("structural_zero_chilled", {})
    if set(structural.get("brands", [])) != {"Style", "Tech"} or structural.get("required_value") != 0:
        raise ForecastValidationError("Style and Tech chilled demand must be structural zero.")
    if metrics.get("wape_zero_denominator") is not None or "wape_zero_denominator" not in metrics:
        raise ForecastValidationError("Zero-denominator WAPE policy must be null.")
    diagnostics = config.get("prediction_diagnostics", {})
    if diagnostics.get("evaluate_raw_predictions") is not True or diagnostics.get("apply_phase17_postprocessing") is not False:
        raise ForecastValidationError("Forecast evaluation must retain raw predictions.")
    if any(diagnostics.get(key) is not True for key in ("count_negative_predictions", "count_nonfinite_predictions", "count_chilled_gt_total")):
        raise ForecastValidationError("All frozen raw-prediction diagnostics must be enabled.")
    series = config.get("series_evaluation", {})
    if series.get("minimum_points") != 10 or series.get("report_macro_average") is not True or series.get("report_micro_average") is not True:
        raise ForecastValidationError("Per-series support and micro/macro reporting must remain frozen.")
    horizons = config.get("horizon_diagnostics", {})
    if horizons.get("enabled") is not True or horizons.get("horizons") != list(EXPECTED_HORIZONS):
        raise ForecastValidationError("Horizon diagnostics must cover 1..10.")


def _settings(config: dict[str, Any]) -> dict[str, Any]:
    validate_validation_config(config)
    return config["backtesting"]


def _canonical_panel(panel: pd.DataFrame) -> pd.DataFrame:
    try:
        return validate_task2a_eda_input(panel)
    except EDAValidationError as error:
        raise ForecastValidationError(str(error)) from error


def validate_phase13_multihorizon_table(panel: pd.DataFrame, table: pd.DataFrame,
                                        feature_config: dict[str, Any] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Check the Phase 13 table against canonical panel dates, labels and lineage."""
    history = _canonical_panel(panel)
    candidate = table.copy(deep=True).reset_index(drop=True)
    for column in (ORIGIN, TARGET, "origin_demand_feature_max_source_week"):
        if column not in candidate:
            raise ForecastValidationError(f"Direct-table {column} is missing.")
        candidate[column] = pd.to_datetime(candidate[column], errors="coerce").dt.normalize()
        if candidate[column].isna().any():
            raise ForecastValidationError(f"Direct-table {column} contains an invalid date.")
    target_calendar = build_feature_registry(feature_config)
    calendar_columns = target_calendar.loc[target_calendar.feature_group.eq("target_calendar"), "feature_name"].tolist()
    if "target_festival_names" in candidate:
        # CSV round trips represent the valid no-festival value as an empty cell.
        candidate["target_festival_names"] = candidate["target_festival_names"].fillna("")
    if any(column not in candidate for column in calendar_columns) or candidate[calendar_columns].isna().any().any():
        raise ForecastValidationError("A target-week official calendar feature is missing.")
    if "target_calendar_days" not in candidate or not candidate.target_calendar_days.eq(7).all():
        raise ForecastValidationError("A target week lacks complete official calendar coverage.")
    try:
        validate_multihorizon_table(candidate, feature_config)
        audit_phase13_feature_lineage(history, candidate, feature_config)
    except (EDAValidationError, ValueError) as error:
        raise ForecastValidationError(str(error)) from error
    source = history[[*SERIES, "week_start_date", "iso_year", "iso_week", "week_status",
                      "total_volume_m3", "chilled_volume_m3"]].rename(columns={
                          "iso_year": "panel_iso_year", "iso_week": "panel_iso_week",
                          "week_status": "panel_week_status", "total_volume_m3": "panel_total_volume_m3",
                          "chilled_volume_m3": "panel_chilled_volume_m3",
                      })
    for side, keys in (("origin", [ORIGIN]), ("target", [TARGET])):
        joined = candidate.merge(source, left_on=[*SERIES, *keys], right_on=[*SERIES, "week_start_date"],
                                 how="left", validate="many_to_one")
        if joined["week_start_date"].isna().any():
            raise ForecastValidationError(f"Direct-table {side} is missing from the canonical panel.")
        if not joined[f"{side}_iso_year"].eq(joined.panel_iso_year).all() or not joined[f"{side}_iso_week"].eq(joined.panel_iso_week).all() or not joined[f"{side}_panel_status"].eq(joined.panel_week_status).all():
            raise ForecastValidationError(f"Direct-table {side} metadata disagrees with the canonical panel.")
        if side == "target":
            for direct, canonical in (("target_total_volume_m3", "panel_total_volume_m3"),
                                      ("target_chilled_volume_m3", "panel_chilled_volume_m3")):
                if not np.isclose(joined[direct].to_numpy(dtype=float), joined[canonical].to_numpy(dtype=float)).all():
                    raise ForecastValidationError(f"Direct-table {direct} disagrees with the canonical panel.")
    candidate = candidate.sort_values([*SERIES, ORIGIN, HORIZON], kind="stable").reset_index(drop=True)
    return history, candidate


def resolve_required_series(history: pd.DataFrame, table: pd.DataFrame) -> tuple[tuple[str, str], ...]:
    required = tuple(sorted(tuple(row) for row in history[list(SERIES)].drop_duplicates().itertuples(index=False, name=None)))
    available = {tuple(row) for row in table[list(SERIES)].drop_duplicates().itertuples(index=False, name=None)}
    if not required or set(required) != available:
        raise ForecastValidationError("Required panel series are missing or unexpected in the direct table.")
    return required


def validate_ten_week_window(rows: pd.DataFrame, origin: pd.Timestamp, series: tuple[str, str]) -> None:
    """Require one row for each exact target week at a series/origin."""
    actual = rows.loc[rows.depot.eq(series[0]) & rows.brand.eq(series[1]) & rows[ORIGIN].eq(origin)].sort_values(HORIZON, kind="stable")
    if len(actual) != 10 or sorted(actual[HORIZON].tolist()) != list(EXPECTED_HORIZONS):
        raise ForecastValidationError("Validation window must have exactly horizons 1..10 once per required series.")
    expected_dates = origin + pd.to_timedelta(actual[HORIZON].to_numpy(dtype=int) * 7, unit="D")
    if not pd.DatetimeIndex(actual[TARGET]).equals(pd.DatetimeIndex(expected_dates)):
        raise ForecastValidationError("Validation target dates are not origin plus exact weekly horizons.")


def find_eligible_forecast_origins(history: pd.DataFrame, table: pd.DataFrame,
                                   required_series: tuple[tuple[str, str], ...],
                                   config: dict[str, Any]) -> list[pd.Timestamp]:
    """Use only date/status coverage; demand magnitudes never choose origins."""
    settings = _settings(config)
    known = history.loc[history.week_status.isin(["OBSERVED_DEMAND", "CONFIRMED_ZERO"])]
    dates_by_series = {
        series: set(known.loc[known.depot.eq(series[0]) & known.brand.eq(series[1]), "week_start_date"])
        for series in required_series
    }
    candidates = sorted(set.intersection(*dates_by_series.values()))
    eligible: list[pd.Timestamp] = []
    for origin in candidates:
        if any(sum(date <= origin for date in dates_by_series[series]) < settings["minimum_training_weeks"] for series in required_series):
            continue
        if any(not all(origin + pd.Timedelta(weeks=h) in dates_by_series[series] for h in EXPECTED_HORIZONS)
               for series in required_series):
            continue
        if any(len(table.loc[table.depot.eq(series[0]) & table.brand.eq(series[1]) & table[ORIGIN].eq(origin)]) != 10
               for series in required_series):
            continue
        for series in required_series:
            validate_ten_week_window(table, origin, series)
        eligible.append(origin)
    return eligible


def select_rolling_origins(eligible: list[pd.Timestamp], config: dict[str, Any]) -> list[pd.Timestamp]:
    settings = _settings(config)
    remaining = sorted(set(eligible))
    chosen: list[pd.Timestamp] = []
    while remaining and len(chosen) < settings["n_backtests"]:
        origin = remaining[-1]
        chosen.append(origin)
        cutoff = origin - pd.Timedelta(weeks=settings["step_weeks"])
        remaining = [date for date in remaining if date <= cutoff]
    if len(chosen) != settings["n_backtests"]:
        raise ForecastValidationError("INSUFFICIENT_BACKTEST_HISTORY: cannot select the configured full ten-week backtests.")
    return sorted(chosen)


def make_forecast_backtest_split(table: pd.DataFrame, origin: pd.Timestamp, backtest_id: str,
                                 required_series: tuple[tuple[str, str], ...]) -> ForecastBacktestSplit:
    train_mask = table[TARGET].le(origin)
    valid_mask = table[ORIGIN].eq(origin)
    train_indices = np.flatnonzero(train_mask.to_numpy())
    validation_indices = np.flatnonzero(valid_mask.to_numpy())
    if not len(train_indices) or not len(validation_indices):
        raise ForecastValidationError("A backtest has empty training or validation rows.")
    if len(validation_indices) != len(required_series) * 10:
        raise ForecastValidationError("A backtest is missing required series or horizons.")
    for series in required_series:
        validate_ten_week_window(table.iloc[validation_indices], origin, series)
    if table.iloc[train_indices][TARGET].max() > origin or table.iloc[validation_indices][TARGET].min() <= origin:
        raise ForecastValidationError("A backtest violates training-label or validation-target availability.")
    if np.intersect1d(train_indices, validation_indices).size:
        raise ForecastValidationError("Training and validation row indices overlap.")
    return ForecastBacktestSplit(
        backtest_id, origin, train_indices, validation_indices,
        table.iloc[validation_indices][TARGET].min(), table.iloc[validation_indices][TARGET].max(),
    )


def audit_future_demand_leakage(history: pd.DataFrame, table: pd.DataFrame,
                                splits: list[ForecastBacktestSplit],
                                feature_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Reconcile Phase 13 features, label cutoffs and the single-block X contract."""
    try:
        lineage = audit_phase13_feature_lineage(history, table, feature_config)
    except ValueError as error:
        raise ForecastValidationError(str(error)) from error
    predictors = get_task2a_feature_columns(feature_config)
    demand_columns = [name for name in predictors if name.startswith(("total_", "chilled_")) or name == "history_weeks_available"]
    for split in splits:
        train = table.iloc[split.train_indices]
        valid = table.iloc[split.validation_indices]
        if not train[TARGET].le(split.origin_week_start_date).all() or not valid[TARGET].gt(split.origin_week_start_date).all():
            raise ForecastValidationError("Training labels or validation targets cross the forecast origin.")
        for _, block in valid.groupby(list(SERIES), sort=False):
            if any(block[name].nunique(dropna=False) != 1 for name in demand_columns):
                raise ForecastValidationError("Future actual demand changed predictors within a ten-week forecast block.")
    return {
        "predictor_source_time_pass": True,
        "training_target_availability_pass": True,
        "future_target_mutation_pass": "SYNTHETIC_TESTED",
        "cross_horizon_isolation_pass": True,
        "validation_fit_scope_contract_pass": True,
        "forbidden_future_feature_count": lineage["future_actual_demand_features"],
    }


def build_rolling_origin_plan(panel: pd.DataFrame, multihorizon_table: pd.DataFrame,
                              feature_config: dict[str, Any] | None,
                              validation_config: dict[str, Any]) -> dict[str, Any]:
    """Return canonical table and reusable split indices without fitting a model."""
    _settings(validation_config)
    history, table = validate_phase13_multihorizon_table(panel, multihorizon_table, feature_config)
    required = resolve_required_series(history, table)
    eligible = find_eligible_forecast_origins(history, table, required, validation_config)
    origins = select_rolling_origins(eligible, validation_config)
    splits = [make_forecast_backtest_split(table, origin, f"BT{i:02d}", required)
              for i, origin in enumerate(origins, start=1)]
    audit = audit_future_demand_leakage(history, table, splits, feature_config)
    if any(not set(splits[i].train_indices).issubset(set(splits[i + 1].train_indices)) for i in range(len(splits) - 1)):
        raise ForecastValidationError("Training information did not expand across backtests.")
    return {"table": table, "splits": splits, "required_series": required,
            "eligible_origin_count": len(eligible), "leakage_audit": audit}
